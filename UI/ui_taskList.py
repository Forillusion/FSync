# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'taskList.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QSizePolicy,
    QTableWidgetItem, QWidget)

from qfluentwidgets import TableWidget

class Ui_taskList(object):
    def setupUi(self, taskList):
        if not taskList.objectName():
            taskList.setObjectName(u"taskList")
        taskList.resize(1129, 1001)
        self.gridLayout = QGridLayout(taskList)
        self.gridLayout.setObjectName(u"gridLayout")
        self.WaitUpTable = TableWidget(taskList)
        self.WaitUpTable.setObjectName(u"WaitUpTable")

        self.gridLayout.addWidget(self.WaitUpTable, 0, 0, 1, 1)


        self.retranslateUi(taskList)

        QMetaObject.connectSlotsByName(taskList)
    # setupUi

    def retranslateUi(self, taskList):
        taskList.setWindowTitle(QCoreApplication.translate("taskList", u"Form", None))
    # retranslateUi

