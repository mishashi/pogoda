import pandas as pd
import numpy as np
import seaborn as sns
import re
import matplotlib
#matplotlib.use("Agg") 
import matplotlib.pyplot as plt
from mkdataset_maxtemp import main as main_t
from mkdataset_osadki import main as main_o
import os
import sys

# Устанавливаем рабочую директорию в папку, где находится сам run.py
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
main_t('all')
main_o('all')

def calculate_mse(actual, predicted):
    return np.mean((actual - predicted) ** 2)

class server:
  def __init__(self,df,title):
      self.df = df
      self.title = title
      self.rmse = {}
      self.mk_rmse()
  def mk_rmse(self):
      for column in self.df.columns:
          if column != 'city' and column != 'fact' and column != 'Дата':
              self.rmse[column] = np.sqrt(calculate_mse(self.df['fact'], self.df[column].apply(float)))
      self.rmse = [self.rmse.keys(),self.rmse.values()]
  def show(self):
      plt.figure(figsize=(10, 6))
      plt.bar(*self.rmse, color='skyblue')
      plt.title(self.title)
      plt.xlabel('Срок предсказаний')
      plt.ylabel('rMSE')
      plt.xticks(rotation=45)
      plt.grid(axis='y', linestyle='--', alpha=0.7)
      plt.tight_layout()
      plt.show()

def graph_all(c,save,s,yp,mr,mi,ww,gs):
  plt.figure(figsize=(12,9))
  plt.plot(*mi.rmse)
  plt.plot(*ww.rmse)
  plt.plot(*mr.rmse)
  plt.plot(*yp.rmse)
  plt.plot(*gs.rmse)
  plt.title('Зависимость RMSE от срока предсказаний для разных сервисов - '+c)
  plt.xlabel('Срок предсказаний')
  plt.ylabel('RMSE')
  plt.legend(['Meteoinfo','World-weather','Mail.ru','Yandex','Gismeteo'])
  #plt.legend([x.title for x in s])
  plt.xticks(rotation=45)
  plt.grid(axis='y', linestyle='--', alpha=0.7)
  plt.tight_layout()
  if save:
      graph_url = '../web/frontend/public/graphs/maxtemp-rmse_'
      plt.savefig(graph_url+c+".png", dpi=300, bbox_inches="tight")
  else:
      plt.show()



def temp_graph(c,save=False):
    print(c)
    #main(c)

    base = './temp_tables/'
    
    mi_df = pd.read_csv(base+f'mi_maxtemp{c}.csv',index_col=0)
    yp_df = pd.read_csv(base+f'yp_maxtemp{c}.csv',index_col=0)
    mr_df = pd.read_csv(base+f'mr_maxtemp{c}.csv',index_col=0)
    ww_df = pd.read_csv(base+f'ww_maxtemp{c}.csv',index_col=0)
    gs_df = pd.read_csv(base+f'gs_maxtemp{c}.csv',index_col=0)
    servers = [server(yp_df,'Яндекс Погода'),server(mr_df,'Погода Mail.ru'),server(mi_df,'Meteoinfo'),server(ww_df,'World-weather'),server(gs_df,'Gismeteo')]

    graph_all(c,save,servers,*servers)

