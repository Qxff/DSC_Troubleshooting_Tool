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
        check_maintenance_popup.resize(945, 576)
        self.tableWidget_check_maintenance_result = QtWidgets.QTableWidget(check_maintenance_popup)
        self.tableWidget_check_maintenance_result.setGeometry(QtCore.QRect(9, 33, 931, 531))
        self.tableWidget_check_maintenance_result.setAlternatingRowColors(True)
        self.tableWidget_check_maintenance_result.setGridStyle(QtCore.Qt.SolidLine)
        self.tableWidget_check_maintenance_result.setObjectName("tableWidget_check_maintenance_result")
        self.tableWidget_check_maintenance_result.setColumnCount(0)
        self.tableWidget_check_maintenance_result.setRowCount(0)
        self.tableWidget_check_maintenance_result.horizontalHeader().setStretchLastSection(False)
        self.tableWidget_check_maintenance_result.verticalHeader().setStretchLastSection(False)
        self.label_45 = QtWidgets.QLabel(check_maintenance_popup)
        self.label_45.setGeometry(QtCore.QRect(9, 9, 220, 18))
        self.label_45.setObjectName("label_45")

        self.retranslateUi(check_maintenance_popup)
        QtCore.QMetaObject.connectSlotsByName(check_maintenance_popup)

    def retranslateUi(self, check_maintenance_popup):
        _translate = QtCore.QCoreApplication.translate
        check_maintenance_popup.setWindowTitle(_translate("check_maintenance_popup", "Maintenance"))
        self.tableWidget_check_maintenance_result.setSortingEnabled(True)
        self.label_45.setText(_translate("check_maintenance_popup", "<html><head/><body><p><span style=\" font-size:11pt; font-weight:600; color:#00aa00;\">All the maintenances till now:</span></p></body></html>"))

