import sys
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile


from Gui.ui.MainWindow import Ui_MainWindow
from Gui.ui.IdentityTab import Ui_Tab
from qt_material import apply_stylesheet
from PySide2.QtWidgets import QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tabs = [Ui_Tab()]
        for tab in self.ui.tabs:
            self.ui.tabWidget.addTab(tab, "")
            tab.setupUi(tab)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
