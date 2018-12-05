"""*******************************************************************************************************

This script is designed for DSC Troubleshooting Tool.

Author: Jason Qin
Version: v1.2 2018.05.14

History:
v1.0	2018.05.11
		Initial version;

v1.1	2018.05.12
		New function: 
		1. Alarms can be inputted any times, each time will clear the former one;
		2. Bond "Enter" key to "Login" button 
		3. Win7 style
		4. Add icon
		Fix bug:
		1. Resolve the crash issue when input blank alarm 
		2. Peer IP address incluing ';' now can be handled

v1.2	2018.05.14
		New function:
		1. Add icon for program
		2. Add icon for mainwindow
		3. Popup window if can't login to DSC
		4. Add custoemr peer input for "ping tool", now just input peer hostname, IP will be inputed automaticly
		5. Alarm list remove duplication 
		6. Add BGP/IP prefix check
		7. Ping tool: add customer election/peer election
		8. Popup send mail window if can't find the peer/realm in ccb

v3.4	2018.11.25
		New function:
		1. Send mail
		2. TraceRoute Ping
		3. DSC Internal Cross Ping
		4. Realtime monitoring of DSC Inter-network
		
		Fix bug:
		1. Add maintenance: special character check to prevent program crash

v3.5	2018.12.21
		New function:
		1. Add maintenance: send calendar


Pending function: 
1. Check maintenance: popup new window with pretty table
2. Multi-service support

*******************************************************************************************************"""

# -*- coding: utf-8 -*-

import sys,os
import re
import paramiko
import copy
import time,datetime
from datetime import datetime, timedelta, timezone
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from DSC_Troubleshooting_Tool_ui import *
from DSC_Login_ui import *
from Input_alarms_ui import *
from ssh_ping_cmd import ssh_onetime_ping, ssh_jump_server_cmd,ssh_jump_server_juniper_cmd,ssh_jump_server_cisco_cmd,ssh_nohup_cmd,ssh_onetime_ping_check_maintenance
from SendEmail import sendemail,html_line_break,send_calendar
from get_router_list_from_traceroute import *
from All_Day_Ping_Result_ui import *
from check_maintenance_popup_ui import *
import threading
import pyperclip
import tarfile
import shutil
import csv
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, drange
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib import style
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.ticker import FuncFormatter
import pytz
from tzlocal import get_localzone

"""****************************************************************************************************"""
"""***************************             1. Main Window            **********************************"""
"""****************************************************************************************************"""

