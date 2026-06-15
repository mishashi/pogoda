
def main_fact(city,server,prefix):
    from datetime import datetime,time,date,timedelta
    from dateutil.relativedelta import relativedelta
    import os
    import json
    import pandas as pd
    fname = './temp_tables/'+prefix+'_maxtemp'+city+'.csv'
    start = datetime(2025, 10, 1)
    end = datetime(date.today().year, date.today().month, 1)
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
                    dayp.append(json.loads(line))
    mt_all = {}
    # Дневные измерения (с 10 до 20 часов) по дням
    mt_day = {}

    for entry in dayp:
        dt_str = list(entry.keys())[0]
        dt = datetime.fromisoformat(dt_str) + timedelta(hours=3)  # корректировка времени
        date_str = dt.date().strftime('%Y-%m-%d')
        t = int(entry[dt_str][2].replace('−', '-'))

        # Сохраняем все измерения
        mt_all.setdefault(date_str, []).append(t)

        # Сохраняем только дневные (10–20 часов)
        if 10 <= dt.hour <= 20:
            mt_day.setdefault(date_str, []).append(t)

    mtt = {}
    for date, all_vals in mt_all.items():
        day_vals = mt_day.get(date, [])
        if len(day_vals) < 15:  # недостаточно дневных измерений
            mtt[date] = None
        else:
            ts = sorted(all_vals, reverse=True)
            mx = max(ts)
            if ts.count(ts[0]) / len(ts) < 0.1 or 2 * ts.count(ts[0]) < ts.count(mx - 1):
                mtt[date] = mx - 1
            else:
                mtt[date] = mx
    df = pd.read_csv(f'./temp_tables/{server}{city}.csv')
    df['fact'] = None
    j = 0
    for i in df.values:
        if i[0] in mtt:
            df.loc[j, "fact"] = mtt[i[0]]
        j += 1
    df = df.rename(columns={'Unnamed: 0': 'Дата'})
    #print(df)
    df.to_csv(fname)
