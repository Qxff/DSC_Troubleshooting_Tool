"""*******************************************************************************************************

This script provide ssh ping commands for DSC.
1. ssh_long_ping(hostname,username,password,sourceip,destinationip,time_mins)
2. ssh_onetime_ping(hostname,username,password,sourceip,destinationip)

Before using the script below, please first do:  pip install paramiko

Author: Jason Qin
Version: 2018.04.17

*******************************************************************************************************"""

import paramiko
from pexpect import popen_spawn
import pexpect, pexpect.popen_spawn
import getpass, os
import time


"""****************************************************************************************************"""
"""***************************             ssh long ping             **********************************"""
"""****************************************************************************************************"""

def ssh_long_ping(hostname,username,password,sourceip,destinationip,time_mins):

	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(hostname=hostname, port=22, username=username, password=password)

	#execute command
	pingtime=time_mins*60
	#ping_result.log is saved in your account home folder
	cmd="ping -I "+ sourceip  + " "+ destinationip + " -s1472 -c " + str(pingtime) + """ | awk '{print $0"\\t"  strftime("%c",systime())} '"""+" > ping_result.log &"
	
	print(cmd)
	ssh.exec_command(cmd)

	#close the connection
	ssh.close()

#ssh_long_ping("10.162.28.187","g800472","Gaoding5658$","173.209.220.115","173.209.215.102",3)


"""****************************************************************************************************"""
"""***************************            ssh ping onetime           **********************************"""
"""****************************************************************************************************"""

def ssh_onetime_ping(hostname,username,password,cmd):

	#paramiko.util.log_to_file('paramiko.log')
	
	#creat SSH object
	ssh = paramiko.SSHClient()

	#skip key
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	#connect to DSC
	ssh.connect(hostname=hostname, port=22, username=username, password=password)
	#stdin.write("Y")

	#execute command
	stdin, stdout, stderr = ssh.exec_command(cmd)
	
	result=[]
	return stdout.readlines()
	#for std in stdout.readlines():
	#	print(std.strip())
	#print(std.strip())
	#return result
	#print(result)

	for std in stderr.readlines():
		#print(std.strip())
		result.append(std.strip())
	return result
	#print(result)

	#close the connection
	ssh.close()

#ssh_onetime_ping("10.162.28.187","g800472","Python666$","ping -I 173.209.220.115 111.71.235.1 -s1472 -c3")


"""****************************************************************************************************"""
"""*****************            ssh ping onetime for check maintenance           **********************"""
"""****************************************************************************************************"""

def ssh_onetime_ping_check_maintenance(hostname,username,password,cmd):

	#paramiko.util.log_to_file('paramiko.log')
	
	#creat SSH object
	ssh = paramiko.SSHClient()

	#skip key
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	#connect to DSC
	ssh.connect(hostname=hostname, port=22, username=username, password=password)
	#stdin.write("Y")

	#execute command
	stdin, stdout, stderr = ssh.exec_command(cmd)
	
	result=[]
	#stdout._set_mode('b')
	return stdout.read().decode('utf-8')
	#for std in stdout.readlines():
	#	print(std.strip())
	#print(std.strip())
	#return result
	#print(result)

	for std in stderr.readlines():
		#print(std.strip())
		result.append(std.strip())
	return result
	#print(result)

	#close the connection
	ssh.close()


"""****************************************************************************************************"""
"""***********************            ssh jump server commands           ******************************"""
"""****************************************************************************************************"""

def ssh_jump_server_cmd(hostname,username,password,cmd):

	#paramiko.util.log_to_file('paramiko.log')
	
	#creat SSH object
	ssh = paramiko.SSHClient()

	#skip key
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	#connect to DSC
	ssh.connect(hostname=hostname, port=22, username=username, password=password)

	chan=ssh.invoke_shell()
	chan.send('ssh r003-sng2-ngn'+'\n')
	res=chan.recv(65535)
	time.sleep(4)
	chan.send(password+'\n')
	time.sleep(2)
	res=chan.recv(65535)
	chan.send(cmd+'\n')
	time.sleep(2)

	result = ''
	while True:
		time.sleep(2)
		res = chan.recv(65535).decode('utf8')
		result = res
		if result:
			results=result.strip('\n')
			if 'UTC' in results:
				return results.split(' UTC')[1].strip()
			else:
				return results

		if res.endswith('> '):
			break

	#close the connection"""
	ssh.close()
	
	
	
	