class MyMainWindow(QMainWindow, Ui_MainWindow):
	
	account_result_signal = pyqtSignal(str)
	send_ping_result_signal = pyqtSignal(str,int)
	start_7_24_ping_signal = pyqtSignal(int,str)
	current_maintenance_list_signal=pyqtSignal(list)
	
	update_textEdit_log_name_content_signal=pyqtSignal(str)
	show_download_kpi_file_popup_signal=pyqtSignal(str)
	show_figure_signal=pyqtSignal(str)
	
	show_download_kpi_file_failed_popup_signal=pyqtSignal(str)
	update_textEdit_log_name_content_list_signal=pyqtSignal(list)

	def __init__(self, parent=None):    
		super(MyMainWindow, self).__init__(parent)
		self.setupUi(self)
		
		#Select DSC
		self.comboBox_DSC.addItems(["DSC","HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC"])
		self.comboBox_DSC.currentIndexChanged.connect(self.generatecmd)
		
		self.dscpipdic={"HK DSC":"173.209.220.115","SG DSC":"173.209.221.115","AMS DSC":"173.209.215.102","FRT DSC":"173.209.215.166","CHI DSC":"131.166.129.119","DAL DSC":"131.166.129.151"}
		self.dscsipdic={"HK DSC":"173.209.220.123","SG DSC":"173.209.221.123","AMS DSC":"173.209.215.118","FRT DSC":"173.209.215.182","CHI DSC":"131.166.129.135","DAL DSC":"131.166.129.167"}
		
		#Customer name inputed
		self.comboBox_customer_name.activated.connect(self.update_customer_list)
		self.comboBox_customer_name.currentIndexChanged.connect(self.update_customer_peer)
		
		#Customer peer hostname inputed
		self.comboBox_customer_peername.currentIndexChanged.connect(self.get_peer_ip)
		
		#Select Customer
		self.comboBox_customer.addItems(["Customer","Customer 1","Customer 2","Customer 3","Customer 4","HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC"])
		self.comboBox_customer.currentIndexChanged.connect(self.generatecmd)
		
		self.lineEdit_customer1pip.textChanged.connect(self.generatecmd)
		self.lineEdit_customer2pip.textChanged.connect(self.generatecmd)
		self.lineEdit_customer3pip.textChanged.connect(self.generatecmd)
		self.lineEdit_customer4pip.textChanged.connect(self.generatecmd)
		self.lineEdit_customer1sip.textChanged.connect(self.generatecmd)
		self.lineEdit_customer2sip.textChanged.connect(self.generatecmd)
		self.lineEdit_customer3sip.textChanged.connect(self.generatecmd)
		self.lineEdit_customer4sip.textChanged.connect(self.generatecmd)

		self.pushButton_netstat.clicked.connect(self.ssh_exe_cmd)
		self.pushButton_p2pping.clicked.connect(self.ssh_exe_cmd)
		self.pushButton_p2ptracert.clicked.connect(self.ssh_exe_cmd)
		self.pushButton_s2sping.clicked.connect(self.ssh_exe_cmd)
		self.pushButton_s2stracert.clicked.connect(self.ssh_exe_cmd)
		self.pushButton_start_7_24_ping.clicked.connect(self.start_7_24_ping)
		self.pushButton_analyze_traceroute_result.clicked.connect(self.analyse_traceroute_result)
		
		self.textEdit_traceroute_result.textChanged.connect(self.reset_trace_analysis_result)
		
		#troubleshooting tool
		self.pushButton_input_alarms.clicked.connect(self.input_alarms)
		self.comboBox_alarm_list.currentIndexChanged.connect(self.generate_alarms)
		self.comboBox_alarm_list.currentIndexChanged.connect(self.generatecmd_troubleshooting)
		self.comboBox_alarm_list.currentIndexChanged.connect(self.send_email_for_Null)

		self.pushButton_netstat_2.clicked.connect(self.ssh_exe_cmd_troubleshooting)
		self.pushButton_p2pping_2.clicked.connect(self.ssh_exe_cmd_troubleshooting)
		self.pushButton_p2ptracert_2.clicked.connect(self.ssh_exe_cmd_troubleshooting)
		self.pushButton_s2sping_2.clicked.connect(self.ssh_exe_cmd_troubleshooting)
		self.pushButton_s2stracert_2.clicked.connect(self.ssh_exe_cmd_troubleshooting)
		self.pushButton_show_route.clicked.connect(self.ssh_exe_cmd_troubleshooting)
		self.pushButton_show_route_customer.clicked.connect(self.ssh_exe_cmd_troubleshooting)
		self.pushButton_sendemail.clicked.connect(self.send_email)
		
		
		#DSC Internal Cross Ping
		self.pushButton_list_package_loss_log.clicked.connect(self.internal_cross_ping_list_package_loss_log)
		self.pushButton_list_all_log.clicked.connect(self.internal_cross_ping_list_all_log)
		self.pushButton_show_log_content.clicked.connect(self.internal_cross_ping_show_log_content)
		self.pushButton_start_internal_cross_ping.clicked.connect(self.start_internal_cross_ping)
		self.pushButton_download_kpi_files.clicked.connect(self.download_DSC_internal_ping_kpi_files)
		self.pushButton_generate_report.clicked.connect(self.generate_report)
		
		self.dlbloginip={"HK DSC":"10.162.28.187","SG DSC":"10.163.28.132","AMS DSC":"10.160.28.221","FRT DSC":"10.161.28.249","CHI DSC":"10.166.28.201","DAL DSC":"10.164.28.190"}
		
		#Send mail: Customer name inputed
		self.comboBox_customer_name_send_mail.activated.connect(self.update_customer_list_sendmail)
		self.comboBox_customer_name_send_mail.currentIndexChanged.connect(self.update_customer_to_list)
		
		self.comboBox_customer_name_maintenance.activated.connect(self.update_customer_list_maintenance)
		
		self.pushButton_sendemail_send_mail.clicked.connect(self.send_email_sendmail)
		self.pushButton_add_maintenance.clicked.connect(self.add_customer_maintenance)
		
		self.pushButton_check_maintenance.clicked.connect(self.check_maintenance)
		
		global username, password,ccb_info
	
	def update_customer_list(self):
		print('okokokokokokok')
		global ccb_info
		
		#self.comboBox_customer_name.clear()
		
		customer_inputted=self.comboBox_customer_name.currentText()
		self.comboBox_customer_name.clear ()
		
		customer_list=[]
		try:
			for row in ccb_info:
				if customer_inputted.lower() in row["Operator"].lower():
					if row["Operator"] not in customer_list:
						customer_list.append(row["Operator"])
	
			print(customer_list)
			self.comboBox_customer_name.addItems(customer_list)
		except:
			pass
		
	def update_customer_peer(self):
		global ccb_info
		customer_name=self.comboBox_customer_name.currentText()
		self.comboBox_customer_peername.clear ()
		
		peer_list=[]
		try:
			for row in ccb_info:
				if customer_name.lower() == row["Operator"].lower():
					if row["Hostname"] not in peer_list:
						peer_list.append(row["Hostname"])
		
		
			print(peer_list)
			self.comboBox_customer_peername.addItems(peer_list)
		except:
			pass

	def test_account(self,username_signal,password_signal):
		global username, password,ccb_info
		username=username_signal
		password=password_signal
		
		self.lineEdit_GID.setText(username)

		#nowTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
		nowTime=datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%Y-%m-%d %H:%M')
		#self.dateTimeEdit_start_time.setDateTime(QDateTime.fromString(nowTime, 'yyyy-MM-dd hh:mm'))
		
		nowTime_utc=datetime.utcnow().replace(tzinfo=timezone.utc)
		start_time_show= nowTime_utc.astimezone(timezone(timedelta(hours=-3))).strftime('%Y-%m-%d %H:%M')
		
		self.dateTimeEdit_start_time.setDateTime(QDateTime.fromString(start_time_show, 'yyyy-MM-dd hh:mm'))
		self.dateTimeEdit_end_time.setDateTime(QDateTime.fromString(nowTime, 'yyyy-MM-dd hh:mm'))
		
		self.dateTimeEdit_start_time_maintenance.setDateTime(QDateTime.fromString(start_time_show, 'yyyy-MM-dd hh:mm'))
		self.dateTimeEdit_end_time_maintenance.setDateTime(QDateTime.fromString(nowTime, 'yyyy-MM-dd hh:mm'))
		
		#print(username,password)
		try:
			ssh_onetime_ping("10.162.28.187",username,password,"netstat -an")
			#print("before emit ok")
			self.account_result_signal.emit("ok")
			ccb_info=self.get_ccb_info()
			print('login ok')
		except paramiko.ssh_exception.AuthenticationException:
			print("before emit nok")
			self.account_result_signal.emit("nok")
		except OSError:
			self.account_result_signal.emit("nok_no_network")
			print('os Error')
			
			
	def get_peer_ip(self):
		global ccb_info
		
		#ccb_info=self.get_ccb_info()
			#print(ccb_info)
			
		print(self.comboBox_customer_peername.currentText())

		for row in ccb_info:
			if row["Hostname"] == self.comboBox_customer_peername.currentText():
				
				if row["Pingable"]:
					self.lineEdit_customerpeer_pingable.setText(row["Pingable"])
				else:
					self.lineEdit_customerpeer_pingable.setText('Null')
				
				if "," in row["SCTP_IP"]:
					self.lineEdit_customer1pip.setText(row["SCTP_IP"].split(",")[0])
					self.lineEdit_customer1sip.setText(row["SCTP_IP"].split(",")[1])
				elif ";" in row["SCTP_IP"]:
					self.lineEdit_customer1pip.setText(row["SCTP_IP"].split(";")[0])
					self.lineEdit_customer1sip.setText(row["SCTP_IP"].split(";")[1])
				else:
					self.lineEdit_customer1pip.setText(row["SCTP_IP"])
					self.lineEdit_customer1sip.setText("")
				print('break-you-ip')
				break
				
			else:
				self.lineEdit_customer1pip.setText('No IP for this peer in CCB')
				self.lineEdit_customer1sip.setText("")
				print('break-no-ip')
				
				
		#print('get ip done')
		
	def generatecmd(self):
		
		for dscname in ["HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC"]:
			if dscname==self.comboBox_DSC.currentText():
				print(dscname)
				self.lineEdit_dscpip.setText(self.dscpipdic[self.comboBox_DSC.currentText()])
				self.lineEdit_dscsip.setText(self.dscsipdic[self.comboBox_DSC.currentText()])
				
		self.Customerpip={"Customer 1":self.lineEdit_customer1pip.text(),"Customer 2":self.lineEdit_customer2pip.text(),"Customer 3":self.lineEdit_customer3pip.text(),"Customer 4":self.lineEdit_customer4pip.text()}
		self.Customersip={"Customer 1":self.lineEdit_customer1sip.text(),"Customer 2":self.lineEdit_customer2sip.text(),"Customer 3":self.lineEdit_customer3sip.text(),"Customer 4":self.lineEdit_customer4sip.text()}
		
		for customer in ["HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC"]:
			if customer==self.comboBox_customer.currentText():
				self.lineEdit_customerselectedpip.setText(self.dscpipdic[self.comboBox_customer.currentText()])
				self.lineEdit_customerselectedsip.setText(self.dscsipdic[self.comboBox_customer.currentText()])
		
				netstatcmd=('netstat -an | grep -E "'+self.dscpipdic[self.comboBox_customer.currentText()]+'|'+self.dscsipdic[self.comboBox_customer.currentText()]+'"')
				print(netstatcmd)
				if netstatcmd[-2]=="|":
					netstatcmd=netstatcmd[:-2]+'"'
					print(netstatcmd)
				self.lineEdit_netstatcmd.setText(netstatcmd)
				
				self.lineEdit_p2ppingcmd.setText('ping -I '+self.lineEdit_dscpip.text()+' '+self.lineEdit_customerselectedpip.text()+' -s1472 -c3')
				self.lineEdit_p2ptracertcmd.setText('traceroute -s '+ self.lineEdit_dscpip.text()+' '+self.lineEdit_customerselectedpip.text())
				self.lineEdit_s2spingcmd.setText('ping -I '+self.lineEdit_dscsip.text()+' '+self.lineEdit_customerselectedsip.text()+' -s1472 -c3')
				self.lineEdit_s2stracertcmd.setText('traceroute -s '+ self.lineEdit_dscsip.text()+' '+self.lineEdit_customerselectedsip.text())
		
		for Customer in ["Customer 1","Customer 2","Customer 3","Customer 4"]:
			if Customer==self.comboBox_customer.currentText():
				print(Customer)
				self.lineEdit_customerselectedpip.setText(self.Customerpip[Customer])
				self.lineEdit_customerselectedsip.setText(self.Customersip[Customer])
				
				netstatcmd=('netstat -an | grep -E "'+self.Customerpip[Customer]+'|'+self.Customersip[Customer]+'"')
				print(netstatcmd)
				if netstatcmd[-2]=="|":
					netstatcmd=netstatcmd[:-2]+'"'
					print(netstatcmd)
				self.lineEdit_netstatcmd.setText(netstatcmd)
				
				self.lineEdit_p2ppingcmd.setText('ping -I '+self.lineEdit_dscpip.text()+' '+self.lineEdit_customerselectedpip.text()+' -s1472 -c3')
				self.lineEdit_p2ptracertcmd.setText('traceroute -s '+ self.lineEdit_dscpip.text()+' '+self.lineEdit_customerselectedpip.text())
				self.lineEdit_s2spingcmd.setText('ping -I '+self.lineEdit_dscsip.text()+' '+self.lineEdit_customerselectedsip.text()+' -s1472 -c3')
				self.lineEdit_s2stracertcmd.setText('traceroute -s '+ self.lineEdit_dscsip.text()+' '+self.lineEdit_customerselectedsip.text())

	def ssh_exe_cmd(self):
		global username, password
		result_log_old=self.textEdit_resultlog.toPlainText()
		
		for dscname in ["HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC"]:
			if dscname==self.comboBox_DSC.currentText():
				hostname=self.dlbloginip[self.comboBox_DSC.currentText()]
		print(hostname)
		cmd_all={'netstat':self.lineEdit_netstatcmd.text(),'P2P: Ping':self.lineEdit_p2ppingcmd.text(),'P2P: TraceRT':self.lineEdit_p2ptracertcmd.text(),'S2S: Ping':self.lineEdit_s2spingcmd.text(),'S2S: TraceRT':self.lineEdit_s2stracertcmd.text()}
		sender=self.sender()
		print(sender.text())
		for sender_name in ['netstat','P2P: Ping','P2P: TraceRT','S2S: Ping','S2S: Ping','S2S: TraceRT']:
			if sender_name==sender.text():
				cmd=cmd_all[sender_name]
		print(cmd)
		results=ssh_onetime_ping(hostname,username,password,cmd)
		result_final=""
		for result in results:
			result_final=result_final+result
		print("result_final:"+result_final)
		self.textEdit_resultlog.setPlainText(result_log_old+"\n***************************************\n"+cmd+"\n"+result_final)
		self.textEdit_resultlog.moveCursor(QtGui.QTextCursor.End) 

	def input_alarms(self):
		input_alarms.show()
		
	def dic_remove_duplication(self,dic):
		dic_new=copy.deepcopy(dic)
		dic_old=copy.deepcopy(dic)
		for i in range(0,len(dic_new)):
			if i in dic_new.keys():
				print('i: '+ str(i))
				for j in range(i+1,len(dic_old)):
					print('i in J loop: '+ str(i))
					print('j: '+str(j))
					if dic_new[i][2]==dic_old[j][2] and dic_new[i][4]==dic_old[j][4]:
						print('meet duplication')
						print(dic_new[i][1][0:4])
						print(dic_old[j][1][0:4])
						if dic_new[i][1][0:4]==dic_old[j][1][0:4]:
							print('same dsc')
							del dic_new[j]
						elif dic_new[i][1][0:4]!=dic_old[j][1][0:4] and dic_new[i][1][0:4] in ['hk1p','sg1p'] and dic_old[j][1][0:4] in ['hk1p','sg1p']:
							dic_new[i].append(dic_old[j][1])
							print('both ap dsc')
							del dic_new[j]
						elif dic_new[i][1][0:4]!=dic_old[j][1][0:4] and dic_new[i][1][0:4] in ['am1p','fr4p'] and dic_old[j][1][0:4] in ['am1p','fr4p']:
							dic_new[i].append(dic_old[j][1])
							print('both ams dsc')
							del dic_new[j]
						elif dic_new[i][1][0:4]!=dic_old[j][1][0:4] and dic_new[i][1][0:4] in ['mdw0','dal0'] and dic_old[j][1][0:4] in ['mdw0','dal0']:
							dic_new[i].append(dic_old[j][1])
							print('both chi dsc')
							del dic_new[j]
						#print("del: "+ str(j))
						#print(dic_new)
						#print(dic_old)
						else:
							print('no match')
				dic_new[i].append('Null')
					
		#print("New alarm dic:")
		#print(dic_new)
		
		i=0
		dic_final={}
		for key,value in dic_new.items():
			dic_final[i]=dic_new[key]
			i=i+1
		#print("dic_final: ")
		#print(dic_final)
		return dic_final

	def alarm_content_handler(self,alarms_content):
		global alarms_dic_final

		#clear current alarm list
		self.comboBox_alarm_list.clear()
		self.lineEdit_alarm.setText("")
		self.lineEdit_time.setText("")
		self.lineEdit_peer_name.setText("")
		self.lineEdit_alarm_description.setText("")
		self.lineEdit_connected_dsc.setText("")
		self.lineEdit_customer.setText("")
		self.lineEdit_pingable_2.setText("")
		self.lineEdit_peerpip.setText("")
		self.lineEdit_peersip.setText("")
		self.lineEdit_connected_dsc.setText("")
		self.lineEdit_alarm_description.setText("")
		self.lineEdit_p2ppingcmd_2.setText("")
		self.lineEdit_p2ptracertcmd_2.setText("")
		self.lineEdit_netstatcmd_2.setText("")
		self.lineEdit_s2spingcmd_2.setText("")
		self.lineEdit_s2stracertcmd_2.setText("")
		self.textEdit_resultlog_troubleshooting.setText("")

		try:
			if alarms_content=="":
				return 0
			alarms_dic={}
			#alarms_list=alarms_content.split('\n')
			#alarms_list=alarms_content.splitlines()
			
			alarms_list=re.split(r'\n',alarms_content) 
			
			#print(alarms_list)
			for item in alarms_list:
				#if item=="  " or item.strip()==' ':
				#	alarms_list.remove(item)
				if item.strip()=="":
					alarms_list.remove(item)
			print("Origin alarms list: ")
			print(alarms_list)
	
			alarms_amount=len(alarms_list)
			print('Length of Origin alarms list	')
			print(alarms_amount)
			
			for alarms_index in range(0,alarms_amount):
				if '|' not in alarms_list[alarms_index]:
					#alarms_list[alarms_index]=alarms_list[alarms_index].split('   ')
					alarms_list[alarms_index]=re.split(r'(   |10302|10312)',alarms_list[alarms_index]) 
	
					while '   ' in alarms_list[alarms_index]:
						alarms_list[alarms_index].remove('   ')
					
					while '' in alarms_list[alarms_index]:
						alarms_list[alarms_index].remove('')
					print("Alarm: " + str(alarms_index)+ " in alarms list after split:")
					print(alarms_list[alarms_index])
	
					for alarms_content_item in alarms_list[alarms_index]:
						if '/' in alarms_content_item:
							alarms_list[alarms_index][0]=alarms_content_item.strip()
						elif '-gen-dsc-' in alarms_content_item:
							alarms_list[alarms_index][1]=alarms_content_item.strip()
						elif '[[AppId' in alarms_content_item or '[16777251' in alarms_content_item:
							
							if '[[AppId' in alarms_content_item:
								realm_before_list=alarms_content_item.strip().replace('[[AppId','((( ').split(' ')
							if '[16777251' in alarms_content_item:
								realm_before_list=alarms_content_item.strip().strip().replace('[16777251','((( ').split(' ')
								
							print(realm_before_list)
							for alarms_items in realm_before_list:
								if '(((' in alarms_items:
									realm_alarm=alarms_items[:-3]
								#if alarms_items=="Realm":
								#	realm_alarm=realm_before_list[realm_before_list.index('Realm')+1]
								#elif  alarms_items=="DSC-APP":
								#	realm_alarm=realm_before_list[realm_before_list.index('DSC-APP')+1]
							print('\n Realm in alarms:')
							print(realm_alarm)
							alarms_list[alarms_index][4]=realm_alarm
							alarms_list[alarms_index][2]="10312"
							alarms_list[alarms_index][3]="The last active peer in this realm is now disconnected"
						elif '([SCTP]' in alarms_content_item:
	
							peer_before_list=alarms_content_item.strip().replace('[',' ').split(' ')
							for alarms_items in peer_before_list:
								if '(' in alarms_items:
									peer_alarm=alarms_items[:-1]
							print('\n Peer in alarms:')
							print(peer_alarm)
							alarms_list[alarms_index][4]=peer_alarm
							alarms_list[alarms_index][2]="10302"
							alarms_list[alarms_index][3]="The peer is disconnected"
							
				elif '|' in alarms_list[alarms_index]:
					print("ok")
					alarms_list[alarms_index]=alarms_list[alarms_index].split('|')
					while '' in alarms_list[alarms_index]:
						alarms_list[alarms_index].remove('')
					#print(alarms_list[alarms_index])
					for alarms_content_item in alarms_list[alarms_index]:
						if '/' in alarms_content_item:
							alarms_list[alarms_index][0]=alarms_content_item.strip()
						elif '-gen-dsc-' in alarms_content_item:
							alarms_list[alarms_index][1]=alarms_content_item.strip()
						elif '10312' in alarms_content_item:
							realm_before_list=alarms_content_item.strip().replace('[',' ').split(' ')
							realm_alarm=realm_before_list[realm_before_list.index('Realm')+1]
							print(realm_alarm)
							alarms_list[alarms_index][4]=realm_alarm
							alarms_list[alarms_index][2]="10312"
							alarms_list[alarms_index][3]="The last active peer in this realm is now disconnected"
						elif '10302' in alarms_content_item:
							peer_before_list=alarms_content_item.strip().replace('[',' ').split(' ')
							for alarms_items in peer_before_list:
								if '(' in alarms_items:
									peer_alarm=alarms_items[:-1]
									print(peer_alarm)
							alarms_list[alarms_index][4]=peer_alarm
							alarms_list[alarms_index][2]="10302"
							alarms_list[alarms_index][3]="The peer is disconnected"
	
				alarms_dic[alarms_index]=alarms_list[alarms_index][0:5]
			print("Origin_alarms_dic_before_remove_duplication:")
			print(alarms_dic)

		
			alarms_dic_final=self.dic_remove_duplication(alarms_dic)
			print("Final alarms dic after remove duplication: ")
			print(alarms_dic_final)
			
			alarm_list_cmobo=[]
			for i in range(1,len(alarms_dic_final)+1):
				alarm_list_cmobo.append("Alarm "+str(i))
			self.comboBox_alarm_list.addItems(alarm_list_cmobo)
		except:
			QMessageBox.information(self,"Warning","Alarm format not supported! \nPlease check again or contact 'Insight Tailor Team!'",QMessageBox.Ok)

	def generate_alarms(self):
		global alarms_dic_final,customer_email_list,customer_nodes,ccb_info
		dsc_name_app_mapping_dic={"hk1p":"HK DSC","sg1p":"SG DSC","am1p":"AMS DSC","fr4p":"FRT DSC","mdw01p":"CHI DSC","dal01p":"DAL DSC"}

		try:
			for value in alarms_dic_final.values():
				for dsc_app_name in ["hk1p","sg1p","am1p","fr4p","mdw01p","dal01p"]:
					if dsc_app_name in value[1]:
						value[1]=dsc_name_app_mapping_dic[dsc_app_name]
					if dsc_app_name in value[5]:
						value[5]=dsc_name_app_mapping_dic[dsc_app_name]
						#print(value[1])

			print(int(self.comboBox_alarm_list.currentText()[-1])-1)
			self.lineEdit_alarm.setText(alarms_dic_final[int(self.comboBox_alarm_list.currentText()[-1])-1][2])
			self.lineEdit_time.setText(alarms_dic_final[int(self.comboBox_alarm_list.currentText()[-1])-1][0])
			self.lineEdit_peer_name.setText(alarms_dic_final[int(self.comboBox_alarm_list.currentText()[-1])-1][4])
			self.lineEdit_alarm_description.setText(alarms_dic_final[int(self.comboBox_alarm_list.currentText()[-1])-1][3])
			self.lineEdit_connected_dsc.setText(alarms_dic_final[int(self.comboBox_alarm_list.currentText()[-1])-1][1])
			self.lineEdit_connected_dsc_2.setText(alarms_dic_final[int(self.comboBox_alarm_list.currentText()[-1])-1][5])
			
	
			#ccb_info=self.get_ccb_info()
			#print(ccb_info)
	
			for row in ccb_info:
				if row["Virtual_Realm"] == alarms_dic_final[int(self.comboBox_alarm_list.currentText()[-1])-1][4] or row["Hostname"]==alarms_dic_final[int(self.comboBox_alarm_list.currentText()[-1])-1][4]:
					#print(type(row["Virtual_Realm"]))
					self.lineEdit_customer.setText(row["Operator"])
					self.lineEdit_pingable_2.setText(row["Pingable"])
					customer_nodes=row['Hostname']
					if row["Customer_Contact"] is not None:
						customer_email_list=row["Customer_Contact"]
						#print("customer_email_list_ok"+customer_email_list)
					else:
						customer_email_list="Null"
						#print("customer_email_list-null, but peer/realm ok")
					if "," in row["SCTP_IP"]:
						self.lineEdit_peerpip.setText(row["SCTP_IP"].split(",")[0])
						self.lineEdit_peersip.setText(row["SCTP_IP"].split(",")[1])
					elif ";" in row["SCTP_IP"]:
						self.lineEdit_peerpip.setText(row["SCTP_IP"].split(";")[0])
						self.lineEdit_peersip.setText(row["SCTP_IP"].split(";")[1])
					else:
						self.lineEdit_peerpip.setText(row["SCTP_IP"])
						self.lineEdit_peersip.setText("")
					break
				else:
					customer_email_list="Null"
			print("customer_email_list-null:"+customer_email_list)
				#if row["Virtual_Realm"] == alarms_dic_final[int(self.comboBox_alarm_list.currentText()[-1])-1][4]:
					#customer_nodes=row['Hostname']
		except IndexError:
			pass
	def get_ccb_info(self):
		#print('get ccb info now')
		import datetime
		import pymysql.cursors
		namelist=[] 
		#连接配置信息
		config = {
			'host':'hk1p-gen-ccb-mdb002.syniverse.com',
			'port':3310,
			'user':'ccbapp',
			'password':'MiC2B$ma',
			'db':'ccb',
			'charset':'utf8mb4',
			'cursorclass':pymysql.cursors.DictCursor,
			}
		# 创建连接,执行sql语句
		try:
			connection = pymysql.connect(**config)
			with connection.cursor() as cursor:
				# 执行sql语句，进行查询
				sql = """select np4.value Virtual_Realm,ci.name Operator,ni.value DSC_Peer,ni.aicent Hostname,np1.value SCTP_IP,np2.value Pingable,np3.value WorkMode,replace(GROUP_CONCAT(DISTINCT con.email),',',';') Customer_Contact from neinfo ni 
left join subscribedservice ss on ss.id=ni.pkgid 
left join customerinfo ci on ci.id=ss.customerid 
left join contactinfo con on con.pkgid=ni.pkgid and con.contacttype in ('Technical','Noc-Imported') and con.email like '%@%' 
left join neavpair np1 on np1.neitemid=ni.id and np1.attribute='SCTP_IP'
left join neavpair np2 on np2.neitemid=ni.id and np2.attribute='Pingable'
left join neavpair np3 on np3.neitemid=ni.id and np3.attribute='WorkMode'
left join neavpair np4 on np4.neitemid=ni.id and np4.attribute='Virtual Realm'
where ni.item='DSC_Peer' group by ni.value;"""
				cursor.execute(sql)
				# 获取查询结果
				results = cursor.fetchall()
				#没有设置默认自动提交，需要主动提交，以保存所执行的语句
			connection.commit()
			connection.close()
		except pymysql.err.OperationalError:
			QMessageBox.information(self,"Warning","Can't connect to CCB, please check your network.",QMessageBox.Ok)
			results=""
		#return(results)

		try:
			import csv
			if os.path.exists("file")==0:
				os.mkdir("file")
			with open('.\\file\ccb_online.csv', 'w',newline='',encoding='utf-8') as csvfile:
				spamwriter = csv.writer(csvfile)
				string=[]
				for keys in results[1]:
					string.append(keys)
				spamwriter.writerow(string)
				for row in results:
					string=[]
					string.append(row['Virtual_Realm'])
					string.append(row['Operator'])
					string.append(row['DSC_Peer'])
					string.append(row['Hostname'])
					string.append(row['SCTP_IP'])
					string.append(row['Pingable'])
					string.append(row['WorkMode'])
					string.append(row['Customer_Contact'])
					spamwriter.writerow(string)
		except:
			pass
		return(results)

	def generatecmd_troubleshooting(self,none):
		self.dscpipdic={"HK DSC":"173.209.220.115","SG DSC":"173.209.221.115","AMS DSC":"173.209.215.102","FRT DSC":"173.209.215.166","CHI DSC":"131.166.129.119","DAL DSC":"131.166.129.151"}
		self.dscsipdic={"HK DSC":"173.209.220.123","SG DSC":"173.209.221.123","AMS DSC":"173.209.215.118","FRT DSC":"173.209.215.182","CHI DSC":"131.166.129.135","DAL DSC":"131.166.129.167"}
		dsc_pip=""
		dsc_sip=""
		for dscname in ["HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC"]:
			if dscname==self.lineEdit_connected_dsc.text():
				#print(dscname)
				dsc_pip=(self.dscpipdic[dscname])
				dsc_sip=(self.dscsipdic[dscname])
		customer_pip=self.lineEdit_peerpip.text()
		customer_sip=self.lineEdit_peersip.text()
		
		if dsc_pip!="":
			netstatcmd=('netstat -an | grep -E "'+customer_pip+'|'+customer_sip+'"')
			#print(netstatcmd)
			if "Null" in netstatcmd:
				netstatcmd=netstatcmd.replace("|Null","")
			if '|"' in netstatcmd:
				netstatcmd=netstatcmd.replace('|"','"')
				#print(netstatcmd)
			self.lineEdit_netstatcmd_2.setText(netstatcmd)
	
			self.lineEdit_p2ppingcmd_2.setText('ping -I '+dsc_pip+' '+customer_pip+' -s1472 -c3')
			self.lineEdit_p2ptracertcmd_2.setText('traceroute -s '+ dsc_pip+' '+customer_pip)
			self.lineEdit_show_route.setText('show route ' + dsc_pip)
			self.lineEdit_show_route_customer.setText('show route ' + customer_pip)
			if customer_sip!="Null":
				self.lineEdit_s2spingcmd_2.setText('ping -I '+dsc_sip+' '+customer_sip+' -s1472 -c3')
				self.lineEdit_s2stracertcmd_2.setText('traceroute -s '+ dsc_sip+' '+customer_sip)
			else:
				self.lineEdit_s2spingcmd_2.setText('Null')
				self.lineEdit_s2stracertcmd_2.setText('Null')

	def ssh_exe_cmd_troubleshooting(self):
		global username, password
		result_log_old=self.textEdit_resultlog_troubleshooting.toPlainText()
		
		for dscname in ["HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC"]:
			if dscname==self.lineEdit_connected_dsc.text():
				hostname=self.dlbloginip[dscname]
		print(hostname)
		
		cmd_all={'netstat':self.lineEdit_netstatcmd_2.text(),'P2P: Ping':self.lineEdit_p2ppingcmd_2.text(),'P2P: TraceRT':self.lineEdit_p2ptracertcmd_2.text(),'S2S: Ping':self.lineEdit_s2spingcmd_2.text(),'S2S: TraceRT':self.lineEdit_s2stracertcmd_2.text(),'Show route: DSC PIP':self.lineEdit_show_route.text(),'Show route: Customer PIP':self.lineEdit_show_route_customer.text()}
		sender=self.sender()
		print(sender.text())
		
		for sender_name in ['netstat','P2P: Ping','P2P: TraceRT','S2S: Ping','S2S: Ping','S2S: TraceRT']:
			if sender_name==sender.text():
				cmd=cmd_all[sender_name]
				print(cmd)
				results=ssh_onetime_ping(hostname,username,password,cmd)
				result_final=""
				for result in results:
					result_final=result_final+result
				print("result_final:"+result_final)
				self.textEdit_resultlog_troubleshooting.setPlainText(result_log_old+"\n***************************************\n"+cmd+"\n"+result_final)
				self.textEdit_resultlog_troubleshooting.moveCursor(QtGui.QTextCursor.End) 
		
		for sender_name in ['Show route: DSC PIP','Show route: Customer PIP']:
			if sender_name==sender.text():
				cmd=cmd_all[sender_name]
				print(cmd)
				results=ssh_jump_server_cmd('10.12.7.16',username,password,cmd)
				result_final=results
				print(result_final)
				self.textEdit_resultlog_troubleshooting.setPlainText(result_log_old+"\n***************************************\n"+result_final)
				self.textEdit_resultlog_troubleshooting.moveCursor(QtGui.QTextCursor.End) 
	
	def send_email_for_Null(self):
		global customer_email_list,customer_nodes
		self.syniverse_peer_dic={'HK DSC':'hkg-01.dra.ipx.syniverse.3gppnetwork.org','SG DSC':'sng-01.dra.ipx.syniverse.3gppnetwork.org','AMS DSC':'ams-01.dra.ipx.syniverse.3gppnetwork.org',
		'FRT DSC':'frt-01.dra.ipx.syniverse.3gppnetwork.org','CHI DSC':'chi-01.dra.ipx.syniverse.3gppnetwork.org', 'DAL DSC':'dal-01.dra.ipx.syniverse.3gppnetwork.org','Null':''}
		
		try:
			if customer_email_list=="Null":
				print("Trigger send email for Null")
				customer_email_list="DSS_Route_Provision@syniverse.com;wind.wang@syniverse.com;joe.mercado@syniverse.com"
				Subject="Can't find the peer/customer contact in CCB for 10302/10312 alarms"
				email_body='''<html><body>
				<p style='font-family:Arial;font-size:13;color:black'>
				Dear DSS team,<br/><br/>
				Greeting from TTAC!<br/><br/> 
				We detect the customer node/realm in 10302/10312 alarms:  <br/>
				<strong><font color="#0066CC">customer_nodes<br/><br/> </font></strong>
				Disconnect with Syniverse diameter node: <br/>
				<strong><font color="#0066CC">Syniverse_peer1<br/></font></strong>
				<strong><font color="#0066CC">Syniverse_peer2<br/><br/></font></strong>
				1. Prilimary troubleshooting on IPX transport shows it is not a transport problem. <br/>
				2. Please help check the peer/realm and contact with customer.<br/><br/>
				<strong>Logs:<br/></strong>
				<i>ping_tracert_logs</i><br/><br/>
				Best regards,<br/>
				<Strong>Syniverse IPX Network Team<br/></Strong>
				</p>
				</body></html>'''
				logs_for_html=html_line_break(self.textEdit_resultlog_troubleshooting.toPlainText())
				email_body=email_body.replace('customer_nodes',self.lineEdit_peer_name.text())
				email_body=email_body.replace('ping_tracert_logs',logs_for_html)
				
				for dsc_name in ["HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC",'Null']:
					if dsc_name==self.lineEdit_connected_dsc.text():
						email_body=email_body.replace('Syniverse_peer1',self.syniverse_peer_dic[dsc_name])
				for dsc_name in ["HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC",'Null']:
					if dsc_name==self.lineEdit_connected_dsc_2.text():
						email_body=email_body.replace('Syniverse_peer2',self.syniverse_peer_dic[dsc_name])
		except:
			pass

		try:
			sendemail(customer_email_list,'DSS_Route_Provision@syniverse.com;TTAC@syniverse.com',Subject,email_body)
		except NameError:
			pass
	
	def send_email(self):
		global customer_email_list,customer_nodes

		self.syniverse_peer_dic={'HK DSC':'hkg-01.dra.ipx.syniverse.3gppnetwork.org','SG DSC':'sng-01.dra.ipx.syniverse.3gppnetwork.org','AMS DSC':'ams-01.dra.ipx.syniverse.3gppnetwork.org',
		'FRT DSC':'frt-01.dra.ipx.syniverse.3gppnetwork.org','CHI DSC':'chi-01.dra.ipx.syniverse.3gppnetwork.org', 'DAL DSC':'dal-01.dra.ipx.syniverse.3gppnetwork.org','Null':''}

		"""if customer_email_list=="Null":
			customer_email_list="DSS_Route_Provision@syniverse.com;wind.wang@syniverse.com;joe.mercado@syniverse.com"
			Subject="Can't find the peer/customer contact in CCB for 10302/10312 alarms"
			email_body='''<html><body>
			<p style='font-family:Arial;font-size:13;color:black'>
			Dear DSS team,<br/><br/>
			Greeting from TTAC!<br/><br/> 
			We detect the customer node/realm in 10302/10312 alarms:  <br/>
			<strong><font color="#0066CC">customer_nodes<br/><br/> </font></strong>
			Disconnect with Syniverse diameter node: <br/>
			<strong><font color="#0066CC">Syniverse_peer1<br/></font></strong>
			<strong><font color="#0066CC">Syniverse_peer2<br/><br/></font></strong>
			1. Prilimary troubleshooting on IPX transport shows it is not a transport problem. <br/>
			2. Please help check the peer/realm and contact with customer.<br/><br/>
			<strong>Logs:<br/></strong>
			<i>ping_tracert_logs</i><br/><br/>
			Best regards,<br/>
			<Strong>Syniverse IPX Network Team<br/></Strong>
			</p>
			</body></html>'''
			logs_for_html=html_line_break(self.textEdit_resultlog_troubleshooting.toPlainText())
			email_body=email_body.replace('customer_nodes',self.lineEdit_peer_name.text())
			email_body=email_body.replace('ping_tracert_logs',logs_for_html)
			
			for dsc_name in ["HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC",'Null']:
				if dsc_name==self.lineEdit_connected_dsc.text():
					email_body=email_body.replace('Syniverse_peer1',self.syniverse_peer_dic[dsc_name])
			for dsc_name in ["HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC",'Null']:
				if dsc_name==self.lineEdit_connected_dsc_2.text():
					email_body=email_body.replace('Syniverse_peer2',self.syniverse_peer_dic[dsc_name])"""
					
		if self.lineEdit_alarm.text()=='10302' and customer_email_list!='Null':
			Subject='Syniverse Alarm Notice – Diameter Peer disconnection with customer_name'
			email_body='''<html><body>
			<p style='font-family:Arial;font-size:13;color:black'>
			Dear Colleagues,<br/><br/>
			Greeting from Syniverse!<br/><br/> 
			We detect your diameter nodes:  <br/>
			<strong><font color="#0066CC">customer_nodes<br/><br/> </font></strong>
			Disconnect with Syniverse diameter node: <br/>
			<strong><font color="#0066CC">Syniverse_peer1<br/></font></strong>
			<strong><font color="#0066CC">Syniverse_peer2<br/><br/></font></strong>
			1. Prilimary troubleshooting on IPX transport shows it is not a transport problem. <br/>
			2. Please help troubleshooting on your Diameter node to check the root cause and fix the problem.<br/><br/>
			<strong>Logs:<br/></strong>
			<i>ping_tracert_logs</i><br/><br/>
			Best regards,<br/>
			<Strong>Syniverse IPX Network Team<br/></Strong>
			</p>
			</body></html>'''
			logs_for_html=html_line_break(self.textEdit_resultlog_troubleshooting.toPlainText())
			Subject=Subject.replace('customer_name', self.lineEdit_customer.text())
			email_body=email_body.replace('customer_nodes',self.lineEdit_peer_name.text())
			email_body=email_body.replace('ping_tracert_logs',logs_for_html)
			
			for dsc_name in ["HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC",'Null']:
				if dsc_name==self.lineEdit_connected_dsc.text():
					email_body=email_body.replace('Syniverse_peer1',self.syniverse_peer_dic[dsc_name])
			for dsc_name in ["HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC",'Null']:
				if dsc_name==self.lineEdit_connected_dsc_2.text():
					email_body=email_body.replace('Syniverse_peer2',self.syniverse_peer_dic[dsc_name])

		elif self.lineEdit_alarm.text()=='10312' and customer_email_list!='Null':
			Subject='Syniverse Alarm Notice – All Diameter Peers disconnection with customer_name'
			email_body='''<html><body>
			<p style='font-family:Arial;font-size:13;color:black'>
			Dear Colleagues,<br/><br/>
			Greeting from Syniverse!<br/><br/> 
			We detect your diameter nodes under realm:  <br/>
			<strong><font color="#0066CC">Realm: customer_realm<br/> </font></strong>
			<strong><font color="#0066CC">Node: customer_nodes<br/><br/> </font></strong>
			Disconnect with Syniverse diameter node: <br/>
			<strong><font color="#0066CC">Syniverse_peer1<br/></font></strong>
			<strong><font color="#0066CC">Syniverse_peer2<br/><br/></font></strong>
			1. Prilimary troubleshooting on IPX transport shows it is not a transport problem. <br/>
			2. Please help troubleshooting on your Diameter node to check the root cause and fix the problem.<br/><br/>
			<strong>Logs:<br/></strong>
			<i>ping_tracert_logs</i><br/><br/>
			Best regards,<br/>
			<Strong>Syniverse IPX Network Team<br/></Strong>
			</p>
			</body></html>'''
			
			logs_for_html=html_line_break(self.textEdit_resultlog_troubleshooting.toPlainText())
			Subject=Subject.replace('customer_name', self.lineEdit_customer.text())
			email_body=email_body.replace('customer_realm',self.lineEdit_peer_name.text())
			email_body=email_body.replace('customer_nodes',customer_nodes)
			email_body=email_body.replace('ping_tracert_logs',logs_for_html)
			
			for dsc_name in ["HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC",'Null']:
				if dsc_name==self.lineEdit_connected_dsc.text():
					email_body=email_body.replace('Syniverse_peer1',self.syniverse_peer_dic[dsc_name])
			for dsc_name in ["HK DSC","SG DSC","AMS DSC","FRT DSC","CHI DSC","DAL DSC",'Null']:
				if dsc_name==self.lineEdit_connected_dsc_2.text():
					email_body=email_body.replace('Syniverse_peer2',self.syniverse_peer_dic[dsc_name])
		
		nowTime_y=datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%Y')
		nowTime_m=datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%m')
		nowTime_d=datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%d')
		nowTime_h=datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%H')
		nowTime_M=datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%M')
		
		NowTime=int(nowTime_y+nowTime_m+nowTime_d+nowTime_h+nowTime_M)
		print("NowTime:")
		print(NowTime)

		try:
			if self.lineEdit_customer.text()=="":
				return 0
			else:
				cmd='cat /data2/TMP/tsdss/DSC_Send_Mail_Tool/DSC_Maintenance_Record.csv'
				current_maintenance=ssh_onetime_ping('10.162.28.185',username,password,cmd)
				print(current_maintenance)
				for item in current_maintenance:
					print(item)
					if item.split(',')[0]==self.lineEdit_customer.text() and int(item.split(',')[1])<=NowTime<=int(item.split(',')[2]):
						
						maintenance_customer=item.split(',')[0]
						maintenance_starttime=item.split(',')[1]
						maintenance_endtime=item.split(',')[2]
						maintenance_owner=item.split(',')[-1]
						
						note_temp=item.split(',')[3:-1]
						note_final=""
						for item in note_temp:
							note_final+=item
						
						maintenance_note=note_final
						#maintenance_note=re.split(r[maintenance_customer or maintenance_starttime or maintenance_endtime or maintenance_owner],item)
						print('maintenance_note:')
						print(maintenance_note)
	
						maintenance_info='Customer: '+maintenance_customer+'\nStart Time(UTC): '+maintenance_starttime+'\nEnd Time(UTC): '+maintenance_endtime+'\nNote: '+maintenance_note+'\nOwner: '+maintenance_owner
						QMessageBox.information(self,"Warning","There's maintenance ongoing for "+self.lineEdit_customer.text()+"!\nPlease don't send mail to customer.\n\nMaintenance details:\n"+maintenance_info,QMessageBox.Ok)
						return 0
				QMessageBox.information(self,"Information","No maintenance ongoing for "+self.lineEdit_customer.text()+', click "OK" to send mail.',QMessageBox.Ok)
				if customer_email_list!='Null':
					sendemail(customer_email_list,'DSS_Route_Provision@syniverse.com;TTAC@syniverse.com',Subject,email_body)
		except NameError:
			pass


