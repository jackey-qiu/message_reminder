#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import pandas as pd
import numpy as np
import calendar
import smtplib
from email.mime.text import MIMEText
from wxpy import *
import getpass
from access_google_sheet import from_google_sheet_to_txt

#credential file for Google sheet API
jason_credential_file="Worship-arrangement-DD-1005ad7eaf1f.json"

debug=raw_input("Do you want to run program in a test mode?Type 'y' for yes or 'n' for no: ")
debug = debug=='y'
send_month_task=raw_input("Do you want to send worship service for one month?Type 'y' for yes or 'n' for no: ")
send_month_task = send_month_task=="y"
which_month,which_year=None,None
if send_month_task:
    which_month_year_to_send=raw_input("Which month (1-12) of which year(eg. 2018)? eg type '8,2018' means Auguest in 2018:")
    which_month,which_year=map(int,which_month_year_to_send.rsplit(","))
if not debug:
    bot=Bot()
if not debug:
    email_address_sender=raw_input("What's your gmail address: ")
    password_of_your_email=getpass.getpass("What's the password of your gmail: ")
else:
    email_address_sender=" "
    password_of_your_email=" "
send_message_Sunday=raw_input("Send message reminder for Sunday?Type 'y' for yes or 'n' for no: ")
send_message_Friday=raw_input("Send message reminder for Friday bible study?Type 'y' for yes or 'n' for no: ")
update_g_sheets=raw_input("Do you want to update fushibiao from Google Sheet?Type 'y' for yes or 'n' for no: ")
send_message_Sunday = send_message_Sunday=='y'
send_message_Friday = send_message_Friday=='y'
update_g_sheets = update_g_sheets=='y'

send_wechat_msg=True
#text file of worship service schedule.
fushibiao='fushibiao.txt'#make sure the name for fushibiao on google sheet is fushibiao, ie without the extension .txt. The same for the following txt files.
fushibiao_friday="fushibiao_bible_study.txt"
#text file of Email corresponding of each person
email_db='email.txt'
wechat_db='wechat.txt'
if update_g_sheets:
    #now update these information from google spreadsheet
    print "Updating fushibiao.txt from google sheet"
    from_google_sheet_to_txt(g_file_name="fushibiao_info_all",save_file="fushibiao.txt",sheet_tag="sunday",jason_credential_file=jason_credential_file)
    print "fushibiao.txt is updated."

    print "Updating fushibiao_friday.txt from google sheet"
    from_google_sheet_to_txt(g_file_name="fushibiao_info_all",save_file="fushibiao_bible_study.txt",sheet_tag="friday",jason_credential_file=jason_credential_file)
    print "fushibiao_friday.txt is updated."
else:
    pass

"""
print "Updating wechat_db.txt from google sheet"
from_google_sheet_to_txt(g_file_name="fushibiao_info_all",save_file="wechat.txt",sheet_tag="wechat",jason_credential_file=jason_credential_file)
print "wechat_db.txt is updated."

print "Updating email_db.txt from google sheet"
from_google_sheet_to_txt(g_file_name="fushibiao_info_all",save_file="email.txt",sheet_tag="email",jason_credential_file=jason_credential_file)
print "email_db.txt is updated."
"""

#Taihe's email address
taihe_email_address="wilfredwongtaiwoo@hotmail.com"
taihe_wechat="泰禾"
#extract email addresses now
email_all=open(email_db,'r').readlines()
email_lib={}
wechat_all=open(wechat_db,'r').readlines()
wechat_lib={}

for each in email_all:
    items=each.rstrip().rsplit()
    email_lib[items[0]]=items[1]

for each in wechat_all:
    items=each.rstrip().rsplit()
    wechat_lib[items[0]]=items[1]
#task for sunday
task_all = open(fushibiao,'r').readlines()
#task for friday
task_all_friday = open(fushibiao_friday,'r').readlines()

#dates (today, this Friday, next weekend, in two weekends, in three weekends)
today_date=datetime.date.today() #today's date
weekend_date=datetime.timedelta(days=(6-today_date.weekday()))+today_date
next_weekend_date=datetime.timedelta(days=(6-today_date.weekday()+7))+today_date
next_next_weekend_date=datetime.timedelta(days=(6-today_date.weekday()+7+7))+today_date
friday_date=datetime.timedelta(days=(4-today_date.weekday())+7*int(today_date.weekday()>4))+today_date
#month,date and year of next weekend
weekend_date_month,weekend_date_day,weekend_date_year=weekend_date.month,weekend_date.day,weekend_date.year
friday_date_month,friday_date_day,friday_date_year=friday_date.month,friday_date.day,friday_date.year

