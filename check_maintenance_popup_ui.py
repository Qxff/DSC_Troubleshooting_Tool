# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'check_maintenance_popup.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_check_maintenance_popup(object):
    def setupUi(self, check_maintenance_popup):
        check_maintenance_popup.setObjectName("check_maintenance_popup")
        check_maintenance_popup.setWindowModality(QtCore.Qt.ApplicationModal)
        check_maintenance_popup.resize(967, 571)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("dsc.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        check_maintenance_popup.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(check_maintenance_popup)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.label_45 = QtWidgets.QLabel(self.centralwidget)
        self.label_45.setObjectName("label_45")
        self.gridLayout.addWidget(self.label_45, 0, 0, 1, 1)
        self.tableWidget_check_maintenance_result = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget_check_maintenance_result.setAlternatingRowColors(True)
        self.tableWidget_check_maintenance_result.setGridStyle(QtCore.Qt.SolidLine)
        self.tableWidget_check_maintenance_result.setObjectName("tableWidget_check_maintenance_result")
        self.tableWidget_check_maintenance_result.setColumnCount(0)
        self.tableWidget_check_maintenance_result.setRowCount(0)
        self.tableWidget_check_maintenance_result.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget_check_maintenance_result.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_check_maintenance_result.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget_check_maintenance_result.verticalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tableWidget_check_maintenance_result, 1, 0, 1, 1)
        check_maintenance_popup.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(check_maintenance_popup)
        self.statusbar.setObjectName("statusbar")
        check_maintenance_popup.setStatusBar(self.statusbar)

        self.retranslateUi(check_maintenance_popup)
        QtCore.QMetaObject.connectSlotsByName(check_maintenance_popup)

    def retranslateUi(self, check_maintenance_popup):
        _translate = QtCore.QCoreApplication.translate
        check_maintenance_popup.setWindowTitle(_translate("check_maintenance_popup", "Maintenance "))
        self.label_45.setText(_translate("check_maintenance_popup", "<html><head/><body><p><span style=\" font-size:11pt; font-weight:600; color:#00aa00;\">All the maintenances till now:</span></p></body></html>"))
        self.tableWidget_check_maintenance_result.setSortingEnabled(True)

