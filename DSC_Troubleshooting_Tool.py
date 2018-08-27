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
		


Pending function: 
1. UPX compressed, smaller size 20M --> 15M

*******************************************************************************************************"""

# -*- coding: utf-8 -*-

import sys,os
import re
import paramiko
import copy
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from DSC_Troubleshooting_Tool_ui import *
from DSC_Login_ui import *
from Input_alarms_ui import *
from ssh_ping_cmd import ssh_onetime_ping, ssh_jump_server_cmd,ssh_jump_server_juniper_cmd,ssh_jump_server_cisco_cmd
from SendEmail import sendemail,html_line_break
from get_router_list_from_traceroute import *
from All_Day_Ping_Result_ui import *


"""****************************************************************************************************"""
"""***************************             1. Main Window            **********************************"""
"""****************************************************************************************************"""

class MyMainWindow(QMainWindow, Ui_MainWindow):
	
	account_result_signal = pyqtSignal(str)
	send_ping_result_signal= pyqtSignal(str)
	
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
		self.comboBox_customer.addItems(["Customer","Customer 1","Customer 2","Customer 3","Customer 4"])
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
		
		self.dlbloginip={"HK DSC":"10.162.28.187","SG DSC":"10.163.28.132","AMS DSC":"10.160.28.221","FRT DSC":"10.161.28.249","CHI DSC":"10.166.28.201","DAL DSC":"10.164.28.190"}
		
		global username, password,ccb_info
	
	def update_customer_list(self):
		print('okokokokokokok')
		global ccb_info
		
		#self.comboBox_customer_name.clear()
		
		customer_inputted=self.comboBox_customer_name.currentText()
		self.comboBox_customer_name.clear ()
		
		customer_list=[]
		for row in ccb_info:
			if customer_inputted.lower() in row["Operator"].lower():
				if row["Operator"] not in customer_list:
					customer_list.append(row["Operator"])

		print(customer_list)
		self.comboBox_customer_name.addItems(customer_list)
		
		
	def update_customer_peer(self):
		global ccb_info
		customer_name=self.comboBox_customer_name.currentText()
		self.comboBox_customer_peername.clear ()
		
		peer_list=[]
		for row in ccb_info:
			if customer_name.lower() == row["Operator"].lower():
				if row["Hostname"] not in peer_list:
					peer_list.append(row["Hostname"])
		
		print(peer_list)
		self.comboBox_customer_peername.addItems(peer_list)

	def test_account(self,username_signal,password_signal):
		global username, password,ccb_info
		username=username_signal
		password=password_signal
		
		self.lineEdit_GID.setText(username)

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

		"""import csv
		if os.path.exists("file")==0:
			os.mkdir("file")
		with open('.\\file\ccb_online.csv', 'w',newline='') as csvfile:
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
				spamwriter.writerow(string)"""
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
		
		for sender_name in ['Show route: DSC PIP','Show route: Customer PIP']:
			if sender_name==sender.text():
				cmd=cmd_all[sender_name]
				print(cmd)
				results=ssh_jump_server_cmd('10.12.7.16',username,password,cmd)
				result_final=results
				print(result_final)
				self.textEdit_resultlog_troubleshooting.setPlainText(result_log_old+"\n***************************************\n"+result_final)
	
	def send_email_for_Null(self):
		global customer_email_list,customer_nodes
		self.syniverse_peer_dic={'HK DSC':'hkg-01.dra.ipx.syniverse.3gppnetwork.org','SG DSC':'sng-01.dra.ipx.syniverse.3gppnetwork.org','AMS DSC':'ams-01.dra.ipx.syniverse.3gppnetwork.org',
		'FRT DSC':'frt-01.dra.ipx.syniverse.3gppnetwork.org','CHI DSC':'chi-01.dra.ipx.syniverse.3gppnetwork.org', 'DAL DSC':'dal-01.dra.ipx.syniverse.3gppnetwork.org','Null':''}
		print("Trigger send email for Null")
		if customer_email_list=="Null":
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
		
		
		try:
			if customer_email_list!='Null':
				sendemail(customer_email_list,'DSS_Route_Provision@syniverse.com;TTAC@syniverse.com',Subject,email_body)
		except NameError:
			pass
			
			

#***    Function: 7*24 Ping     ***

	def start_7_24_ping(self):
		global username, password
		username="g800472"
		password="Selenium666$"
		try:
			print(self.textEdit_traceroute_result.toPlainText())
			router_list=get_router_list_from_traceroute(self.textEdit_traceroute_result.toPlainText(),username,password)
			print(router_list)
		except Exception as e:
			QMessageBox.information(self,"Warning","The traceroute result log you pasted is not right(Check the example).",QMessageBox.Ok)
		
		else:
			all_Day_Ping_Result.show()

			router1=router_list[0]['router_name']
			ping_result=ssh_jump_server_juniper_cmd(router1,username,password,"ping 192.168.71.206 count 5 rapid wait 1","show system uptime | match current")
			print(ping_result)
			self.send_ping_result_signal.emit(ping_result)
		"""for i in router_list:
			t= threading.Thread(target=self.send_multi_routers,args=(i,))
			t.start()
		self.label_status.setText('Status: In Progress...')"""


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
		#self.lineEdit_gib.setText('g800472')
		#self.lineEdit_password.setText('Python666$')
		self.login_signal.emit(self.lineEdit_gib.text(),self.lineEdit_password.text())
		self.lineEdit_password.clear()
		self.lineEdit_gib.clear()

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
"""***************************          4. All day ping result window          ********************************"""
"""****************************************************************************************************"""

class All_Day_Ping_Result(QMainWindow, Ui_all_day_ping_result_popup):

	#alarms_inputed_signal = pyqtSignal(str)

	def __init__(self, parent=None):    
		super(All_Day_Ping_Result, self).__init__(parent)
		self.setupUi(self)

		#self.pushButton_cancel.clicked.connect(self.close)
		#self.pushButton_ok.clicked.connect(self.alarms_inputed)
		
	def receive_ping_result(self,str_received_ping_result):
		result_log_old=self.textEdit_ping_result_1.toPlainText()
		self.textEdit_ping_result_1.setPlainText(result_log_old+"\n***************************************\n"+"\n"+str_received_ping_result)
		



"""****************************************************************************************************"""
"""***************************                  5. Run               **********************************"""
"""****************************************************************************************************"""
if __name__=="__main__":  
	app = QApplication(sys.argv)  
	myWin = MyMainWindow()  
	myWin.show()  
	mylogin = My_login()  
	mylogin.show()
	all_Day_Ping_Result=All_Day_Ping_Result() 
	
	myWin.account_result_signal.connect(mylogin.close_login_window)
	myWin.send_ping_result_signal.connect(all_Day_Ping_Result.receive_ping_result)
	mylogin.login_signal.connect(myWin.test_account)

	input_alarms=Input_alarms()
	input_alarms.alarms_inputed_signal.connect(myWin.alarm_content_handler)
	input_alarms.alarms_inputed_signal.connect(myWin.generatecmd_troubleshooting)
	


	sys.exit(app.exec_())  
