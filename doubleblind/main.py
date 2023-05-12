from PyQt6 import QtCore,QtWidgets, QtGui
from pathlib import Path
import sys
from doubleblind import blinding,utils, gui

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    app.setDesktopFileName('DoubleBlind')
    icon_pth = str(Path(__file__).parent.parent.joinpath('favicon.ico').absolute())
    app.setWindowIcon(QtGui.QIcon(icon_pth))

    window = gui.MainWindow()
    window.show()
    window.check_for_updates(False)

    sys.exit(app.exec())