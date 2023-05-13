import functools
from pathlib import Path

from PyQt6 import QtWidgets, QtCore, QtGui

from doubleblind import __version__, blinding, gui_style


class HelpButton(QtWidgets.QToolButton):
    __slots__ = {'param_name': 'name of the parameter',
                 'desc': 'description of the parameter'}

    def __init__(self, desc: str, parent=None):
        super().__init__(parent)
        self.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion))
        self.desc = desc
        self.clicked.connect(self._show_help_desc)

    QtCore.pyqtSlot()

    def _show_help_desc(self):
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), self.desc)


class PathLineEdit(QtWidgets.QWidget):
    textChanged = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = QtWidgets.QLineEdit('', self)
        self.open_button = QtWidgets.QPushButton('Choose folder', self)
        self._is_legal = False

        self.layout = QtWidgets.QGridLayout(self)
        self.setLayout(self.layout)
        self.layout.addWidget(self.open_button, 1, 0)
        self.layout.addWidget(self.file_path, 1, 1)

        self.file_path.textChanged.connect(self._check_legality)
        self.open_button.clicked.connect(self.choose_folder)
        contents = 'No folder chosen'
        self.file_path.setText(contents)

    def clear(self):
        self.file_path.clear()

    @property
    def is_legal(self):
        return self._is_legal

    def _check_legality(self):
        current_path = self.file_path.text()
        if Path(current_path).is_dir() and Path(current_path).exists():
            self._is_legal = True
        else:
            self._is_legal = False
        self.set_file_path_bg_color()
        self.textChanged.emit(self.is_legal)

    def set_file_path_bg_color(self):
        if self.is_legal:
            self.file_path.setStyleSheet("QLineEdit{border: 1.5px solid #57C4AD;}")
        else:
            self.file_path.setStyleSheet("QLineEdit{border: 1.5px solid #DB4325;}")

    def disable_bg_color(self):
        self.file_path.setStyleSheet("QLineEdit{}")

    def setEnabled(self, to_enable: bool):
        self.setDisabled(not to_enable)

    def setDisabled(self, to_disable: bool):
        if to_disable:
            self.disable_bg_color()
        else:
            self.set_file_path_bg_color()
        super().setDisabled(to_disable)

    def choose_folder(self):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose a folder")
        if dirname:
            self.file_path.setText(dirname)

    def text(self):
        return self.file_path.text()

    def setText(self, text: str):
        return self.file_path.setText(text)

    def path(self):
        return Path(self.text())


class OptionalPath(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.other = PathLineEdit(self)
        self.checkbox = QtWidgets.QCheckBox('Disable this parameter?')
        self.toggled = self.checkbox.toggled

        self.init_ui()

    def clear(self):
        self.checkbox.setChecked(False)
        try:
            self.other.clear()
        except AttributeError:
            pass

    def init_ui(self):
        self.toggled.connect(self.other.setDisabled)
        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.other)
        self.checkbox.setChecked(True)

    def check_other(self):
        self.other.setDisabled(self.checkbox.isChecked())

    def path(self):
        if self.checkbox.isChecked():
            return None
        return self.other.path()


class TabPage(QtWidgets.QWidget):
    FILE_TYPES = {'Olympus microscope images (.vsi)': 0,
                  'Image/video files (.tif, .png, .mp4, etc...)': 1,
                  'Other file type': 2}
    ENCODER_TYPES = {0: blinding.VSICoder,
                     1: blinding.ImageCoder,
                     2: blinding.GenericCoder}
    PARAM_DESCS = {0: ('file_types', 'File types to blind:',
                       'Choose the type of files you want to blind. '),
                   1: ('other_file_type', 'File format to blind:',
                       ''),
                   2: ('input_dir', 'Input directory:',
                       'Choose the input directory, which contains the files you want to blind. '),
                   3: ('output_dir', 'Output directory for a mapping table:\n(optional)',
                       'Choose the output directory in which the filename mapping table will be saved. \n'
                       "If you don't set an output directory, "
                       "DoubleBlind will save the mapping table in the input directory. \n"
                       "The mapping table is for your convenience only, "
                       "DoubleBlind can later un-blind your files without it!"),
                   4: ('recursive', 'Apply to files in subfolders:',
                       'Choose whether blinding should be applied recuresively to files in sub-folders as well, '
                       'or only to files in the top level. ')}

    def __init__(self, tab_name: str, parent=None):
        super().__init__(parent)
        self.tab_name = tab_name
        self.layout = QtWidgets.QVBoxLayout(self)
        self.param_grid = QtWidgets.QGridLayout()
        self.file_types = QtWidgets.QComboBox(self)
        self.other_file_type = QtWidgets.QLineEdit(self)
        self.input_dir = PathLineEdit(self)
        self.output_dir = OptionalPath(self)
        self.recursive = QtWidgets.QCheckBox(self)
        self.apply_button = QtWidgets.QPushButton(self.tab_name)

    def init_ui(self):
        self.apply_button.clicked.connect(self.run)
        self.recursive.setChecked(True)
        self.file_types.currentTextChanged.connect(self.show_file_type_box)
        self.layout.addLayout(self.param_grid)

        for i, (widget_name, label, desc) in self.PARAM_DESCS.items():
            self.param_grid.addWidget(QtWidgets.QLabel(label, self), i, 0)
            self.param_grid.addWidget(getattr(self, widget_name), i, 1)
            self.param_grid.addWidget(HelpButton(desc, self), i, 2)

        self.param_grid.setColumnStretch(1, 1)
        self.layout.addWidget(self.apply_button)
        self.file_types.addItems(self.FILE_TYPES.keys())

    def show_file_type_box(self, combobox_content: str):
        show_lineedit = self.FILE_TYPES[combobox_content] == 2
        for ind in range(3):
            widget = self.param_grid.itemAtPosition(1, ind).widget()
            widget.setVisible(show_lineedit)

    def run(self):
        raise NotImplementedError

    def get_encoder(self):
        encoder_type = self.ENCODER_TYPES[self.FILE_TYPES[self.file_types.currentText()]]
        args = [self.input_dir.path(), self.recursive.isChecked()]
        if encoder_type == blinding.GenericCoder:
            file_type = self.other_file_type.text()
            if not file_type.startswith('.'):
                file_type = '.' + file_type
            args.append({file_type})
        encoder = encoder_type(*args)
        return encoder


