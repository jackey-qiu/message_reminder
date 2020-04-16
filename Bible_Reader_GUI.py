#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import urllib,random
from urllib.parse import quote
import string
from lxml import etree
import datetime,time
import numpy as np
import calendar
import smtplib
from email.mime.text import MIMEText
from wxpy import *
# import getpass
# from access_google_sheet import from_google_sheet_to_txt
# from docx import Document
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
print(msg_path)
# msg_path = os.path.dirname(os.path.dirname(script_path))
bible_books = \
['创世记',
 '出埃及记',
 '利未记',
 '民数记',
 '申命记',
 '约书亚记',
 '士师记',
 '路得记',
 '撒母耳记上',
 '撒母耳记下',
 '列王纪上',
 '列王纪下',
 '历代志上',
 '历代志下',
 '以斯拉记',
 '尼希米记',
 '以斯帖记',
 '约伯记',
 '诗篇',
 '箴言',
 '传道书',
 '雅歌',
 '以赛亚书',
 '耶利米书',
 '耶利米哀歌',
 '以西结书',
 '但以理书',
 '何西阿书',
 '约珥书',
 '阿摩司书',
 '俄巴底亚书',
 '约拿书',
 '弥迦书',
 '那鸿书',
 '哈巴谷书',
 '西番雅书',
 '哈该书',
 '撒迦利亚书',
 '玛拉基书',
 '马太福音',
 '马可福音',
 '路加福音',
 '约翰福音',
 '使徒行传',
 '罗马书',
 '哥林多前书',
 '哥林多后书',
 '加拉太书',
 '以弗所书',
 '腓立比书',
 '歌罗西书',
 '帖撒罗尼迦前书',
 '帖撒罗尼迦后书',
 '提摩太前书',
 '提摩太后书',
 '提多书',
 '腓利门书',
 '希伯来书',
 '雅各书',
 '彼得前书',
 '彼得后书',
 '约翰一书',
 '约翰二书',
 '约翰三书',
 '犹大书',
 '启示录']

class MyMainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(MyMainWindow, self).__init__(parent)
        #pg.mkQApp()
        uic.loadUi(os.path.join(msg_path,'ui_bible_reading_reminder_new.ui'),self)
        self.setWindowTitle('Bible Reader')
        sock = urllib.request.urlopen("http://mobile.chinesebibleonline.com/bible")  
        self.html_overview = etree.HTML(sock.read())
        sock.close()

        url_overview_ds = "https://www.24en.com/novel/religion/streams-in-the-desert.html"
        sock = urllib.request.urlopen(url_overview_ds)
        self.html_overview_ds = etree.HTML(sock.read())
        sock.close()

        self.bible_today_tag = ""
        self.today_date = None
        self.spring_desert_date = None
        self.total_chapter = 1189
        self.old_testimony = 929
        self.reading_plan = ['4_2_2','2'][0]
        self.speed = 2
        self.first_day_in_plan = None 
        self.comboBox_book.clear()
        self.comboBox_book.addItems(bible_books)
        self.update_count_down_time()
        self.get_spring_desert_article()

        #signal-slot-pair connection
        self.calendarWidget.selectionChanged.connect(self.get_spring_desert_article)
        self.pushButton_today.clicked.connect(self.get_scripture_for_today)
        self.pushButton_specified.clicked.connect(self.get_scripture_specified)
        self.pushButton_load.clicked.connect(self.load_all_notes)
        self.pushButton_save.clicked.connect(self.save_notes)
        self.spinBox_start_date.valueChanged.connect(self.update_count_down_time)
        self.spinBox_start_month.valueChanged.connect(self.update_count_down_time)
        self.comboBox_book.currentIndexChanged.connect(self.set_bible_book)
        self.comboBox_plan.currentIndexChanged.connect(self.update_reading_plan)


    def get_scripture_specified(self):
        chapter_content = []
        book = self.lineEdit_book.text()
        if book not in bible_books:
            for each in bible_books:
                if sum([int(each_charater in each) for each_charater in book])==len(book):
                    book = each
                    break
        #assert book in bible_books,'something is wrong about typed book name!'
        # book = 'Genesis'
        chapters_bounds = [int(each) for each in self.lineEdit_book_chapter.text().rsplit('-')]
        chapters = range(chapters_bounds[0],chapters_bounds[1]+1)
        for chapter in chapters:
            url = quote("http://mobile.chinesebibleonline.com/book/{}/{}".format(book,chapter),safe=string.printable)
            sock_temp =urllib.request.urlopen(url)
            html_temp = etree.HTML(sock_temp.read())
            sock_temp.close()
            book_name = ["\n《{}》第{}章\n".format(book,chapter)]
            try:
                scriptures = html_temp.xpath("/html/body/div[2]/div/span[2]/text()")
                verse_number = html_temp.xpath("/html/body/div[2]/div/span[1]/text()")
                combined = [verse_number[ii].rstrip()+scriptures[ii]+'\n' for ii in range(len(scriptures))]
                chapter_content = chapter_content + book_name + combined
            except:
                pass
        self.textBrowser_bible.clear()
        cursor = self.textBrowser_bible.textCursor()
        cursor.insertHtml('''<p><span style="color: blue;size:15;">{} <br></span>'''.format(" "))
        self.textBrowser_bible.setText(''.join(chapter_content)) 
        

    def get_scripture_for_today(self):
        books = []
        chapters = []
        method = self.reading_plan.rsplit("_")
        print(method)
        if len(method)==1:
            speed = int(method[0])
        elif len(method)==3:
            speed_old = int(method[1])
            speed_new = int(method[2])
        if 'speed' in locals().keys():
            # self.speed = speed
            num_nodes_book =  len(self.html_overview.xpath("/html/body/div[2]/ul/div")) 
            acc_chapters = 0
            node_index = []
            book_names = []
            start_chapter_index = []
            end_chapter_index = []
            target_chapters = speed*(int(self.total_chapter/speed)+[1,0][int((self.total_chapter%speed)==0)]-int(self.lineEdit_count_down.text()))
            print('target_chapters',target_chapters,speed)
            for i in range(num_nodes_book):
                current_book_length = len(self.html_overview.xpath("/html/body/div[2]/ul/div[{}]/ul/li".format(i+1)))
                acc_chapters+= current_book_length
                if acc_chapters>target_chapters:
                    #book_names.append(self.html_overview.xpath("/html/body/div[2]/ul/div"))
                    node_index.append(i+1)
                    start_chapter_index.append(target_chapters - (acc_chapters - current_book_length) + 1)
                    end_chapter_index_= start_chapter_index[-1] + speed
                    if end_chapter_index_>current_book_length:
                        end_chapter_index.append(current_book_length+1)
                        end_chapter_index.append(end_chapter_index_ - current_book_length)
                        start_chapter_index.append(1)
                        if len(self.html_overview.xpath("/html/body/div[2]/ul/div[{}]/ul/li".format(i+2)))==0:
                            node_index.append(i+3)
                        else:
                            node_index.append(i+2)
                    else:
                        end_chapter_index.append(end_chapter_index_)
                    break
            print(node_index,start_chapter_index,end_chapter_index) 
            chapter_content = []
            for i in range(len(node_index)):
                each_node_index = node_index[i]
                start, end = start_chapter_index[i], end_chapter_index[i]
                for j in range(start, end):
                    try:
                        url_tail = self.html_overview.xpath("/html/body/div[2]/ul/div[{}]/ul/li[{}]/a/@href".format(each_node_index,j))[0]
                    except:
                        url_tail = self.html_overview.xpath("/html/body/div[2]/ul/div[{}]/ul/li[{}]/a/@href".format(each_node_index+1,j))[0]
                    print(url_tail)
                    url = "http://mobile.chinesebibleonline.com{}".format(url_tail)
                    sock_temp =urllib.request.urlopen(url)
                    html_temp = etree.HTML(sock_temp.read())
                    sock_temp.close()
                    book_name = ["\n《{}》第{}章\n".format(html_temp.xpath("/html/body/div[2]/div[1]/text()")[0],j)]
                    try:
                        scriptures = html_temp.xpath("/html/body/div[2]/div/span[2]/text()")
                        verse_number = html_temp.xpath("/html/body/div[2]/div/span[1]/text()")
                        combined = [verse_number[ii].rstrip()+scriptures[ii]+'\n' for ii in range(len(scriptures))]
                        chapter_content = chapter_content + book_name + combined
                    except:
                        pass
            self.textBrowser_bible.clear()
            chapter_content = ['------------------------------------------------------------------------------------------------------------------------------------------------\n'] + chapter_content
            cursor = self.textBrowser_bible.textCursor()
            cursor.insertHtml('''<p><span style="color: blue;size:15;">{} <br></span>'''.format(" "))
            #for each in chapter_content:
            #    each=each+'\n'
            #    cursor = self.textBrowser_bible.textCursor()
            #    cursor.insertHtml('''<p><span style="color: blue;size:15;">{} <br></span>'''.format(each))
            self.textBrowser_bible.setText(''.join(chapter_content)) 

    def get_spring_desert_article(self):
        selected_date = self.calendarWidget.selectedDate().toPyDate()
        y,m,d = selected_date.year, selected_date.month, selected_date.day
        url = self.html_overview_ds.xpath('/html/body/div[2]/div[4]/div[1]/div[2]/div[{}]/ul/li/a/@href'.format(int(m)*2))[int(d)-1]
        sock = urllib.request.urlopen(url)
        html = etree.HTML(sock.read())
        sock.close()
        content = html.xpath('/html/body/div[2]/div[4]/div/div[4]/div[2]/p/text()')
        self.textBrowser.clear()
        for each in content:
            each=each+'\n'
            cursor = self.textBrowser.textCursor()
            cursor.insertHtml('''<p><span style="color: green;size:15;">{} <br></span>'''.format(each))
        # self.textBrowser.setText('\n'.join(content))

    def update_reading_plan(self):
        plan = self.comboBox_plan.currentText()
        if plan == "一日四章（新旧各两章）":
            self.reading_plan = '4-2-2'
            self.speed = 4
        elif plan == "一天两章（顺序）":
            self.reading_plan = '2'
            self.speed = 2

    def update_count_down_time(self):
        start_month = int(self.spinBox_start_month.value())
        start_date = int(self.spinBox_start_date.value())
        start_year = int(datetime.date.today().year)
        start = datetime.date(start_year, start_month, start_date)
        count_down =  int(self.total_chapter/self.speed)+[1,0][int((self.total_chapter%self.speed)==0)] - (datetime.date.today()-start).days
        self.lineEdit_count_down.setText(str(count_down))


    def set_bible_book(self):
        self.lineEdit_book.setText(self.comboBox_book.currentText())

    def save_notes(self):
        notes_path = os.path.join(msg_path,'Bible_reader_notes.txt')
        y,m,d = datetime.date.today().year, datetime.date.today().month, datetime.date.today().day
        if self.plainTextEdit.toPlainText()!='':
            if not os.path.exists(notes_path):
                with open(notes_path,'w') as f:
                    f.write("{}月{}月{}日\n".format(y,m,d))
                    f.write(self.plainTextEdit.toPlainText())
            else:
                with open(notes_path,'a+') as f:
                    f.write("{}月{}月{}日\n".format(y,m,d))
                    # f.write("{}-{}-{}\n".format(y,m,d))
                    f.write(self.plainTextEdit.toPlainText())
        else:
            pass

    def load_all_notes(self):
        notes_path = os.path.join(msg_path,'Bible_reader_notes.txt')
        # self.save_notes()
        if os.path.exists(notes_path):
            with open(notes_path,'r') as f:
                self.plainTextEdit.setPlainText("".join(f.readlines()))
        else:
            pass



if __name__ == "__main__":
    QApplication.setStyle("windows")
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())