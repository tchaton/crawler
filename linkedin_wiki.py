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

def get_schools(browser):
    schools = []
    acronyms = []
    wikis = ["https://fr.wikipedia.org/wiki/Liste_des_%C3%A9coles_d'ing%C3%A9nieurs_en_France"]                     
    for wiki in wikis:
        browser.get(wiki) 
        page = BeautifulSoup(browser.page_source, "html.parser") 
        j = 1
        numbers = [str(i) for i in range(210)]
        for td in page.find_all('td'):
            if td.text in numbers:
                j=1
            j+=1
            if j == 4:
                try:
                    schools.append(td.text)
                except:
                    continue
            if j == 5:
                try:
                    if td.text != '':
                        acronyms.append(td.text)
                except:
                    continue
    return acronyms

def get_people(page):
    links = [] 
    for link in page.find_all('a'): 
        url = link.get('href') 
        if url: 
            if 'profile/view?id=' in url and '&trk=nav_responsive_tab_profile' not in url and url not in links:
                links.append(url)
    return links 
    
def extract_data(page):
    data = {}
    Skills = []
    websites = []
    name = '0' 
    job = '0'
    past= '0'
    linkedin = '0' 
    actual = '0'
    edu = '0'
    email='0'
    try:
        name = page.find('span',attrs={"class":'full-name'}).text
    except:
       name = '0' 
    try:
        job = page.find('p',attrs={"class":'title'}).text
    except:
        job = '0'
    try:
        linkedin  = page.find('a',attrs={"class":'view-public-profile'}).get('href') 
    except:
        linkedin = '0'
    for skill in page.find_all("li"):
        try:
            nb = skill.find('span',attrs={"class":'num-endorsements'}).text
            comp = skill.find('span',attrs={"class":'endorse-item-name-text'}).text
            Skills.append([nb,comp]) 
        except:
            continue
    try:
        tmp = page.find('tr',attrs={"id":'overview-summary-current'})
        for a in tmp.find_all('a'):
            if 'curr_pos' in str(a.get('href')):
                actual = str(a.text)
                break
    except:
        actual = '0'
    try:
        tmp = page.find('tr',attrs={"id":'verview-summary-past'})
        for a in tmp.find_all('a'):
            if 'prev_pos' in str(a.get('href')):
                past = str(a.text)
                break
    except:
        past = '0'
    try:
        tmp = page.find('tr',attrs={"id":'overview-summary-education'})
        for a in tmp.find_all('a'):
            if 'school' in str(a.get('href')):
                edu = str(a.text)
                break
    except:
        edu = '0'
    try:
        for a in page.find_all('a'):
            if 'mailto' in str(a.get('href')):
                email = a.get('href')
    except:
        email = '0'
    try:
        for a in page.find_all('a'):
            if '/redir/redirect?' in str(a.get('href')) and 'linkedin' not in str(a.get('href')):#and 'twitter' in str(a.get('href')):
                websites.append(str(a.get('href')))
    except:
        websites.append('0')
        #nb = skill.find('span',attrs={"class":'num-endorsements'}).text
        #comp = skill.find('span',attrs={"class":'endorse-item-name-text'}).text
        #Skills.append([nb,comp])
    websites.append('0')
    print(websites,email)
    data['name']=name
    data['job']=job
    data['linkedin']=linkedin
    data['email']=str(email)
    data['actual']=str(actual)
    data['edu']=str(edu)
    data['past']=str(past)
    data['Skills']=[]
    for skill in Skills:
        data['Skills'].append(skill)
    data['websites']=[]
    for web in websites:
        data['websites'].append(web)     
    return data

def save_data(data,people_link):
    keys = [key for key in data.keys()]
    link = StringField(primary_key=True)
    name = data['name']
    job = data['job']
    linkedin = data['linkedin']
    email = data['email']
    actual = data['actual']
    past = data['past']
    edu = data['edu']
    Skills = data['Skills']
    websites = data['websites']
    people = People(link=people_link,name=name,email=email,job=job,linkedin=linkedin,actual=actual,past=past,edu=edu)
    for skill in Skills:
        people.skills.append(Skill(nb=skill[0],skill=skill[1]))
    for web in websites:
        try:
            people.webs.append(Website(web=str(web)))
        except:
            continue
    print(people)
    people.save()

class Skill(EmbeddedDocument):
    nb = StringField()
    skill = StringField(max_length=120)

class Website(EmbeddedDocument):
    web = StringField(max_length=500)

