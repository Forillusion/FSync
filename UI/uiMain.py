import sys
import threading
from time import sleep
from timeit import timeit

from PySide6.QtGui import QIcon, QColor, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt, Signal

from UI.config import cfg
from UI.failList import failListWindow
from UI.finishList import finishListWindow
from UI.taskList import taskListWindow
from UI.upList import upListWindow
from qfluentwidgets import FluentWindow, FluentIcon as FIF, NavigationItemPosition, FluentTranslator
from UI.setting import SettingWindow
from database import saveDB

from task import loadTask
from var import v


# designer()
# app = QApplication(sys.argv)
# label = QLabel("Hello World!")
# label.show()
# app.exec()


class window(FluentWindow):
    def __init__(self):
        self.alive = True
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)  # 设置高DPI缩放因子
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 启用高DPI缩放
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # 使用高DPI图标

        self.app = QApplication(sys.argv)

        locale = cfg.get(cfg.language).value  # 设置语言
        fluentTranslator = FluentTranslator(locale)  # 设置翻译
        self.app.installTranslator(fluentTranslator)

        super().__init__()
        self.show()
        self.initWindow()

    def initWindow(self):
        self.setWindowTitle("FSync")
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.navigationInterface.setAcrylicEnabled(True)  # 设置导航界面背景为亚克力效果
        self.resize(800, 600)

        # # 添加子界面
        self.taskListWindow = taskListWindow(self)
        self.upListWindow = upListWindow(self)
        self.finishListWindow = finishListWindow(self)
        self.failListWindow = failListWindow(self)
        self.settingWindow = SettingWindow(self)

        # self.webWindow = WebWindow(self)
        # self.settingWindow = SettingWindow(self)

        self.addSubInterface(self.taskListWindow, FIF.CALENDAR, '任务列表')
        self.addSubInterface(self.upListWindow, FIF.UP, '上传列表')
        self.addSubInterface(self.finishListWindow, FIF.ACCEPT, '完成列表')
        self.addSubInterface(self.failListWindow, FIF.CLOSE, '失败列表')
        # self.addSubInterface(self.webWindow,FIF.SPEED_OFF,'网页统计')
        self.addSubInterface(self.settingWindow, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

        self.navigationInterface.setMinimumExpandWidth(16000)

        self.createTrayIcon()
        if cfg.get(cfg.silentStart):
            self.hide()
        # screen = QDesktopWidget().screenGeometry()
        # size = self.geometry()
        # self.setGeometry(int( (screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2),700,500)

    def createTrayIcon(self):
        # self.setVisible(False)
        # 隐藏窗口
        # self.hide()

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon(":/qfluentwidgets/images/logo.png"))  # 替换为你的图标路径
        self.trayIcon.setVisible(True)

        # 创建上下文菜单
        self.restoreAction = QAction('主窗口', self)
        self.quitAction = QAction('退出', self)

        # 连接信号槽
        self.trayIcon.activated.connect(self.onTrayIconActivated)
        self.restoreAction.triggered.connect(self.onRestoreActionTriggered)
        self.quitAction.triggered.connect(self.onQuitActionTriggered)

        # 设置上下文菜单
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)
        self.trayIcon.setContextMenu(self.trayIconMenu)

    def onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.onRestoreActionTriggered()

    def onRestoreActionTriggered(self):
        self.showNormal()  # 还原窗口
        # self.trayIcon.hide()

    def runWindow(self):
        self.upListWindow.updateTable()
        # print(timeit(self.upListWindow.updateTable, number=1, globals=globals()))
        self.finishListWindow.updateTable()
        self.failListWindow.updateTable()
        QApplication.processEvents()

    def onQuitActionTriggered(self):
        self.trayIcon.deleteLater()
        self.alive = False
        self.app.quit()

    def closeEvent(self, event):
        # self.createTrayIcon()
        self.hide()
        event.ignore()


def startUI():
    w = window()
    mainThread = threading.main_thread()
    while w.alive and not v.mainQuitFlag and mainThread.is_alive():
        w.runWindow()
        # print(f"{timeit(w.runWindow, number=1, globals=globals()):.6f}")
        sleep(0.001)
    v.mainQuitFlag = True

def startUIThread():
    v.UITh = threading.Thread(target=startUI)
    v.UITh.start()

# while w.isVisible():
#     w.runWindow()
#     print("runWindow")
#
# def initWindow():
#
#     app = QApplication(sys.argv)  # 创建应用程序
#     w = window()
#     w.show()
#     return w
#
# def runWindow():
#
#     QApplication.processEvents()  # 使程序不会卡死
