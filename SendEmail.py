#First, install pywin32 by using "python -m pip install pypiwin32" on Windows Command console

import win32com.client as win32 
import datetime,time,os

def sendemail (Tolist,Cclist, Subject, Sentence1):
	outlook = win32.Dispatch('outlook.application') 
	mail = outlook.CreateItem(0)
	print(dir())
	mail.To = Tolist
	mail.CC = Cclist
	mail.Subject = Subject
	mail.HTMLBody=Sentence1
	#mail.Attachments.Add(r'C:\Users\g801781\Desktop\python_work\SendEmail.py')
	mail.Display()
	return(0)
	
def sende_plain_mail (Tolist, Cclist, Subject, Sentence1):
	outlook = win32.Dispatch('outlook.application') 
	mail = outlook.CreateItem(0)
	mail.To = Tolist
	mail.CC = Cclist
	mail.Subject = Subject
	mail.Body=Sentence1
	#mail.Attachments.Add(r'C:\Users\g801781\Desktop\python_work\SendEmail.py')
	mail.Display() 

def html_line_break(email_body):
	new_email_body=email_body.replace('\n','<br/>')
	return new_email_body
	
	
def send_calendar(recipients,start_time,end_time,Subject, Sentence1):
	outlook = win32.Dispatch('outlook.application') 
	mail = outlook.CreateItem(1)
	mail.MeetingStatus= 1 

	mail.Subject = Subject
	#mail.start=datetime.datetime.now() + datetime.timedelta(hours=8)
	#print(datetime.datetime.now() + datetime.timedelta(hours=8))
	mail.start=start_time
	#mail.Duration=60
	#mail.end=datetime.datetime.now() + datetime.timedelta(hours=8)
	mail.end=end_time
	mail.Body=Sentence1
	mail.location='Null'
	mail.ReminderMinutesBeforeStart = 30
	
	for recipient in recipients:
		invitee= mail.Recipients.Add(recipient)
		#invitee.Type = OUTLOOK_OPTIONAL_ATTENDEE
	
	mail.Display()
	return(0)

#send_calendar (['TTAC@syniverse.com','scc@syniverse.com','PS-RCC-AP@syniverse.com','ao-rcc-ap@syniverse.com','DSS_Route_Provision@syniverse.com'],1,2, 'Test Email','This Email is sent using Python script')