class EncodeTab(TabPage):
    def __init__(self, parent=None):
        super().__init__('Blind data', parent)
        self.init_ui()

    def run(self):
        encoder = self.get_encoder()
        encoder.blind(self.output_dir.path())
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle('Data blinded')
        msg.setText('Data was blinded successfully!')
        msg.exec()


class DecodeTab(TabPage):
    PARAM_DESCS = TabPage.PARAM_DESCS.copy()
    PARAM_DESCS.pop(3)
    PARAM_DESCS[3] = ('other_files', 'Replace blinded names in more files:\n(optional)',
                      'Folder with additional files (such as tables with quantification results) '
                      'which contain the blinded names. \n'
                      'DoubleBlind will look for the blinded names in these files, '
                      'and replace them with the original names. ')

    def __init__(self, parent=None):
        super().__init__('Un-blind data', parent)
        self.other_files = OptionalPath(self)
        self.output_dir.deleteLater()
        self.init_ui()

    def run(self):
        encoder = self.get_encoder()
        others = encoder.unblind(self.other_files.path())
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle('Data un-blinded')
        text = 'Data was un-blinded successfully!'
        if len(others) > 0:
            text += '\nThe folli=owing additional data files were unblinded:\n\n' + \
                    '\n'.join([f"'{item.as_posix()}'" for item in others if item is not None])
            print(others)
            print(text)
        msg.setText(text)
        msg.exec()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.encode_tab = EncodeTab(self)
        self.decode_tab = DecodeTab(self)
        self.tabs = QtWidgets.QTabWidget(self)
        self.menu_bar = QtWidgets.QMenuBar(self)

        self.tabs.addTab(self.encode_tab, self.encode_tab.tab_name)
        self.tabs.addTab(self.decode_tab, self.decode_tab.tab_name)
        self.setCentralWidget(self.tabs)
        self.setMenuBar(self.menu_bar)
        self.setWindowTitle(f'DoubleBlind {__version__}')

        self.font_name = 'Arial'
        self.base_font_size = 11
        self.dark_mode = False

        self.update_style_sheet()
        self.init_menus()

    def init_menus(self):
        view_menu = self.menu_bar.addMenu('View')

        self.dark_mode_action = QtGui.QAction("Dark mode")
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.triggered.connect(self.update_dark_mode)

        self.font_size_action = view_menu.addMenu('Font size')
        group = QtGui.QActionGroup(self)
        group.setExclusive(True)
        for size in (8, 10, 11, 12, 14, 18, 24, 36, 48, 72):
            action = QtGui.QAction(str(size), self)
            action.setCheckable(True)
            action.triggered.connect(functools.partial(self.update_font_size, size))
            group.addAction(action)
            self.font_size_action.addAction(action)
            if self.base_font_size == size:
                action.trigger()

        view_menu.addActions([self.dark_mode_action])
        help_menu = self.menu_bar.addMenu('Help')

    @QtCore.pyqtSlot(bool)
    def update_dark_mode(self, dark_mode: bool):
        self.dark_mode = dark_mode
        self.update_style_sheet()

    @QtCore.pyqtSlot(bool)
    def update_font_size(self, base_font_size: int, enabled: bool):
        if enabled:
            self.base_font_size = base_font_size
            self.update_style_sheet()

    def update_style_sheet(self):
        self.setStyleSheet(gui_style.get_stylesheet(self.font_name, self.base_font_size, self.dark_mode))

    def check_for_updates(self, confirm_updated: bool = True):
        pass
