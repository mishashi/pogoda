import random
print('start')
from webdriver_manager.chrome import ChromeDriverManager
from email.message import EmailMessage
from bs4 import *
import smtplib
import json
from pathlib import Path
from datetime import *
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#driver = webdriver.Chrome(service=Service("./chromedriver"), options=options)
#driver = webdriver.Chrome(options=options)
nm = "noreply.pogoda@gmail.com"
pwd = "dwzs ecwy swts nijl"
ct = ['Самара', 'Лыткарино', 'Подольск', 'Химки', 'Королёв', 'Сочи', 'Анапа', 'Дербент', 'Ярославль', 'Калуга', 'Волгоград', 'Санкт-Петербург', 'Екатеринбург', 'Пермь']
with open('l.log','a') as f:
    f.write('ddd')
TO = [{'Москва':['donotreply.pogoda@outlook.com']},{'Москва':['donotreply.pogoda@outlook.com'],random.choice(ct):['donotreply.pogoda@outlook.com'],random.choice(ct):['donotreply.pogoda@outlook.com']}]

def error(e,d,i,p):
    print(e,d,i,p)

def yandex_parser(pos):
    now = datetime.now()
    today = date.today()
    driver.get(f"https://yandex.ru/pogoda/ru{pos}")
    soup1 = BeautifulSoup(driver.page_source, "html.parser")
    a = soup1.find("ul",{"class":"MainPage_appForecast__5mP3d"})
    #print(a)
    soup = BeautifulSoup(str(a),"html.parser")
    print(len(soup.find_all("li")))
    day = today
    res = []
    for d in soup.find_all("li"):
        spd = BeautifulSoup(str(d),"html.parser")
        sh = spd.find("p")
        if sh is None:
            continue
        ms = spd.find_all("div",{"class":"AppForecastDayPart_temp__kKbJG"})
        mso = spd.find_all("div", {"class": "AppForecastDayPart_showWide__hsoFN"})
        morning_sky = mso[0].get_text()
        morning_temp = ms[0].get_text()[:-1]
        day_sky = mso[1].get_text()
        day_temp = ms[1].get_text()[:-1]
        evening_sky = mso[2].get_text()
        evening_temp = ms[2].get_text()[:-1]
        night_sky = mso[3].get_text()
        night_temp = ms[3].get_text()[:-1]
        #print(day_temp,night_temp,day_sky,day)
        short_describtion = sh.get_text()
        res.append({day.isoformat():[short_describtion,morning_temp,morning_sky,day_temp,day_sky,evening_temp,evening_sky,night_temp,night_sky]})
        day = day + timedelta(days=1)

    a2 = soup1.find_all("ul")[4]#,{"class":"AppHourly_list__gXAeN"})
    #print(a2)
    a3 = BeautifulSoup(str(a2),"html.parser").find_all("li")
    nd = False
    res2 = []
    for i in a3:
        sp = BeautifulSoup(str(i),"html.parser")
        #print(sp)
        tm = sp.find("time")
        if not tm:
            nd = True
            continue
        tm = tm.get_text()
        x = sp.find_all("p")
        x1 = x[0].get_text()
        descr = x[1].get_text()
        if "Закат" in x1 or "Восход" in x1:
            continue
        temp = x1[:-1]
        res2.append({tm:[nd,temp,descr]})
    #
    res = {now.isoformat():{"hours":res2,"days":res}}
    return res

def gismeteo_parser(pos):
    today = date.today()
    now = datetime.now()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    days = ["", "tomorrow", "3-day", "4-day", "5-day", "6-day", "7-day", "8-day", "9-day", "10-day"]
    res = []
    di = today
    for i in days:
        driver.get(f"https://www.gismeteo.ru/weather-{pos}/{i}")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        a1 = str(soup.find("div", {"class": "widget-body"}))
        a2 = BeautifulSoup(a1, "html.parser")
        sky = []
        a22 = a2.find_all('div', {'class': 'row-item'})
        cnt = 0
        for tag in a22:
            if cnt < 8 and 'data-tooltip' in tag.attrs:
                cnt += 1
                sky.append(tag.attrs['data-tooltip'])
        temps = a2.find_all("temperature-value")[1:9]
        temps = list(map(lambda x: x.get_text(), temps))
        prs = a2.find_all("pressure-value")[1:9]
        prs = list(map(lambda x: x.get_text(), prs))
        a3 = str(a2.find("div", {"data-row": "humidity"}))
        vlazhs = BeautifulSoup(a3, "html.parser").find_all("div")[1:]
        vlazhs = list(map(lambda x: x.get_text(), vlazhs))
        if not temps:
            error("Не найдена темпреатура", di, i, pos)
        if not sky:
                error("Не найдено состояние небо", di, i, pos)
        if temps and vlazhs and prs:
            res.append({di.isoformat(): {"t": temps,'s':sky, "p": prs, "v": vlazhs}})
        print(di)
        di = di + timedelta(days=1)
    res = {now.isoformat(): res}
    return res

