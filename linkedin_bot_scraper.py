import argparse, os, time 
import urllib.parse, random 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys 
from bs4 import BeautifulSoup
from mongoengine import *

class Url(Document):
    link = StringField(primary_key=True)

class User(Document):
    link = StringField(primary_key=True)

    email = StringField(max_length=50)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    
def getPeopleLinks(page): 
    links = [] 
    for link in page.find_all('a'): 
        url = link.get('href') 
        if url: 
            if 'profile/view?id=' in url:
                links.append(url)
    return links 
 
def getJobLinks(page): 
    links = [] 
    for link in page.find_all('a'): 
        url = link.get('href') 
        if url:         
            if '/jobs' in url: 
                links.append(url) 
    return links 
 
def getID(url): 
    pUrl = urllib.parse.urlparse(url) 
    return urllib.parse.parse_qs(pUrl.query)['id'][0]
def People():

 
def ViewBot(browser): 
    visited = {} 
    pList = [] 
    count = 0 
    while True: 
        #sleep to make sure everything loads, add random to make us look human. 
        time.sleep(random.uniform(2.5,6)) 
        page = BeautifulSoup(browser.page_source, "html.parser") 
        people = getPeopleLinks(page) 
        if people: 
            for person in people: 
                ID = getID(person) 
                if ID not in visited: 
                    pList.append(person) 
                    visited[ID] = 1 
        if pList: #if there is people to look at look at them 
            person = pList.pop() 
            browser.get(person)
            Url(link=person.split('&')[0]).save()
            count += 1 
        else: #otherwise find people via the job pages 
            jobs = getJobLinks(page) 
            if jobs: 
                job = random.choice(jobs) 
                root = 'http://www.linkedin.com' 
                roots = 'https://www.linkedin.com' 
                if root not in job or roots not in job: 
                    job = 'https://www.linkedin.com'+job 
                browser.get(job) 
            else: 
                print("I'm Lost Exiting") 
                break 
 
        #Output (Make option for this)
        linkedin_profile = browser.current_url.split("?")[0]
        print("[+] "+browser.title+ " " + linkedin_profile + " Visited! \n(" +str(count)+"/"+str(len(pList))+") Visited/Queue)") 
                     
 
def Main(): 
    parser = argparse.ArgumentParser() 
    parser.add_argument("email", help="linkedin email") 
    parser.add_argument("password", help="linkedin password") 
    args = parser.parse_args() 
 
    browser = webdriver.Firefox() 
 
    browser.get("https://linkedin.com/uas/login") 
 
 
    emailElement = browser.find_element_by_id("session_key-login") 
    emailElement.send_keys(args.email)
    passElement = browser.find_element_by_id("session_password-login") 
    passElement.send_keys(args.password)
    passElement.submit() 
 
    os.system('clear') 
    print("[+] Success! Logged In, Bot Starting!") 
    ViewBot(browser) 
    browser.close() 
 
if __name__ == '__main__':
    connect('linkedin_db')
    Main()