#********************************************************************************************************
#********************************    Function: 7*24 Ping     ********************************************
#********************************************************************************************************

	def analyse_traceroute_result(self):
		global username, password,router_list

		try:
			self.textEdit_traceroute_analysis_result.clear()
			#print(self.textEdit_traceroute_result.toPlainText())
			router_list=get_router_list_from_traceroute(self.textEdit_traceroute_result.toPlainText(),username,password)
			print(router_list)
			n=1
			for router in router_list:
				routerinfo_old=self.textEdit_traceroute_analysis_result.toPlainText()
				self.textEdit_traceroute_analysis_result.setPlainText(routerinfo_old+'\n'+str(n)+': '+str(router))
				n=n+1
		except Exception as e:
			print(e)
			QMessageBox.information(self,"Warning","The traceroute result you pasted is not right. Please check the example.",QMessageBox.Ok)

	def start_7_24_ping(self):
		global username, password,router_list

		"""try:
			print(self.textEdit_traceroute_result.toPlainText())
			#information_start="You are going to start the 7*24 ping hop-by-hop per your traceroute."+"\n" +"Click OK to start(May take few seconds)."
			#QMessageBox.information(self,"Information",information_start,QMessageBox.Ok)
			all_Day_Ping_Result.show()
			router_list=get_router_list_from_traceroute(self.textEdit_traceroute_result.toPlainText(),username,password)
			print(router_list)

		except Exception as e:
			QMessageBox.information(self,"Warning","The traceroute result log you pasted is not right(Check the example).",QMessageBox.Ok)
			all_Day_Ping_Result.close()
		else:
			#all_Day_Ping_Result.show()
			#router1=router_list[3]['router_name']"""
		
		if self.textEdit_incident_description.toPlainText() =="":
			QMessageBox.information(self,"Warning","Please input the INC description",QMessageBox.Ok)
		else:
			try:
				#all_Day_Ping_Result.show()
				for router in router_list:
					t= threading.Thread(target=self.ping_routers_exe,args=(router,router_list.index(router)))
					print(router)
					print(router_list.index(router))
					t.start()
				#ping_result=ssh_jump_server_juniper_cmd(router1,username,password,"ping 192.168.71.206 count 5 rapid wait 1","show system uptime | match current")
				#print(ping_result)
			except:
				#all_Day_Ping_Result.close()
				QMessageBox.information(self,"Warning","Please analyze your traceroute result first(step2)",QMessageBox.Ok)
			else:
				all_Day_Ping_Result.show()
				self.start_7_24_ping_signal.emit(1,self.textEdit_incident_description.toPlainText())
	
	def stop_7_24_ping_flag(self,stop_flag):
		global stop_ping_flag
		if stop_flag=='Stop':
			stop_ping_flag=0
			
	
	def reset_trace_analysis_result(self):
		self.textEdit_traceroute_analysis_result.clear()
	
	def ping_routers_exe(self,router,router_index):
		global username, password, stop_ping_flag
		#print(router)
		#print(router_index)
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname="10.12.7.16", port=22, username=username, password=password)
		chan=ssh.invoke_shell()
		if router['vendor']=='Juniper':
			ssh_router_cmd="ssh " + router['router_name']
			print(ssh_router_cmd)
			chan.send(ssh_router_cmd+'\n')
			time.sleep(4)
			res=chan.recv(65535).decode('utf8')
			if '(yes/no)' in res:
				chan.send('yes'+'\n')
				time.sleep(2)
			chan.send(password+'\n')
			time.sleep(2)
			res=chan.recv(65535)
			cmd1="show system uptime | match current"
			cmd2="ping " + router['next_hop_ip'] +' count 5 rapid wait 1'
		else:
			telnet_router_cmd="telnet " + router['router_name']
			print(telnet_router_cmd)
			chan.send(telnet_router_cmd+'\n')
			time.sleep(2)
			res=chan.recv(65535).decode('utf8')
			if '(yes/no)' in res:
				chan.send('yes'+'\n')
				time.sleep(2)
			chan.send(username+'\n')
			time.sleep(2)
			chan.send(password+'\n')
			time.sleep(2)
			res=chan.recv(65535)
			cmd1="show clock"
			cmd2="ping " + router['next_hop_ip']

		result = ''
		stop_ping_flag=1
		while stop_ping_flag:
			chan.send(cmd1+'\n')
			time.sleep(1)
			chan.send(cmd2+'\n')
			time.sleep(2)

			res = chan.recv(65535).decode('utf8')
			wait_time=5
			while wait_time>1:
				#print(wait_time)
				if  '100 percent' not in res and '5 packets received' not in res:
					res1=res
					#print(res1)
					time.sleep(1)
					print("receive date again--before")
					chan.settimeout(2)
					try:
						res = res1+chan.recv(65535).decode('utf8')
					except:
						pass
					print("receive date again--done")
					wait_time=wait_time-1
					print(wait_time)
					print(res)
				else:
					print("result_pingable")
					break
					
			result = res
			#print(result)
			
			if result:
				ping_result=result.strip('\n')
				#print(ping_result)
				self.send_ping_result_signal.emit(ping_result,router_index)

			#if res.endswith('> '):
			#	break
			#	ssh.close()

			#self.label_status.setText('Status: In Progress...')

