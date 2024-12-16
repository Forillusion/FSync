import time

from PySide6.QtCore import QEasingCurve
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout
from qfluentwidgets import ScrollArea, FlowLayout, PushButton, CardWidget, BodyLabel, CheckBox

from var import v
# from UI.ui_taskBlock import Ui_TaskBlock


class taskListWindow(ScrollArea):
    def __init__(self, parent=None):  # parent=None:表示没有父窗口
        super().__init__(parent=parent)  # 调用父类的构造函数
        self.setObjectName("taskLiskWindow")
        self.enableTransparentBackground()

        #网格布局
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setVerticalSpacing(0)
        self.layout.setHorizontalSpacing(0)


        # 添加一个按钮在右上角
        self.addButton = PushButton(self)
        self.addButton.setText("添加任务")
        self.addButton.setFixedSize(100, 30)
        self.addButton.move(0, 0)
        self.layout.addWidget(self.addButton, 0, 1, 1, 1)

        # 添加任务块
        self.taskBlocks = taskBlocks(self)
        # 占2个单元格
        self.layout.addWidget(self.taskBlocks, 1, 0, 1, 2)



class taskBlocks(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 透明背景
        self.setObjectName("taskBlocks")
        self.setStyleSheet("#taskBlocks{background-color:transparent;}")
        layout = FlowLayout(self, needAni=True)
        layout.setAnimation(250, QEasingCurve.OutQuad)

        # layout.setContentsMargins(30, 30, 30, 30)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(10)

        for task in v.taskList:
            layout.addWidget(taskBlock(task))
            layout.addWidget(taskBlock(task))



class taskBlock(CardWidget):
    def __init__(self, task):
        super().__init__()
        self.task = task
        name = task["name"]
        localPath = task["localPath"]
        cloudPath = task["cloudPath"]
        lastRunTime = task["lastRunTime"]
        nextRunTime = task["nextRunTime"]

        self.setObjectName("taskBlock")
        # self.setStyleSheet("#taskBlock{border-radius:10px;background-color:white;}")#border:1px solid #d3d3d3;
        self.setFixedSize(320, 150)
        self.setContentsMargins(20, 20, 20, 20)
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setVerticalSpacing(10)
        self.layout.setHorizontalSpacing(10)



        # 设置可以点击
        # self.setEnabled(True)
        self.clicked.connect(self.checkEvent)

        self.NameLabel = BodyLabel(self)
        self.NameLabel.setText(name)
        self.layout.addWidget(self.NameLabel, 0, 0, 1, 1)

        # self.EnabledBox = CheckBox(self)
        # self.EnabledBox.setText("Enabled")
        # self.layout.addWidget(self.EnabledBox, 0, 1, 1, 1)

        self.LocalPathLabel = BodyLabel(self)
        self.LocalPathLabel.setText("本地："+localPath)
        self.layout.addWidget(self.LocalPathLabel, 1, 0, 1, 1)

        self.CloudPathLabel = BodyLabel(self)
        self.CloudPathLabel.setText("云端："+cloudPath)
        self.layout.addWidget(self.CloudPathLabel, 1, 1, 1, 1)

        self.LastRunTimeLabel = BodyLabel(self)
        self.LastRunTimeLabel.setText(time.strftime("上次：%m-%d %H:%M:%S", time.localtime(lastRunTime)))
        self.layout.addWidget(self.LastRunTimeLabel, 2, 0, 1, 1)

        self.NextRunTimeLabel = BodyLabel(self)
        self.NextRunTimeLabel.setText(time.strftime("下次：%m-%d %H:%M:%S", time.localtime(nextRunTime)))
        self.layout.addWidget(self.NextRunTimeLabel, 2, 1, 1, 1)

    def checkEvent(self):
        print("checkEvent")




