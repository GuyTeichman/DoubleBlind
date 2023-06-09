import re
from pathlib import Path
from typing import Literal

import qdarkstyle

FONTPLACEHOLDER = "$FONTPLACEHOLDER"
FONTSIZEPLACEHOLDER = "$FONTSIZEPLACEHOLDER"
STYLESHEETS = {'light': qdarkstyle.LightPalette, 'dark': qdarkstyle.DarkPalette}
PARAMETRIC_STYLESHEET_PATH = 'parametric_style.qss'


def get_parametric_stylesheet(font_base_size: int, font_name: str):
    assert isinstance(font_base_size, int) and font_base_size >= 1
    assert isinstance(font_name, str)
    with open(Path.joinpath(Path(__file__).parent, PARAMETRIC_STYLESHEET_PATH)) as f:
        style_text = f.read()

    style_text = style_text.replace(FONTPLACEHOLDER, font_name)

    fontsize_pattern = f"\\{FONTSIZEPLACEHOLDER}\\*[0-9]*\\.?[0-9]+"
    for fontsize_match in reversed(list(re.finditer(fontsize_pattern, style_text))):
        multiplier = float(fontsize_match.group(0)[len(FONTSIZEPLACEHOLDER) + 1:])
        start, end = fontsize_match.span()
        style_text = style_text[:start] + f"{int(font_base_size * multiplier)}pt" + style_text[end:]
    style_text = style_text.replace(FONTSIZEPLACEHOLDER, str(font_base_size))
    return style_text


def get_stylesheet(font_name: str, font_base_size: int, dark_mode: Literal['light', 'dark']):
    palette = STYLESHEETS[dark_mode]
    param_stylesheet = get_parametric_stylesheet(font_base_size, font_name)
    other_stylesheet = qdarkstyle.load_stylesheet(qt_api='pyqt6', palette=palette)
    return param_stylesheet + '\n' + other_stylesheet