#********************************************************************************************************
#**************************    Function: DSC Internal Cross Ping     ************************************
#********************************************************************************************************

	def internal_cross_ping_list_package_loss_log(self):
		global username, password
		#cmd='pwd'
		cmd='ls /data2/TMP/tsdss/DSC_Internal_Cross_Ping_Tool/internal_ping_logs | grep loss'
		package_loss_log_list=ssh_onetime_ping('10.162.28.185',username,password,cmd)
		#print(package_loss_log_list)
		self.textEdit_log_name_content.setPlainText('')
		for item in package_loss_log_list:
			log_name_content_old=self.textEdit_log_name_content.toPlainText()

			self.textEdit_log_name_content.setPlainText(log_name_content_old+item)
			self.textEdit_log_name_content.moveCursor(QtGui.QTextCursor.End) 
		
	def internal_cross_ping_list_all_log(self):
		global username, password
		
		cmd='ls /data2/TMP/tsdss/DSC_Internal_Cross_Ping_Tool/internal_ping_logs'
		all_log_list=ssh_onetime_ping('10.162.28.185',username,password,cmd)
		
		self.textEdit_log_name_content.setPlainText('')
		for item in all_log_list:
			log_name_content_old=self.textEdit_log_name_content.toPlainText()

			self.textEdit_log_name_content.setPlainText(log_name_content_old+item)
			self.textEdit_log_name_content.moveCursor(QtGui.QTextCursor.End) 

		
	def internal_cross_ping_show_log_content(self):
		global username, password
		
		if self.textEdit_log_file_name.toPlainText()=='':
			QMessageBox.information(self,"Warning","Please input the log file name you need to check(* is allowed)",QMessageBox.Ok)
		else:
			log_file_name=self.textEdit_log_file_name.toPlainText()
			cmd='cat /data2/TMP/tsdss/DSC_Internal_Cross_Ping_Tool/internal_ping_logs/'+log_file_name
			log_content=ssh_onetime_ping('10.162.28.185',username,password,cmd)
			
			self.textEdit_log_name_content.setPlainText('')
			for item in log_content:
				log_name_content_old=self.textEdit_log_name_content.toPlainText()
	
				self.textEdit_log_name_content.setPlainText(log_name_content_old+item)
				self.textEdit_log_name_content.moveCursor(QtGui.QTextCursor.End) 
				
				
	def start_internal_cross_ping(self):
		global username, password
		
		cmd_check_status="ps -ef | grep DSC_Internal_Cross_Ping_for_Linux"
		check_internal_cross_ping_status=ssh_onetime_ping('10.162.28.185',username,password,cmd_check_status)
		print(check_internal_cross_ping_status)
		
		str_check_internal_cross_ping_status=""
		for item in check_internal_cross_ping_status:
			str_check_internal_cross_ping_status=str_check_internal_cross_ping_status+item
		print(str_check_internal_cross_ping_status)
		
		if "python3 /data2/TMP/tsdss/DSC_Internal_Cross_Ping_Tool/DSC_Internal_Cross_Ping_for_Linux.py" in str_check_internal_cross_ping_status:
			QMessageBox.information(self,"Information","Already running for some time, please check log directly",QMessageBox.Ok)
			self.textEdit_log_name_content.setPlainText('DSC internal cross ping status: Already running')

		else:
			#cmd_start_internal_cross_ping="cd /data2/TMP/tsdss/DSC_Internal_Cross_Ping_Tool;nohup python3 DSC_Internal_Cross_Ping_for_Linux.py "+username+" "+password+" &"
			cmd_start_internal_cross_ping="nohup python3 /data2/TMP/tsdss/DSC_Internal_Cross_Ping_Tool/DSC_Internal_Cross_Ping_for_Linux.py "+username+" "+password+" >/dev/null 2>&1  &"
			#cmd_start_internal_cross_ping="pwd"
			print(cmd_start_internal_cross_ping)
			start_internal_cross_ping_result=ssh_nohup_cmd('10.162.28.185',username,password,cmd_start_internal_cross_ping)
			print(start_internal_cross_ping_result)
			QMessageBox.information(self,"Information","Just start the internal cross ping, you can check logs after 1 min",QMessageBox.Ok)

			self.textEdit_log_name_content.setPlainText('DSC internal cross ping status: Just started')
			
			