people_next_task=[]
people_next1_task=[]
people_next2_task=[]
people_next_task_friday=[]
people_one_month_sunday=[]
people_one_month_Friday=[]
#date formate like this dd/mm/year, e.g. 4/5/2018 represents May 4th in 2018. 04/05/2018 will not be reconized! Remove redundant 0 from the month and day.

for i in range(len(task_all[1:])):#skip the first label row
    each=task_all[1:][i]
    items=each.rstrip().rsplit()
    if items[0].split('/')==[str(weekend_date_day),str(weekend_date_month),str(weekend_date_year)]:
        people_next_task=items[1:]
        people_next1_task=task_all[1:][i+1].rstrip().rsplit()[1:]
        people_next2_task=task_all[1:][i+2].rstrip().rsplit()[1:]
        if not send_month_task:
            break
    else:
        if items[0].split('/')[1:]==[str(which_month),str(which_year)]:
            date_temp=items[0][0:-5].split("/")
            people_one_month_sunday.append(['{0}月{1}日'.format(date_temp[1],date_temp[0])]+items[1:])
        else:
            pass

bible_study_learn_chapter=None
for each in task_all_friday[1:]:#skip the first row of labelling
    items=each.rstrip().rsplit()
    if items[0].split('/')==[str(friday_date_day),str(friday_date_month),str(friday_date_year)]:
        people_next_task_friday=items[1:5]+items[6:8]
        bible_study_learn_chapter=items[5]
        if not send_month_task:
            break
    else:
        if items[0].split('/')[1:]==[str(which_month),str(which_year)]:
            date_temp=items[0][0:-5].split("/")
            people_one_month_Friday.append(['{0}月{1}日'.format(date_temp[1],date_temp[0])]+items[1:8])
        else:
            pass
if people_one_month_sunday!=[]:
    temp=np.array(people_one_month_sunday).transpose()
    index=np.array(['日期','领诗','司乐','音控','司会','圣餐','讲道','茶点','打扫','接待','儿童','助手'])[:,np.newaxis]
    people_one_month_sunday=np.append(index,temp,axis=1)
    column_num=people_one_month_sunday.shape[1]
    #print "column number=",column_num
    #print people_one_month_sunday[0,:]
    people_one_month_sunday_formated=''
    if column_num==6:
        for each in people_one_month_sunday:
            people_one_month_sunday_formated+='{:15}{:15}{:15}{:15}{:15}{:15}\n'.format(each[0],each[1],each[2],each[3],each[4],each[5])
    elif column_num==5:
        for each in people_one_month_sunday:
            people_one_month_sunday_formated+='{:15}{:15}{:15}{:15}{:15}\n'.format(each[0],each[1],each[2],each[3],each[4])
    elif column_num==4:
        for each in people_one_month_sunday:
            people_one_month_sunday_formated+='{:15}{:15}{:15}{:15}\n'.format(each[0],each[1],each[2],each[3])
    elif column_num==3:
        for each in people_one_month_sunday:
            people_one_month_sunday_formated+='{:15}{:15}{:15}\n'.format(each[0],each[1],each[2])
    elif column_num==2:
        for each in people_one_month_sunday:
            people_one_month_sunday_formated+='{:15}{:15}\n'.format(each[0],each[1])
    people_one_month_sunday=people_one_month_sunday_formated
if people_one_month_Friday!=[]:
    temp=np.array(people_one_month_Friday).transpose()
    index=np.array(['日期','领诗','司乐','带领1','带领2','经文','茶点','打扫'])[:,np.newaxis]
    people_one_month_Friday=np.append(index,temp,axis=1)
    column_num=people_one_month_Friday.shape[1]
    people_one_month_Friday_formated=''
    if column_num==6:
        for each in people_one_month_Friday:
            people_one_month_Friday_formated+='{:15}{:15}{:15}{:15}{:15}{:15}\n'.format(each[0],each[1],each[2],each[3],each[4],each[5])
    if column_num==5:
        for each in people_one_month_Friday:
            people_one_month_Friday_formated+='{:15}{:15}{:15}{:15}{:15}\n'.format(each[0],each[1],each[2],each[3],each[4])
    if column_num==4:
        for each in people_one_month_Friday:
            people_one_month_Friday_formated+='{:15}{:15}{:15}{:15}\n'.format(each[0],each[1],each[2],each[3])
    elif column_num==3:
        for each in people_one_month_Friday:
            people_one_month_Friday_formated+='{:15}{:15}{:15}\n'.format(each[0],each[1],each[2])
    elif column_num==2:
        for each in people_one_month_Friday:
            people_one_month_Friday_formated+='{:15}{:15}\n'.format(each[0],each[1])
    people_one_month_Friday=people_one_month_Friday_formated
