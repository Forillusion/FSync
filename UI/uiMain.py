import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from PySide6.scripts.pyside_tool import designer
from qfluentwidgets import FluentWindow
from UI.taskList import Ui_taskList
from qfluentwidgets import FluentWindow, FluentIcon as FIF


# designer()
# app = QApplication(sys.argv)
# label = QLabel("Hello World!")
# label.show()
# app.exec()


class WebWindow(QWidget, Ui_taskList):
    def __init__(self, parent=None):  # parent=None:表示没有父窗口
        super().__init__(parent=parent)  # 调用父类的构造函数
        self.setupUi(self)
        self.gridLayout.setContentsMargins(20, 20, 20, 20)  # 设置组件与窗口边缘的距离
        self.initTable()

    def initTable(self):
        # 启用边框并设置圆角
        self.WaitUpTable.setBorderVisible(True)  # 设置边框可见
        self.WaitUpTable.setBorderRadius(8)  # 设置圆角

        self.WaitUpTable.setWordWrap(False)  # 设置文本不换行
        self.WaitUpTable.setRowCount(0)  # 设置行数
        self.WaitUpTable.setColumnCount(1)  # 设置列数

        self.WaitUpTable.setHorizontalHeaderLabels(['等待上传'])  # 设置表头
        # 设置每一列的宽度
        self.WaitUpTable.setColumnWidth(0, 200)
        # self.TableWidget.setColumnWidth(1, 200)
        # self.TableWidget.setColumnWidth(2, 200)
        # self.WaitUpTable.verticalHeader().hide() # 隐藏垂直表头


class window(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo")
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.navigationInterface.setAcrylicEnabled(True)  # 设置导航界面背景为亚克力效果

        # # 添加子界面
        self.mainWindow = WebWindow(self)
        # self.webWindow = WebWindow(self)
        # self.settingWindow = SettingWindow(self)

        self.addSubInterface(self.mainWindow, FIF.SPEED_OFF, '应用统计')
        # self.addSubInterface(self.webWindow,FIF.SPEED_OFF,'网页统计')
        # self.addSubInterface(self.settingWindow, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

        self.navigationInterface.setMinimumExpandWidth(16000)
        self.resize(700, 500)
        # screen = QDesktopWidget().screenGeometry()
        # size = self.geometry()
        # self.setGeometry(int( (screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2),700,500)

    def closeEvent(self, event):
        event.accept()


app = QApplication(sys.argv)  # 创建应用程序
w = window()
w.show()
while w.isVisible():
    QApplication.processEvents()  # 使程序不会卡死