#********************************************************************************************************
#************************    Function: DSC Internal Cross Ping Diagram   ********************************
#********************************************************************************************************

	def add0_datetime(self,datetime):
		if int(datetime)<10:
			datetime=str(0)+str(datetime)
			return datetime
		else:
			return datetime
			
	def getfiledate(self,kpi_file_name):
		#print(kpi_file_name)
		#print(type(kpi_file_name))
		filedate=kpi_file_name.split('.')[-2].split('_')[-1]
		#print(filedate)
		return filedate

	def download_DSC_internal_ping_kpi_files(self):
		self.textEdit_log_name_content.setPlainText('')
		t= threading.Thread(target=self.download_DSC_internal_ping_kpi_files_soldier)
		t.start()

	def update_textEdit_log_name_content(self,value):
		content_old=self.textEdit_log_name_content.toPlainText()
		self.textEdit_log_name_content.setPlainText(content_old+value+'\n')
		
	def update_textEdit_log_name_content_list(self,file_list):
		for item in file_list:
			content_old=self.textEdit_log_name_content.toPlainText()
			self.textEdit_log_name_content.setPlainText(content_old+item+'\n')
		
	def show_download_kpi_file_failed_popup(self,value):
		if value=='failed':
			QMessageBox.information(self,"Information",'No KPI files for the timeslot you selected.',QMessageBox.Ok)
		else:
			QMessageBox.information(self,"Information",'Download KPI files Successfully!',QMessageBox.Ok)
		

	def download_DSC_internal_ping_kpi_files_soldier(self):
		global username, password, start_datetime,end_datetime
		
		start_datetime_year=self.dateTimeEdit_start_time.date().year()
		end_datetime_year=self.dateTimeEdit_end_time.date().year()
		
		start_datetime_month=self.add0_datetime(self.dateTimeEdit_start_time.date().month())
		end_datetime_month=self.add0_datetime(self.dateTimeEdit_end_time.date().month())
		
		
		start_datetime_day=self.add0_datetime(self.dateTimeEdit_start_time.date().day())
		end_datetime_day=self.add0_datetime(self.dateTimeEdit_end_time.date().day())
		
		start_datetime_hour=self.add0_datetime(self.dateTimeEdit_start_time.time().hour())
		end_datetime_hour=self.add0_datetime(self.dateTimeEdit_end_time.time().hour())
		
		start_datetime_min=self.add0_datetime(self.dateTimeEdit_start_time.time().minute())
		end_datetime_min=self.add0_datetime(self.dateTimeEdit_end_time.time().minute())
		
		start_date=str(start_datetime_year)+str(start_datetime_month)+str(start_datetime_day)
		end_date=str(end_datetime_year)+str(end_datetime_month)+str(end_datetime_day)
		print(start_date)
		print(end_date)
		
		start_datetime=str(start_datetime_year)+str(start_datetime_month)+str(start_datetime_day)+str(start_datetime_hour)+str(start_datetime_min)
		end_datetime=str(end_datetime_year)+str(end_datetime_month)+str(end_datetime_day)+str(end_datetime_hour)+str(end_datetime_min)
		
		print(start_datetime)
		print(end_datetime)

		self.update_textEdit_log_name_content_signal.emit('(1/4)Check KPI files in DSC starts...') 
		cmd='cd /data2/TMP/tsdss/DSC_Internal_Cross_Ping_Tool/internal_ping_logs/; ls *.csv'
		#cmd='pwd;ls'
		#print(cmd)
		all_kpi_csv_list=ssh_onetime_ping('10.162.28.185',username,password,cmd)
		#Aresult=all_kpi_csv_list.split('\n')
		#print(all_kpi_csv_list)
		all_kpi_csv_filename=[]
		for item in all_kpi_csv_list:
			all_kpi_csv_filename.append(item.split('\n')[0])
		#print('all_kpi_file_name:')
		#print(all_kpi_csv_filename)


		kpi_file_meet_datetime_list=[]
		for i in all_kpi_csv_filename:
			if start_date<=self.getfiledate(i)<=end_date:
				#print(start_datetime+self.getfiledate(i)+end_datetime)
				kpi_file_meet_datetime_list.append(i)
		print('kpi_file_meet_datetime_list:')
		print(kpi_file_meet_datetime_list)
		
		if kpi_file_meet_datetime_list==[]:
			
			self.update_textEdit_log_name_content_signal.emit('(1/4)Check KPI files in DSC failed!')
			self.show_download_kpi_file_failed_popup_signal.emit('failed')
			#QMessageBox.information(self,"Information","No KPI files for the time slot you selected.",QMessageBox.Ok)
	
		else:
			
			try:
				shutil.rmtree(os.getcwd()+"\\file\\kpi_files\\")
			except:
				pass
			
			self.update_textEdit_log_name_content_signal.emit('(1/4)Check KPI files in DSC done!')
			self.update_textEdit_log_name_content_signal.emit('(2/4)Tar & Download KPI files from DSC start...')
			tarfilelist=''
			for i in kpi_file_meet_datetime_list:
				tarfilelist=tarfilelist+'"'+i+'"'+' '
			
			cmd='cd /data2/TMP/tsdss/DSC_Internal_Cross_Ping_Tool/internal_ping_logs/; tar czvf /data2/TMP/tsdss/DSC_Internal_Cross_Ping_Tool/internal_ping_logs/KPI_file.tar.gz '+tarfilelist
			#print(cmd)
			tar_result=ssh_onetime_ping('10.162.28.185',username,password,cmd)
			#print(tar_result)
			
			kpidirectory=os.getcwd()+r'\\file\\kpi_files\\'
			if not os.path.exists(kpidirectory):
				os.makedirs(kpidirectory)
				
			transport = paramiko.Transport('10.162.28.185', 22)
			transport.connect(username=username, password=password)
			sftp = paramiko.SFTPClient.from_transport(transport)
			sftp.get('/data2/TMP/tsdss/DSC_Internal_Cross_Ping_Tool/internal_ping_logs/KPI_file.tar.gz',os.getcwd()+"\\file\\kpi_files\\KPI_file.tar.gz")
			
			remove_tar_file = ssh_onetime_ping('10.162.28.185',username,password,'cd /data2/TMP/tsdss/DSC_Internal_Cross_Ping_Tool/internal_ping_logs/; rm KPI_file.tar.gz')
	
	
			self.update_textEdit_log_name_content_signal.emit('(2/4)Tar & Download KPI files from DSC done!')
			
			self.update_textEdit_log_name_content_signal.emit('(3/4)Extract KPI files start...')
			tar = tarfile.open(os.getcwd()+"\\file\\kpi_files\\KPI_file.tar.gz")
			names = tar.getnames()
			for name in names:
				tar.extract(name, os.getcwd()+"\\file\\kpi_files")
			tar.close()
			os.remove(os.getcwd()+"\\file\\kpi_files\\KPI_file.tar.gz")
			
			dirs = os.listdir(os.getcwd()+"\\file\\kpi_files\\")

			self.update_textEdit_log_name_content_signal.emit('(3/4)Extract KPI files done!')
			
			#self.textEdit_log_name_content.setPlainText("KPI files list:\n")
			file_list=[]
			for item in dirs:
				file_list.append(item)
			
			#QMessageBox.information(self,"Information",'Download KPI files Successfully!',QMessageBox.Ok)
			
			self.update_textEdit_log_name_content_signal.emit('(4/4)Download KPI files successful!')
			self.update_textEdit_log_name_content_signal.emit('\nKPI files list:')
			self.update_textEdit_log_name_content_list_signal.emit(file_list)
			
			self.show_download_kpi_file_failed_popup_signal.emit('ok')

	def get_line_ready(self,path,kpi_file_name_item):
		
		line_path=[]
		if path in kpi_file_name_item:
			with open(os.getcwd()+"\\file\\kpi_files\\"+kpi_file_name_item, 'r') as myFile:  
				lines=csv.reader(myFile)  
				for row in lines:
					line_path.append([row[0],row[1]])
		return line_path
		
	def get_line_meet_timeslot(self,start_time,end_time,line):
		#print(start_time)
		#print(end_time)
		new_line=[]
		for item in line:
			#print(item[0]+item[1])
			if start_time<=item[0]<=end_time:
				#print(item[0]+' '+item[1])
				new_line.append(item)
				#new_line_rate.append(item[0])
				#print(item)
		#print('new line:')
		#print(new_line)
		#return new_line
		new_line_final=[]
		new_line_final_time=[]

		for item in new_line:
			for item1 in new_line_final:
				if item1[0] not in new_line_final_time:
					new_line_final_time.append(item1[0])
			if item[0] not in new_line_final_time:
				new_line_final.append(item)
		return new_line_final


	def get_line_time_ready(self,line):
		line_time_ready=[]
		for item in line:
			line_time_ready.append(item[0])
		return line_time_ready
			

	def got_y_axis_final(self,line_meet_timeslot,x_axis_final_hk_dsc):

		y_axis_final=[]
		for x_axis in x_axis_final_hk_dsc:
			for y_axis in line_meet_timeslot:
				if y_axis[0]==x_axis:
					y_axis_final.append(float(y_axis[1].strip('%'))/100)
		return y_axis_final
		
	def got_x_axis_final(self,l1,l2,l3,l4,l5):
		x_axis_final_hk_dsc=[]
		for i in l1:
			if i in l2 and i in l3 and i in l4 and i in l5:
				x_axis_final_hk_dsc.append(i)
		return x_axis_final_hk_dsc

	def generate_report(self):
		self.textEdit_log_name_content.setPlainText('')
		t= threading.Thread(target=self.generate_report_soldier)
		t.start()

	def update_textEdit_log_name_content(self,value):
		content_old=self.textEdit_log_name_content.toPlainText()
		self.textEdit_log_name_content.setPlainText(content_old+value+'\n')
		
	def show_download_kpi_file_popup(self,value):
		QMessageBox.information(self,"Information",'Please download KPI files before generate report!',QMessageBox.Ok)


	def generate_report_soldier(self):
		global username,password,start_datetime,end_datetime
		global x_axis_final_hk_dsc,y_axis_final_hk_sg_hk_dsc,y_axis_final_hk_ams_hk_dsc,y_axis_final_hk_frt_hk_dsc,y_axis_final_hk_chi_hk_dsc,y_axis_final_hk_dal_hk_dsc
		global x_axis_final_sg_dsc,y_axis_final_hk_sg_sg_dsc,y_axis_final_sg_ams_sg_dsc,y_axis_final_sg_frt_sg_dsc,y_axis_final_sg_chi_sg_dsc,y_axis_final_sg_dal_sg_dsc
		global x_axis_final_ams_dsc,y_axis_final_hk_ams_ams_dsc,y_axis_final_sg_ams_ams_dsc,y_axis_final_ams_chi_ams_dsc,y_axis_final_ams_dal_ams_dsc,y_axis_final_ams_frt_ams_dsc
		global x_axis_final_frt_dsc,y_axis_final_hk_frt_frt_dsc,y_axis_final_sg_frt_frt_dsc,y_axis_final_ams_frt_frt_dsc,y_axis_final_frt_chi_frt_dsc,y_axis_final_frt_dal_frt_dsc
		global x_axis_final_chi_dsc,y_axis_final_hk_chi_chi_dsc,y_axis_final_sg_chi_chi_dsc,y_axis_final_ams_chi_chi_dsc,y_axis_final_frt_chi_chi_dsc,y_axis_final_chi_dal_chi_dsc
		global x_axis_final_dal_dsc,y_axis_final_hk_dal_dal_dsc,y_axis_final_sg_dal_dal_dsc,y_axis_final_ams_dal_dal_dsc,y_axis_final_frt_dal_dal_dsc,y_axis_final_chi_dal_dal_dsc
		
		#self.textEdit_log_name_content.setPlainText('')
		kpi_file_name = os.listdir(os.getcwd()+"\\file\\kpi_files\\")
		#print('Got kpi_file_name')

			#self.textEdit_log_name_content.setPlainText("KPI files list:\n")
		line_hk_sg=[]
		line_hk_ams=[]
		line_hk_frt=[]
		line_hk_chi=[]
		line_hk_dal=[]
		line_sg_ams=[]
		line_sg_frt=[]
		line_sg_chi=[]
		line_sg_dal=[]
		line_ams_chi=[]
		line_ams_dal=[]
		line_ams_frt=[]
		line_frt_chi=[]
		line_frt_dal=[]	
		line_chi_dal=[]
		print('(1/4)Collecting of KPI source data starts...')
		"""content_old=self.textEdit_log_name_content.toPlainText()
		self.textEdit_log_name_content.setPlainText(content_old+'(1/4)Collecting of KPI source data starts...'+'\n')"""
		self.update_textEdit_log_name_content_signal.emit('(1/4)Collecting of KPI source data starts...')
		for item in kpi_file_name:
			line_hk_sg+=self.get_line_ready('HK DSC-SG DSC',item)
			line_hk_ams+=self.get_line_ready('HK DSC-AMS DSC',item)
			line_hk_frt+=self.get_line_ready('HK DSC-FRT DSC',item)
			line_hk_chi+=self.get_line_ready('HK DSC-CHI DSC',item)
			line_hk_dal+=self.get_line_ready('HK DSC-DAL DSC',item)
			line_sg_ams+=self.get_line_ready('SG DSC-AMS DSC',item)
			line_sg_frt+=self.get_line_ready('SG DSC-FRT DSC',item)
			line_sg_chi+=self.get_line_ready('SG DSC-CHI DSC',item)
			line_sg_dal+=self.get_line_ready('SG DSC-DAL DSC',item)
			line_ams_chi+=self.get_line_ready('AMS DSC-CHI DSC',item)
			line_ams_dal+=self.get_line_ready('AMS DSC-DAL DSC',item)
			line_ams_frt+=self.get_line_ready('AMS DSC-FRT DSC',item)
			line_frt_chi+=self.get_line_ready('FRT DSC-CHI DSC',item)
			line_frt_dal+=self.get_line_ready('FRT DSC-DAL DSC',item)
			line_chi_dal+=self.get_line_ready('CHI DSC-DAL DSC',item)
		print('(1/4)Collecting of KPI source data Done!')
		"""content_old=self.textEdit_log_name_content.toPlainText()
		self.textEdit_log_name_content.setPlainText(content_old+'(1/4)Collecting of KPI source data Done!'+'\n')"""
		self.update_textEdit_log_name_content_signal.emit('(1/4)Collecting of KPI source data Done!')
		line_hk_sg_meet_timeslot=[]
		line_hk_ams_meet_timeslot=[]
		line_hk_frt_meet_timeslot=[]
		line_hk_chi_meet_timeslot=[]
		line_hk_dal_meet_timeslot=[]
		line_sg_ams_meet_timeslot=[]
		line_sg_frt_meet_timeslot=[]
		line_sg_chi_meet_timeslot=[]
		line_sg_dal_meet_timeslot=[]
		line_ams_chi_meet_timeslot=[]
		line_ams_dal_meet_timeslot=[]
		line_ams_frt_meet_timeslot=[]
		line_frt_chi_meet_timeslot=[]
		line_frt_dal_meet_timeslot=[]
		line_chi_dal_meet_timeslot=[]
		print('(2/4)Analysis of KPI source data starts(may take few mins)...')
		"""content_old=self.textEdit_log_name_content.toPlainText()
		self.textEdit_log_name_content.setPlainText(content_old+'(2/4)Analysis of KPI source data starts...'+'\n')"""
		self.update_textEdit_log_name_content_signal.emit('(2/4)Analysis of KPI source data starts(may take few mins)...')
		try:
			line_hk_sg_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_hk_sg)
			line_hk_ams_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_hk_ams)
			line_hk_frt_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_hk_frt)
			line_hk_chi_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_hk_chi)
			line_hk_dal_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_hk_dal)
			line_sg_ams_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_sg_ams)
			line_sg_frt_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_sg_frt)
			line_sg_chi_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_sg_chi)
			line_sg_dal_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_sg_dal)
			line_ams_chi_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_ams_chi)
			line_ams_dal_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_ams_dal)
			line_ams_frt_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_ams_frt)
			line_frt_chi_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_frt_chi)
			line_frt_dal_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_frt_dal)
			line_chi_dal_meet_timeslot=self.get_line_meet_timeslot(start_datetime,end_datetime,line_chi_dal)
			print('(2/4)Analysis of KPI source data Done!')
			"""content_old=self.textEdit_log_name_content.toPlainText()
			self.textEdit_log_name_content.setPlainText(content_old+'(2/4)Analysis of KPI source data Done!'+'\n')"""
			self.update_textEdit_log_name_content_signal.emit('(2/4)Analysis of KPI source data Done!')
			#print('line_hk_sg_meet_timeslot:\n')
			#print(line_hk_sg_meet_timeslot)
			#print(start_datetime+' '+end_datetime)
		except NameError:
			#print(NameError)
			print('(2/4)Analysis of KPI source data failed!')
			"""content_old=self.textEdit_log_name_content.toPlainText()
			self.textEdit_log_name_content.setPlainText(content_old+'(2/4)Analysis of KPI source data failed!'+'\n')"""
			self.update_textEdit_log_name_content_signal.emit('(2/4)Analysis of KPI source data failed!')
			self.show_download_kpi_file_popup_signal.emit('ok')
			#QMessageBox.information(self,"Information",'Please download KPI files before generate report!',QMessageBox.Ok)
			return 1

		print('(3/4)Build X/Y axis starts...')
		"""content_old=self.textEdit_log_name_content.toPlainText()
		self.textEdit_log_name_content.setPlainText(content_old+'(3/4)Build X/Y axis starts...'+'\n')"""
		self.update_textEdit_log_name_content_signal.emit('(3/4)Build X/Y axis starts...')
		time_hk_sg  =self.get_line_time_ready(line_hk_sg_meet_timeslot)
		time_hk_ams =self.get_line_time_ready(line_hk_ams_meet_timeslot)
		time_hk_frt =self.get_line_time_ready(line_hk_frt_meet_timeslot)
		time_hk_chi =self.get_line_time_ready(line_hk_chi_meet_timeslot)
		time_hk_dal =self.get_line_time_ready(line_hk_dal_meet_timeslot)
		time_sg_ams =self.get_line_time_ready(line_sg_ams_meet_timeslot)
		time_sg_frt =self.get_line_time_ready(line_sg_frt_meet_timeslot)
		time_sg_chi =self.get_line_time_ready(line_sg_chi_meet_timeslot)
		time_sg_dal =self.get_line_time_ready(line_sg_dal_meet_timeslot)
		time_ams_chi =self.get_line_time_ready(line_ams_chi_meet_timeslot)
		time_ams_dal =self.get_line_time_ready(line_ams_dal_meet_timeslot)
		time_ams_frt =self.get_line_time_ready(line_ams_frt_meet_timeslot)
		time_frt_chi =self.get_line_time_ready(line_frt_chi_meet_timeslot)
		time_frt_dal =self.get_line_time_ready(line_frt_dal_meet_timeslot)
		time_chi_dal =self.get_line_time_ready(line_chi_dal_meet_timeslot)
		
		x_axis_final_hk_dsc=self.got_x_axis_final(time_hk_sg,time_hk_ams,time_hk_frt,time_hk_chi,time_hk_dal)
		#print('Got X axis')
		#print(len(x_axis_final_hk_dsc))
		y_axis_final_hk_sg_hk_dsc=self.got_y_axis_final(line_hk_sg_meet_timeslot,x_axis_final_hk_dsc)
		y_axis_final_hk_ams_hk_dsc=self.got_y_axis_final(line_hk_ams_meet_timeslot,x_axis_final_hk_dsc)
		y_axis_final_hk_frt_hk_dsc=self.got_y_axis_final(line_hk_frt_meet_timeslot,x_axis_final_hk_dsc)
		y_axis_final_hk_chi_hk_dsc=self.got_y_axis_final(line_hk_chi_meet_timeslot,x_axis_final_hk_dsc)
		y_axis_final_hk_dal_hk_dsc=self.got_y_axis_final(line_hk_dal_meet_timeslot,x_axis_final_hk_dsc)
		#print('Got Y axis')
		#print(y_axis_final_hk_sg)
		
		
		x_axis_final_sg_dsc=self.got_x_axis_final(time_hk_sg,time_sg_ams,time_sg_frt,time_sg_chi,time_sg_dal)
		y_axis_final_hk_sg_sg_dsc=self.got_y_axis_final(line_hk_sg_meet_timeslot,x_axis_final_sg_dsc)
		y_axis_final_sg_ams_sg_dsc=self.got_y_axis_final(line_sg_ams_meet_timeslot,x_axis_final_sg_dsc)
		y_axis_final_sg_frt_sg_dsc=self.got_y_axis_final(line_sg_frt_meet_timeslot,x_axis_final_sg_dsc)
		y_axis_final_sg_chi_sg_dsc=self.got_y_axis_final(line_sg_chi_meet_timeslot,x_axis_final_sg_dsc)
		y_axis_final_sg_dal_sg_dsc=self.got_y_axis_final(line_sg_dal_meet_timeslot,x_axis_final_sg_dsc)
		
		
		x_axis_final_ams_dsc=self.got_x_axis_final(time_hk_ams ,time_sg_ams ,time_ams_chi,time_ams_dal,time_ams_frt)
		y_axis_final_hk_ams_ams_dsc=self.got_y_axis_final(line_hk_ams_meet_timeslot,x_axis_final_ams_dsc)
		y_axis_final_sg_ams_ams_dsc=self.got_y_axis_final(line_sg_ams_meet_timeslot,x_axis_final_ams_dsc)
		y_axis_final_ams_chi_ams_dsc=self.got_y_axis_final(line_ams_chi_meet_timeslot,x_axis_final_ams_dsc)
		y_axis_final_ams_dal_ams_dsc=self.got_y_axis_final(line_ams_dal_meet_timeslot,x_axis_final_ams_dsc)
		y_axis_final_ams_frt_ams_dsc=self.got_y_axis_final(line_ams_frt_meet_timeslot,x_axis_final_ams_dsc)
		
		
		x_axis_final_frt_dsc=self.got_x_axis_final(time_hk_frt ,time_sg_frt,time_ams_frt,time_frt_chi,time_frt_dal)
		y_axis_final_hk_frt_frt_dsc=self.got_y_axis_final(line_hk_frt_meet_timeslot,x_axis_final_frt_dsc)
		y_axis_final_sg_frt_frt_dsc=self.got_y_axis_final(line_sg_frt_meet_timeslot,x_axis_final_frt_dsc)
		y_axis_final_ams_frt_frt_dsc=self.got_y_axis_final(line_ams_frt_meet_timeslot,x_axis_final_frt_dsc)
		y_axis_final_frt_chi_frt_dsc=self.got_y_axis_final(line_frt_chi_meet_timeslot,x_axis_final_frt_dsc)
		y_axis_final_frt_dal_frt_dsc=self.got_y_axis_final(line_frt_dal_meet_timeslot,x_axis_final_frt_dsc)
		
		
		x_axis_final_chi_dsc=self.got_x_axis_final(time_hk_chi ,time_sg_chi ,time_ams_chi,time_frt_chi,time_chi_dal)
		y_axis_final_hk_chi_chi_dsc=self.got_y_axis_final(line_hk_chi_meet_timeslot,x_axis_final_chi_dsc)
		y_axis_final_sg_chi_chi_dsc=self.got_y_axis_final(line_sg_chi_meet_timeslot,x_axis_final_chi_dsc)
		y_axis_final_ams_chi_chi_dsc=self.got_y_axis_final(line_ams_chi_meet_timeslot,x_axis_final_chi_dsc)
		y_axis_final_frt_chi_chi_dsc=self.got_y_axis_final(line_frt_chi_meet_timeslot,x_axis_final_chi_dsc)
		y_axis_final_chi_dal_chi_dsc=self.got_y_axis_final(line_chi_dal_meet_timeslot,x_axis_final_chi_dsc)
		
		
		
		x_axis_final_dal_dsc=self.got_x_axis_final(time_hk_dal ,time_sg_dal ,time_ams_dal,time_frt_dal,time_chi_dal)
		y_axis_final_hk_dal_dal_dsc=self.got_y_axis_final(line_hk_dal_meet_timeslot,x_axis_final_dal_dsc)
		y_axis_final_sg_dal_dal_dsc=self.got_y_axis_final(line_sg_dal_meet_timeslot,x_axis_final_dal_dsc)
		y_axis_final_ams_dal_dal_dsc=self.got_y_axis_final(line_ams_dal_meet_timeslot,x_axis_final_dal_dsc)
		y_axis_final_frt_dal_dal_dsc=self.got_y_axis_final(line_frt_dal_meet_timeslot,x_axis_final_dal_dsc)
		y_axis_final_chi_dal_dal_dsc=self.got_y_axis_final(line_chi_dal_meet_timeslot,x_axis_final_dal_dsc)
		
		
		print('(3/4)Build X/Y axis Done!(Amount: ' + str(len(y_axis_final_hk_sg_hk_dsc)) +')')
		"""content_old=self.textEdit_log_name_content.toPlainText()
		self.textEdit_log_name_content.setPlainText(content_old+'(3/4)Build X/Y axis Done!(Amount: ' + str(len(y_axis_final_hk_sg)) +')'+'\n')"""
		self.update_textEdit_log_name_content_signal.emit('(3/4)Build X/Y axis Done!(Amount: ' + str(len(x_axis_final_hk_dsc)) +'*'+ str(len(y_axis_final_hk_sg_hk_dsc)) +'*6)')
		
		self.show_figure_signal.emit('ok')
		
		
	def show_figure(self):
		global x_axis_final_hk_dsc,y_axis_final_hk_sg_hk_dsc,y_axis_final_hk_ams_hk_dsc,y_axis_final_hk_frt_hk_dsc,y_axis_final_hk_chi_hk_dsc,y_axis_final_hk_dal_hk_dsc
		global x_axis_final_sg_dsc,y_axis_final_hk_sg_sg_dsc,y_axis_final_sg_ams_sg_dsc,y_axis_final_sg_frt_sg_dsc,y_axis_final_sg_chi_sg_dsc,y_axis_final_sg_dal_sg_dsc
		global x_axis_final_ams_dsc,y_axis_final_hk_ams_ams_dsc,y_axis_final_sg_ams_ams_dsc,y_axis_final_ams_chi_ams_dsc,y_axis_final_ams_dal_ams_dsc,y_axis_final_ams_frt_ams_dsc
		global x_axis_final_frt_dsc,y_axis_final_hk_frt_frt_dsc,y_axis_final_sg_frt_frt_dsc,y_axis_final_ams_frt_frt_dsc,y_axis_final_frt_chi_frt_dsc,y_axis_final_frt_dal_frt_dsc
		global x_axis_final_chi_dsc,y_axis_final_hk_chi_chi_dsc,y_axis_final_sg_chi_chi_dsc,y_axis_final_ams_chi_chi_dsc,y_axis_final_frt_chi_chi_dsc,y_axis_final_chi_dal_chi_dsc
		global x_axis_final_dal_dsc,y_axis_final_hk_dal_dal_dsc,y_axis_final_sg_dal_dal_dsc,y_axis_final_ams_dal_dal_dsc,y_axis_final_frt_dal_dal_dsc,y_axis_final_chi_dal_dal_dsc
		
		
		"""time_hk_sg,   b      = '-')
		time_hk_ams ,  g     = '--')
		time_hk_frt ,  r     = '-.')
		time_hk_chi ,  y     = ':')
		time_hk_dal ,   purple     = '-')
		time_sg_ams ,    k         = '--'
		time_sg_frt,   c           = '-.'
		time_sg_chi ,  m           = ':')
		time_sg_dal ,  teal         = '-')
		time_ams_chi,  tomato       = '--'
		time_ams_dal,  tan          = '-.'
		time_ams_frt,   olive       = ':')
		time_frt_chi,  cyan         = '-')
		time_frt_dal,  darksage     = '--'
		time_chi_dal   pink         = '-.'"""
		
		print('(4/4)Show figure!')
		"""content_old=self.textEdit_log_name_content.toPlainText()
		self.textEdit_log_name_content.setPlainText(content_old+'(4/4)Show figure!'+'\n')"""
		self.update_textEdit_log_name_content_signal.emit('(4/4)Show figure!')
		
		#style.use('ggplot')
		fig = plt.figure(num='DSC internal cross ping: package loss rate diagram')
		
		ax1 = fig.add_subplot(2,3,1)
		line_hk_sg_diagram,  =plt.plot(x_axis_final_hk_dsc, y_axis_final_hk_sg_hk_dsc,color='b', linewidth=1, alpha=1,linestyle = '-')
		line_hk_ams_diagram, =plt.plot(x_axis_final_hk_dsc, y_axis_final_hk_ams_hk_dsc,color='g', linewidth=1, alpha=1, linestyle = '--')
		line_hk_frt_diagram, =plt.plot(x_axis_final_hk_dsc, y_axis_final_hk_frt_hk_dsc,color='r', linewidth=1, alpha=1,linestyle = '-.')
		line_hk_chi_diagram, =plt.plot(x_axis_final_hk_dsc, y_axis_final_hk_chi_hk_dsc,color='y', linewidth=1, alpha=1, linestyle = ':')
		line_hk_dal_diagram, =plt.plot(x_axis_final_hk_dsc, y_axis_final_hk_dal_hk_dsc,color='purple', linewidth=1, alpha=1,linestyle = '-')
		plt.title('HK DSC: Internal package loss rate', color='g',size=10)
		plt.legend(handles = [line_hk_sg_diagram, line_hk_ams_diagram,line_hk_frt_diagram,line_hk_chi_diagram,line_hk_dal_diagram], labels = ['HKDSC-SGDSC', 'HKDSC-AMSDSC','HKDSC-FRTDSC', 'HKDSC-CHIDSC','HKDSC-DALDSC'], loc = 'best')
		#plt.ylim((0, 1.1))
		#plt.yticks([0, 0.2,0.4,0.6,0.8,1],['0%','20%','40%','60%','80%','100%'])

		def to_percent(temp, position):
			return '%2.1f'%(100*temp) + '%'
		plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
		plt.xlabel(u'Package loss time',fontsize=12)
		plt.ylabel(u'Package loss rate',fontsize=12)
		

		ax2 = fig.add_subplot(2,3,4,sharey=ax1)
		line_hk_sg_diagram,  =plt.plot(x_axis_final_sg_dsc, y_axis_final_hk_sg_sg_dsc,color='b', linewidth=1, alpha=1,linestyle = '-')
		line_sg_ams_diagram, =plt.plot(x_axis_final_sg_dsc, y_axis_final_sg_ams_sg_dsc,color='k', linewidth=1, alpha=1, linestyle = '--')
		line_sg_frt_diagram, =plt.plot(x_axis_final_sg_dsc, y_axis_final_sg_frt_sg_dsc,color='c', linewidth=1, alpha=1,linestyle = '-.')
		line_sg_chi_diagram, =plt.plot(x_axis_final_sg_dsc, y_axis_final_sg_chi_sg_dsc,color='m', linewidth=1, alpha=1, linestyle = ':')
		line_sg_dal_diagram, =plt.plot(x_axis_final_sg_dsc, y_axis_final_sg_dal_sg_dsc,color='teal', linewidth=1, alpha=1,linestyle = '-')
		plt.title('SG DSC: Internal package loss rate', color='g',size=10)
		plt.legend(handles = [line_hk_sg_diagram, line_sg_ams_diagram,line_sg_frt_diagram,line_sg_chi_diagram,line_sg_dal_diagram], labels = ['HKDSC-SGDSC', 'SGDSC-AMSDSC','SGDSC-FRTDSC', 'SGDSC-CHIDSC','SGDSC-DALDSC'], loc = 'best')
		#plt.ylim((0, 1.1))
		#plt.yticks([0, 0.2,0.4,0.6,0.8,1],['0%','20%','40%','60%','80%','100%'])

		def to_percent(temp, position):
			return '%2.1f'%(100*temp) + '%'
		plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
		plt.xlabel(u'Package loss time',fontsize=12)
		plt.ylabel(u'Package loss rate',fontsize=12)
		
		
		ax3 = fig.add_subplot(2,3,2,sharey=ax1)
		line_hk_ams_diagram,  =plt.plot(x_axis_final_ams_dsc, y_axis_final_hk_ams_ams_dsc,color='g', linewidth=1, alpha=1,linestyle = '--')
		line_sg_ams_diagram, =plt.plot(x_axis_final_ams_dsc, y_axis_final_sg_ams_ams_dsc,color='k', linewidth=1, alpha=1, linestyle = '--')
		line_ams_chi_diagram, =plt.plot(x_axis_final_ams_dsc, y_axis_final_ams_chi_ams_dsc,color='tomato', linewidth=1, alpha=1,linestyle = '--')
		line_ams_dal_diagram, =plt.plot(x_axis_final_ams_dsc, y_axis_final_ams_dal_ams_dsc,color='tan', linewidth=1, alpha=1, linestyle = '-.')
		line_ams_frt_diagram, =plt.plot(x_axis_final_ams_dsc, y_axis_final_ams_frt_ams_dsc,color='olive', linewidth=1, alpha=1,linestyle = ':')
		plt.title('AMS DSC: Internal package loss rate', color='g',size=10)
		plt.legend(handles = [line_hk_ams_diagram, line_sg_ams_diagram,line_ams_chi_diagram,line_ams_dal_diagram,line_ams_frt_diagram], labels = ['HKDSC-AMSDSC', 'SGDSC-AMSDSC','AMSDSC-CHIDSC', 'AMSDSC-DALDSC','AMSDSC-FRTDSC'], loc = 'best')
		#plt.yticks([0, 0.2,0.4,0.6,0.8,1],['0%','20%','40%','60%','80%','100%'])
		
		def to_percent(temp, position):
			return '%2.1f'%(100*temp) + '%'
		plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
		plt.xlabel(u'Package loss time',fontsize=12)
		plt.ylabel(u'Package loss rate',fontsize=12)
		
		
		ax4 = fig.add_subplot(2,3,5,sharey=ax1)
		line_hk_frt_diagram,  =plt.plot(x_axis_final_frt_dsc, y_axis_final_hk_frt_frt_dsc,color='r', linewidth=1, alpha=1,linestyle = '-.')
		line_sg_frt_diagram, =plt.plot(x_axis_final_frt_dsc, y_axis_final_sg_frt_frt_dsc,color='c', linewidth=1, alpha=1, linestyle = '-.')
		line_ams_frt_diagram, =plt.plot(x_axis_final_frt_dsc, y_axis_final_ams_frt_frt_dsc,color='olive', linewidth=1, alpha=1,linestyle = ':')
		line_frt_chi_diagram, =plt.plot(x_axis_final_frt_dsc, y_axis_final_frt_chi_frt_dsc,color='cyan', linewidth=1, alpha=1, linestyle = '-')
		line_frt_dal_diagram, =plt.plot(x_axis_final_frt_dsc, y_axis_final_frt_dal_frt_dsc,color='lightgreen', linewidth=1, alpha=1,linestyle = '--')
		plt.title('FRT DSC: Internal package loss rate', color='g',size=10)
		plt.legend(handles = [line_hk_frt_diagram, line_sg_frt_diagram,line_ams_frt_diagram,line_frt_chi_diagram,line_frt_dal_diagram], labels = ['HKDSC-FRTDSC', 'SGDSC-FRTDSC','AMSDSC-FRTDSC', 'FRTDSC-CHIDSC','FRTDSC-DALDSC'], loc = 'best')
		#plt.yticks([0, 0.2,0.4,0.6,0.8,1],['0%','20%','40%','60%','80%','100%'])

		def to_percent(temp, position):
			return '%2.1f'%(100*temp) + '%'
		plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
		plt.xlabel(u'Package loss time',fontsize=12)
		plt.ylabel(u'Package loss rate',fontsize=12)
		
		ax5 = fig.add_subplot(2,3,3,sharey=ax1)
		line_hk_chi_diagram,  =plt.plot(x_axis_final_chi_dsc, y_axis_final_hk_chi_chi_dsc,color='y', linewidth=1, alpha=1,linestyle = ':')
		line_sg_chi_diagram, =plt.plot(x_axis_final_chi_dsc, y_axis_final_sg_chi_chi_dsc,color='m', linewidth=1, alpha=1, linestyle = ':')
		line_ams_chi_diagram, =plt.plot(x_axis_final_chi_dsc, y_axis_final_ams_chi_chi_dsc,color='tomato', linewidth=1, alpha=1,linestyle = '--')
		line_frt_chi_diagram, =plt.plot(x_axis_final_chi_dsc, y_axis_final_frt_chi_chi_dsc,color='cyan', linewidth=1, alpha=1, linestyle = '-')
		line_chi_dal_diagram, =plt.plot(x_axis_final_chi_dsc, y_axis_final_chi_dal_chi_dsc,color='pink', linewidth=1, alpha=1,linestyle = '-.')
		plt.title('CHI DSC: Internal package loss rate', color='g',size=10)
		plt.legend(handles = [line_hk_chi_diagram, line_sg_chi_diagram,line_ams_chi_diagram,line_frt_chi_diagram,line_chi_dal_diagram], labels = ['HKDSC-CHIDSC', 'SGDSC-CHIDSC','AMSDSC-CHIDSC', 'FRTDSC-CHIDSC','CHIDSC-DALDSC'], loc = 'best')
		#plt.yticks([0, 0.2,0.4,0.6,0.8,1],['0%','20%','40%','60%','80%','100%'])
		
		def to_percent(temp, position):
			return '%2.1f'%(100*temp) + '%'
		plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
		plt.xlabel(u'Package loss time',fontsize=12)
		plt.ylabel(u'Package loss rate',fontsize=12)
		
		
		ax6 = fig.add_subplot(2,3,6,sharey=ax1)
		line_hk_dal_diagram,  =plt.plot(x_axis_final_dal_dsc, y_axis_final_hk_dal_dal_dsc,color='purple', linewidth=1, alpha=1,linestyle = '-')
		line_sg_dal_diagram, =plt.plot(x_axis_final_dal_dsc, y_axis_final_sg_dal_dal_dsc,color='teal', linewidth=1, alpha=1, linestyle = '-')
		line_ams_dal_diagram, =plt.plot(x_axis_final_dal_dsc, y_axis_final_ams_dal_dal_dsc,color='tan', linewidth=1, alpha=1,linestyle = '-.')
		line_frt_dal_diagram, =plt.plot(x_axis_final_dal_dsc, y_axis_final_frt_dal_dal_dsc,color='lightgreen', linewidth=1, alpha=1, linestyle = '--')
		line_chi_dal_diagram, =plt.plot(x_axis_final_dal_dsc, y_axis_final_chi_dal_dal_dsc,color='pink', linewidth=1, alpha=1,linestyle = '-.')
		plt.title('DAL DSC: Internal package loss rate', color='g',size=10)
		plt.legend(handles = [line_hk_dal_diagram, line_sg_dal_diagram,line_ams_dal_diagram,line_frt_dal_diagram,line_chi_dal_diagram], labels = ['HKDSC-DALDSC', 'SGDSC-DALDSC','AMSDSC-DALDSC', 'FRTDSC-DADSC','CHIDSC-DALDSC'], loc = 'best')
		#plt.yticks([0, 0.2,0.4,0.6,0.8,1],['0%','20%','40%','60%','80%','100%'])
		
		def to_percent(temp, position):
			return '%2.1f'%(100*temp) + '%'
		plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
		plt.xlabel(u'Package loss time',fontsize=12)
		plt.ylabel(u'Package loss rate',fontsize=12)
		
		
		ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
		for label in ax1.xaxis.get_ticklabels():
			label.set_rotation(30)
			label.set_horizontalalignment('right')
			
		ax2.xaxis.set_major_locator(mticker.MaxNLocator(10))
		for label in ax2.xaxis.get_ticklabels():
			label.set_rotation(30)
			label.set_horizontalalignment('right')
			
		ax3.xaxis.set_major_locator(mticker.MaxNLocator(10))
		for label in ax3.xaxis.get_ticklabels():
			label.set_rotation(30)
			label.set_horizontalalignment('right')
			
		ax4.xaxis.set_major_locator(mticker.MaxNLocator(10))
		for label in ax4.xaxis.get_ticklabels():
			label.set_rotation(30)
			label.set_horizontalalignment('right')
			
		ax5.xaxis.set_major_locator(mticker.MaxNLocator(10))
		for label in ax5.xaxis.get_ticklabels():
			label.set_rotation(30)
			label.set_horizontalalignment('right')
			
		ax6.xaxis.set_major_locator(mticker.MaxNLocator(10))
		for label in ax6.xaxis.get_ticklabels():
			label.set_rotation(30)
			label.set_horizontalalignment('right')

		#ax1.grid(True)
		#plt.tight_layout()
		#plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.3, hspace=0.5)
		plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.3, hspace=0.5)

		plt.show()
		
		
		