#function to extract personal info for Sunday
extract_info=lambda info_list:[info_list[3],info_list[4],info_list[0],info_list[5],info_list[1],info_list[2],info_list[6],info_list[7],info_list[8],info_list[9],info_list[10]]

#person for Friday
lingshi_friday=people_next_task_friday[0]
siyue_friday=people_next_task_friday[1]
leader_friday=people_next_task_friday[2:4]
learn_chapter=bible_study_learn_chapter
chadian_friday=people_next_task_friday[4]
clean_up=people_next_task_friday[5]

#email address being sent from
#FROM = "andrewsfchai@gmail.com"
FROM = email_address_sender
#email adresses to send to
TO=[]
TO_friday=[]
TO_wechat=[]
TO_friday_wechat=[]
for each in people_next_task:
    if (each in email_lib.keys()) and (email_lib[each] not in TO):
        TO.append(email_lib[each])
        if each!="无":
            TO_wechat.append(wechat_lib[each])

for each in people_next_task_friday:
    if (each in email_lib.keys()) and (email_lib[each] not in TO_friday):
        TO_friday.append(email_lib[each])
        if each!="无":
            TO_friday_wechat.append(wechat_lib[each])
if wechat_lib["蔡师母"] not in TO_wechat:
    TO_wechat.append(wechat_lib["蔡师母"])
if wechat_lib["蔡师母"] not in TO_friday_wechat:
    TO_friday_wechat.append(wechat_lib["蔡师母"])
#subject and body
SUBJECT = "周末敬拜（%s）服侍提醒!"%(weekend_date.isoformat())
SUBJECT_friday = "周五查经（%s）服侍提醒!"%(friday_date.isoformat())

TEXT_friday = """大家好,

请注意你在这周五查经中有服侍任务:
经文学习:%s
领诗:%s
司乐:%s
带查经:%s and %s
茶点:%s
清场:%s

也许你发现服侍的日期有调动，这是有原因的，请体谅，也请按新的服侍表当值。若有困难，请联系蔡师母。

Thanks,

蔡师母"""%(learn_chapter,lingshi_friday,siyue_friday,leader_friday[0],leader_friday[1],chadian_friday,clean_up)

TEXT = """大家好,

请注意你在这周末主日崇拜中有服侍任务:
司会:%s
圣餐:%s
领诗:%s
证道:%s
司乐:%s
音控:%s
茶点:%s
打扫:%s
接待:%s
儿童主日学:%s and %s

也许你发现服侍的日期有调动，这是有原因的，请体谅，也请按新的服侍表当值。若有困难，请联系蔡师母。

Thanks,

蔡师母"""%tuple(extract_info(people_next_task))

TEXT_to_taihe = """Hi 泰禾,

下两周的服侍安排如下:
Date:%s
司会:%s
圣餐:%s
领诗:%s
证道:%s
司乐:%s
音控:%s
茶点:%s
打扫:%s
接待:%s
儿童主日学:%s and %s

Date:%s
司会:%s
圣餐:%s
领诗:%s
证道:%s
司乐:%s
音控:%s
茶点:%s
打扫:%s
接待:%s
儿童主日学:%s and %s

Thanks,

蔡师母"""%tuple([next_weekend_date.isoformat()]+extract_info(people_next1_task)+[next_next_weekend_date.isoformat()]+extract_info(people_next2_task))

if debug:
    print "Now running this program in debug mode! That means not sending message to anyone, but just display the message on screen!"
# Prepare actual message
message = """Subject: %s From: %s To: %s

%s
""" % (SUBJECT,FROM, ", ".join(TO), TEXT)

message_to_taihe = """Subject: %s From: %s To: %s

%s
""" % ("Workship service for next two weekends",FROM, taihe_email_address, TEXT_to_taihe)

