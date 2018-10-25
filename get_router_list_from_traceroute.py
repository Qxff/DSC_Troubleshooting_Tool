#coding:utf-8
# -*- coding: utf-8 -*-
import requests
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth
import getpass

traceroute=""" 1  173.209.220.113 (173.209.220.113)  1.530 ms  2.939 ms  3.874 ms 
 2  173.209.213.85 (173.209.213.85)  3.884 ms  3.917 ms  3.883 ms
 3  192.168.71.206 (192.168.71.206)  34.558 ms  34.533 ms  34.589 ms
 4  10.163.0.30 (10.163.0.30)  51.888 ms  51.937 ms  51.904 ms
 5  131.166.146.78 (131.166.146.78)  35.356 ms  35.528 ms  35.769 ms
 6  * * *
 7  * * *
 8  * * *
 9  * * *
10  * * *
11  * * *
12  * * *"""


def get_router_list_from_traceroute(traceroute,user_name,password):
	r1 = traceroute.split("\n")
	if r1[1].find('131.166.129.145') >=0:
		r = r1[3:]
	else:
		r = r1[1:]
	ip_list = []
	for i in r:
		ii = i.split(" ")
		ip = ii[3]
		if ip.startswith("*") != True:
			ip_list.append(ip)

			
	
	router_hostnames = []
	
	
	new_ip_list= []
	
	
	for ip in ip_list:
		ip_add = ip
		auth=HTTPBasicAuth(user_name,password)
		url_query = "http://10.12.7.109:8581/odata/api/devices?$filter=((substringof('"+ip_add+"', interfaces/IPAddresses) eq true))"
		r=requests.get(url= url_query,auth=auth)
		t = r.text
		if t.count("syniverse") >= 1:
			list = t.split(',')
			router_hostnames.append(list[19])
			new_ip_list.append(ip_add)

	customer_ip = ip_list[ip_list.index(new_ip_list[-1])+1]
	new_ip_list.append(customer_ip)

	
	router_types = []
	number_of_item = len(router_hostnames)
	n_vendors = 0 
	while n_vendors < number_of_item:
		router_types.append("NO BG")
		n_vendors=n_vendors+1
	router_types[-1] = "BG"

	
	vendors = []
	for hostname in router_hostnames:
		if hostname.count("ngn") == 1:
			vendor_type = "Juniper"
			vendors.append(vendor_type)
		else:
			vendor_type = "Cisco"
			vendors.append(vendor_type)

	
	number_of_item = len(router_hostnames)
	
	output = []
	m = 0
	while m < number_of_item:
		record = {}
		record["router_name"] = router_hostnames[m]
		record["vendor"] = vendors[m]
		record["type"] = router_types[m]

		record['next_hop_ip'] = new_ip_list[m+1]
		output.append(record)
		m += 1
	return output

#get_router_list_from_traceroute(traceroute,user_name,password)



	






