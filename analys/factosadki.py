from datetime import datetime,time,date,timedelta
from dateutil.relativedelta import relativedelta
import os
import json
import pandas as pd

def main_fact(city,server,prefix,tps='day'):
    from datetime import datetime, time, date, timedelta
    from dateutil.relativedelta import relativedelta
    import os
    import json
    import pandas as pd
    def skytoint(sky):
        sky = sky.lower()
        if "снег с дождем" in sky:
            return 2.5
        if 'небольшой дождь' in sky or 'слабый дождь' in sky:
            return 1
        if 'снег' in sky:
            return 3
        if 'дождь' in sky:
            return 2
        return 0

    fname = './osadki_tables/'+prefix+'_osadki'+tps+city+'.csv'

    start = datetime(2025, 10, 1)
    end = datetime(datetime.today().year, datetime.today().month, 1)
    ms = []
    delta = relativedelta(months=1)
    q = start
    while q <= end:
        ms.append((q.year, q.month))
        q += delta

    dayp = []
    for i in ms:
        for j in range(1,32):
            path = f'../run/fact/{city}/{i[0]}{i[1]}/{j}.txt'
            if os.path.exists(path):
                f = open(path,'r',encoding='utf-8')
                w = f.readlines()
                for line in w:
                    dayp.append(json.loads(line.lower()))
    d_mt = {}
    for i in dayp:
        d1 = list(i.keys())[0]
        d = datetime.fromisoformat(d1)+timedelta(hours=3)
        date = (d).date().strftime('%Y-%m-%d')
        t = i[d1][1]
        if 12 < d.time().hour < 18:
            if date not in d_mt:
                d_mt[date] = []
            #print(t,skytoint(t))
            d_mt[date].append(skytoint(t))
    #print(d_mt)
    mtt = {}
    for (k,v) in d_mt.items():
        ts = sorted(v,reverse=True)
        #print(ts)
        if len(ts) < 12:
            mtt[k] = None
        elif ts.count(3) > 0.1*len(ts):
            mtt[k] = 3
        elif 2 in ts or (ts.count(0) + ts.count(3)) < 0.85*len(ts):
            mtt[k] = 2
        elif (ts.count(0) + ts.count(3)) < 0.95 * len(ts):
            mtt[k] = 1
        else:
            mtt[k] = 0
        #print(k,ts)
    df = pd.read_csv(f'./osadki_tables/osadki{tps}{server}{city}.csv')
    #print(mtt)
    df['fact'] = None
    j = 0
    for i in df.values:
        if i[0] in mtt:
            df.loc[j, "fact"] = mtt[i[0]]
        j += 1
    df = df.rename(columns={'Unnamed: 0':'Дата'})
    #print(df)
    df.to_csv(fname)
main_fact('Москва','gismeteo','yp','day')
