from servermaxtemp import main
from factmaxtemp import main_fact

city = 'Москва'
servers = [('meteoinfo','mi'),('yandexpogoda','yp'),('gismeteo','gs'),('worldweather','ww'),('pogodamailru','mr')]
for server,prefix in servers:
    fname = server+city+'.csv'
    main(city,server)
    main_fact(city,server,prefix)