#********************************************************************************************************
#********************************    Function: Send Mail     ********************************************
#********************************************************************************************************


	def update_customer_list_sendmail(self):
		global ccb_info
		
		customer_inputted=self.comboBox_customer_name_send_mail.currentText()
		self.comboBox_customer_name_send_mail.clear ()
		
		customer_list=[]
		try:
			for row in ccb_info:
				if customer_inputted.lower() in row["Operator"].lower():
					if row["Operator"] not in customer_list:
						customer_list.append(row["Operator"])
	
			print(customer_list)
			self.comboBox_customer_name_send_mail.addItems(customer_list)
		except:
			pass


	def update_customer_list_maintenance(self):
		global ccb_info
		
		customer_inputted=self.comboBox_customer_name_maintenance.currentText()
		self.comboBox_customer_name_maintenance.clear ()
		
		customer_list=[]
		try:
			for row in ccb_info:
				if customer_inputted.lower() in row["Operator"].lower():
					if row["Operator"] not in customer_list:
						customer_list.append(row["Operator"])
	
			print(customer_list)
			self.comboBox_customer_name_maintenance.addItems(customer_list)
		except:
			pass

	def update_customer_to_list(self):
		global ccb_info
		customer_name=self.comboBox_customer_name_send_mail.currentText()
		self.lineEdit_send_mail_to.clear ()
		self.textEdit_mail_body.clear()
		
		to_list=""
		try:
			for row in ccb_info:
				if customer_name.lower() == row["Operator"].lower():
					if row["Customer_Contact"] is not None:
						to_list=row["Customer_Contact"]
					else:
						to_list="Null"
			print(to_list)
			self.lineEdit_send_mail_to.setText(to_list)
			
			mail_body_temp="Dear " + customer_name + " colleagues,\n\n\n\n\n\n\n\n\n\nBest regards,\nYour Name xxx xxx"
			self.textEdit_mail_body.setText(mail_body_temp)
		except:
			pass


	def send_email_sendmail(self):

		Subject=self.lineEdit_send_mail_subject.text()
		to_list=self.lineEdit_send_mail_to.text()
		cc_list=self.lineEdit_send_mail_cc.text()
		email_body=self.textEdit_mail_body.toHtml()
		
		nowTime_y=datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%Y')
		#nowTime_m=self.add0_datetime(datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%m'))
		#nowTime_d=self.add0_datetime(datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%d'))
		#nowTime_h=self.add0_datetime(datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%H'))
		#nowTime_M=self.add0_datetime(datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%M'))
		
		nowTime_m=datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%m')
		nowTime_d=datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%d')
		nowTime_h=datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%H')
		nowTime_M=datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%M')
		
		NowTime=int(nowTime_y+nowTime_m+nowTime_d+nowTime_h+nowTime_M)
		print("NowTime:")
		print(NowTime)

		if to_list=="":
			QMessageBox.information(self,"Warning",'Please choose "Customer".',QMessageBox.Ok)
		elif Subject=="":
			QMessageBox.information(self,"Warning",'Please input "Subject".',QMessageBox.Ok)
		elif email_body=="":
			QMessageBox.information(self,"Warning",'There is nothing in your mail body!',QMessageBox.Ok)
		else:
			try:
				if to_list!='Null':
					cmd='cat /data2/TMP/tsdss/DSC_Send_Mail_Tool/DSC_Maintenance_Record.csv'
					current_maintenance=ssh_onetime_ping('10.162.28.185',username,password,cmd)
					print(current_maintenance)
					for item in current_maintenance:
						print(item)
						if item.split(',')[0]==self.comboBox_customer_name_send_mail.currentText() and int(item.split(',')[1])<=NowTime<=int(item.split(',')[2]):
							
							maintenance_customer=item.split(',')[0]
							maintenance_starttime=item.split(',')[1]
							maintenance_endtime=item.split(',')[2]
							maintenance_owner=item.split(',')[-1]
							
							note_temp=item.split(',')[3:-1]
							note_final=""
							for item in note_temp:
								note_final+=item
							
							maintenance_note=note_final
							#maintenance_note=re.split(r[maintenance_customer or maintenance_starttime or maintenance_endtime or maintenance_owner],item)
							print('maintenance_note:')
							print(maintenance_note)

							maintenance_info='Customer: '+maintenance_customer+'\nStart Time(UTC): '+maintenance_starttime+'\nEnd Time(UTC): '+maintenance_endtime+'\nNote: '+maintenance_note+'\nOwner: '+maintenance_owner
							QMessageBox.information(self,"Warning","There's maintenance ongoing for "+self.comboBox_customer_name_send_mail.currentText()+"!\nPlease don't send mail to customer.\n\nMaintenance details:\n"+maintenance_info,QMessageBox.Ok)
							return 0
					QMessageBox.information(self,"Information","No maintenance ongoing for "+self.comboBox_customer_name_send_mail.currentText()+', click "OK" to send mail.',QMessageBox.Ok)
					sendemail(to_list,cc_list,Subject,email_body)
			except NameError:
				pass


	def add_customer_maintenance(self):
		global username, password,ccb_info

		start_datetime_year=self.dateTimeEdit_start_time_maintenance.date().year()
		end_datetime_year=self.dateTimeEdit_end_time_maintenance.date().year()
		
		start_datetime_month=self.add0_datetime(self.dateTimeEdit_start_time_maintenance.date().month())
		end_datetime_month=self.add0_datetime(self.dateTimeEdit_end_time_maintenance.date().month())
		
		
		start_datetime_day=self.add0_datetime(self.dateTimeEdit_start_time_maintenance.date().day())
		end_datetime_day=self.add0_datetime(self.dateTimeEdit_end_time_maintenance.date().day())
		
		start_datetime_hour=self.add0_datetime(self.dateTimeEdit_start_time_maintenance.time().hour())
		end_datetime_hour=self.add0_datetime(self.dateTimeEdit_end_time_maintenance.time().hour())
		
		start_datetime_min=self.add0_datetime(self.dateTimeEdit_start_time_maintenance.time().minute())
		end_datetime_min=self.add0_datetime(self.dateTimeEdit_end_time_maintenance.time().minute())
		
		#start_date=str(start_datetime_year)+str(start_datetime_month)+str(start_datetime_day)
		#end_date=str(end_datetime_year)+str(end_datetime_month)+str(end_datetime_day)
		#print(start_date)
		#print(end_date)
		
		start_datetime=str(start_datetime_year)+str(start_datetime_month)+str(start_datetime_day)+str(start_datetime_hour)+str(start_datetime_min)
		end_datetime=str(end_datetime_year)+str(end_datetime_month)+str(end_datetime_day)+str(end_datetime_hour)+str(end_datetime_min)
		
		#print(start_datetime)
		#print(end_datetime)
		
		customer_name=self.comboBox_customer_name_maintenance.currentText()
		notes=self.textEdit_maintenance_notes.toPlainText()
		
		#try:
		#	notes.encode('utf8')
		#	print('encode ok')
		#except Exception as e:
		#	print(e)
		#	QMessageBox.information(self,"Warning",'Please check format of "Note".',QMessageBox.Ok)
		
		if '—' in notes:
			QMessageBox.information(self,"Warning",'Please check format of "Note"."—" is not allowed.',QMessageBox.Ok)
			return 0
		
		owner=self.lineEdit_GID.text()
		
		maintenance_item=[customer_name,start_datetime,end_datetime,notes,owner]
		
		if customer_name=="":
			QMessageBox.information(self,"Warning",'Please input maintenance "Customer".',QMessageBox.Ok)
		elif notes=="":
			QMessageBox.information(self,"Warning",'Please input maintenance "Note".',QMessageBox.Ok)
		else:
			print(maintenance_item)
			
			cmd='cat /data2/TMP/tsdss/DSC_Send_Mail_Tool/DSC_Maintenance_Record.csv'
			current_maintenance=ssh_onetime_ping('10.162.28.185',username,password,cmd)
			print(current_maintenance)
			
			if current_maintenance==[]:
				print('csv file not exist')
				mtdirectory=os.getcwd()+r'\\file\\maintenance_files\\'
				if not os.path.exists(mtdirectory):
					os.makedirs(mtdirectory)
				
				with open(mtdirectory+'/DSC_Maintenance_Record.csv', 'a+') as mt_files:
					writer = csv.writer(mt_files)
					writer.writerow([maintenance_item[0],maintenance_item[1],maintenance_item[2],maintenance_item[3],maintenance_item[4]])
				
				transport = paramiko.Transport('10.162.28.185', 22)
				transport.connect(username=username, password=password)
				sftp = paramiko.SFTPClient.from_transport(transport)
				sftp.put(mtdirectory+'\\DSC_Maintenance_Record.csv','/data2/TMP/tsdss/DSC_Send_Mail_Tool/DSC_Maintenance_Record.csv')
				print('upload successfully')
				
				cmd='chmod 777 /data2/TMP/tsdss/DSC_Send_Mail_Tool/DSC_Maintenance_Record.csv'
				ssh_onetime_ping('10.162.28.185',username,password,cmd)
				
				os.remove(mtdirectory+'\\DSC_Maintenance_Record.csv')
				QMessageBox.information(self,"Information","Congrats! Add maintenance successfully!\nClick 'OK' to send meeting request to relevant teams.",QMessageBox.Ok)
				Subject='Maintenance notification from customer: '+maintenance_item[0]
				send_calendar(['TTAC@syniverse.com','scc@syniverse.com','PS-RCC-AP@syniverse.com','ao-rcc-ap@syniverse.com','DSS_Route_Provision@syniverse.com'],start_datetime,end_datetime,Subject, maintenance_item[3])
			else:
				print('csv file already exist')
				
				mtdirectory=os.getcwd()+r'\\file\\maintenance_files\\'
				if not os.path.exists(mtdirectory):
					os.makedirs(mtdirectory)
				
				transport = paramiko.Transport('10.162.28.185', 22)
				transport.connect(username=username, password=password)
				sftp = paramiko.SFTPClient.from_transport(transport)
				sftp.get('/data2/TMP/tsdss/DSC_Send_Mail_Tool/DSC_Maintenance_Record.csv',mtdirectory+'\\DSC_Maintenance_Record.csv')
				print('download ok')

				with open(mtdirectory+'/DSC_Maintenance_Record.csv', 'a+') as mt_files:
					writer = csv.writer(mt_files)
					writer.writerow([maintenance_item[0],maintenance_item[1],maintenance_item[2],maintenance_item[3],maintenance_item[4]])
				print('write mt file ok, now start upload')
				
				transport = paramiko.Transport('10.162.28.185', 22)
				transport.connect(username=username, password=password)
				sftp = paramiko.SFTPClient.from_transport(transport)
				sftp.put(mtdirectory+'\\DSC_Maintenance_Record.csv','/data2/TMP/tsdss/DSC_Send_Mail_Tool/DSC_Maintenance_Record.csv')
				print('upload successfully')
				
				cmd='chmod 777 /data2/TMP/tsdss/DSC_Send_Mail_Tool/DSC_Maintenance_Record.csv'
				ssh_onetime_ping('10.162.28.185',username,password,cmd)
				
				os.remove(mtdirectory+'\\DSC_Maintenance_Record.csv')
				QMessageBox.information(self,"Information","Congrats! Maintenance added successfully!\nClick 'OK' to send meeting request to relevant teams.",QMessageBox.Ok)
				Subject='Maintenance notification from customer: '+maintenance_item[0]
				
				tz = get_localzone()
				print(tz)
				
				#start_datetime=self.dateTimeEdit_start_time_maintenance.dateTime().toString('yyyy-MM-dd hh:mm')
				start_datetime=self.dateTimeEdit_start_time_maintenance.dateTime().toString('yyyy,MM,dd,hh,mm')
				print(start_datetime)
				
				t = datetime(int(start_datetime_year),int(start_datetime_month),int(start_datetime_day),int(start_datetime_hour),int(start_datetime_min))
				print(t)
				#start_datetime=self.dateTimeEdit_start_time_maintenance.dateTime()
				
				utc = pytz.utc
				utc_dt = utc.localize(t)
				print(utc_dt)
				start_date_time = str(utc_dt.astimezone(tz)).split('+')[0]
				print(start_date_time)
				
				
				t_end = datetime(int(end_datetime_year),int(end_datetime_month),int(end_datetime_day),int(end_datetime_hour),int(end_datetime_min))
				print(t_end)
				utc_dt_end = utc.localize(t_end)
				
				end_date_time = str(utc_dt_end.astimezone(tz)).split('+')[0]
				print(end_date_time)
				
				#end_datetime=self.dateTimeEdit_end_time_maintenance.dateTime().toString('yyyy-MM-dd hh:mm')
				#print(end_datetime)
				send_calendar(['TTAC@syniverse.com','scc@syniverse.com','PS-RCC-AP@syniverse.com','ao-rcc-ap@syniverse.com','DSS_Route_Provision@syniverse.com'],start_date_time,end_date_time,Subject, maintenance_item[3])
			
	def check_maintenance(self):
		global username, password,ccb_info
		
		cmd='cat /data2/TMP/tsdss/DSC_Send_Mail_Tool/DSC_Maintenance_Record.csv'
		current_maintenance=ssh_onetime_ping('10.162.28.185',username,password,cmd)
		#current_maintenance=ssh_onetime_ping_check_maintenance('10.162.28.185',username,password,cmd)
		
		print(current_maintenance)
		print(type(current_maintenance))
		
		"""self.textEdit_mail_body.setText('All current maintenance listed here:\n\nCustomer	Start Time	End Time	Notes	Owner\n\n')
		for item in current_maintenance:
			if '\n' in item:
				item=item.split('\n')[0]
			print(item)
			current_maintenance_old=self.textEdit_mail_body.toPlainText()
			current_maintenance_old=current_maintenance_old[:-1]
			self.textEdit_mail_body.setText(current_maintenance_old+item)"""
			
		
		print('check_maintenance_tabwidget:\n')
		
		
		if current_maintenance==[]:
			print('csv file not exist, no maintenance')
			QMessageBox.information(self,"Information","There's no maintenance till now.",QMessageBox.Ok)
		else:
			print('csv file already exist, maintenance exist')
			
			mtdirectory=os.getcwd()+r'\\file\\maintenance_files\\'
			if not os.path.exists(mtdirectory):
				os.makedirs(mtdirectory)
			
			transport = paramiko.Transport('10.162.28.185', 22)
			transport.connect(username=username, password=password)
			sftp = paramiko.SFTPClient.from_transport(transport)
			sftp.get('/data2/TMP/tsdss/DSC_Send_Mail_Tool/DSC_Maintenance_Record.csv',mtdirectory+'\\DSC_Maintenance_Record.csv')
			print('download ok')
			
			current_maintenance_list=[]
			with open(mtdirectory+'/DSC_Maintenance_Record.csv', 'r') as mt_files:
				#current_maintenance_list=mt_files.readlines()
				cv = csv.reader(mt_files)
				#print(type(cv))
				#print(cv)
				
				for line in cv: 
					if line!=[]:
						current_maintenance_list.append(line)
				
				print(current_maintenance_list)
			self.current_maintenance_list_signal.emit(current_maintenance_list)
			os.remove(mtdirectory+'\\DSC_Maintenance_Record.csv')



