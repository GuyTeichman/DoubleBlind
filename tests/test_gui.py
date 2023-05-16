from doubleblind import __version__
from doubleblind.gui import *

LEFT_CLICK = QtCore.Qt.MouseButton.LeftButton
RIGHT_CLICK = QtCore.Qt.MouseButton.RightButton


def test_main_window(qtbot):
    main_window = MainWindow()
    qtbot.addWidget(main_window)

    assert main_window.windowTitle() == f'DoubleBlind {__version__}'
    assert main_window.tabs.count() == 2
    assert isinstance(main_window.encode_tab, EncodeTab)
    assert isinstance(main_window.decode_tab, DecodeTab)


def test_encode_tab(qtbot):
    encode_tab = EncodeTab()
    qtbot.addWidget(encode_tab)

    assert encode_tab.tab_name == 'Blind data'
    assert encode_tab.recursive.isChecked()

    # Test if the file_types combo box contains the correct number of items
    assert encode_tab.file_types.count() == len(encode_tab.FILE_TYPES)


def test_decode_tab(qtbot):
    decode_tab = DecodeTab()
    qtbot.addWidget(decode_tab)

    assert decode_tab.tab_name == 'Un-blind data'

    # Test if the file_types combo box contains the correct number of items
    assert decode_tab.file_types.count() == len(decode_tab.FILE_TYPES)


def test_dark_mode(qtbot):
    main_window = MainWindow()
    qtbot.addWidget(main_window)

    # Toggle dark mode and check if the settings value is updated
    main_window.dark_mode_action.setChecked(True)
    main_window.update_dark_mode(True)
    assert main_window.settings.value('dark_mode') == 'dark'

    main_window.dark_mode_action.setChecked(False)
    main_window.update_dark_mode(False)
    assert main_window.settings.value('dark_mode') == 'light'


def test_update_font_size(qtbot):
    main_window = MainWindow()
    qtbot.addWidget(main_window)

    test_size = 14
    test_action = None
    for action in main_window.font_size_action.actions():
        if action.text() == str(test_size):
            test_action = action
            break

    if test_action:
        test_action.trigger()
        assert main_window.settings.value('base_font_size') == test_size


def test_ErrorMessage_message(qtbot):
    err_text = 'my error text'
    try:
        raise ValueError(err_text)
    except ValueError as e:
        err_tb = e.__traceback__
        err_value = e
    dialog = ErrorMessage(ValueError, err_value, err_tb)
    dialog.show()
    qtbot.add_widget(dialog)
    assert 'ValueError' in dialog.widgets['error_text'].toPlainText()
    assert err_text in dialog.widgets['error_text'].toPlainText()


def test_ErrorMessage_close(qtbot, monkeypatch):
    closed = []

    def mock_close(*args, **kwargs):
        closed.append(1)

    monkeypatch.setattr(ErrorMessage, 'close', mock_close)
    err_text = 'my error text'
    try:
        raise ValueError(err_text)
    except ValueError as e:
        err_tb = e.__traceback__
        err_value = e
    dialog = ErrorMessage(ValueError, err_value, err_tb)
    dialog.show()
    qtbot.add_widget(dialog)
    qtbot.mouseClick(dialog.widgets['ok_button'], LEFT_CLICK)

    assert closed == [1]


def test_ErrorMessage_copy_to_clipboard(qtbot, monkeypatch):
    err_text = 'my error text'
    try:
        raise ValueError(err_text)
    except ValueError as e:
        err_tb = e.__traceback__
        err_value = e

    dialog = ErrorMessage(ValueError, err_value, err_tb)
    dialog.show()
    qtbot.add_widget(dialog)
    qtbot.mouseClick(dialog.widgets['copy_button'], LEFT_CLICK)

    assert 'ValueError' in QtWidgets.QApplication.clipboard().text()
    assert err_text in QtWidgets.QApplication.clipboard().text()


def test_AboutWindow(qtbot, monkeypatch):
    window = AboutWindow()


def test_HowToCiteWindow(qtbot, monkeypatch):
    exit_calls = []

    def mock_close(*args, **kwargs):
        exit_calls.append(1)

    monkeypatch.setattr(HowToCiteWindow, 'close', mock_close)

    window = HowToCiteWindow()
    qtbot.mouseClick(window.ok_button, LEFT_CLICK)
    assert exit_calls == [1]
