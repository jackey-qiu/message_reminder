#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib,random
from lxml import etree
import datetime,time
import pandas as pd
import numpy as np
import calendar
import smtplib
from email.mime.text import MIMEText
from wxpy import *
# import getpass
# from access_google_sheet import from_google_sheet_to_txt
# from docx import Document
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from emoji import emojize
import sys,os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsScene
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from util import *
try:
    from . import locate_path
except:
    import locate_path
msg_path = locate_path.module_path_locator()
# msg_path = os.path.dirname(os.path.dirname(script_path))

class MyMainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(MyMainWindow, self).__init__(parent)
        #pg.mkQApp()
        uic.loadUi(os.path.join(msg_path,'ui_bible_reading_reminder.ui'),self)
        self.setWindowTitle('Daily Bible reading reminder')
        self.bible_today_tag = ""
        self.today_date = None
        self.picked_date = None
        self.plan_lookup_table = None
        self.scripture_extracted = None
        self.image_reminder = None
        self.web_site = None
        self.wechat_group = []
        self.book_coor_lib = None
        self.bible_reading_plan = os.path.join(msg_path,"bible_reading_plan_kiel.txt")
        self.scripture_today_tag = {}
        self.scripture_today = {}
        self.bot = Bot()
        self.dateEdit.setDate(QDate.currentDate())
        self.pushButton_extract.clicked.connect(self.extract_scripture)
        self.pushButton_send.clicked.connect(self.send_wechat)
        self.pushButton_load.clicked.connect(self.load_scripture)

    def send_wechat(self):
        self.bot.file_helper.send_image(os.path.join(msg_path,"base_img_revised.jpg"))
        self.bot.file_helper.send_msg(self.message)
        if self.lineEdit_group_names.text()!="":
            for friend in self.lineEdit_group_names.text().rsplit(","):
                temp_group=self.bot.search(friend)[0]
                temp_group.send_msg(self.message)
                temp_group.send_image(os.path.join(msg_path,"base_img_revised.jpg"))
        
    def load_scripture(self):
        scripture_tag = self.lineEdit_scripture.text().rsplit(";")
        self.scripture_today = {}
        for i in range(len(scripture_tag)):
            self.scripture_today[i] = scripture_tag[i] 
        self.extract_scripture_from_website()
        self.textBrowser.setText("\n".join(self.scripture_extracted))

    def extract_scripture(self):
        self.get_date_today()
        self.key_today = "/".join([str(self.dateEdit.date().month()),str(self.dateEdit.date().day())])
        self.today_date = (str(self.dateEdit.date().month()),str(self.dateEdit.date().day()))
        self.create_bible_reading_lib()
        self.get_scripture_today_tag()
        self.extract_scripture_from_website()
        self.lineEdit_scripture.setText(";".join([str(each) for each in self.scripture_today.values()]))
        self.textBrowser.setText("\n".join(self.scripture_extracted))
        self.prepare_scripture_proverb()
        self.prepare_image_reminder()

    def get_date_today(self):
        self.today_date = (str(datetime.date.today().month), str(datetime.date.today().day))
        self.key_today = "/".join(self.today_date)

    def create_bible_reading_lib(self):
        bible_reading = open(self.bible_reading_plan,'r').readlines()[1:]
        self.textEdit_plan.setText("".join(bible_reading))
        bible_reading_lib={}
        for each in bible_reading:
            items=each.rstrip().rsplit()
            bible_reading_lib[items[0]]=items[1:]
        self.bible_reading_lib = bible_reading_lib

    def get_scripture_today_tag(self):
        self.scripture_today = {}
        self.scripture_today["oldtestament"]=self.bible_reading_lib[self.key_today][0]
        self.scripture_today["newtestament"]=self.bible_reading_lib[self.key_today][1]

    def extract_scripture_from_website(self):
        temp_scripture_holder = []
        for bible_today_tag in self.scripture_today.values():
            if bible_today_tag != "-":
                book,chapter_verse = bible_today_tag.rsplit(",")
                print(chapter_verse)
                chapters,verse=chapter_verse.rsplit(':')
                book=book_corr_lib[book]
                chapters_boundary=list(map(int,chapters.rsplit('-')))
                if len(chapters_boundary)==2:
                    chapters=range(chapters_boundary[0],chapters_boundary[1]+1)
                elif len(chapters_boundary)==1:
                    chapters=range(chapters_boundary[0],chapters_boundary[0]+1)
                verse=verse.rsplit("-")
                if verse[0]!="*":
                    verse=[int(verse[0]),int(verse[1])]
                for chapter in chapters:
                    #print "Chapter {} of {}\n".format(chapter,book)
                    temp_scripture_holder.append("Chapter {} of {}\n".format(chapter,book))
                    sock=urllib.request.urlopen("http://www.chinesebibleonline.com/book/{0}/{1}".format(book,chapter))
                    htmlsource=sock.read()
                    sock.close()
                    s1=etree.HTML(htmlsource)
                    text_whole_chapter=s1.xpath('//*[@id="page_container"]/div[2]/div[position() mod2=0]/span/text()')
                    text_whole_chapter=[each for each in text_whole_chapter]
                    if verse[0]=="*":
                        for i in range(len(text_whole_chapter)):
                            #print i+1,text_whole_chapter[i]
                            temp_scripture_holder.append('{0}.{1}'.format(i+1,text_whole_chapter[i]))
                    else:
                        for i in range(verse[0]-1,verse[1]):
                            #print i+1,text_whole_chapter[i]
                            temp_scripture_holder.append("{0}.{1}".format(i+1,text_whole_chapter[i]))
                self.scripture_extracted = temp_scripture_holder

    def send_wechat_group(self):
        for friend in self.wechat_group:
            temp_group=bot.search(friend)[0]
            temp_group.send_msg(self.message)
            temp_group.send_image("base_img_revised.jpg")

    def prepare_scripture_proverb(self):
        cv_p=chapter_verse_proverbs[random.randint(0,31)]
        sock=urllib.request.urlopen("http://www.chinesebibleonline.com/book/{0}/{1}".format("Proverbs",cv_p[0]))
        htmlsource=sock.read()
        sock.close()
        s1=etree.HTML(htmlsource)
        text_whole_chapter=s1.xpath('//*[@id="page_container"]/div[2]/div[position() mod2=0]/span/text()')
        self.scripture_proverb=[each for each in text_whole_chapter][cv_p[1]-1].rstrip()

    def prepare_image_reminder(self):
        line1=alignment(("本周2020年%s月%s日读经章节"%tuple(self.today_date)), 28, align = 'center')
        line2=alignment(("*"*22), 28, align = 'center')
        line3=alignment(("旧约：%s"%tuple([self.scripture_today["oldtestament"].replace(":*","")])), 28, align = 'center')
        line4=alignment(("新约：%s"%tuple([self.scripture_today["newtestament"].replace(":*","")])), 28, align = 'center')
        line5=alignment(("*"*28), 28, align = 'center')
        line6=self.scripture_proverb
        num_end=int(len(line6)/2-1)
        if len(line6)>=num_end:
            #print(len(line6),num_end)
            line6=alignment(line6[0:(len(line6)-num_end)], 28, align = 'center')+u"\n"+alignment((line6[(len(line6)-num_end):]), 28, align = 'center')
            line7=alignment("(:祝大家读经愉快:)", 28, align = 'center')
        line8=alignment(("*"*22), 28, align = 'center')
        TEXT="\n".join([line1,line2,line3,line4,line5,line6,line7,line8])
        self.message = TEXT
        img = Image.open(os.path.join(msg_path,"base_images/winter/base_img{0}.jpg".format(self.today_date[1])))
        if img.size!=(640,1136):
            img=img.resize((640,1136))
        _ = ImageDraw.Draw(img)
        font = ImageFont.truetype("/Library/Fonts/Microsoft/JingDianKaiTiJian-1.ttf", 32)
        poly_size = (1000,570)
        poly_offset = (0,0)
        poly = Image.new('RGBA', poly_size )
        pdraw = ImageDraw.Draw(poly)
        pdraw.polygon([ (0,0),  (1000,0),(1000,570), (0,570)],
                      fill=(0,0,200,100), outline=None)
        pdraw.text((95, 50),TEXT,(256,256,256),font=font)
        img.paste(poly, poly_offset, mask=poly)
        img.save(os.path.join(msg_path,"base_img_revised.jpg"))
        self.scene = QGraphicsScene()
        self.pixmap = QPixmap(os.path.join(msg_path,"base_img_revised.jpg"))
        self.scene.addPixmap(self.pixmap)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        #item[, aspectRadioMode=Qt.IgnoreAspectRatio]
        self.graphicsView.show()


if __name__ == "__main__":
    QApplication.setStyle("windows")
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())