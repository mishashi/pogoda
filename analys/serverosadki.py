from datetime import datetime,time,date,timedelta
from dateutil.relativedelta import relativedelta
import os
import json
import pandas as pd
import numpy as np


def main(city,server,tps = 'day'):
    def skytoint(sky):
        sky = sky.lower()
        if "дождь со снегом" in sky or 'снег с дождем' in sky:
            return 2.5
        if 'небольшой дождь' in sky or 'cлабый дождь' in sky:
            return 1
        if 'снег' in sky:
            return 3
        if 'дождь' in sky:
            return 2
        return 0

    def gs_meansky(ms):
        if len(ms) == 2:
            if ms[0] == ms[1]:
                return ms[0]
            if 'дождь' in ms[0] and 'снег' in ms[1] or 'снег' in ms[0] and 'дождь' in ms[1]:
                return "дождь со снегом"
            elif 'дождь' in ms[0] and 'дождь' in ms[1] and 'неболь' not in ms[0] and 'неболь' not in ms[1]:
                return 'дождь'
            elif 'дождь' not in ms[0] and 'дождь' not in ms[1]:
                return 'малооблачно'
            else:
                return "небольшой дождь"

    fname = './osadki_tables/'+"osadki"+tps+server+city+'.csv'

    start = datetime(2025,10,1)
    end = datetime(date.today().year,date.today().month,date.today().day)
    ms = []
    delta = relativedelta(months=1)
    q = start
    while q <= end:
        ms.append((q.year,q.month))
        q+=delta
    dayp = []
    ddd = end
    #print(ms)

    for i in ms:
        for j in range(1,32):
            path = f'../run/{server}/{i[0]}{i[1]}/{j}/{city}.txt'
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    w = f.readline().strip()
                    if w:
                        try:
                            dayp.append(json.loads(w))
                        except json.JSONDecodeError as e:
                            print(f"Ошибка JSON в файле {path}: {e}")

    def yp(dayp):
        dayp = [list(x.values())[0]['days'] for x in dayp]
        dayp = [x for x in dayp if x]
        msx = []
        for i in dayp:
            date0 = list(i[0].keys())[0]
            for j in i:
                date = list(j.keys())[0]
                t = j[date]
                os = [t[2],t[4],t[6]]
                dd = datetime.strptime(date,'%Y-%m-%d') - datetime.strptime(date0,'%Y-%m-%d')
                if datetime.strptime(date,'%Y-%m-%d') < ddd:
                    msx.append([date,*os,dd.days])
        return msx

    def gs(dayp):
        dayp = [list(x.values())[0] for x in dayp]
        dayp = [x for x in dayp if x]
        msx = []
        for i in dayp:
            #print(i)
            date0 = list(i[0].keys())[0]
            #print(date0)
            for j in i:
                date = list(j.keys())[0]
                t = [x.lower().replace('"','') for x in j[date]['s']]
                msky = gs_meansky(t[2:4])
                dsky = gs_meansky(t[4:6])
                esky = gs_meansky(t[6:8])
                dd = datetime.strptime(date, '%Y-%m-%d') - datetime.strptime(date0, '%Y-%m-%d')
                if datetime.strptime(date, '%Y-%m-%d') < ddd:
                    msx.append([date, msky,dsky,esky, dd.days])
        return msx

    def mr(dayp):
        #print(dayp)
        dayp = [list(x.values())[0] for x in dayp]
        dayp = [x for x in dayp if x]
        msx = []
        #print(dayp)
        for i in dayp:
            if i != []:
                date0 = list(i[0].keys())[0]
                for j in i:
                    date = list(j.keys())[0]
                    tx = [j[date]['утро'][1],j[date]['день'][1],j[date]['вечер'][1]]
                    #print(tx)
                    dd = datetime.strptime(date, '%Y-%m-%d') - datetime.strptime(date0, '%Y-%m-%d')
                    if datetime.strptime(date, '%Y-%m-%d') < ddd:
                        msx.append([date, *tx, dd.days])
            #break
        return msx

    def ww(dayp):
        #print(dayp)
        dayp = [list(x.values())[0] for x in dayp]
        dayp = [x for x in dayp if x]
        msx = []
        #print(dayp)
        for i in dayp:
            date0 = list(i[0].keys())[0]
            for j in i:
                date = list(j.keys())[0]
                #print(j[date])
                if 'Вечер' in j[date]:
                    tx = [j[date]['Утро'][1],j[date]['День'][1],j[date]['Вечер'][1]]
                else:
                    tx = [j[date]['Утро'][1],j[date]['День'][1],j[date]['День'][1]]
                #print(tx)
                dd = datetime.strptime(date, '%Y-%m-%d') - datetime.strptime(date0, '%Y-%m-%d')
                if datetime.strptime(date, '%Y-%m-%d') < ddd:
                    msx.append([date, *tx, dd.days])
        return msx

    def mi(dayp):
        #print(dayp)
        dayp = [list(x.values())[0] for x in dayp]
        dayp = [x for x in dayp if x]
        msx = []
        #print(dayp)
        for i in dayp:
            #print(i)
            date0 = list(i[0].keys())[0]
            for j in i:
                date = list(j.keys())[0]
                tx = j[date][1]
                #print(tx)
                dd = datetime.strptime(date, '%Y-%m-%d') - datetime.strptime(date0, '%Y-%m-%d')
                if datetime.strptime(date, '%Y-%m-%d') < ddd:
                    msx.append([date, tx,tx,tx, dd.days])
        return msx

    #print(server,dayp)
    if server == 'yandexpogoda':
        msx = yp(dayp)
    if server == 'gismeteo':
        msx = gs(dayp)
    if server == 'pogodamailru':
        msx = mr(dayp)
    if server == 'worldweather':
        msx = ww(dayp)
    if server == 'meteoinfo':
        msx = mi(dayp)

    msx.sort()
    #print(msx)
    df = {}
    d1 = ''
    for (d, m, t, e, r) in msx:
            if d != d1:
                df[d] = {}
            df[d][f"За {r} дней"] = skytoint(t)
            d1 = d
    df = pd.DataFrame(df).transpose()
    #print(df)
    df.to_csv(fname)
main('Москва','gismeteo','day')
