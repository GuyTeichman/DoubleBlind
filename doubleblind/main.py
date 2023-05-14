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
    window.show()
    window.check_for_updates(False)

    sys.exit(app.exec())


if __name__ == '__main__':
    run()
