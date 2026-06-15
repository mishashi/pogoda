from webdriver_manager.chrome import ChromeDriverManager
from email.message import EmailMessage
from bs4 import *
import smtplib
import random
import requests
import json
import os
from pathlib import Path
from datetime import *
from dotenv import load_dotenv
'''from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
options = Options()
options.add_argument("--no-sandbox")
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#driver = webdriver.Chrome(options=options)'''
print('go')
ms = []
#with open('htmltext.txt','r') as f:

base_dir = Path(__file__).parent.parent.parent   # поднимаемся из run/ в корень
env_path = base_dir / '.env'

load_dotenv(dotenv_path=env_path)
nm = os.getenv('EMAIL')
pwd = os.getenv('EMAIL_KEY')

TO = [{'Москва':['donotreply.pogoda@outlook.com']},{'Москва':['donotreply.pogoda@outlook.com']}]
#poses = {"Москва":"/moscow",'Самара':'/samara','Лыткарино':'/lytkarino','Сочи':'?lat=43.58547211&lon=39.72309875','Волгоград':'lat=48.70706558&lon=44.5169754'}
now = datetime.now()


def send_mail(city,to,text,title='Погода в городе '):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(nm, pwd)
    for t in to:
        em = EmailMessage()
        em.set_content(text)
        em["To"] = t
        em["From"] = nm
        em["Subject"] = title+city
        server.send_message(em)
    print('send mail')
    server.quit()

def to_file(data, city):
    base = "/home/sg/projects/pogoda/run/fact"
   # base = "C:/users/gogov/duck"
    data = json.dumps({now.isoformat():data}, ensure_ascii=False)
    pth = Path(f"{base}/{city}/{str(now.year)+str(now.month)}")
    if not pth.exists():
        pth.mkdir(parents=True)
        '''for a,b in TO[1].items():
            now2 = now-timedelta(days=1)
            with open(f'{base}/{city}/{str(now2.year)+str(now2.month)}/{str(now2.day)}.txt') as f:
                send_mail(a,b,f.read())'''
    with open(f"{base}/{city}/{str(now.year)+str(now.month)}/{str(now.day)}.txt", "a", encoding="utf-8") as f:
        #print('ga',file=f)
        r = random.randint(0,4000)
        if city in TO[1] and r % 1 == 0:
            send_mail(city,TO[1][city],data)
        #print(data[79])
        f.write(data)
        f.write('\n')

def parse(pos):
    resp = requests.get(f'https://yandex.ru/pogoda/ru{pos}').content
    soup1 = BeautifulSoup(resp, "html.parser")
    a = BeautifulSoup(str(soup1.find('article')),'html.parser').find_all('p')
    descr = a[0].get_text()
    temp = a[1].get_text()[:-1]
    x = soup1.find_all('span',{'class':"AppFact_warning__first_text___wtkV" })[0].get_text()
    if len(x.split('.')) > 1:
        sky = x.split('.')[0]
    else:
        sky = x.split('законч')[0]
    pres = soup1.find_all('li',{'class':"AppFact_details__item__QFIXI"})[1].get_text()
    return [descr,sky,temp,pres]
poses = {"Москва":"/moscow",'Самара':'/samara',
         'Лыткарино':'/lytkarino',"Подольск":"/podolsk",
         "Химки":"/himki","Королёв":"/korolev",
         'Сочи':'/sochi',"Анапа":"/anapa","Дербент":"/derbent",
         "Ярославль":"?lat=57.62656021&lon=39.89381409","Калуга":"/kaluga",
         'Волгоград':'/volgograd',"Санкт-Петербург":"/saint-petersburg",
         "Екатеринбург":"/yekaterinburg","Пермь":"/perm","Казань": "/kazan",
    "Нижний Новгород": "/nizhny-novgorod",
    "Владивосток": "/vladivostok",
    "Мурманск": "/murmansk",
    "Новосибирск": "/novosibirsk",
    "Красноярск": "/krasnoyarsk",
    "Новый Уренгой": "/noviy-urengoy",
    "Омск": "/omsk",
    "Рязань": "/ryazan",
    "Тверь": "/tver",
    "Якутск": "/yakutsk",
    "Краснодар": "/krasnodar",
    "Ростов-на-Дону": "/rostov-na-donu",
    "Пятигорск": "/pyatigorsk",
    "Иркутск": "/irkutsk",
"Киров": "/kirov",
"Севастополь": "/sevastopol",
"Челябинск": "/chelyabinsk",
"Уфа": "/ufa",
"Магадан": "/magadan",
"Астрахань": "/astrakhan",
"Петропавловск-Камчатский": "/petropavlovsk",
"Воронеж": "/voronezh",
"Калининград": "/kaliningrad",
"Сургут": "/surgut"}
res = {}
for (city,p) in poses.items():
    print(city,p)
    ya = parse(p)
    to_file(ya,city)
print(res)
#driver.quit()
