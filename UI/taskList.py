import time

from PySide6.QtCore import QEasingCurve
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout
from qfluentwidgets import ScrollArea, FlowLayout, PushButton, CardWidget, BodyLabel, CheckBox

from task import newTask, addTask, updateTask, deleteTask
from var import v
from UI.taskDetail import taskDetailMsgBox
# from UI.ui_taskBlock import Ui_TaskBlock

from qfluentwidgets import FluentWindow, FluentIcon as FIF, NavigationItemPosition, FluentTranslator


class taskListWindow(ScrollArea):
    def __init__(self, parent=None):  # parent=None:表示没有父窗口
        super().__init__(parent=parent)  # 调用父类的构造函数
        self.parent = parent
        self.setObjectName("taskListWindow")
        self.enableTransparentBackground()

        # 网格布局
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

        self.addButton.clicked.connect(self.newTaskEvent)

    def newTaskEvent(self):
        task = newTask()
        x = self.showTaskDetail(task, 1)
        if x:
            addTask(task)
            self.taskBlocks.addTask(task)

    def showTaskDetail(self, task, newTask=0):
        w = taskDetailMsgBox(task, newTask, self.parent)
        if w.exec():
            task["name"] = w.nameLine.text()
            task["enabled"] = w.enabledButton.isChecked()
            task["localPath"] = w.localPathLine.text()
            task["cloudPath"] = w.cloudPathLine.text()
            task["deleteCloudFile"] = w.deleteButton.isChecked()
            task["scheduled"]["type"] = w.scheduledBox.currentData()
            if task["scheduled"]["type"] == "time":
                t = w.setTimePicker.time
                task["scheduled"]["time"] = f"{t.hour():02d}:{t.minute():02d}:{t.second():02d}"
                task["scheduled"]["week"] = []
                for i in range(7):
                    if w.weekButtons[i].isChecked():
                        task["scheduled"]["week"].append(i+1)
                task["scheduled"]["missed"] = w.missedButton.isChecked()
            elif task["scheduled"]["type"] == "interval":
                t = w.setTimePicker.time
                task["scheduled"]["interval"] = t.hour() * 3600 + t.minute() * 60 + t.second()
                task["scheduled"]["missed"] = w.missedButton.isChecked()

            updateTask(task)
            self.taskBlocks.update()
            return 1
        else:
            if w.deleteFlag:
                print("delete")
                self.taskBlocks.deleteTask(task)
                deleteTask(task)
            else:
                print("cancel")
            return 0


class taskBlocks(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        # 透明背景
        self.setObjectName("taskBlocks")
        self.setStyleSheet("#taskBlocks{background-color:transparent;}")
        self.layout = FlowLayout(self, needAni=True)
        self.layout.setAnimation(250, QEasingCurve.OutQuad)

        # layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setVerticalSpacing(20)
        self.layout.setHorizontalSpacing(10)

        self.blocks = []
        for task in v.taskList:
            self.blocks.append(taskBlock(task, self.parent))
            self.layout.addWidget(self.blocks[-1])

    def update(self):
        for block in self.blocks:
            block.update()

    def addTask(self, task):
        self.blocks.append(taskBlock(task, self.parent))
        self.layout.addWidget(self.blocks[-1])

    def deleteTask(self, task):
        for block in self.blocks:
            if block.task == task:
                self.layout.removeWidget(block)
                block.deleteLater()
                self.blocks.remove(block)
                break


class taskBlock(CardWidget):
    def __init__(self, task, parentWindow):
        super().__init__()
        self.task = task
        self.parentWindow = parentWindow

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
        self.LocalPathLabel.setText("本地：" + localPath)
        self.layout.addWidget(self.LocalPathLabel, 1, 0, 1, 1)

        self.CloudPathLabel = BodyLabel(self)
        self.CloudPathLabel.setText("云端：" + cloudPath)
        self.layout.addWidget(self.CloudPathLabel, 1, 1, 1, 1)

        self.LastRunTimeLabel = BodyLabel(self)
        self.LastRunTimeLabel.setText(time.strftime("上次：%m-%d %H:%M:%S", time.localtime(lastRunTime)))
        self.layout.addWidget(self.LastRunTimeLabel, 2, 0, 1, 1)

        self.NextRunTimeLabel = BodyLabel(self)
        self.NextRunTimeLabel.setText(time.strftime("下次：%m-%d %H:%M:%S", time.localtime(nextRunTime)))
        self.layout.addWidget(self.NextRunTimeLabel, 2, 1, 1, 1)

    def update(self):
        self.NameLabel.setText(self.task["name"])
        self.LocalPathLabel.setText("本地：" + self.task["localPath"])
        self.CloudPathLabel.setText("云端：" + self.task["cloudPath"])
        self.LastRunTimeLabel.setText(time.strftime("上次：%m-%d %H:%M:%S", time.localtime(self.task["lastRunTime"])))
        self.NextRunTimeLabel.setText(time.strftime("下次：%m-%d %H:%M:%S", time.localtime(self.task["nextRunTime"])))

    def checkEvent(self):
        self.parentWindow.showTaskDetail(self.task)
        # taskDetialWindow = taskDetailWindow(self.task,self.parent())
