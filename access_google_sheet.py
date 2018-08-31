#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np

#install oauth2client and gspread using pip install
#before run this program you must enable google drive and google sheet api on your google cloud console platform
#create a new project as your wish
#navigate to APIs&Service Dashboard
#On top left, enable APIS (google drive and google sheet)
#click Credentials panel
#click Create credentials-->Service account key-->New service account-->name it-->select a role (usually Project-->Editor)
#select JSON key type, and click Create
#The Json credential file is created
#open the file using a text editor, find the line starting with "client_email", and copy the email after the key word
#Go you your google sheet platform, open one sheet file you want to get access to, click share, and paste the email address you just copy
#Now you are ready to run the following scripts

def from_google_sheet_to_txt(g_file_name="persons",save_file=["file.txt"],sheet_tag=["sheet1"],jason_credential_file="Worship-arrangement-DD-1005ad7eaf1f.json"):
    if type(sheet_tag)!=type([]):
        sheet_tag=[].append(sheet_tag)
    if type(save_file)!=type([]):
        save_file=[].append(save_file)
    google_sheet_file_name=g_file_name#name of your google sheet file
    which_sheet=sheet_tag#tag name of the sheet, you may have several sheets
    jason_key_file=jason_credential_file#credential info in json format you saved
    #scope for google sheet and google drive api (it may change, just google it if so)
    scope=['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    credentials=ServiceAccountCredentials.from_json_keyfile_name(jason_key_file,scope)
    gc=gspread.authorize(credentials)
    table=gc.open(google_sheet_file_name.decode("utf8"))
    wks_list=[table.worksheet(each) for each in sheet_tag]
    for ii in range(len(wks_list)):
        wks=wks_list[ii]
        col_lables=wks.row_values(1)
        values=np.array(col_lables)[np.newaxis,:][0:0]
        for i in range(2,wks.row_count+1):
            if wks.row_values(i)!=[]:
                values=np.append(values,np.array(wks.row_values(i))[np.newaxis,:],axis=0)
            else:
                break
        #table information in pandas dataframe format
        table_df=pd.DataFrame(values,columns=col_lables)
        table_df.to_csv(path_or_buf=save_file[ii],sep="\t",encoding="utf8",index=False)
