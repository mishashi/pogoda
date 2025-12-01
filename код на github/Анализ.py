
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
          if column != 'fact' and column != 'Дата':
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

def graph_all(s,yp,mr,mi,ww,gs):
  plt.figure(figsize=(12,9))
  plt.plot(*mi.rmse)
  plt.plot(*ww.rmse)
  plt.plot(*mr.rmse)
  plt.plot(*yp.rmse)
  plt.plot(*gs.rmse)
  plt.title('Завасимость rMSE от срока прдсказаний для разных сервисов')
  plt.xlabel('Срок предсказаний')
  plt.ylabel('rMSE')
  #plt.legend(['Meteoinfo','World-weather','Mail.ru','Yandex','Gismeteo'])
  plt.legend([x.title for x in s])
  plt.xticks(rotation=45)
  plt.grid(axis='y', linestyle='--', alpha=0.7)
  plt.tight_layout()
  plt.show()

mi_df = pd.read_csv('./mi_maxtempМосква.csv',index_col=0)
yp_df = pd.read_csv('./yp_maxtempМосква.csv',index_col=0)
mr_df = pd.read_csv('./mr_maxtempМосква.csv',index_col=0)
ww_df = pd.read_csv('./ww_maxtempМосква.csv',index_col=0)
gs_df = pd.read_csv('./gs_maxtempМосква.csv',index_col=0)
servers = [server(yp_df,'Яндекс Погода'),server(mr_df,'Погода Mail.ru'),server(mi_df,'Meteoinfo'),server(ww_df,'World-weather'),server(gs_df,'Gismeteo')]

graph_all(servers,*servers)
for s in servers:
  s.show()