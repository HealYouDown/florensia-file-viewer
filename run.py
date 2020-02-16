import sys

from PySide2 import QtWidgets
import qdarkstyle
from florensia_file_viewer import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside2"))
    mw = MainWindow()
    mw.show()
    app.exec_()
