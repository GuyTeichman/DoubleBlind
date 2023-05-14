import functools
import sys
import traceback
from pathlib import Path

from PyQt6 import QtWidgets, QtCore, QtGui

import utils
from doubleblind import __version__, blinding, gui_style

class TextWithCopyButton(QtWidgets.QWidget):
    __slots__ = {'text': 'text',
                 'copy_button': 'copy button',
                 'copied_label': 'label indicating when copy button was pressed',
                 'layout': 'widget layout'}

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.text = text
        self.text_edit = QtWidgets.QTextBrowser(self)
        self.copy_button = QtWidgets.QPushButton('Copy to clipboard')
        self.copied_label = QtWidgets.QLabel()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.init_ui()

    def init_ui(self):
        self.text_edit.setHtml(self.text)
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.layout.addWidget(self.copy_button)
        self.layout.addWidget(self.copied_label)

    def copy_to_clipboard(self):
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.text_edit.toPlainText())
        self.copied_label.setText('Copied to clipboard')

class HowToCiteWindow(QtWidgets.QDialog):
    CITATION = """
    Teichman, G., Ewe, CK., and Rechavi, O. (2023).
    DoubleBlind: Blind and unblind file names automatically to maintain experimental integrity.
    <br>
    <a href=https://guyteichman.github.io/DoubleBlind>https://guyteichman.github.io/DoubleBlind</a>
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        img_path = str(Path(__file__).parent.joinpath('splash_transparent.png'))
        text = f"""<p align="center"><b>DoubleBlind version {__version__}</b>
                </p>
                <br><br>
                <img src="{img_path}" width="250"/>"""
        self.label = QtWidgets.QLabel(text)

        self.citation_labels = []
        self.citations = []

        txt = f"If you use DoubleBlind in your research, please cite:"
        self.citation_labels.append(QtWidgets.QLabel(txt))
        self.citations.append(TextWithCopyButton(self.CITATION))

        self.ok_button = QtWidgets.QPushButton('Close')

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll_widget = QtWidgets.QWidget(self.scroll)
        self.layout = QtWidgets.QVBoxLayout(self.scroll_widget)
        self.init_ui()

    def init_ui(self):
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.scroll_widget)
        self.layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)

        self.main_layout.addWidget(self.scroll)

        self.setWindowTitle("How to cite DoubleBlind")
        self.layout.addWidget(self.label)

        for label, citation in zip(self.citation_labels, self.citations):
            self.layout.addWidget(label)
            self.layout.addWidget(citation)

        self.ok_button.clicked.connect(self.close)
        self.layout.addWidget(self.ok_button)


class AboutWindow(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        img_path = str(Path(__file__).parent.joinpath('splash_transparent.png'))
        text = f"""<br>
                <p align="center"><b>DoubleBlind</b> version {__version__}</b>
                </p>
                <br><br>
                <img src="{img_path}" width="500"/>
                <p>
                Development lead: Guy Teichman (<a href="mailto:guyteichman@gmail.com">guyteichman@gmail.com</a>)
                </p>
                <p>
                Contributors: Chee Kiang (Ethan) Ewe
                </p>"""
        self.setText(text)
        self.setWindowTitle("About DoubleBlind")
        self.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        self.buttonClicked.connect(self.close)

class ErrorMessage(QtWidgets.QDialog):
    def __init__(self, exc_type, exc_value, exc_tb, parent=None):
        super().__init__(parent)
        self.exception = exc_type, exc_value, exc_tb
        self.layout = QtWidgets.QVBoxLayout(self)
        self.widgets = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Error")
        self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxCritical))

        self.widgets['error_label'] = QtWidgets.QLabel('<i>RNAlysis</i> has encountered the following error:')
        self.layout.addWidget(self.widgets['error_label'])

        self.widgets['error_summary'] = QtWidgets.QLabel(f'<b>{";".join(self.exception[1].args)}</b>')
        self.widgets['error_summary'].setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.widgets['error_summary'].setWordWrap(True)
        self.layout.addWidget(self.widgets['error_summary'])

        self.layout.addSpacing(3)
        self.widgets['full_text_label'] = QtWidgets.QLabel('Full error report:')
        self.layout.addWidget(self.widgets['full_text_label'])

        tb = "\n".join(traceback.format_exception(*self.exception))
        self.widgets['error_text'] = QtWidgets.QPlainTextEdit(tb)
        self.widgets['error_text'].setReadOnly(True)
        self.layout.addWidget(self.widgets['error_text'])

        self.widgets['ok_button'] = QtWidgets.QPushButton('OK')
        self.widgets['ok_button'].clicked.connect(self.close)
        self.layout.addWidget(self.widgets['ok_button'])

        self.widgets['copy_button'] = QtWidgets.QPushButton('Copy to clipboard')
        self.widgets['copy_button'].clicked.connect(self.copy_to_clipboard)
        self.layout.addWidget(self.widgets['copy_button'])

        self.widgets['copied_label'] = QtWidgets.QLabel()
        self.layout.addWidget(self.widgets['copied_label'])

    def copy_to_clipboard(self):
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText("".join(traceback.format_exception(*self.exception)), mode=cb.Clipboard)
        self.widgets['copied_label'].setText('Copied to clipboard')


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

        self.settings = QtCore.QSettings('DoubleBlind', 'DoubleBlind')
        self.error_window = None
        self.about_window = AboutWindow(self)
        self.cite_window = HowToCiteWindow(self)

        self.update_style_sheet()
        self.init_menus()

    def init_menus(self):
        view_menu = self.menu_bar.addMenu('&View')

        self.dark_mode_action = QtGui.QAction("&Dark mode")
        self.dark_mode_action.setCheckable(True)
        if self.settings.value('dark_mode') == 'dark':
            self.dark_mode_action.setChecked(True)
        self.dark_mode_action.triggered.connect(self.update_dark_mode)

        self.font_size_action = view_menu.addMenu('&Font size')
        group = QtGui.QActionGroup(self)
        group.setExclusive(True)
        for size in (8, 10, 11, 12, 14, 18, 24, 36, 48, 72):
            action = QtGui.QAction(str(size), self)
            action.setCheckable(True)
            action.triggered.connect(functools.partial(self.update_font_size, size))
            group.addAction(action)
            self.font_size_action.addAction(action)
            if self.settings.value('base_font_size') == size:
                action.trigger()

        self.reset_action = QtGui.QAction('&Reset view settings')
        self.reset_action.triggered.connect(self.clear_settings)

        view_menu.addActions([self.dark_mode_action, self.reset_action])

        help_menu = self.menu_bar.addMenu('&Help')
        self.about_action = QtGui.QAction('&About DoubleBlind')
        self.about_action.triggered.connect(self.about)

        self.update_action = QtGui.QAction('Check for &Updates...')
        self.update_action.triggered.connect(functools.partial(self.check_for_updates, True))

        self.cite_action = QtGui.QAction('How to &Cite DoubleBlind')
        self.cite_action.triggered.connect(self.how_to_cite)

        help_menu.addActions([self.update_action, self.about_action, self.cite_action])

    def about(self):
        self.about_window.exec()

    def how_to_cite(self):
        self.cite_window.exec()

    def clear_settings(self):
        self.settings.clear()
        self.dark_mode_action.setChecked(False)
        self.update_style_sheet()

    @QtCore.pyqtSlot(bool)
    def update_dark_mode(self, dark_mode: bool):
        self.settings.setValue('dark_mode', 'dark' if dark_mode else 'light')
        self.update_style_sheet()

    @QtCore.pyqtSlot(bool)
    def update_font_size(self, base_font_size: int, enabled: bool):
        if enabled:
            self.settings.setValue('base_font_size', base_font_size)
            self.update_style_sheet()

    def update_style_sheet(self):
        font_name = self.settings.value('font_name', 'Arial')
        base_font_size = self.settings.value('base_font_size', 11)
        dark_mode = self.settings.value('dark_mode', 'light')
        self.setStyleSheet(gui_style.get_stylesheet(font_name, base_font_size, dark_mode))

    def check_for_updates(self, confirm_updated: bool = True):
        if utils.is_app_outdated():
            reply = QtWidgets.QMessageBox.question(self, 'A new version is available',
                                                   'A new version of DoubleBlind is available! '
                                                   'Do you wish to download it?')
            if reply == QtWidgets.QMessageBox.Yes:
                url = QtCore.QUrl('https://github.com/GuyTeichman/DoubleBlind/releases/latest')
                if not QtGui.QDesktopServices.openUrl(url):
                    QtGui.QMessageBox.warning(self, 'Connection failed', 'Could not download new version')
            return

        if confirm_updated:
            _ = QtWidgets.QMessageBox.information(self, 'You are using the latest version of DoubleBlind',
                                                  f'Your version of DoubleBlind ({__version__}) is up to date!')

    def excepthook(self, exc_type, exc_value, exc_tb):  # pragma: no cover
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        self.error_window = ErrorMessage(exc_type, exc_value, exc_tb, self)
        self.error_window.exec()
