import sys

from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from UI.config import cfg
from UI.failList import failListWindow
from UI.finishList import finishListWindow
from UI.taskList import taskListWindow
from UI.upList import upListWindow
from qfluentwidgets import FluentWindow, FluentIcon as FIF, NavigationItemPosition, FluentTranslator
from UI.setting import SettingWindow

from task import loadTask


# designer()
# app = QApplication(sys.argv)
# label = QLabel("Hello World!")
# label.show()
# app.exec()


class window(FluentWindow):
    def __init__(self):
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough) # 设置高DPI缩放因子
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling) # 启用高DPI缩放
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps) # 使用高DPI图标

        self.app = QApplication(sys.argv)

        locale = cfg.get(cfg.language).value # 设置语言
        fluentTranslator = FluentTranslator(locale) # 设置翻译
        self.app.installTranslator(fluentTranslator)

        super().__init__()
        self.show()
        self.initWindow()


    def initWindow(self):
        self.setWindowTitle("Demo")
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.navigationInterface.setAcrylicEnabled(True)  # 设置导航界面背景为亚克力效果

        # # 添加子界面
        self.upListWindow = upListWindow(self)
        self.finishListWindow = finishListWindow(self)
        self.failListWindow = failListWindow(self)
        self.taskListWindow = taskListWindow(self)
        self.settingWindow=SettingWindow(self)

        # self.webWindow = WebWindow(self)
        # self.settingWindow = SettingWindow(self)

        self.addSubInterface(self.upListWindow, FIF.UP, '上传列表')
        self.addSubInterface(self.finishListWindow, FIF.ACCEPT, '完成列表')
        self.addSubInterface(self.failListWindow, FIF.CLOSE, '失败列表')
        self.addSubInterface(self.taskListWindow, FIF.CALENDAR, '任务列表')
        # self.addSubInterface(self.webWindow,FIF.SPEED_OFF,'网页统计')
        self.addSubInterface(self.settingWindow, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

        self.navigationInterface.setMinimumExpandWidth(16000)
        self.resize(800, 600)
        # screen = QDesktopWidget().screenGeometry()
        # size = self.geometry()
        # self.setGeometry(int( (screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2),700,500)

    def runWindow(self):
        self.upListWindow.updateTable()
        self.finishListWindow.updateTable()
        QApplication.processEvents()

    def closeEvent(self, event):
        event.accept()

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