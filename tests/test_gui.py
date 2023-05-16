import pytest

from doubleblind.gui import *
from doubleblind import __version__

@pytest.fixture(scope='module')
def app():
    app = QtWidgets.QApplication([])
    yield app


def test_main_window(app, qtbot):
    main_window = MainWindow()
    qtbot.addWidget(main_window)

    assert main_window.windowTitle() == f'DoubleBlind {__version__}'
    assert main_window.tabs.count() == 2
    assert isinstance(main_window.encode_tab, EncodeTab)
    assert isinstance(main_window.decode_tab, DecodeTab)


def test_encode_tab(app, qtbot):
    encode_tab = EncodeTab()
    qtbot.addWidget(encode_tab)

    assert encode_tab.tab_name == 'Blind data'
    assert encode_tab.recursive.isChecked()

    # Test if the file_types combo box contains the correct number of items
    assert encode_tab.file_types.count() == len(encode_tab.FILE_TYPES)


def test_decode_tab(app, qtbot):
    decode_tab = DecodeTab()
    qtbot.addWidget(decode_tab)

    assert decode_tab.tab_name == 'Un-blind data'

    # Test if the file_types combo box contains the correct number of items
    assert decode_tab.file_types.count() == len(decode_tab.FILE_TYPES)


def test_dark_mode(app, qtbot):
    main_window = MainWindow()
    qtbot.addWidget(main_window)

    # Toggle dark mode and check if the settings value is updated
    main_window.dark_mode_action.setChecked(True)
    main_window.update_dark_mode(True)
    assert main_window.settings.value('dark_mode') == 'dark'

    main_window.dark_mode_action.setChecked(False)
    main_window.update_dark_mode(False)
    assert main_window.settings.value('dark_mode') == 'light'


def test_update_font_size(app, qtbot):
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
