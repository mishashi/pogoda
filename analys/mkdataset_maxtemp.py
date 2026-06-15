def main(city):
    import sys
    import os
    import pandas as pd
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    Path('./temp_tables').mkdir(exist_ok=True)
    from servermaxtemp import main
    from factmaxtemp import main_fact
    from web.backend.use_bd import get_cities

    servers = [('meteoinfo','mi'),('yandexpogoda','yp'),('gismeteo','gs'),('worldweather','ww'),('pogodamailru','mr')]
    if city == 'all':
        cc = get_cities()
        print(cc)
        for city in cc:
            for server,prefix in servers:
                fname = server+city+'.csv'
                main(city,server)
                main_fact(city,server,prefix)
        all_dfs = {prefix: [] for _, prefix in servers}  # prefix: mi, yp, mr, ww, gs
        #print(all_dfs)
        for city in cc:
            for _, prefix in servers:
                fname = f'./temp_tables/{prefix}_maxtemp{city}.csv'
                if os.path.exists(fname):
                    df_city = pd.read_csv(fname, index_col=0)
                    print(df_city)
                    # Добавляем колонку 'city' для идентификации (опционально, но полезно)
                    df_city['city'] = city
                    all_dfs[prefix].append(df_city)
                else:
                    print(f"Предупреждение: файл {fname} не найден для города {city}")
        print(all_dfs)
        # Объединяем и сохраняем для каждого сервера
        for prefix, df_list in all_dfs.items():
            if df_list:
                df_all = pd.concat(df_list, ignore_index=True)
                # Сохраняем без колонки 'city', если она не нужна для temp_graph
                # (можно оставить, temp_graph её проигнорирует)
                out_file = f'./temp_tables/{prefix}_maxtempall.csv'
                df_all.to_csv(out_file)
                print(f"Создан объединённый файл: {out_file} (записей: {len(df_all)})")
            else:
                print(f"Нет данных для сервера {prefix}")
    else:
            #city = 'Москва'
            for server,prefix in servers:
                fname = server+city+'.csv'
                main(city,server)
                main_fact(city,server,prefix)

main('Москва')