class People(Document):
    link = StringField(primary_key=True)
    name = StringField(max_length=100)
    email = StringField(max_length=100)
    job = StringField(max_length=200)
    linkedin = StringField(max_length=100)
    actual = StringField(max_length=100)
    past = StringField(max_length=100)
    edu = StringField(max_length=200)
    linkedin = StringField(max_length=100)
    skills = ListField(EmbeddedDocumentField(Skill))
    webs = ListField(EmbeddedDocumentField(Website))


def next_page_link(first_link,pos):
    return first_link[:-1]+str(pos+1)

def firstlink(page):
    url = 0
    for a in page.find_all("a", class_="page-link"):
        url = a.get('href')
        break
    time.sleep(random.uniform(0.5,3))
    return url

def filter_people_link(people_link):
    url = people_link.split('&')[0].split('=')[-1]
    print(url)
    return url
def create_ip(ip_tuple):
    return str(ip_tuple[0])+'.'+str(ip_tuple[1])+'.'+str(ip_tuple[2])+'.'+str(ip_tuple[3])

def ip_range(input_string):
    octets = input_string.split('.')
    parsed_ranges = [list(map(int, octet.split('-'))) for octet in octets]
    ranges = [range(r[0], r[1] + 1) if len(r) == 2 else r for r in parsed_ranges]
    addresses = itertools.product(*ranges)
    return [create_ip(ip_tuple) for ip_tuple in addresses]

def ViewBot(browser,acronyms,opt): 
    visited = {} 
    pList = [] 
    count = 0 
    root_link ='https://www.linkedin.com'
    #ips = [address for address in ip_range('192.168.1-50.1-50')]
    #ports = [i for i in range(2000,20000) if i%2==0]
    for acro in acronyms:
        pos = 1
        print(acro)
        wait = WebDriverWait(browser, 10)
        wait.until(EC.element_to_be_clickable((By.ID,'main-search-box'))) 
        try:
            search_input = browser.find_element_by_id('main-search-box')
        except NoSuchElementException:
            continue
        try:
            select = Select(browser.find_element_by_id('main-search-category'));
            for option in select.options:
                if option.text == opt:
                    select.select_by_visible_text(option.text)
        except NoSuchElementException:
            continue
        search_input.clear()
        search_input.send_keys(acro)
# 
        search_form = browser.find_element_by_id('global-search')
        search_form.submit()
        time.sleep(random.uniform(2.5,4)) 
        page = BeautifulSoup(browser.page_source, "html.parser")
        first_link = firstlink(page)
        print(first_link)
        ## BEGINNING
        while True:
            time.sleep(random.uniform(1.5,3)) 
            page_total = BeautifulSoup(browser.page_source, "html.parser")
            for i,people_link in enumerate(get_people(page_total)):
                if i%2==0:
                    #browser = ChangeProxy_test(browser,random.choice(ips),random.choice(ports))
                    browser.get(people_link)
                    time.sleep(random.uniform(1.5,3)) 
                    try:
                        browser.find_element_by_id("contact-info-tab").click()
                        time.sleep(random.uniform(1.5,3))
                        print('info')
                    except :
                        pass
                    page = BeautifulSoup(browser.page_source, "html.parser")
                    data = extract_data(page)
                    save_data(data,filter_people_link(people_link))
            pos+=1
            next_p = next_page_link(first_link,pos)
            print(next_p)
            try:
                browser.get(root_link+next_p)
            except:
                break

def ChangeProxy(ProxyHost ,ProxyPort):
    print("Define Firefox Profile with you ProxyHost and ProxyPort")
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.http", ProxyHost )
    profile.set_preference("network.proxy.http_port", int(ProxyPort))
    profile.update_preferences()
    return webdriver.Firefox(firefox_profile=profile)


def FixProxy(webdriver):
    print("Reset Firefox Profile")
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 0)
    return webdriver.Firefox(firefox_profile=profile)


def Main(): 

    parser = argparse.ArgumentParser() 
    parser.add_argument("email", help="linkedin email") 
    parser.add_argument("password", help="linkedin password") 
    args = parser.parse_args() 
    
    ProxyHost = "54.84.95.51" 
    ProxyPort = "8083"

    browser = ChangeProxy(ProxyHost,ProxyPort)
    schools_names = get_schools(browser)
    browser.get("https://linkedin.com/uas/login") 
    print(dir(browser))
 
    emailElement = browser.find_element_by_id("session_key-login") 
    emailElement.send_keys('mr.ribault@gmail.com')
    passElement = browser.find_element_by_id("session_password-login") 
    passElement.send_keys('la banane')
    passElement.submit() 
 
    os.system('clear') 
    print("[+] Success! Logged In, Bot Starting!") 
    ViewBot(browser,schools_names,'Personnes') 
    browser.close() 
 
if __name__ == '__main__':
    connect('linkedin_db')
    Main()
