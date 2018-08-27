# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'All_Day_Ping_Result.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_all_day_ping_result_popup(object):
    def setupUi(self, all_day_ping_result_popup):
        all_day_ping_result_popup.setObjectName("all_day_ping_result_popup")
        all_day_ping_result_popup.resize(1342, 688)
        self.centralwidget = QtWidgets.QWidget(all_day_ping_result_popup)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 30, 1321, 16))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setMaximumSize(QtCore.QSize(400, 16777215))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 50, 1321, 611))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.textEdit_package_loss_log = QtWidgets.QTextEdit(self.layoutWidget1)
        self.textEdit_package_loss_log.setMaximumSize(QtCore.QSize(400, 16777215))
        self.textEdit_package_loss_log.setObjectName("textEdit_package_loss_log")
        self.horizontalLayout_2.addWidget(self.textEdit_package_loss_log)
        self.line = QtWidgets.QFrame(self.layoutWidget1)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_2.addWidget(self.line)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.textEdit_ping_result_7 = QtWidgets.QTextEdit(self.layoutWidget1)
        self.textEdit_ping_result_7.setObjectName("textEdit_ping_result_7")
        self.gridLayout.addWidget(self.textEdit_ping_result_7, 2, 0, 1, 1)
        self.textEdit_ping_result_5 = QtWidgets.QTextEdit(self.layoutWidget1)
        self.textEdit_ping_result_5.setObjectName("textEdit_ping_result_5")
        self.gridLayout.addWidget(self.textEdit_ping_result_5, 1, 1, 1, 1)
        self.textEdit_ping_result_4 = QtWidgets.QTextEdit(self.layoutWidget1)
        self.textEdit_ping_result_4.setObjectName("textEdit_ping_result_4")
        self.gridLayout.addWidget(self.textEdit_ping_result_4, 1, 0, 1, 1)
        self.textEdit_ping_result_1 = QtWidgets.QTextEdit(self.layoutWidget1)
        self.textEdit_ping_result_1.setPlaceholderText("")
        self.textEdit_ping_result_1.setObjectName("textEdit_ping_result_1")
        self.gridLayout.addWidget(self.textEdit_ping_result_1, 0, 0, 1, 1)
        self.textEdit_ping_result_3 = QtWidgets.QTextEdit(self.layoutWidget1)
        self.textEdit_ping_result_3.setObjectName("textEdit_ping_result_3")
        self.gridLayout.addWidget(self.textEdit_ping_result_3, 0, 2, 1, 1)
        self.textEdit_ping_result_9 = QtWidgets.QTextEdit(self.layoutWidget1)
        self.textEdit_ping_result_9.setObjectName("textEdit_ping_result_9")
        self.gridLayout.addWidget(self.textEdit_ping_result_9, 2, 2, 1, 1)
        self.textEdit_ping_result_2 = QtWidgets.QTextEdit(self.layoutWidget1)
        self.textEdit_ping_result_2.setObjectName("textEdit_ping_result_2")
        self.gridLayout.addWidget(self.textEdit_ping_result_2, 0, 1, 1, 1)
        self.textEdit_ping_result_8 = QtWidgets.QTextEdit(self.layoutWidget1)
        self.textEdit_ping_result_8.setObjectName("textEdit_ping_result_8")
        self.gridLayout.addWidget(self.textEdit_ping_result_8, 2, 1, 1, 1)
        self.textEdit_ping_result_6 = QtWidgets.QTextEdit(self.layoutWidget1)
        self.textEdit_ping_result_6.setObjectName("textEdit_ping_result_6")
        self.gridLayout.addWidget(self.textEdit_ping_result_6, 1, 2, 1, 1)
        self.horizontalLayout_2.addLayout(self.gridLayout)
        all_day_ping_result_popup.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(all_day_ping_result_popup)
        self.statusbar.setObjectName("statusbar")
        all_day_ping_result_popup.setStatusBar(self.statusbar)

        self.retranslateUi(all_day_ping_result_popup)
        QtCore.QMetaObject.connectSlotsByName(all_day_ping_result_popup)

    def retranslateUi(self, all_day_ping_result_popup):
        _translate = QtCore.QCoreApplication.translate
        all_day_ping_result_popup.setWindowTitle(_translate("all_day_ping_result_popup", "All Day Ping Result"))
        self.label_2.setText(_translate("all_day_ping_result_popup", "<html><head/><body><p align=\"center\"><span style=\" font-size:9pt; font-weight:600; color:#ff0000;\">Package Loss log:</span></p></body></html>"))
        self.label.setText(_translate("all_day_ping_result_popup", "<html><head/><body><p align=\"center\"><span style=\" font-size:9pt; font-weight:600; color:#00aa00;\">Result log of 7*24 Ping (Hop-by-Hop):</span></p></body></html>"))

