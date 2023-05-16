from unittest.mock import MagicMock, mock_open

import pytest

from doubleblind import gui_style
from doubleblind.gui_style import *


@pytest.fixture
def sample_parametric_stylesheet(tmp_path):
    # Create a sample parametric stylesheet file for testing
    font_name = "Arial"
    font_base_size = 12
    style_text = f"font-family: {FONTPLACEHOLDER};\nfont-size: {FONTSIZEPLACEHOLDER}pt;"
    file_path = tmp_path / PARAMETRIC_STYLESHEET_PATH
    with open(file_path, 'w') as f:
        f.write(style_text)
    return file_path


def test_get_parametric_stylesheet_invalid_input():
    # Test the get_parametric_stylesheet function with invalid input
    font_name = 123
    font_base_size = "12"
    with pytest.raises(AssertionError):
        get_parametric_stylesheet(font_base_size, font_name)


def test_get_stylesheet_invalid_dark_mode(mocker):
    # Test the get_stylesheet function with invalid dark_mode
    font_name = "Arial"
    font_base_size = 12
    dark_mode = "True"

    # Mock STYLESHEETS
    mocker.patch("doubleblind.gui_style.STYLESHEETS", {"light": qdarkstyle.LightPalette, "dark": qdarkstyle.DarkPalette})

    with pytest.raises(KeyError):
        get_stylesheet(font_name, font_base_size, dark_mode)


# Test data
parametric_stylesheet_content = """
/* style for window types : */

QWidget {
font: $FONTPLACEHOLDER;
font-size: $FONTSIZEPLACEHOLDER*1;
}

MainWindow{
font: $FONTPLACEHOLDER;
font-size: $FONTSIZEPLACEHOLDER*2;
}


TabPage {
font: $FONTPLACEHOLDER;
font-size: $FONTSIZEPLACEHOLDER*2;
}

QTabBar {
font: $FONTPLACEHOLDER;
font-weight: bold;
font-size: $FONTSIZEPLACEHOLDER;
}


DataView > QLabel {
font: $FONTPLACEHOLDER;
font-size: $FONTSIZEPLACEHOLDER*2;
}


QGroupBox {
font: $FONTPLACEHOLDER;
font-weight: bold;
font-size: $FONTSIZEPLACEHOLDER*1;
}


QLabel {
font: $FONTPLACEHOLDER;
font-size: $FONTSIZEPLACEHOLDER*1;
}


QPushButton {
font: $FONTPLACEHOLDER;
font-weight: bold;
font-size: $FONTSIZEPLACEHOLDER*1;
}

QToolButton {
font: $FONTPLACEHOLDER;
font-weight: bold;
font-size: $FONTSIZEPLACEHOLDER*1.5;
}
"""
mocked_stylesheet = "mocked_stylesheet"


@pytest.fixture
def mock_file_reading(monkeypatch):
    m = mock_open(read_data=parametric_stylesheet_content)
    monkeypatch.setattr("builtins.open", m)
    return m


@pytest.fixture
def mock_load_stylesheet(monkeypatch):
    mock_load_stylesheet = MagicMock(return_value=mocked_stylesheet)
    monkeypatch.setattr("qdarkstyle.load_stylesheet", mock_load_stylesheet)
    return mock_load_stylesheet


@pytest.mark.parametrize("font_base_size,font_name", [
    (10, "Arial"),
    (20, "Times New Roman")
])
def test_get_parametric_stylesheet(font_base_size, font_name, mock_file_reading):
    result = gui_style.get_parametric_stylesheet(font_base_size, font_name)
    assert f"{font_name}" in result
    assert f"{font_base_size}pt" in result
    assert f"{int(font_base_size * 1.5)}pt" in result
    assert f"{int(font_base_size * 2)}pt" in result


@pytest.mark.parametrize("font_name,font_base_size,dark_mode", [
    ("Arial", 10, "light"),
    ("Times New Roman", 20, "dark")
])
def test_get_stylesheet(font_name, font_base_size, dark_mode, mock_file_reading, mock_load_stylesheet):
    result = gui_style.get_stylesheet(font_name, font_base_size, dark_mode)
    assert f"{font_name}" in result
    assert f"{font_base_size}pt" in result
    assert f"{int(font_base_size * 1.5)}pt" in result
    assert f"{int(font_base_size * 2)}pt" in result
    assert mocked_stylesheet in result
