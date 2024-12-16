import os

from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QTableWidgetItem
from PySide6.QtCore import Qt
from qfluentwidgets import BodyLabel, ProgressBar, TableWidget

from var import v


class finishListWindow(QWidget):
    def __init__(self, parent=None):
        super(finishListWindow, self).__init__(parent)
        self.setObjectName("finishList")
        self.setStyleSheet("#finishList{background-color:transparent;}")

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setVerticalSpacing(20)
        self.layout.setHorizontalSpacing(20)

        self.table = TableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["文件名", "路径", "状态", "大小"])
        self.layout.addWidget(self.table, 0, 0, 1, 1)

    def updateTable(self):
        self.table.setRowCount(len(v.finishQueue))
        for i in range(len(v.finishQueue)):
            self.table.setItem(i, 0, QTableWidgetItem(v.finishQueue[i]["fillName"]))
            self.table.setItem(i, 1, QTableWidgetItem(os.path.dirname(v.finishQueue[i]["path"])))
            self.table.setItem(i, 2, QTableWidgetItem(v.finishQueue[i]["status"]))
            if "size" in v.finishQueue[i]:
                self.table.setItem(i, 3, QTableWidgetItem(str(round(v.finishQueue[i]["size"] / 1024, 2)) + "KB"))
