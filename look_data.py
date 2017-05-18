import argparse, os, time 
import urllib.parse, random 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys 
from bs4 import BeautifulSoup
from mongoengine import *
from selenium.webdriver.support.ui import Select
import urllib.parse, random 
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
import itertools
import random
from pymongo import MongoClient
import re

def fiter(p):
    try:
        money = int(str(p['money'][0]['money'])[1:].replace(',',''))
    except:
        money = 1000
    if money > 20 and len(list(p['webs']))>0:
        return True
    else:
        return False
def Main(db): 

    print(db.database_names())
    print(db['linkedin_db'].collection_names())
    print(db['linkedin_db'].people.find_one())
    print(db['linkedin_db'].people.count())
    for p in db['linkedin_db'].people.find():
        print(p)


if __name__ == '__main__':
    db = connect('linkedin_db')
    Main(db)