def world_weather_parser(pos):
    now = datetime.now()
    today = date.today()
    driver.get(f"https://world-weather.ru/pogoda/russia/{pos}/10days/")
    soup1 = BeautifulSoup(driver.page_source, "html.parser")
    a1 = soup1.find_all("tbody")[1:]
    day = today
    res = []
    for i in a1:
        a2 = BeautifulSoup(str(i), "html.parser").find_all("tr")
        dw = {}
        for j in a2:
            sp = BeautifulSoup(str(j), "html.parser")
            td = sp.find_all("td")
            type = td[0].get_text()
            temp = td[1].get_text()[:-1]
            sky = sp.find("div")["title"]
            ver_osadki = td[3].get_text()
            press = td[4].get_text()
            vlazh = td[6].get_text()
            dw[type] = [temp, sky, ver_osadki, press, vlazh]
        res.append({day.isoformat(): dw})
        day = day + timedelta(days=1)
    res = {now.isoformat(): res}
    return res

def mail_pogoda_parser(pos):
    today = date.today()
    now = datetime.now()
    driver.get(f"https://pogoda.mail.ru/prognoz/{pos}/extended/")
    soup1 = BeautifulSoup(driver.page_source, "html.parser")
    a1 = soup1.find_all('div',{'class':'p-flex_content_justify'})
    day = today
    res = []
    for i in a1:
        a2 = BeautifulSoup(str(i), "html.parser").find_all('div',{'class':'p-flex__column'})[:4]
        w = {}
        #print(a2[0])
        for j in a2:
            td = BeautifulSoup(str(j), "html.parser").find_all('span')
            #print(td)
            type = td[0].get_text()
            temp = td[2].get_text()[:-1]
            sky = td[3].get_text()
            ver_osadki = td[-1].get_text()
            press = td[5].get_text()[:3]
            vlazh = td[8].get_text()
            w[type] = [temp,sky,ver_osadki,press,vlazh]
        res.append({day.isoformat():w})
        day = day + timedelta(days=1)
    res = {now.isoformat(): res}
    return res

def meteoinfo_parser(pos):
    now = datetime.now()
    today = date.today()
    driver.get(f"https://meteoinfo.ru/forecasts/russia/{pos}")
    soup1 = BeautifulSoup(driver.page_source, "html.parser")
    a1 = soup1.find_all("tbody")[3]
    print(a1)
    sp2 = BeautifulSoup(str(a1), "html.parser")
    day = today
    res = []
    if '/moscow' in pos:
        ms = sp2.find_all("i")
        for i in range(len(ms)):
            if i % 6 == 0:
                res.append({day.isoformat(): [ms[i].get_text()]})
            if i % 3 == 1 or i % 6 == 3:
                res[-1][day.isoformat()].append(ms[i].get_text())
            if i % 6 == 5:
                day = day + timedelta(days=1)
    else:
        ms = sp2.find_all("span")
        day = today

        for i in range(len(ms)):
            if i > 2:
                t = ms[i].get_text()[:-1]
                if t[0].isdigit():
                    t = '+'+t
                if i % 2 == 1:
                    res.append({day.isoformat(): [t]})
                else:
                    res[-1][day.isoformat()].append(t)
                    day = day + timedelta(days=1)
    res = {now.isoformat(): res}
    print(res)
    return res

def send_mail(to,text,title = "Прогноз погоды"):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(nm, pwd)
    for t in to:
        em = EmailMessage()
        em.set_content(text)
        em["To"] = t
        em["From"] = nm
        em["Subject"] = title
        print(t,nm,text)
        server.send_message(em)
    server.quit()

