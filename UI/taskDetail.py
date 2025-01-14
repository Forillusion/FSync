import os.path

from PySide6.QtCore import QTime, QTimer
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout
from qfluentwidgets import ScrollArea, ExpandLayout, PushButton, SubtitleLabel, LineEdit, MessageBoxBase, BodyLabel, \
    TransparentTogglePushButton, SwitchButton, ComboBox, TimePicker


class taskDetailMsgBox(MessageBoxBase):
    def __init__(self, task, newTask, parent=None):
        super().__init__(parent)
        self.task = task
        self.newTask = newTask
        self.deleteFlag = False
        self.checkFlag = False

        self.layout = QGridLayout(self)
        self.titleLabel = SubtitleLabel("任务详情")

        self.nameLable = BodyLabel("任务名：")
        self.layout.addWidget(self.nameLable, 0, 0, 1, 1)

        self.nameLine = LineEdit()
        self.nameLine.setText(task["name"])
        self.layout.addWidget(self.nameLine, 0, 1, 1, 1)

        self.enabledButton = TransparentTogglePushButton("启用")
        self.enabledButton.setChecked(task["enabled"])
        self.layout.addWidget(self.enabledButton, 0, 2, 1, 1)

        self.localPathLable = BodyLabel("本地路径：")
        self.layout.addWidget(self.localPathLable, 2, 0, 1, 1)

        self.localPathLine = LineEdit()
        self.localPathLine.setText(task["localPath"])
        self.layout.addWidget(self.localPathLine, 2, 1, 1, 2)

        self.cloudPathLable = BodyLabel("云端路径：")
        self.layout.addWidget(self.cloudPathLable, 3, 0, 1, 1)

        self.cloudPathLine = LineEdit()
        self.cloudPathLine.setText(task["cloudPath"])
        self.layout.addWidget(self.cloudPathLine, 3, 1, 1, 2)

        self.deleteLable = BodyLabel("删除云端文件：")
        self.layout.addWidget(self.deleteLable, 4, 0, 1, 1)

        self.deleteButton = SwitchButton()
        self.deleteButton.setOnText("是")
        self.deleteButton.setOffText("否")
        self.deleteButton.setChecked(task["deleteCloudFile"])
        self.layout.addWidget(self.deleteButton, 4, 1, 1, 1)

        self.scheduledLable = BodyLabel("任务模式：")
        self.layout.addWidget(self.scheduledLable, 5, 0, 1, 1)

        self.scheduledBox = ComboBox()
        self.scheduledBox.addItem("无", userData="none")
        self.scheduledBox.addItem("软件启动时", userData="start")
        self.scheduledBox.addItem("定时", userData="time")
        self.scheduledBox.addItem("间隔", userData="interval")
        self.layout.addWidget(self.scheduledBox, 5, 1, 1, 2)
        # self.scheduledBox.currentIndexChanged.connect(self.scheduledChange)

        self.weekLable = BodyLabel("重复星期：")
        self.layout.addWidget(self.weekLable, 6, 0, 1, 1)

        self.weekLayout = QGridLayout()
        self.weekButtons = []
        self.weekButtons.append(TransparentTogglePushButton("一"))
        self.weekButtons.append(TransparentTogglePushButton("二"))
        self.weekButtons.append(TransparentTogglePushButton("三"))
        self.weekButtons.append(TransparentTogglePushButton("四"))
        self.weekButtons.append(TransparentTogglePushButton("五"))
        self.weekButtons.append(TransparentTogglePushButton("六"))
        self.weekButtons.append(TransparentTogglePushButton("日"))
        for i in range(7):
            self.weekLayout.addWidget(self.weekButtons[i], 0, i, 1, 1)
        self.layout.addLayout(self.weekLayout, 6, 1, 1, 2)

        self.setTimeLable = BodyLabel("设置时间：")
        self.layout.addWidget(self.setTimeLable, 7, 0, 1, 1)

        self.setTimePicker = TimePicker()
        self.setTimePicker.setColumnVisible(2, True)
        self.layout.addWidget(self.setTimePicker, 7, 1, 1, 2)

        self.missedLable = BodyLabel("运行错过的任务：")
        self.layout.addWidget(self.missedLable, 8, 0, 1, 1)

        self.missedButton = SwitchButton()
        self.missedButton.setOnText("是")
        self.missedButton.setOffText("否")
        self.layout.addWidget(self.missedButton, 8, 1, 1, 1)

        if not self.newTask:
            self.runCountLable = BodyLabel("运行次数：" + str(task["runCount"]))
            self.layout.addWidget(self.runCountLable, 9, 0, 1, 2)

            self.deleteTaskButton = PushButton("删除任务")
            self.layout.addWidget(self.deleteTaskButton, 9, 2, 1, 1)
            self.deleteTaskButton.clicked.connect(self.deleteTaskEvent)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addLayout(self.layout)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)
        self.showScheduled()

        self.scheduledBox.currentIndexChanged.connect(self.scheduledChange)

        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.checkInput)
        # self.timer.start(100)
        self.nameLine.textChanged.connect(self.checkInput)
        self.localPathLine.textChanged.connect(self.checkInput)
        self.cloudPathLine.textChanged.connect(self.checkInput)
        self.scheduledBox.currentIndexChanged.connect(self.checkInput)
        for x in self.weekButtons:
            x.clicked.connect(self.checkInput)
        self.checkInput()


    def showScheduled(self):
        if self.task["scheduled"]["type"] == "none":
            self.scheduledBox.setCurrentText("无")
            self.showScheduledNone()

        elif self.task["scheduled"]["type"] == "start":
            self.scheduledBox.setCurrentText("软件启动时")
            self.showScheduledStart()

        elif self.task["scheduled"]["type"] == "time":
            self.scheduledBox.setCurrentText("定时")
            self.showScheduledTime(self.task["scheduled"]["week"], self.task["scheduled"]["time"],
                                   self.task["scheduled"]["missed"])

        elif self.task["scheduled"]["type"] == "interval":
            self.scheduledBox.setCurrentText("间隔")
            self.showScheduledInterval(self.task["scheduled"]["interval"], self.task["scheduled"]["missed"])

    def removeScheduled(self):
        self.weekLable.setVisible(False)
        for x in self.weekButtons:
            x.setVisible(False)
        self.setTimeLable.setVisible(False)
        self.setTimePicker.setVisible(False)
        self.missedLable.setVisible(False)
        self.missedButton.setVisible(False)

    def showScheduledNone(self):
        self.removeScheduled()

    def showScheduledStart(self):
        self.removeScheduled()

    def showScheduledTime(self, week, time, missed):
        self.removeScheduled()
        self.weekLable.setVisible(True)
        for x in self.weekButtons:
            x.setVisible(True)
        self.setTimeLable.setVisible(True)
        self.setTimePicker.setVisible(True)
        self.missedLable.setVisible(True)
        self.missedButton.setVisible(True)

        for x in week:
            self.weekButtons[x - 1].setChecked(True)
        self.setTimePicker.setTime(self.strToQT(time))
        self.missedButton.setChecked(missed)

    def showScheduledInterval(self, interval, missed):
        self.removeScheduled()
        self.setTimeLable.setVisible(True)
        self.setTimePicker.setVisible(True)
        self.missedLable.setVisible(True)
        self.missedButton.setVisible(True)

        self.setTimePicker.setTime(self.secondToQT(interval))
        self.missedButton.setChecked(missed)

    def scheduledChange(self):
        if self.scheduledBox.currentData() == "none":
            self.showScheduledNone()

        elif self.scheduledBox.currentData() == "start":
            self.showScheduledStart()

        elif self.scheduledBox.currentData() == "time":
            if self.task["scheduled"]["type"] == "time":
                self.showScheduledTime(self.task["scheduled"]["week"], self.task["scheduled"]["time"],
                                       self.task["scheduled"]["missed"])
            else:
                self.showScheduledTime([], "00:00:00", True)

        elif self.scheduledBox.currentData() == "interval":
            if self.task["scheduled"]["type"] == "interval":
                self.showScheduledInterval(self.task["scheduled"]["interval"], self.task["scheduled"]["missed"])
            else:
                self.showScheduledInterval(0, True)

    def strToQT(self, time):
        s = time.split(":")
        return QTime(int(s[0]), int(s[1]), int(s[2]))

    def secondToQT(self, second):
        h = second // 3600
        m = (second % 3600) // 60
        s = second % 60
        return QTime(h, m, s)

    def deleteTaskEvent(self):
        self.deleteFlag = True
        self.close()

    def checkInput(self):
        self.checkFlag=True
        if self.nameLine.text() == "":
            self.checkFlag=False

        if self.localPathLine.text() == "":
            self.checkFlag=False
        elif not os.path.exists(self.localPathLine.text()):
            self.checkFlag=False
        elif not os.path.isdir(self.localPathLine.text()):
            self.checkFlag=False

        if self.cloudPathLine.text() == "":
            self.checkFlag=False

        if self.scheduledBox.currentData() == "time":
            f = False
            for x in self.weekButtons:
                if x.isChecked():
                    f = True
                    break

            if not f:
                self.checkFlag=False

        self.yesButton.setEnabled(self.checkFlag)
        return self.checkFlag