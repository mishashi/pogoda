from datetime import *
import os
import json
import pandas as pd

def main_fact(city,server,prefix):
    fname = prefix+'_maxtemp'+city+'.csv'
    start = (2025,10)
    #end = str(date.today().year)+str(date.today().month)
    end = (2025,11)
    ms = [start,end] #v

    dayp = []
    for i in ms:
        for j in range(1,32):
            path = f'./run/fact/{city}/{i[0]}{i[1]}/{j}.txt'
            if os.path.exists(path):
                f = open(path,'r',encoding='utf-8')
                w = f.readlines()
                for line in w:
                    dayp.append(json.loads(line))

    mt = {}
    for i in dayp:
        d = list(i.keys())[0]
        date = (datetime.fromisoformat(d)+timedelta(hours=3)).date().strftime('%Y-%m-%d')
        t = int(i[d][2].replace('−','-'))
        if date not in mt:
            mt[date] = []
        mt[date].append(t)
    mtt = []
    for (k,v) in mt.items():
        ts = sorted(v,reverse=True)
        mx = max(ts)
        if ts.count(ts[0]) / len(ts) < 0.1 or 2*ts.count(ts[0]) < ts.count(mx - 1):
            mtt.append(mx-1)
        else:
            mtt.append(mx)
        #print(k,ts)
    df = pd.read_csv(f'./{server}{city}.csv')
    df['fact'] = mtt
    df = df.rename(columns={'Unnamed: 0':'Дата'})
    print(df)
    df.to_csv(fname)