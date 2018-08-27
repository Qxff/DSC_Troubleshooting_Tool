#coding:utf-8



# -*- coding: utf-8 -*-
import requests
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth
import getpass



# ~ traceroute = '''
	# ~ traceroute -s 173.209.215.102 217.15.121.229
	# ~ traceroute to 217.15.121.229 (217.15.121.229), 30 hops max, 60 byte packets
	# ~ 1 173.209.215.97 (173.209.215.97) 1.668 ms 1.629 ms 2.953 ms
	# ~ 2 173.209.213.67 (173.209.213.67) 3.156 ms 3.207 ms 3.188 ms
	# ~ 3 192.168.71.186 (192.168.71.186) 6.863 ms 7.176 ms 7.362 ms
	# ~ 4 10.161.0.89 (10.161.0.89) 7.542 ms 7.834 ms 8.234 ms
	# ~ 5 131.166.150.234 (131.166.150.234) 215.019 ms 215.165 ms 215.388 ms
	# ~ 6 172.19.201.2 (172.19.201.2) 219.649 ms 215.182 ms 215.211 ms
	# ~ 7 172.18.0.233 (172.18.0.233) 222.246 ms 393.261 ms 393.284 ms
	# ~ 8 172.18.0.153 (172.18.0.153) 214.235 ms 214.290 ms *
	# ~ 9 172.18.0.153 (172.18.0.153) 416.876 ms 416.915 ms 416.890 ms
	# ~ 10 172.18.0.153 (172.18.0.153) 215.719 ms 216.261 ms 216.484 ms
	# ~ 11 172.18.0.153 (172.18.0.153) 216.105 ms 216.131 ms 216.789 ms
	# ~ 12 * * *
	# ~ 13 * * *
	# ~ 14 * * *
	# ~ 15 * * *
	# ~ 16 * * *
	# ~ 17 * * *
	# ~ 18 * * *
	# ~ 19 * * *
	# ~ 20 * * *
	# ~ 21 * * *
	# ~ 22 * * *
	# ~ 23 * * *
	# ~ 24 * * *
	# ~ 25 * * *
	# ~ 26 * * *
	# ~ 27 * * *
	# ~ 28 * * *
	# ~ 29 * * *
	# ~ 30 * * *'''
	

traceroute = ''' 
 1  * * *
 2  173.209.213.85 (173.209.213.85)  3.916 ms  3.879 ms  3.899 ms
 3  192.168.71.206 (192.168.71.206)  35.546 ms  35.509 ms  36.432 ms
 4  * 192.168.71.229 (192.168.71.229)  74.583 ms  74.711 ms
 5  192.168.71.70 (192.168.71.70)  74.786 ms  75.796 ms  75.639 ms
 6  172.27.4.213 (172.27.4.213)  75.686 ms  73.319 ms  73.354 ms
 7  131.166.150.157 (131.166.150.157)  73.967 ms  73.725 ms  73.803 ms
 8  10.91.25.209 (10.91.25.209)  73.642 ms  73.498 ms  73.590 ms
 9  * * *
10  * * *
11  * * *
12  * * *
13  * * *
14  * * *
15  * * *
16  * * *
17  * * *
18  * * *
19  * * *
20  * * *
21  * * *
22  * * *
23  * * *
24  * * *
25  * * *
26  * * *
27  * * *
28  * * *
29  * * *
30  * * *'''


def get_router_list_from_traceroute(traceroute,user_name,password):
	r1 = traceroute.split("\n")
	#print(r1[0:4])
	r = r1[1:]
	ip_list = []
	for i in r:
		#print(i)
		ii = i.split(" ")
		ip = ii[3]
		#ip = ii[1]
		#print(ip)
		if ip.startswith("*") != True:
			ip_list.append(ip)
	#print(ip_list)
			
	
	router_hostnames = []
	for ip in ip_list:
		ip_add = ip
		auth=HTTPBasicAuth(user_name,password)
		#url_query ="http://10.12.7.109:8581/odata/api/routers?$filter=((interfaces/IPAddresses eq"+" "+"'"+ip_add+"'))"
		url_query = "http://10.12.7.109:8581/odata/api/devices?$filter=((substringof('"+ip_add+"', interfaces/IPAddresses) eq true))"
		r=requests.get(url= url_query,auth=auth)
		#print(r.text)
		t = r.text
		if t.count("syniverse") >= 1:
			list = t.split(',')
			#print(list[19])
			router_hostnames.append(list[19])
	#print(router_hostnames)
		
	
	router_types = []
	number_of_item = len(router_hostnames)
	n_vendors = 0 
	while n_vendors < number_of_item:
		router_types.append("NO BG")
		n_vendors=n_vendors+1
	router_types[-1] = "BG"
	#print(router_types)
	
	
	vendors = []
	for hostname in router_hostnames:
		if hostname.count("ngn") == 1:
			vendor_type = "Juniper"
			vendors.append(vendor_type)
		else:
			vendor_type = "Cisco"
			vendors.append(vendor_type)
	#print(vendors)	
	
	number_of_item = len(router_hostnames)
	
	output = []
	m = 0
	while m < number_of_item:
		record = {}
		record["router_name"] = router_hostnames[m]
		record["vendor"] = vendors[m]
		record["type"] = router_types[m]
		record['next_hop_ip'] = ip_list[m+1]
		output.append(record)
		m += 1
	return (output)
	#for o in output:
	#	print(o)
		
		
if __name__=="__main__": 
	get_router_list_from_traceroute(traceroute,"g800472","Selenium666$")