"""****************************************************************************************************"""
"""***************************             2. Login Window            *********************************"""
"""****************************************************************************************************"""
class My_login(QMainWindow, Ui_Dialog_login):

	login_signal = pyqtSignal(str,str)

	def __init__(self, parent=None):    
		super(My_login, self).__init__(parent)
		self.setupUi(self)
		
		#self.pushButton_login.clicked.connect(self. close)
		self.pushButton_login.clicked.connect(self.send_login_signal)
		
	def send_login_signal(self):

		self.login_signal.emit(self.lineEdit_gib.text(),self.lineEdit_password.text())
		self.lineEdit_password.clear()
		#self.lineEdit_gib.clear()

	def close_login_window(self,account_result):
		if account_result == "ok":
			#print("Not closed")
			self. close()
			#print("closed")
		elif account_result == "nok_no_network":
			QMessageBox.information(self,"Warning","Can't connect to DSC, please check your network.",QMessageBox.Ok)
		else:
			QMessageBox.information(self,"Warning","Wrong account/password, please input again.",QMessageBox.Ok)


"""****************************************************************************************************"""
"""***************************          3. Input alarm window          ********************************"""
"""****************************************************************************************************"""

class Input_alarms(QMainWindow, Ui_Dialog_input_alarms):

	alarms_inputed_signal = pyqtSignal(str)

	def __init__(self, parent=None):    
		super(Input_alarms, self).__init__(parent)
		self.setupUi(self)

		self.pushButton_cancel.clicked.connect(self.close)
		self.pushButton_ok.clicked.connect(self.alarms_inputed)
		

	def alarms_inputed(self):
		self.alarms_inputed_signal.emit(self.textEdit_alarm_content.toPlainText())
		self.textEdit_alarm_content.setPlainText('')
		self.close()


