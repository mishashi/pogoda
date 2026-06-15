import random
print('start')
from email.message import EmailMessage
from bs4 import *
import requests
import smtplib
import json
from pathlib import Path
from datetime import *
import os
import sys
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from web.backend.use_bd import subscribe_dict,newlog,last_mail_log_ts
TO2 = subscribe_dict()
SYSTEM_ID = 3

print(TO2)

newlog(SYSTEM_ID,'Run','Запущен парсинг сайтов погоды')

base_dir = Path(__file__).parent.parent
env_path = base_dir / '.env'

load_dotenv(dotenv_path=env_path)
nm = os.getenv('EMAIL')
pwd = os.getenv('EMAIL_KEY')

ct = ['Самара', 'Лыткарино', 'Подольск', 'Химки', 'Королёв', 'Сочи', 'Анапа', 'Дербент', 'Ярославль', 'Калуга', 'Волгоград', 'Санкт-Петербург', 'Екатеринбург', 'Пермь',
    'Казань', 'Нижний Новгород', 'Владивосток', 'Мурманск', 'Новосибирск',
    'Красноярск', 'Новый Уренгой', 'Омск', 'Рязань', 'Тверь', 'Якутск',
    'Краснодар', 'Ростов-на-Дону', 'Пятигорск', 'Иркутск', 'Киров', 'Севастополь',
    'Челябинск', 'Уфа', 'Магадан', 'Астрахань', 'Петропавловск-Камчатский', 'Воронеж',
    'Калининград', 'Сургут']
TO = [{'Москва':['donotreply.pogoda@outlook.com']},{'Москва':['donotreply.pogoda@outlook.com'],random.choice(ct):['donotreply.pogoda@outlook.com'],random.choice(ct):['donotreply.pogoda@outlook.com']}]
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.gismeteo.ru/",
    "Upgrade-Insecure-Requests": "1"
        }

def error(e,d,i,p):
    print(e,d,i,p)

def yandex_parser(pos):
    now = datetime.now()
    today = date.today()
    resp = requests.get(f"https://yandex.ru/pogoda/ru{pos}", headers=headers).content
   # print(pos,'go')
    soup1 = BeautifulSoup(resp, "html.parser")
    a = soup1.find_all("ul")[-1]#,{"class":"MainPage_appForecast__5mP3d"})
    #print(a)
    #return
    soup = BeautifulSoup(str(a),"html.parser")
    #print(pos,len(soup.find_all("li")))
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
    #print(pos,res)
    a2 = soup1.find_all("ul")[-2]#,{"class":"AppHourly_list__gXAeN"})
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
    #print(res2)
    res = {now.isoformat():{"hours":res2,"days":res}}
    return res

