from Анализ import temp_graph, boxplot_graph, osadki_graph
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from web.backend.use_bd import get_cities

ms = ['all']+get_cities()
#ms = ['Москва']
for c in ms:
    temp_graph(c,True)
    boxplot_graph(c,True)
    osadki_graph(c,save=True,snow=False)
    osadki_graph(c,True)
