import sys
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile, QCoreApplication, QRect, Slot


from Gui.ui.MainWindow import Ui_MainWindow
from Gui.ui.IdentityTab import Ui_Tab
from Gui.ui.GuildTab import Ui_Guild
from qt_material import apply_stylesheet
from PySide2.QtWidgets import QWidget, QPushButton, QTabBar
from qasync import QEventLoop
import asyncio

import node
import blockchain

class IdentityTab(Ui_Tab):
    def __init__(self, MainWindow, tabWidget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tabWidget = tabWidget
        self._MainWindow = MainWindow
        self.tabs = []

    def setupUi(self, Tab):
        super().setupUi(Tab)
        self._tabWidget.addTab(self, "")
        setattr(self._MainWindow.ui, f'idTab_{self._tabWidget.indexOf(Tab)}', self)
        self.setObjectName(f'idTab_{self._tabWidget.indexOf(Tab)}')
        self._tabWidget.setTabText(self._tabWidget.indexOf(Tab),
                                     QCoreApplication.translate("MainWindow", f"Identity {self._tabWidget.indexOf(Tab)}", None))
        tabs = [GuildTab(self._MainWindow, self.tabWidget)]
        for tab in tabs:
            tab.setupUi(tab)
        self.plusButton = QPushButton()
        self.plusButton.setObjectName("plusbutton")
        self.plusButton.setGeometry(QRect(70, 70, 88, 34))
        self.tabWidget.tabBar().setTabButton(0, QTabBar.LeftSide, self.plusButton)
        self.plusButton.setText(QCoreApplication.translate("Tab", u"+", None))
        self.plusButton.clicked.connect(self.new_tab)

    def new_tab(self):
        tab = GuildTab(self._MainWindow, self.tabWidget)
        self.tabs.append(tab)
        tab.setupUi(tab)



class GuildTab(Ui_Guild):
    def __init__(self, MainWindow, tabWidget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tabWidget = tabWidget
        self._MainWindow = MainWindow

    def setupUi(self, Tab):
        super().setupUi(Tab)
        self._tabWidget.insertTab(0, self, "")
        setattr(self._MainWindow.ui, f'guildTab_{self._tabWidget.indexOf(Tab)}', self)
        self.setObjectName(f'guildTab_{self._tabWidget.indexOf(Tab)}')
        self._tabWidget.setTabText(self._tabWidget.indexOf(Tab),
                                     QCoreApplication.translate("MainWindow", f"Guild {self._tabWidget.indexOf(Tab)}", None))
        self.splitter.setStretchFactor(1, 2)


class MainWindow(QMainWindow):
    def __init__(self):
        self.node = node.Node()
        g = blockchain.Guild()
        self.node.guilds.update({g.raw: g})
        asyncio.ensure_future(self.node.main())
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        tabs = [IdentityTab(self, self.ui.tabWidget)]
        for tab in tabs:
            tab.setupUi(tab)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    apply_stylesheet(app, theme='dark_red.xml')
    window = MainWindow()
    window.show()
    with loop:
        loop.run_forever()
