import importlib
import os
import sys
from pathlib import Path

from PyQt6 import QtWidgets, QtGui

from doubleblind import gui


def run():
    app = QtWidgets.QApplication([])
    app.setDesktopFileName('DoubleBlind')
    icon_pth = str(Path(__file__).parent.joinpath('favicon.ico').absolute())
    app.setWindowIcon(QtGui.QIcon(icon_pth))
    window = gui.MainWindow()
    sys.excepthook = window.excepthook

    # close built-in splash screen in frozen app version of DoubleBlind
    if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash
        pyi_splash.close()

    window.show()
    window.check_for_updates(False)
    sys.exit(app.exec())


if __name__ == '__main__':
    run()