def osadki_graph(c, save=False,snow=True):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from pathlib import Path
    import re

    services = {
        'mi': 'Meteoinfo',
        'yp': 'Yandex',
        'mr': 'Mail.ru',
        'ww': 'World-weather',
        'gs': 'Gismeteo'
    }

    def extract_days(col_name):
        match = re.search(r'\d+', col_name)
        return int(match.group()) if match else None

    prec_data = {svc: {} for svc in services.values()}
    rec_data  = {svc: {} for svc in services.values()}
    f1_data   = {svc: {} for svc in services.values()}

    for prefix, svc_name in services.items():
        fname = f'./osadki_tables/{prefix}_osadkiday{c}.csv'
        if not Path(fname).exists():
            print(f"Файл {fname} не найден, пропускаем сервис {svc_name}")
            continue
        df = pd.read_csv(fname, index_col=0)
        if 'fact' not in df.columns:
            print(f"В файле {fname} нет колонки fact, пропускаем")
            continue

        if snow:
            xxx = ''
            xxx2 = 'осадков'
        else:
            xxx = '_rainonly'
            xxx2 = 'дождей'

        for col in df.columns:
            if col in ['fact', 'city', 'Дата']:
                continue
            days = extract_days(col)
            if days is None:
                continue

            tp = fp = fn = 0
            for fact_val, pred_val in zip(df['fact'], df[col]):
                if pd.isna(fact_val) or pd.isna(pred_val):
                    continue

                if fact_val + pred_val == 5.5:
                    continue

                if snow:
                    y_true = 1 if fact_val >= 1 else 0
                else:
                    y_true = 1 if (fact_val >= 1 and fact_val < 3) else 0

                if snow:
                    y_pred = 1 if pred_val >= 1 else 0
                else:
                    y_pred = 1 if (pred_val >= 1 and pred_val < 3) else 0

                if y_true == 1 and y_pred == 1:
                    tp += 1
                elif y_true == 0 and y_pred == 1:
                    fp += 1
                elif y_true == 1 and y_pred == 0:
                    fn += 1
            #print(col,prefix,tp,fp,fn)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            prec_data[svc_name][days] = precision
            rec_data[svc_name][days]  = recall
            f1_data[svc_name][days]   = f1

    def plot_metric(metric_data, metric_name, ylabel, filename):
        plt.figure(figsize=(12, 7))
        for svc_name, days_dict in metric_data.items():
            if not days_dict:
                continue
            days_sorted = sorted(days_dict.keys())
            values = [days_dict[d] for d in days_sorted]
            plt.plot(days_sorted, values, marker='o', label=svc_name)
        plt.title(f'{metric_name} прогноза {xxx2} для города {c}')
        plt.xlabel('Срок прогноза, дни')
        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(sorted(set().union(*[list(d.keys()) for d in metric_data.values()])))
        plt.tight_layout()
        if save:
            graph_url = '../web/frontend/public/graphs/'
            plt.savefig(graph_url + filename, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        plt.close()
    plot_metric(prec_data, 'Precision', 'Precision (точность)', f'osadki{xxx}-precision_{c}.png')
    plot_metric(rec_data,  'Recall',    'Recall (полнота)',    f'osadki{xxx}-recall_{c}.png')
    plot_metric(f1_data,   'F1-score',  'F1-мера',             f'osadki{xxx}-f1_{c}.png')



def boxplot_graph(c, save=False):
    #main(c)

    base = './temp_tables/'
    services = {
        'Meteoinfo':     pd.read_csv(base + f'mi_maxtemp{c}.csv', index_col=0),
        'Yandex':        pd.read_csv(base + f'yp_maxtemp{c}.csv', index_col=0),
        'Mail.ru':       pd.read_csv(base + f'mr_maxtemp{c}.csv', index_col=0),
        'World-weather': pd.read_csv(base + f'ww_maxtemp{c}.csv', index_col=0),
        'Gismeteo':      pd.read_csv(base + f'gs_maxtemp{c}.csv', index_col=0)
    }

    def extract_days(col_name):
        match = re.search(r'\d+', col_name)
        return int(match.group()) if match else None

    records = []
    for service_name, df in services.items():
        df['fact'] = pd.to_numeric(df['fact'], errors='coerce')
        for col in df.columns:
            if col in ['city', 'Дата', 'fact']:
                continue
            day = extract_days(col)
            if day is None:
                continue
            pred = pd.to_numeric(df[col], errors='coerce')
            errors = (pred - df['fact']).dropna()
            for err in errors:
                records.append({
                    'service': service_name,
                    'period': day,
                    'error': err
                })

    if not records:
        print("Нет данных для построения boxplot'ов")
        return

    data_df = pd.DataFrame(records)

    print(f"\n=== Город {c} ===")
    print(f"Всего записей errors: {len(records)}")
    print(f"Уникальные периоды: {sorted(data_df['period'].unique())}")
    print(f"Уникальные сервисы: {data_df['service'].unique()}")
    print(f"Диапазон ошибок: min={data_df['error'].min():.2f}, max={data_df['error'].max():.2f}")
    plt.figure(figsize=(14, 8))
    sns.boxplot(x='period', y='error', hue='service', data=data_df, palette='tab10')
    plt.title(f'Распределение ошибок прогноза максимальной температуры – {c}')
    plt.xlabel('Срок прогноза, дни')
    plt.ylabel('Ошибка (прогноз - факт), °C')
    #plt.legend(title='Сервис', bbox_to_anchor=(1.05, 1), loc='upper left')
    legend = plt.legend(title='Сервис', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    if save:
        graph_url = '../web/frontend/public/graphs/maxtemp-boxplot_'   
        plt.savefig(graph_url + c + '.png', dpi=300,
                bbox_extra_artists=[legend],
                bbox_inches='tight')
        plt.close()
    else:
        plt.show()

#main('Москва')
#boxplot_graph('Москва')

