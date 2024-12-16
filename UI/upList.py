import os

from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QTableWidgetItem
from PySide6.QtCore import Qt
from qfluentwidgets import BodyLabel, ProgressBar, TableWidget

from var import v


class upListWindow(QWidget):
    def __init__(self, parent=None):
        super(upListWindow, self).__init__(parent)
        self.setObjectName("upList")
        self.setStyleSheet("#upList{background-color:transparent;}")

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setVerticalSpacing(20)
        self.layout.setHorizontalSpacing(20)

        self.L1 = BodyLabel("总进度")
        self.layout.addWidget(self.L1, 0, 0, 1, 1)

        self.totalProgress = ProgressBar(self)
        self.layout.addWidget(self.totalProgress, 0, 1, 1, 1)

        self.LProgress = BodyLabel()
        self.layout.addWidget(self.LProgress, 0, 2, 1, 1)

        self.LTotAFin = BodyLabel("")
        self.layout.addWidget(self.LTotAFin, 0, 3, 1, 1)

        self.LFileName = BodyLabel("文件名")
        self.layout.addWidget(self.LFileName, 1, 0, 1, 1)

        self.fileProgress = ProgressBar(self)
        self.layout.addWidget(self.fileProgress, 1, 1, 1, 1)
        self.fileProgress.setValue(0)

        self.LfileProgress = BodyLabel()
        self.layout.addWidget(self.LfileProgress, 1, 2, 1, 1)

        self.LPath = BodyLabel()
        self.layout.addWidget(self.LPath, 2, 0, 1, 4)

        self.LSize = BodyLabel()
        self.layout.addWidget(self.LSize, 1, 3, 1, 1)

        self.table = TableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["文件名", "路径", "状态", "大小"])
        self.layout.addWidget(self.table, 3, 0, 1, 4)

    def updateTable(self):
        self.updateTotalProgress()
        x = 0
        if v.currentUpLoad != None:
            self.LFileName.setText(v.currentUpLoad["fillName"])
            self.LPath.setText(os.path.dirname(v.currentUpLoad["path"]))
            self.LSize.setText(str(round(v.currentUpLoad["size"] / 1024, 2)) + "KB")
            if "totalProgress" in v.currentUpLoad:
                self.fileProgress.setValue(v.currentUpLoad["totalProgress"])
                self.LfileProgress.setText(str(f"{v.currentUpLoad['totalProgress']:.2f}%"))
            else:
                self.fileProgress.setValue(0)
                self.LfileProgress.setText("0.00%")

        else:
            self.LFileName.setText("无正在上传")
            self.LPath.setText("")
            self.LSize.setText("")
            self.fileProgress.setValue(0)
            self.LfileProgress.setText("0.00%")

        if len(v.sliceQueue) > 0 and v.currentUpLoad != None and v.sliceQueue[0]["path"] != v.currentUpLoad["path"]:
            x += 1
            self.table.setRowCount(len(v.sliceQueue) + x)
            self.table.setItem(0, 0, QTableWidgetItem(v.sliceQueue[0]["fillName"]))
            self.table.setItem(0, 1, QTableWidgetItem(v.sliceQueue[0]["path"]))
            self.table.setItem(0, 2, QTableWidgetItem("等待上传"))
            if "size" in v.sliceQueue[0]:
                self.table.setItem(0, 3, QTableWidgetItem(str(round(v.sliceQueue[0]["size"] / 1024, 2)) + "KB"))

        if v.currentHandle != None:
            x += 1
            self.table.setRowCount(len(v.sliceQueue) + x)
            self.table.setItem(0, 0, QTableWidgetItem(v.currentHandle["fillName"]))
            self.table.setItem(0, 1, QTableWidgetItem(v.currentHandle["path"]))
            handle = ""
            if v.currentHandle["status"] == "create folder":
                handle = "创建文件夹中"
            elif v.currentHandle["status"] == "delete folder":
                handle = "删除文件夹中"
            elif v.currentHandle["status"] == "create file":
                handle = "获取分片中"
            elif v.currentHandle["status"] == "delete file":
                handle = "删除文件中"
            elif v.currentHandle["status"] == "update file":
                handle = "更新文件中"

            self.table.setItem(0, 2, QTableWidgetItem(handle))
            if "size" in v.currentHandle:
                self.table.setItem(0, 3, QTableWidgetItem(str(round(v.currentHandle["size"] / 1024, 2)) + "KB"))

        self.table.setRowCount(len(v.upQueue) + x)
        for i in range(len(v.upQueue)):
            self.table.setItem(i + x, 0, QTableWidgetItem(v.upQueue[i]["fillName"]))
            self.table.setItem(i + x, 1, QTableWidgetItem(os.path.dirname(v.upQueue[i]["path"])))
            self.table.setItem(i + x, 2, QTableWidgetItem("waiting"))
            if "size" in v.upQueue[i]:
                self.table.setItem(i + x, 3, QTableWidgetItem(str(round(v.upQueue[i]["size"] / 1024, 2)) + "KB"))

    def updateTotalProgress(self):
        if v.cTask != None and v.total["uploadSize"] != 0:
            self.totalProgress.setValue(v.finish["uploadSize"] / v.total["uploadSize"] * 100)
            self.LProgress.setText(str(f"{v.finish["uploadSize"] / v.total["uploadSize"] * 100:.2f}%"))
            total=v.total["createFolder"]+v.total["deleteFolder"]+v.total["createFiles"]+v.total["updateFiles"]+v.total["deleteFiles"]
            finish=v.finish["createFolder"]+v.finish["deleteFolder"]+v.finish["createFiles"]+v.finish["updateFiles"]+v.finish["deleteFiles"]
            self.LTotAFin.setText(f"{finish}/{total}")

        else:
            self.totalProgress.setValue(0)
            self.LProgress.setText("0.00%")
            self.LTotAFin.setText("0/0")