message_friday = """Subject: %s From: %s To: %s

%s
""" % (SUBJECT_friday,FROM, ", ".join(TO_friday), TEXT_friday)

# Send the mail
if not debug:
    username = str(email_address_sender)
    password = str(password_of_your_email)
    server = smtplib.SMTP("smtp.gmail.com",587,timeout=10)
    server.set_debuglevel(1)
    server.starttls()
    server.login(username,password)
    if send_message_Sunday:
        try:
            if "amyclwong@gmail.com" in TO:
                server.sendmail(FROM, TO, message)
            else:
                server.sendmail(FROM, TO+["amyclwong@gmail.com"], message)
            server.sendmail(FROM, [taihe_email_address]+["amyclwong@gmail.com"], message_to_taihe)
            print ("The reminder e-mails of weekend workship service were sent !")
        except:
            print ("Failure to send the reminder e-mails of weekend workship service!")
    if send_message_Friday:
        try:
            if "amyclwong@gmail.com" in TO_friday:
                server.sendmail(FROM, TO_friday, message_friday)
            else:
                server.sendmail(FROM, TO_friday+["amyclwong@gmail.com"], message_friday)
            print ("The reminder e-mails of Friday Bible study workship service were sent !")
        except:
            print ("Failure to send the reminder e-mails of Friday Bible study workship service!")
    server.quit()
if debug:
    if send_message_Sunday:
        print(message)
        print('\nMessage sent to Taihe:')
        print(message_to_taihe)
    if send_message_Friday:
        print(message_friday)
    if send_month_task:
        print '{0}月主日崇拜服侍表'.format(which_month).decode("utf8")
        print(people_one_month_sunday.decode("utf8"))
        print '{0}月周五查经服侍表'.format(which_month).decode("utf8")
        print(people_one_month_Friday.decode("utf8"))
        with open("month_task.txt","w") as text_file:
            text_file.write('{0}月主日崇拜服侍表\n'.format(which_month))
            text_file.write(people_one_month_sunday)
            text_file.write("\n")
            text_file.write('{0}月周五查经服侍表\n'.format(which_month))
            text_file.write(people_one_month_Friday)
if send_wechat_msg and (not debug):
    if send_month_task:
        temp_group=bot.search("基督徒团契".decode("utf8"))[0]
        with open("month_task.txt","w") as text_file:
            text_file.write('{0}月主日崇拜服侍表\n'.format(which_month))
            text_file.write(people_one_month_sunday)
            text_file.write("\n")
            text_file.write('{0}月周五查经服侍表\n'.format(which_month))
            text_file.write(people_one_month_Friday)
        temp_group.send_msg('{0}月主日崇拜和周五查经服侍表'.format(which_month).decode("utf8"))
        temp_group.send_file("month_task.txt")
        #temp_group.send_msg(people_one_month_sunday.decode("utf8"))
        #temp_group.send_msg('{0}月周五查经服侍表'.format(which_month).decode("utf8"))
        #temp_group.send_msg(people_one_month_Friday.decode("utf8"))
        temp_group.send_msg("有需要调整的服侍人员，请联系蔡师母！".decode("utf8"))
    if send_message_Sunday:
        for each in TO_wechat:
            try:
                temp_friend=bot.search(each.decode("utf8"))[0]
                temp_friend.send_msg(TEXT.decode("utf8"))
                print "Sunday worship reminder Message to %s is sent via Wechat!"%(each.decode("utf8"))
            except:
                print "Failure to send Sunday worship reminder message to %s via Wechat!"%(each.decode("utf8"))
        #wechat message to Taihe
        try:
            temp_friend=bot.search(taihe_wechat.decode("utf8"))[0]
            temp_friend.send_msg(TEXT_to_taihe.decode("utf8"))
            print "Message to %s is sent via Wechat!"%(taihe_wechat)
        except:
            print "Failure to send Message to %s via Wechat!"%(taihe_wechat)
    if send_message_Friday:
        for each in TO_friday_wechat:
            try:
                temp_friend=bot.search(each.decode("utf8"))[0]
                temp_friend.send_msg(TEXT_friday.decode("utf8"))
                print "Friday bible study reminder Message to %s is sent via Wechat!"%(each.decode("utf8"))
            except:
                print "Failure to send Friday bible study reminder message to %s via Wechat!"%(each.decode("utf8"))
