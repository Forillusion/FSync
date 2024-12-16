import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from UI.taskList import taskListWindow
from UI.upList import upListWindow
from qfluentwidgets import FluentWindow, FluentIcon as FIF

from task import loadTask


# designer()
# app = QApplication(sys.argv)
# label = QLabel("Hello World!")
# label.show()
# app.exec()


class window(FluentWindow):
    def __init__(self):
        self.app = QApplication(sys.argv)
        super().__init__()
        print("debug1")
        self.show()
        self.initWindow()


    def initWindow(self):
        self.setWindowTitle("Demo")
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.navigationInterface.setAcrylicEnabled(True)  # 设置导航界面背景为亚克力效果

        # # 添加子界面
        self.upListWindow = upListWindow(self)
        self.taskListWindow = taskListWindow(self)

        # self.webWindow = WebWindow(self)
        # self.settingWindow = SettingWindow(self)

        self.addSubInterface(self.upListWindow, FIF.SPEED_OFF, '上传列表')
        self.addSubInterface(self.taskListWindow, FIF.SPEED_OFF, '任务列表')
        # self.addSubInterface(self.webWindow,FIF.SPEED_OFF,'网页统计')
        # self.addSubInterface(self.settingWindow, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

        self.navigationInterface.setMinimumExpandWidth(16000)
        self.resize(700, 500)
        # screen = QDesktopWidget().screenGeometry()
        # size = self.geometry()
        # self.setGeometry(int( (screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2),700,500)

    def runWindow(self):
        self.upListWindow.updateTable()
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