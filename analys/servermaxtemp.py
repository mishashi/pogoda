from datetime import datetime,time,date,timedelta
from dateutil.relativedelta import relativedelta
import os
import json
import pandas as pd
import numpy as np
import sys


def main(city,server):
    fname = './temp_tables/'+server+city+'.csv'

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

    for i in ms:
        for j in range(1,32):
            path = f'../run/{server}/{i[0]}{i[1]}/{j}/{city}.txt'
            if os.path.exists(path):
                f = open(path,'r',encoding='utf-8')
                if server != 'meteoinfo':
            #                    print(f.readline())
                    try: 
                        w = json.loads(f.readline())
                    except:
                        continue
                    line = w
                    key = list(line.keys())[0]
                    if not line[key]:
#                            print(f"ПРЕДУПРЕЖДЕНИЕ: пустое значение для {key} в файле {path}")
                            continue
                    dayp.append(w)
                else:
                    e = f.readlines()
                    f = True
                    for line in e:
                        line = json.loads(line)
                        key = list(line.keys())[0]
                        if not line[key]:
#                            print(f"ПРЕДУПРЕЖДЕНИЕ: пустое значение для {key} в файле {path}")
                            continue
                        dt = datetime.fromisoformat(list(line.keys())[0])
                        if dt.time() > time(hour=8,minute=0,second=0):
                            dayp.append(line)
                            #print(line)
                            f = False
                            break
                    #if f:
                        #dayp.pop(-1)
                        #print(e)
                        #sys.exit()

    def yp(dayp):
        dayp = [list(x.values())[0]['days'] for x in dayp]
        msx = []
        for i in dayp:
            try:
                date0 = list(i[0].keys())[0]
                for j in i:
                    date = list(j.keys())[0]
                    day_temp = max(int(j[date][3].replace('−','-')),int(j[date][5].replace('−','-')))
                    dd = datetime.strptime(date,'%Y-%m-%d') - datetime.strptime(date0,'%Y-%m-%d')
                    if datetime.strptime(date,'%Y-%m-%d') < ddd:
                        msx.append([date,day_temp,dd.days])
            except:
                pass#max.append()
        return msx

    def gs(dayp):
        dayp = [list(x.values())[0] for x in dayp]
        msx = []
        for i in dayp:
            date0 = list(i[0].keys())[0]
            for j in i:
                date = list(j.keys())[0]
                t = [int(x.replace('−','-')) for x in j[date]['t']]
                day_temp = max(t[4:6])
                dd = datetime.strptime(date, '%Y-%m-%d') - datetime.strptime(date0, '%Y-%m-%d')
                if datetime.strptime(date, '%Y-%m-%d') < ddd:
                    msx.append([date, day_temp, dd.days])
        return msx

    def mr(dayp):
        #print(dayp)
        dayp = [list(x.values())[0] for x in dayp]
        msx = []
        #print(dayp)
        for i in dayp:
            date0 = list(i[0].keys())[0]
            for j in i:
                date = list(j.keys())[0]
                tx = [j[date]['день'][0],j[date]['вечер'][0]]
                t = [int(x.replace('−','-')) for x in tx]
                day_temp = max(t)
                dd = datetime.strptime(date, '%Y-%m-%d') - datetime.strptime(date0, '%Y-%m-%d')
                if datetime.strptime(date, '%Y-%m-%d') < ddd:
                    msx.append([date, day_temp, dd.days])
        return msx

    def ww(dayp):
        #print(dayp)
        dayp = [list(x.values())[0] for x in dayp]
        msx = []
        #print(dayp)
        for i in dayp:
            date0 = list(i[0].keys())[0]
            for j in i:
                date = list(j.keys())[0]
                #print(date,j[date])
                if 'Вечер' in j[date]:
                    tx = [j[date]['День'][0],j[date]['Вечер'][0]]
                else:
                    tx = [j[date]['День'][0]]
                t = [int(x.replace('−','-')) for x in tx]
                day_temp = max(t)
                dd = datetime.strptime(date, '%Y-%m-%d') - datetime.strptime(date0, '%Y-%m-%d')
                if datetime.strptime(date, '%Y-%m-%d') < ddd:
                    msx.append([date, day_temp, dd.days])
        return msx

    def mi(dayp):
        #print(dayp)
        dayp = [list(x.values())[0] for x in dayp]
        msx = []
        print()
        #print(dayp[67:74])
        for i in dayp:
            #print('f',i)
            date0 = list(i[0].keys())[0]
            for j in i:
                date = list(j.keys())[0]
                tx = j[date][0].split('..')
                t = [int(x.replace('−','-')) for x in tx]
                day_temp = np.ceil(np.mean(t))
                dd = datetime.strptime(date, '%Y-%m-%d') - datetime.strptime(date0, '%Y-%m-%d')
                if datetime.strptime(date, '%Y-%m-%d') < ddd:
                    msx.append([date, day_temp, dd.days])
        return msx

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
    #print('msx',msx)
    df = {}
    d1 = ''
    for (d, t, r) in msx:
            if d != d1:
                df[d] = {}
            df[d][f"За {r} дней"] = t
            d1 = d
    df = pd.DataFrame(df).transpose()
    df.to_csv(fname)
