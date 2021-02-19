import sys
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile, QCoreApplication, QRect, Slot


from Gui.ui.MinimalWindow import Ui_MainWindow
from Gui.ui.IdentityTab import Ui_Tab
from Gui.ui.GuildTab import Ui_Guild
from qt_material import apply_stylesheet
from PySide2.QtWidgets import QWidget, QPushButton, QTabBar
from qasync import QEventLoop
import asyncio

import node
import blockchain


class MainWindow(QMainWindow):
    def __init__(self):
        self.node = node.Node()
        g = blockchain.Guild()
        self.node.guilds.update({g.raw: g})
        asyncio.ensure_future(self.node.main())
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    apply_stylesheet(app, theme='dark_red.xml')
    window = MainWindow()
    window.show()
    with loop:
        loop.run_forever()