"""****************************************************************************************************"""
"""***********************          4. All day ping result window          ****************************"""
"""****************************************************************************************************"""

class All_Day_Ping_Result(QMainWindow, Ui_all_day_ping_result_popup):
	global router_list
	stop_7_24_ping_signal = pyqtSignal(str)

	def __init__(self, parent=None):    
		super(All_Day_Ping_Result, self).__init__(parent)
		self.setupUi(self)

		#self.pushButton_cancel.clicked.connect(self.close)
		#self.pushButton_ok.clicked.connect(self.alarms_inputed)
		self.pushButton_copy_package_loss_log.clicked.connect(self.copy_package_loss_log)
		self.pushButton_copy_result_log.clicked.connect(self.copy_result_log)
		self.pushButton_stop_ping.clicked.connect(self.stop_7_24_ping_signal_send)
		
	def receive_ping_result(self,str_received_ping_result,router_index):

		#self.label_status.setText('Status: In Progress...')

		if '100 percent' not in str_received_ping_result and '5 packets received' not in str_received_ping_result:
			#print(str_received_ping_result)
			package_loss_log_old=self.textEdit_package_loss_log.toPlainText()
			self.textEdit_package_loss_log.setPlainText(package_loss_log_old+"\n***************************************\n"+str_received_ping_result)
		
		if router_index==0:
			self.label_route1.setText('Router1: '+router_list[0]['router_name'])
			result_log_old_1=self.textEdit_ping_result_1.toPlainText()
			self.textEdit_ping_result_1.setPlainText(result_log_old_1+"\n***************************************\n"+str_received_ping_result)
			self.textEdit_ping_result_1.moveCursor(QtGui.QTextCursor.End) 
		elif router_index==1:
			self.label_route2.setText('Router2: '+router_list[1]['router_name'])
			result_log_old_2=self.textEdit_ping_result_2.toPlainText()
			self.textEdit_ping_result_2.setPlainText(result_log_old_2+"\n***************************************\n"+str_received_ping_result)
			self.textEdit_ping_result_2.moveCursor(QtGui.QTextCursor.End) 
		elif router_index==2:
			self.label_route3.setText('Router3: '+router_list[2]['router_name'])
			result_log_old_3=self.textEdit_ping_result_3.toPlainText()
			self.textEdit_ping_result_3.setPlainText(result_log_old_3+"\n***************************************\n"+str_received_ping_result)
			self.textEdit_ping_result_3.moveCursor(QtGui.QTextCursor.End) 
		elif router_index==3:
			self.label_route4.setText('Router4: '+router_list[3]['router_name'])
			result_log_old_4=self.textEdit_ping_result_4.toPlainText()
			self.textEdit_ping_result_4.setPlainText(result_log_old_4+"\n***************************************\n"+str_received_ping_result)
			self.textEdit_ping_result_4.moveCursor(QtGui.QTextCursor.End) 
		elif router_index==4:
			self.label_route5.setText('Router5: '+router_list[4]['router_name'])
			result_log_old_5=self.textEdit_ping_result_5.toPlainText()
			self.textEdit_ping_result_5.setPlainText(result_log_old_5+"\n***************************************\n"+str_received_ping_result)
			self.textEdit_ping_result_5.moveCursor(QtGui.QTextCursor.End) 
		elif router_index==5:
			self.label_route6.setText('Router6: '+router_list[5]['router_name'])
			result_log_old_6=self.textEdit_ping_result_6.toPlainText()
			self.textEdit_ping_result_6.setPlainText(result_log_old_6+"\n***************************************\n"+str_received_ping_result)
			self.textEdit_ping_result_6.moveCursor(QtGui.QTextCursor.End) 
		elif router_index==6:
			self.label_route7.setText('Router7: '+router_list[6]['router_name'])
			result_log_old_7=self.textEdit_ping_result_7.toPlainText()
			self.textEdit_ping_result_7.setPlainText(result_log_old_7+"\n***************************************\n"+str_received_ping_result)
			self.textEdit_ping_result_7.moveCursor(QtGui.QTextCursor.End) 
		elif router_index==7:
			self.label_route8.setText('Router8: '+router_list[7]['router_name'])
			result_log_old_8=self.textEdit_ping_result_8.toPlainText()
			self.textEdit_ping_result_8.setPlainText(result_log_old_8+"\n***************************************\n"+str_received_ping_result)
			self.textEdit_ping_result_8.moveCursor(QtGui.QTextCursor.End) 
		else:
			print('router_index=')
			print(router_index)
			self.label_route9.setText('Router9: '+router_list[8][router_name])
			result_log_old_9=self.textEdit_ping_result_9.toPlainText()
			self.textEdit_ping_result_9.setPlainText(result_log_old_9+"\n***************************************\n"+str_received_ping_result)
			self.textEdit_ping_result_9.moveCursor(QtGui.QTextCursor.End) 


	def copy_package_loss_log(self):
		copy_package_loss_log=self.textEdit_package_loss_log.toPlainText()
		pyperclip.copy(copy_package_loss_log)
		
		
	def copy_result_log(self):
		
		copy_result_log1=self.label_route1.text()+ '\n\n'+ self.textEdit_ping_result_1.toPlainText() 
		copy_result_log2=self.label_route2.text()+ '\n\n'+ self.textEdit_ping_result_2.toPlainText() 
		copy_result_log3=self.label_route3.text()+ '\n\n'+ self.textEdit_ping_result_3.toPlainText() 
		copy_result_log4=self.label_route4.text()+ '\n\n'+ self.textEdit_ping_result_4.toPlainText()
		copy_result_log5=self.label_route5.text()+ '\n\n'+ self.textEdit_ping_result_5.toPlainText() 
		copy_result_log6=self.label_route6.text()+ '\n\n'+ self.textEdit_ping_result_6.toPlainText()
		copy_result_log7=self.label_route7.text()+ '\n\n'+ self.textEdit_ping_result_7.toPlainText() 
		copy_result_log8=self.label_route8.text()+ '\n\n'+ self.textEdit_ping_result_8.toPlainText()
		copy_result_log9=self.label_route9.text()+ '\n\n'+ self.textEdit_ping_result_9.toPlainText()
		
		copy_result_log=copy_result_log1+'\n\n\n\n'+copy_result_log2+'\n\n\n\n'+copy_result_log3+'\n\n\n\n'+copy_result_log4+'\n\n\n\n'+copy_result_log5+'\n\n\n\n'+copy_result_log6+'\n\n\n\n'+copy_result_log7+'\n\n\n\n'+copy_result_log8+'\n\n\n\n'+copy_result_log9
		pyperclip.copy(copy_result_log)
		
	def stop_7_24_ping_signal_send(self):
		self.stop_7_24_ping_signal.emit("Stop")
		self.label_7_24_ping_status.setText('Status: Stoped')

	def closeEvent(self, event):
		self.stop_7_24_ping_signal_send()
		event.accept()
		
	def reset_all_day_ping_window(self,flag,inc_description):
		if flag==1:
			self.textEdit_incident_description.setText(inc_description)
			self.textEdit_ping_result_1.clear()
			self.textEdit_ping_result_2.clear()
			self.textEdit_ping_result_3.clear()
			self.textEdit_ping_result_4.clear()
			self.textEdit_ping_result_5.clear()
			self.textEdit_ping_result_6.clear()
			self.textEdit_ping_result_7.clear()
			self.textEdit_ping_result_8.clear()
			self.textEdit_ping_result_9.clear()
			self.textEdit_package_loss_log.clear()
			self.label_7_24_ping_status.setText('Status: Running')
			self.label_route1.setText('Router1:')
			self.label_route2.setText('Router2:')
			self.label_route3.setText('Router3:')
			self.label_route4.setText('Router4:')
			self.label_route5.setText('Router5:')
			self.label_route6.setText('Router6:')
			self.label_route7.setText('Router7:')
			self.label_route8.setText('Router8:')
			self.label_route9.setText('Router9:')


"""****************************************************************************************************"""
"""*********************          5. Check maintenance result window          *************************"""
"""****************************************************************************************************"""

class Check_maintenance_popup(QMainWindow, Ui_check_maintenance_popup):

	def __init__(self, parent=None):    
		super(Check_maintenance_popup, self).__init__(parent)
		self.setupUi(self)
		self.tableWidget_check_maintenance_result.horizontalHeader().setSectionResizeMode(3)

	def show_current_maintenance(self,current_maintenance_list):

		print(current_maintenance_list)
		self.tableWidget_check_maintenance_result.setRowCount(len(current_maintenance_list))
		self.tableWidget_check_maintenance_result.setColumnCount(5)

		rowindex=0
		for item in current_maintenance_list:
			print(item)
			maintenance_customer=QTableWidgetItem(item[0])
			maintenance_starttime=QTableWidgetItem(item[1])
			maintenance_endtime=QTableWidgetItem(item[2])
			maintenance_note=QTableWidgetItem(item[3])
			maintenance_owner=QTableWidgetItem(item[4])
			#print(maintenance_customer)
			
			self.tableWidget_check_maintenance_result.setItem(rowindex,0,maintenance_customer)
			self.tableWidget_check_maintenance_result.setItem(rowindex,1,maintenance_starttime)
			self.tableWidget_check_maintenance_result.setItem(rowindex,2,maintenance_endtime)
			self.tableWidget_check_maintenance_result.setItem(rowindex,3,maintenance_note)
			self.tableWidget_check_maintenance_result.setItem(rowindex,4,maintenance_owner)

			#self.tableWidget_check_maintenance_result.item(rowindex,1).setForeground(QBrush(QColor(255,0,0)))

			rowindex=rowindex+1
		
		#column width adjust with content
		self.tableWidget_check_maintenance_result.horizontalHeader().setSectionResizeMode(3)
		
		#add header
		horizontalHeader=['Customer','Start Time','End Time','Notes','Owner']
		self.tableWidget_check_maintenance_result.setHorizontalHeaderLabels(horizontalHeader)

		check_maintenance_popup.show()






"""****************************************************************************************************"""
"""***************************                  6. Run               **********************************"""
"""****************************************************************************************************"""
if __name__=="__main__":  
	app = QApplication(sys.argv)  
	myWin = MyMainWindow()  
	myWin.show()  
	mylogin = My_login()  
	mylogin.show()
	all_Day_Ping_Result=All_Day_Ping_Result()
	all_Day_Ping_Result.stop_7_24_ping_signal.connect(myWin.stop_7_24_ping_flag)
	
	myWin.account_result_signal.connect(mylogin.close_login_window)
	myWin.send_ping_result_signal.connect(all_Day_Ping_Result.receive_ping_result)
	myWin.start_7_24_ping_signal.connect(all_Day_Ping_Result.reset_all_day_ping_window)
	mylogin.login_signal.connect(myWin.test_account)

	myWin.update_textEdit_log_name_content_signal.connect(myWin.update_textEdit_log_name_content)
	myWin.show_download_kpi_file_popup_signal.connect(myWin.show_download_kpi_file_popup)
	myWin.show_figure_signal.connect(myWin.show_figure)
	
	myWin.show_download_kpi_file_failed_popup_signal.connect(myWin.show_download_kpi_file_failed_popup)
	myWin.update_textEdit_log_name_content_list_signal.connect(myWin.update_textEdit_log_name_content_list)
	
	input_alarms=Input_alarms()
	input_alarms.alarms_inputed_signal.connect(myWin.alarm_content_handler)
	input_alarms.alarms_inputed_signal.connect(myWin.generatecmd_troubleshooting)
	
	check_maintenance_popup=Check_maintenance_popup()
	myWin.current_maintenance_list_signal.connect(check_maintenance_popup.show_current_maintenance)
	

	sys.exit(app.exec_())  