def to_file(data, city, dir):
    base = "/home/sg/projects/pogoda/run"
    #base = "C:/users/gogov/duck"
    dt = datetime.fromisoformat(list(data.keys())[0])
    data = json.dumps(data, ensure_ascii=False)
    yap = Path(f"{base}/{dir}/{str(dt.year)+str(dt.month)}/{str(dt.day)}")
    print(dt,yap)
    yap.mkdir(parents=True,exist_ok=True)
    with open(f"{base}/{dir}/{str(dt.year)+str(dt.month)}/{str(dt.day)}/{city}.txt", "a", encoding="utf-8") as f:
        print(data, file=f)

def mk_otchet(city,ya,ww,mr,mi,gm):
    ans = 'Gismeteo: '+str(gm)
    ans += '\nYandex: '+str(ya)
    ans += '\nWorld-weather: '+str(ww)
    ans += '\nMeteoinfo: '+str(mi)
    ans +=  '\nMail.ru: '+str(mr)
    if city in TO[1]:
        send_mail(TO[1][city],ans,title = 'Прогноз погоды для города '+city)

def main():
    poses = {"Москва":["/moscow","moscow","moskva","moscow-area/moscow"],
             "Самара":["/samara","samara","samara","samara-area/samara"],
             "Санкт-Петербург":["/saint-petersburg","saint_petersburg","sankt_peterburg","leningrad-region/sankt-peterburg"],
             "Лыткарино":["/lytkarino","lytkarino","lytkarino",None],
             "Химки":["?lat=55.88936234&lon=37.44485474","khimki_1","khimki",None],
             "Подольск":["?lat=55.43113708&lon=37.54499817","podolsk","podolsk",None],
             "Королёв":["?lat=55.91895294&lon=37.81521225","korolev","korolev",None],
             "Сочи":["?lat=43.58547211&lon=39.72309875","sochi","sochi",None],
             "Анапа":["?lat=44.89426804&lon=37.31690598","anapa","anapa","krasnodar-territory/anapa"],
             "Дербент":["?lat=42.05767059&lon=48.2887764","derbent","derbent","republic-dagestan/derbent"],
             "Волгоград":["?lat=48.70706558&lon=44.5169754","volgograd","volgograd","volgograd-area/volgograd"],
             "Ярославль":["?lat=57.62656021&lon=39.89381409","yaroslavl","yaroslavl","yaroslavl-area/jaroslavl"],
             "Калуга":["?lat=54.5136795&lon=36.26134109","kaluga","kaluga","kaluga-area/kaluga-A"],
             "Пермь":["?lat=58.01045609&lon=56.2294426","perm","perm","perm-area/perm"],
             "Екатеринбург":["?lat=56.83743668&lon=60.59763718","yekaterinburg","ekaterinburg","sverdlovsk-area/ekaterinburg"]}
    gisposes = {"Москва":"moscow-4368","Санкт-Петербург":"sankt-peterburg-4079","Самара":"samara-4618",
                "Лыткарино":"lytkarino-12640","Химки":"khimki-11582","Подольск":"podolsk-11955","Королёв":"korolev-11404",
                "Сочи":"sochi-5233","Анапа":"anapa-5211","Дербент":"derbent-5268",
                "Волгоград":"volgograd-5089","Ярославль":"yaroslavl-4313","Калуга":"kaluga-4387",
                "Екатеринбург":"yekaterinburg-4517","Пермь":"perm-4476"}

    res = {}
    for (city,p) in poses.items():
        ya = yandex_parser(p[0])
        to_file(ya,city,'yandexpogoda')
        ww = world_weather_parser(p[1])
        to_file(ww,city,'worldweather')
        mr = mail_pogoda_parser(p[2])
        to_file(mr,city,'pogodamailru')
        if p[3] is not None:
            print(city,p)
            mi = meteoinfo_parser(p[3])
            to_file(mi,city,'meteoinfo')
        else:
            mi = 'Нет прогноза для города '+city
        res[city] = [ya,ww,mr,mi]
    for (city,pos) in gisposes.items():
        gm = gismeteo_parser(pos)
        res[city].append(gm)
        to_file(gm, city, 'gismeteo')
    for i in poses.keys():
        mk_otchet(i,*res[i])
main()
#meteoinfo_parser('samara-area/samara')

driver.quit()