def gismeteo_parser(pos):
    from datetime import date, datetime, timedelta
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time
    import requests
    from bs4 import BeautifulSoup

    today = date.today()
    now = datetime.now()
    days_suffixes = ["", "tomorrow", "3-day", "4-day", "5-day", "6-day", "7-day", "8-day", "9-day", "10-day"]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
    }

    def fetch_day(suffix, idx):
        url = f"https://www.gismeteo.ru/weather-{pos}/{suffix}"
        date_iso = (today + timedelta(days=idx)).isoformat()

        for attempt in range(3):
            try:
                resp = requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.content, "html.parser")
                widget = soup.find("div", {"class": "widget-body"})
                if not widget:
                    widget = soup.find("div", {"class": "weather-widget"})
                if not widget:
                    print(f"Не найден виджет для {pos}, {suffix}")
                    return None

                rows = widget.find_all('div', {'class': 'row-item'})
                sky = []
                for row in rows:
                    if 'data-tooltip' in row.attrs:
                        sky.append(row['data-tooltip'])
                        if len(sky) == 8:
                            break

                temp_vals = widget.find_all("temperature-value")
                if not temp_vals:
                    temp_vals = widget.find_all("span", class_="unit_temperature_c")
                if not temp_vals:
                    temp_vals = widget.find_all("div", class_="temp")
                temps = [t.get('value') or t.get_text().replace('°', '') for t in temp_vals[1:9]]

                press_vals = widget.find_all("pressure-value")
                if not press_vals:
                    press_vals = widget.find_all("span", class_="unit_pressure_mm_hg")
                pressures = [p.get('value') or p.get_text() for p in press_vals[1:9]]

                humidity_block = widget.find("div", {"data-row": "humidity"})
                if not humidity_block:
                    humidity_block = widget.find("div", class_="row-item humidity")
                humidity = []
                if humidity_block:
                    hum_divs = humidity_block.find_all("div")[1:]
                    humidity = [h.get_text(strip=True) for h in hum_divs]

                if not temps or not sky or len(temps) != len(sky):
                    print(f"Неполные данные для {pos}, {suffix}")
                    return None

                temps_clean = []
                for t in temps:
                    try:
                        temps_clean.append(str(int(t.replace('−', '-'))))
                    except:
                        temps_clean.append(t)

                return {date_iso: {"t": temps_clean, "s": sky, "p": pressures, "v": humidity}}

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                print(f"Сетевая ошибка {pos}/{suffix}, попытка {attempt+1}: {e}")
                time.sleep(2 ** attempt)  # 1, 2, 4 секунды
            except Exception as e:
                print(f"Ошибка парсинга {pos}/{suffix}: {e}")
                return None

        return None  

    # Параллельный запуск
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_idx = {
            executor.submit(fetch_day, suffix, idx): idx
            for idx, suffix in enumerate(days_suffixes)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                data = future.result()
                if data is not None:
                    results.append(data)
            except Exception as e:
                print(f"Непредвиденная ошибка для дня {idx}: {e}")

    results.sort(key=lambda x: list(x.keys())[0])
    return {now.isoformat(): results}


def world_weather_parser(pos):
    now = datetime.now()
    today = date.today()
    #driver.get(f"https://world-weather.ru/pogoda/russia/{pos}/10days/")
    resp = requests.get(f"https://world-weather.ru/pogoda/russia/{pos}/10days/", headers=headers).content
    #print(resp)
    soup1 = BeautifulSoup(resp, "html.parser")
    a1 = soup1.find_all("table")[1:]
    #print(a1)
    #return
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
    #print(res)
    return res

def mail_pogoda_parser(pos):
    today = date.today()
    now = datetime.now()
    #driver.get(f"https://pogoda.mail.ru/prognoz/{pos}/extended/")
    #print('!!!')
    resp = requests.get(f"https://pogoda.mail.ru/prognoz/{pos}/extended/").content
    soup1 = BeautifulSoup(resp, "html.parser")
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
    resp = requests.get(f"https://meteoinfo.ru/forecasts/russia/{pos}").content
    soup1 = BeautifulSoup(resp, "html.parser")
    a1 = soup1.find_all("table")[3]
    #print(len(a1))
    #print(*a1,sep='\n')
    #return
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
    #print(res)
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
       # print(t,nm,text)
        server.send_message(em)
    server.quit()

def to_file(data, city, dir):
    base = "/home/sg/projects/pogoda/run"
    #base = "C:/users/gogov/duck"
    dt = datetime.fromisoformat(list(data.keys())[0])
    data = json.dumps(data, ensure_ascii=False)
    if len(data) < 40:
        print('!!!!!', dir, city)
    yap = Path(f"{base}/{dir}/{str(dt.year)+str(dt.month)}/{str(dt.day)}")
    #print(dt,yap)
    yap.mkdir(parents=True,exist_ok=True)
    with open(f"{base}/{dir}/{str(dt.year)+str(dt.month)}/{str(dt.day)}/{city}.txt", "a", encoding="utf-8") as f:
        print(data, file=f)

def format_weather_message(city, gm_data, ya_data, ww_data, mr_data, mi_data):
    gm_root = gm_data[list(gm_data.keys())[0]]   # список дней
    ya_root = ya_data[list(ya_data.keys())[0]]   # {'days': [...], 'hours': [...]}
    ww_root = ww_data[list(ww_data.keys())[0]]   # список дней
    mr_root = mr_data[list(mr_data.keys())[0]]   # список дней
    if type(mi_data) != type(ya_data):
        mi_root = []
    else:
        mi_root = mi_data[list(mi_data.keys())[0]]   # список дней (Meteoinfo может быть короче)

    def get_date_from_str(date_str):
        return datetime.strptime(date_str, '%Y-%m-%d').date()

    # Собираем все даты из всех сервисов
    all_dates = set()
    for day in gm_root:
        all_dates.add(get_date_from_str(list(day.keys())[0]))
    for day in ww_root:
        all_dates.add(get_date_from_str(list(day.keys())[0]))
    for day in mr_root:
        all_dates.add(get_date_from_str(list(day.keys())[0]))
    if mi_root:
        for day in mi_root:
            all_dates.add(get_date_from_str(list(day.keys())[0]))
    # Yandex: даты в ya_root['days']
    for day in ya_root['days']:
        all_dates.add(get_date_from_str(list(day.keys())[0]))
    all_dates = sorted(all_dates)
    today = datetime.now().date()
    # Оставляем только будущие дни (включая сегодня, если ещё не прошло)
    future_dates = [d for d in all_dates if d >= today]
    # Ограничиваем 10 днями (обычно столько есть во всех сервисах)
    future_dates = future_dates[:10]

    # Вспомогательная функция для получения max/min температуры из данных сервиса
    def get_temp_range_from_ya(date):
        """Для Яндекс возвращает (min, max) из дневных температур"""
        for item in ya_root['days']:
            dt_str = list(item.keys())[0]
            if get_date_from_str(dt_str) == date:
                day_data = item[dt_str]
                # day_data = ['текст', 'утро_temp', 'утро_опис', 'день_temp', ...]
                temps = []
                for i in [1,3,5,7]:  # утро, день, вечер, ночь
                    val = day_data[i]
                    if val and val != '-':
                        temps.append(int(val.replace('−', '-')))
                return min(temps), max(temps) if temps else (None, None)
        return None, None

    def get_rain_from_ya(date):
        """Ожидаются ли осадки в Яндекс"""
        for item in ya_root['days']:
            if get_date_from_str(list(item.keys())[0]) == date:
                day_data = item[list(item.keys())[0]]
                # описание погоды днём
                desc = day_data[4]  # дневное описание
                return 'дождь' in desc.lower() or 'ливень' in desc.lower() or 'гроза' in desc.lower()
        return False


    def get_gm_data(date):
        for day in gm_root:
            dt_str = list(day.keys())[0]
            if get_date_from_str(dt_str) == date:
                return day[dt_str]  # словарь с ключами 't','s','p','v'
        return None

    def get_ww_data(date):
        for day in ww_root:
            dt_str = list(day.keys())[0]
            if get_date_from_str(dt_str) == date:
                return day[dt_str]  # словарь {'Ночь': [...], 'Утро': [...], ...}
        return None

    def get_mr_data(date):
        for day in mr_root:
            dt_str = list(day.keys())[0]
            if get_date_from_str(dt_str) == date:
                return day[dt_str]  # аналогично
        return None

    def get_mi_data(date):
        for day in mi_root:
            dt_str = list(day.keys())[0]
            if get_date_from_str(dt_str) == date:
                return day[dt_str]  # список строк, например ['22..24', 'описание', ...]
        return None

    # Формирование вывода
    lines = []
    lines.append(f"Прогноз погоды для города {city}\n")
    for i, date in enumerate(future_dates):
        date_str = date.strftime('%d.%m.%Y')
        lines.append(f"\n--- {date_str} ---")
        # Детализация для первых 3 дней
        detailed = i < 3

        # Gismeteo
        gm = get_gm_data(date)
        if gm:
            t_arr = gm['t']
            sky_arr = gm['s']
            pressure_arr = gm['p']
            humidity_arr = gm['v']
            if detailed:
                parts = ['Ночь', 'Утро', 'День', 'Вечер']
                lines.append("Gismeteo:")
                for idx, part in enumerate(parts):
                    if idx*2 < len(t_arr):
                        t = t_arr[idx*2] if idx*2 < len(t_arr) else '?'
                        sky = sky_arr[idx*2] if idx*2 < len(sky_arr) else '?'
                        p = pressure_arr[idx*2] if idx*2 < len(pressure_arr) else '?'
                        v = humidity_arr[idx*2] if idx*2 < len(humidity_arr) else '?'
                        lines.append(f"  {part}: {t}°C, {sky}, давление {p}, влажность {v.strip()}%")
            else:
                # кратко: макс/мин
                temps = [int(x.replace('−','-')) for x in t_arr]
                max_t = max(temps)
                min_t = min(temps)
                # наличие дождя: проверяем наличие слов 'дождь' в sky_arr
                rain = any('дождь' in s.lower() for s in sky_arr)
                rain_str = "🌧️ ожидается дождь" if rain else "☀️ без осадков"
                lines.append(f"Gismeteo: {min_t}…{max_t}°C, {rain_str}")

        # Yandex
        y_min, y_max = get_temp_range_from_ya(date)
        if y_min is not None:
            rain_ya = get_rain_from_ya(date)
            rain_str = "🌧️ дождь" if rain_ya else "☀️ ясно/облачно"
            lines.append(f"Yandex: {y_min}…{y_max}°C, {rain_str}")

        # World-weather
        ww = get_ww_data(date)
        if ww:
            temps = []
            rains = []
            for part in ['Ночь','Утро','День','Вечер']:
                if part in ww:
                    data = ww[part]
                    t = int(data[0].replace('−','-'))
                    temps.append(t)
                    if 'дождь' in data[1].lower() or 'ливень' in data[1].lower():
                        rains.append(True)
                    else:
                        rains.append(False)
            if detailed:
                lines.append("World-weather:")
                for part in ['Ночь','Утро','День','Вечер']:
                    if part in ww:
                        data = ww[part]
                        t = data[0]
                        sky = data[1]
                        prob = data[2]
                        press = data[3]
                        hum = data[4]
                        lines.append(f"  {part}: {t}°C, {sky}, в/о {prob}, давление {press} мм, влажн. {hum}")
            else:
                max_t = max(temps)
                min_t = min(temps)
                any_rain = any(rains)
                rain_str = "🌧️ возможен дождь" if any_rain else "☀️ без осадков"
                lines.append(f"World-weather: {min_t}…{max_t}°C, {rain_str}")

        # Mail.ru
        mr = get_mr_data(date)
        if mr:
            temps = []
            rains = []
            for part in ['ночь','утро','день','вечер']:
                if part in mr:
                    data = mr[part]
                    t = int(data[0].replace('−','-'))
                    temps.append(t)
                    if 'дождь' in data[1].lower():
                        rains.append(True)
                    else:
                        rains.append(False)
            if detailed:
                lines.append("Mail.ru:")
                for part in ['ночь','утро','день','вечер']:
                    if part in mr:
                        data = mr[part]
                        t = data[0]
                        sky = data[1]
                        prob = data[2]
                        press = data[3]
                        hum = data[4]
                        lines.append(f"  {part.capitalize()}: {t}°C, {sky}, в/о {prob}, давление {press} мм, влажн. {hum}")
            else:
                max_t = max(temps)
                min_t = min(temps)
                any_rain = any(rains)
                rain_str = "🌧️ дождь" if any_rain else "☀️ без осадков"
                lines.append(f"Mail.ru: {min_t}…{max_t}°C, {rain_str}")

        # Meteoinfo (может отсутствовать)
        mi = get_mi_data(date)
        if mi:
            # mi - список строк, например: ['22..24', 'Переменная облачность...', '9..11', '...']
            if len(mi) >= 2:
                temp_range = mi[0] if len(mi) > 0 else '?'
                description = mi[1] if len(mi) > 1 else '?'
                lines.append(f"Meteoinfo: {temp_range}°C, {description}")
            else:
                lines.append(f"Meteoinfo: {mi[0]}")
       # else:
        #    lines.append("Meteoinfo: данные отсутствуют")

        lines.append("")  # пустая строка между днями

    return "\n".join(lines)

def mk_otchet(city,ya,ww,mr,mi,gm):
    ans = 'Gismeteo: '+str(gm)
    ans += '\nYandex: '+str(ya)
    ans += '\nWorld-weather: '+str(ww)
    ans += '\nMeteoinfo: '+str(mi)
    ans +=  '\nMail.ru: '+str(mr)
    if city in TO[1]:
        send_mail(TO[1][city],ans,title = 'Прогноз погоды для города '+city)
        #send_mail(TO[1][city],format_weather_message(city, gm, ya, ww, mr, mi),title = 'Прогноз погоды для города '+city)
    llts = last_mail_log_ts()
    if llts is None or llts.date() < date.today() and datetime.now().hour >= 5:
        if city in TO2:
            send_mail(TO2[city],format_weather_message(city, gm, ya, ww, mr, mi),title = 'Прогноз погоды для города '+city)

def main():
    poses = {"Москва":["/moscow","moscow","moskva","moscow-area/moscow"],
             "Самара":["/samara","samara","samara","samara-area/samara"],
             "Санкт-Петербург":["/saint-petersburg","saint_petersburg","sankt_peterburg","leningrad-region/sankt-peterburg"],
             "Лыткарино":["/lytkarino","lytkarino","lytkarino",None],
             "Химки":["/himki","khimki_1","khimki",None],
             "Подольск":["/podolsk","podolsk","podolsk",None],
             "Королёв":["/korolev","korolev","korolev",None],
             "Сочи":["/sochi","sochi","sochi","krasnodar-territory/adler"],
             "Анапа":["/anapa","anapa","anapa","krasnodar-territory/anapa"],
             "Дербент":["/derbent","derbent","derbent","republic-dagestan/derbent"],
             "Волгоград":["/volgograd","volgograd","volgograd","volgograd-area/volgograd"],
             "Ярославль":["?lat=57.62656021&lon=39.89381409","yaroslavl","yaroslavl","yaroslavl-area/jaroslavl"],
             "Калуга":["/kaluga","kaluga","kaluga","kaluga-area/kaluga-A"],
             "Пермь":["/perm","perm","perm","perm-area/perm"],
             "Екатеринбург":["/yekaterinburg","yekaterinburg","ekaterinburg","sverdlovsk-area/ekaterinburg"],
             "Казань": ["/kazan", "kazan", "kazan", "republic-tatarstan/kasan"],
            "Нижний Новгород": ["/nizhny-novgorod", "nizhny_novgorod", "nizhniy_novgorod", "nizhegorodskaya-area/niznij-novgoro"],
            "Владивосток": ["/vladivostok", "vladivostok", "vladivostok", "primorski-krai/vladivostok"],
            "Мурманск": ["/murmansk", "murmansk", "murmansk", "murmansk-area/murmansk"],
            "Новосибирск": ["/novosibirsk", "novosibirsk", "novosibirsk", "novosibirsk-area/novosibirsk"],
            "Красноярск": ["/krasnoyarsk", "krasnoyarsk", "krasnoyarsk", "krasnoyarsk-territory/krasnojarsk"],
            "Новый Уренгой": ["/noviy-urengoy", "novyy_urengoy", "novy_urengoy", "jamalo-nenetskij-ar/novyi-urengoi"],
            "Омск": ["/omsk", "omsk", "omsk", "omsk-area/omsk"],
            "Рязань": ["/ryazan", "ryazan", "ryazan", "ryazan-area/rjazan"],
            "Тверь": ["/tver", "tver", "tver", "tver-area/tver"],
            "Якутск": ["/yakutsk", "yakutsk", "yakutsk", "republic-saha-yakutia/jakutsk"],
            "Краснодар": ["/krasnodar", "krasnodar", "krasnodar", "krasnodar-territory/krasnodar"],
            "Ростов-на-Дону": ["/rostov-na-donu", "rostov_na_donu", "rostov-na-donu", "rostov-area/rostov-na-donu"],
            "Пятигорск": ["/pyatigorsk", "pyatigorsk", "pyatigorsk", "stavropol-territory/pjatigorsk"],
            "Иркутск": ["/irkutsk", "irkutsk", "irkutsk", "irkutsk-area/irkutsk"],
		"Киров": ["/kirov", "kirov", "kirov", "kirov-area/kirov"],
	"Севастополь": ["/sevastopol", "sevastopol", "sevastopol", "republic-krym/sevastopol"],
	"Челябинск": ["/chelyabinsk", "chelyabinsk", "chelyabinsk", "chelyabinsk-area/cheljabinsk"],
	"Уфа": ["/ufa", "ufa", "ufa", "republic-bashkortostan/ufa"],
	"Магадан": ["/magadan", "magadan", "magadan", "magadan-area/magadan"],
	"Астрахань": ["/astrakhan", "astrakhan", "astrakhan", "astrakhan-area/astrahan"],
	"Петропавловск-Камчатский": ["/petropavlovsk", "petropavlovsk_kamchatsky", "petropavlovsk-kamchatskiy", "kamchatka-area/petropavlovsk-"],
	"Воронеж": ["/voronezh", "voronezh", "voronezh", "voronezh-area/voronez"],
	"Калининград": ["/kaliningrad", "kaliningrad", "kaliningrad", "kaliningrad-area/kaliningrad"],
	"Сургут": ["/surgut", "surgut", "surgut", "hanty-mansijskij-ar/surgut"]	}
    gisposes = {"Москва":"moscow-4368","Санкт-Петербург":"sankt-peterburg-4079","Самара":"samara-4618",
                "Лыткарино":"lytkarino-12640","Химки":"khimki-11582","Подольск":"podolsk-11955","Королёв":"korolev-11404",
                "Сочи":"sochi-5233","Анапа":"anapa-5211","Дербент":"derbent-5268",
                "Волгоград":"volgograd-5089","Ярославль":"yaroslavl-4313","Калуга":"kaluga-4387",
                "Екатеринбург":"yekaterinburg-4517","Пермь":"perm-4476","Казань": "kazan-4364",           
                "Нижний Новгород": "nizhny-novgorod-4355",  
                "Владивосток": "vladivostok-4877",          
                "Мурманск": "murmansk-3903",                
                "Новосибирск": "novosibirsk-4690",          
                "Красноярск": "krasnoyarsk-4674",           
                "Новый Уренгой": "novy-urengoy-3966",      
                "Омск": "omsk-4578",
                "Рязань": "ryazan-4394",                    
                "Тверь": "tver-4327",                       
                "Якутск": "yakutsk-4039", 
                "Краснодар": "krasnodar-5136",
                "Ростов-на-Дону": "rostov-na-donu-5110",    
                "Пятигорск": "pyatigorsk-5225",
                "Иркутск": "irkutsk-4787",
		"Киров":"kirov-4292",
		"Севастополь":"sevastopol-5003",
		"Челябинск": "chelyabinsk-4565",
		"Уфа":"ufa-4588",
		"Магадан":"magadan-4063",
		"Астрахань":"astrakhan-5130",
		"Петропавловск-Камчатский":"petropavlovsk-kamchatsky-4907",
		"Воронеж":"voronezh-5026",
		"Калининград":"kaliningrad-4225",
		"Сургут":"surgut-3994"}
   # gisposes = {"Москва":"moscow-4368","Санкт-Петербург":"sankt-peterburg-4079","Самара":"samara-4618", "Лыткарино":"lytkarino-12640",}
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
        print('gismeteo',city,pos)
        gm = gismeteo_parser(pos)
        #print(gm)
        res[city].append(gm)
        to_file(gm, city, 'gismeteo')
    for i in poses.keys():
        mk_otchet(i,*res[i])
    llts = last_mail_log_ts()
    if llts is None or llts.date() < date.today() and datetime.now().hour >= 5:
        for city in poses.keys():
            if city in TO2 and len(TO2[city]) > 0:
                newlog(SYSTEM_ID,'Send mail','Отправлены письма по всем подпискам для города '+city)

main()
newlog(SYSTEM_ID,'Run','Парсинг сайтов погоды успешно завершён')
#meteoinfo_parser('samara-area/samara')