"""****************************************************************************************************"""
"""**********************            ssh Juniper router commands           ****************************"""
"""****************************************************************************************************"""

def ssh_jump_server_juniper_cmd(router_name,username,password,cmd1,cmd2):

	#paramiko.util.log_to_file('paramiko.log')
	
	#creat SSH object
	ssh = paramiko.SSHClient()

	#skip key
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	#connect to DSC
	ssh.connect(hostname="10.12.7.16", port=22, username=username, password=password)

	chan=ssh.invoke_shell()
	ssh_router_cmd="ssh " + router_name
	print(ssh_router_cmd)
	chan.send(ssh_router_cmd+'\n')
	res=chan.recv(65535)
	time.sleep(4)
	chan.send(password+'\n')
	time.sleep(2)
	res=chan.recv(65535)
	chan.send(cmd1+'\n')
	time.sleep(1)
	chan.send(cmd2+'\n')
	time.sleep(2)

	result = ''
	while True:
		time.sleep(2)
		res = chan.recv(65535).decode('utf8')
		result = res
		if result:
			results=result.strip('\n')
			if 'UTC' in results:
				return results.split(' UTC')[1].strip()
			else:
				return results

		if res.endswith('> '):
			break

	#close the connection"""
	ssh.close()


"""****************************************************************************************************"""
"""**********************            ssh Cisco router commands           ****************************"""
"""****************************************************************************************************"""

def ssh_jump_server_cisco_cmd(router_name,username,password,cmd1,cmd2):

	#paramiko.util.log_to_file('paramiko.log')
	
	#creat SSH object
	ssh = paramiko.SSHClient()

	#skip key
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	#connect to DSC
	ssh.connect(hostname="10.12.7.16", port=22, username=username, password=password)

	chan=ssh.invoke_shell()
	telnet_router_cmd="telnet " + router_name
	print(telnet_router_cmd)
	chan.send(telnet_router_cmd+'\n')
	res=chan.recv(65535)
	time.sleep(2)
	chan.send(username+'\n')
	time.sleep(2)
	chan.send(password+'\n')
	time.sleep(2)
	res=chan.recv(65535)
	time.sleep(1)
	chan.send(cmd1+'\n')
	time.sleep(2)
	chan.send(cmd2+'\n')
	time.sleep(2)

	result = ''
	while True:
		time.sleep(2)
		res = chan.recv(65535).decode('utf8')
		result = res
		if result:
			results=result.strip('\n')
			return results

		if res.endswith('> '):
			break

	#close the connection"""
	ssh.close()



"""****************************************************************************************************"""
"""***********************            ssh for nohup commands           ******************************"""
"""****************************************************************************************************"""

def ssh_nohup_cmd(hostname,username,password,cmd):

	#paramiko.util.log_to_file('paramiko.log')
	
	#creat SSH object
	ssh = paramiko.SSHClient()

	#skip key
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	#connect to DSC
	ssh.connect(hostname=hostname, port=22, username=username, password=password)

	chan=ssh.invoke_shell()
	chan.send(cmd+'\n')
	#res=chan.recv(65535)
	time.sleep(0.5)
	chan.send('\n')
	time.sleep(0.5)
	
	res = chan.recv(65535).decode('utf8')
	result = res
	ssh.close()
	return result


if __name__=="__main__": 
	print('before')
	#results=ssh_jump_server_juniper_cmd("r002-hnk2-ngn.ncc.syniverse.com","g800472","Selenium666$","ping 192.168.71.206 count 5 rapid wait 1","show system uptime | match current")
	#results=ssh_jump_server_cisco_cmd("airtel-bng-india.ncc.syniverse.com","g800472","Selenium666$","show clock","ping 131.166.150.157 ")
	print('after')
	print('results: ')
	print(results)





