from webdriver_manager.chrome import ChromeDriverManager
from email.message import EmailMessage
from bs4 import *
import smtplib
import random
import json
from pathlib import Path
from datetime import *
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
options = Options()
options.add_argument("--no-sandbox")
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#driver = webdriver.Chrome(options=options)
print('gp')
ms = []
#with open('htmltext.txt','r') as f:

nm = "noreply.pogoda@gmail.com"
pwd = "dwzs ecwy swts nijl"
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
    driver.get(f'https://yandex.ru/pogoda/ru{pos}')
    soup1 = BeautifulSoup(driver.page_source, "html.parser")
    a = BeautifulSoup(str(soup1.find('article')),'html.parser').find_all('p')
    descr = a[0].get_text()
    temp = a[1].get_text()[:-1]
    x = a[2].get_text()
    if len(x.split('.')) > 1:
        sky = x.split('.')[0]
    else:
        sky = x.split('законч')[0]
    pres = soup1.find_all('p',{'class':'AppRangeWithSpace_chart__description__a9Wnh AppRangeWithSpace_chart__description_small__nq8nx'})[1].get_text()
    return [descr,sky,temp,pres]
poses = {"Москва":"/moscow",'Самара':'/samara',
         'Лыткарино':'/lytkarino',"Подольск":"?lat=55.43113708&lon=37.54499817",
         "Химки":"?lat=55.88936234&lon=37.44485474","Королёв":"?lat=55.91895294&lon=37.81521225",
         'Сочи':'?lat=43.58547211&lon=39.72309875',"Анапа":"?lat=44.89426804&lon=37.31690598","Дербент":"?lat=42.05767059&lon=48.2887764",
         "Ярославль":"?lat=57.62656021&lon=39.89381409","Калуга":"?lat=54.5136795&lon=36.26134109",
         'Волгоград':'?lat=48.70706558&lon=44.5169754',"Санкт-Петербург":"/saint-petersburg",
         "Екатеринбург":"?lat=56.83743668&lon=60.59763718","Пермь":"?lat=58.01045609&lon=56.2294426",}
res = {}
for (city,p) in poses.items():
    print(city,p)
    ya = parse(p)
    to_file(ya,city)
print(res)
