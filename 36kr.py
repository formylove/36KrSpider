#-*- coding:utf-8 -*-
import requests
import re
import selenium
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import sqlite3
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def save_news(article):
    sql = f'''
    insert into
    news(profile, title, summary, content, position, date) 
    values('{article.profile}', '{article.title}', '{article.summary}',
     '{article.content}', {article.position}, '{article.date}')
    '''
    conn = sqlite3.connect("news.sqlite3")
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()

def get_article(url,article):
    r=requests.get(url,headers=headers)
    b=BeautifulSoup(r.text)
    if b.find(id='app') is None or b.find(id='app').next_sibling is None or b.find(id='app').next_sibling.next_sibling.string.find('"title"')==-1 or b.find(id='app').next_sibling.next_sibling.string.find('"content"')==-1:
        return False
    else:
      text=b.find(id='app').next_sibling.next_sibling.string
      article.title = text[text.index('"title":"')+9:text.index('"catch_title"')-2]
      article.content = text[text.index('"content":"') + 11:text.index('"cover"') - 2]
      article.summary=text[text.index('"summary":"')+11:text.index('"content"')-2]
      return True
class Article:

    def __init__(self,profile,position):
        now = datetime.datetime.now()
        self.profile=profile;
        self.position=position
        self.title='';
        self.content=''
        self.summary=''
        self.date=str(now.month).rjust(2,'0')+str(now.day).rjust(2,'0')

    def __str__(self):
        return f'title {self.title}\nsummary {self.summary}\ncontent {self.content}\nprofile {self.profile}\ndate {self.date}'

headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
# br=webdriver.Chrome(r'C:\Users\A\Desktop\chromedriver_win32\chromedriver.exe')

br=webdriver.PhantomJS()
br.get("http://36kr.com")
js = "window.scrollTo(0,document.body.scrollHeight);"
time.sleep(1)
br.execute_script(js)
bs=BeautifulSoup(br.page_source)

sliders =   bs.find_all(attrs={"data-stat-click":re.compile("^youxuanrongzi")})
recommend = bs.find(class_='pc_list').find_all(attrs={"data-stat-click":re.compile("^bainjituijian")})
latest  =   bs.find_all(attrs={"data-stat-click":re.compile("^latest.zhufeed.wenzhangtupian")},limit=2)
newsletter =bs.find_all(attrs={"data-stat-click":re.compile("^kuaixunmokuai.kuaixunbiaoti")})

# assert len(sliders)==5

#滑动
re_img_url=re.compile(r'^background-image: url\("?([^"]+)"?\)')
for s in sliders:
    if s.find('span',class_="mark") is not None:continue
    img_url=re_img_url.match(s.get('style')).group(1)
    a = Article(img_url,1)
    if get_article(s.get('href'),a):
        save_news(a)
        print(a)
#推荐
for r in recommend:
    img_url=r.find('img').get('src')
    a = Article(img_url,2)
    if get_article(r.find('a').get('href'),a):
        save_news(a)
        print(a)

#最新
ll=['https://pic.36krcnd.com/201808/21144209/eph9ny3d28wp1qg5!heading','https://pic.36krcnd.com/201808/15064838/7aksyug3rlh6ehon']
for l in latest:
    # wait = WebDriverWait(br,40)
    # wait.until(lambda s: s.find_element(By.XPATH, '//@class="load-img fade"[1]').get_attribute('src') != None and s.find_element(By.XPATH, '//@class="load-img fade"[2]').get_attribute('src') != None and s.find_element(By.XPATH, '//@class="load-img fade"[3]').get_attribute('src') != None)
    br.execute_script(js)
    img_url=l.find('img').get('src')
    a = Article(img_url,3)
    if a.profile is None:a.profile=ll.pop()
    if get_article('http://36kr.com'+l.get('href'),a):
        save_news(a)
        print(a)

# 快讯
for nl in newsletter:
    a = Article('',4)
    a.title=nl.string
    a.summary=list(nl.parent.next_sibling.strings)[0]
    print(a)
    save_news(a)

#r = requests.get('http://36kr.com/',headers=headers)
#r.encoding='utf-8'
#print(r.cookies['example_cookie_name'])

