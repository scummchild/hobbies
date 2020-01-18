"""Create a plot of the turtle tank temperatures every day"""
import datetime

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
from mongoengine.queryset.visitor import Q
from pandas.plotting import register_matplotlib_converters

import tankdb.mongo_setup as mongo_setup
from tankdb.tempreading import TempReading

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

mongo_setup.global_init()
query_results = list(TempReading.objects.filter(
    Q(reading_time__gte=yesterday) & Q(reading_time__lt=today)))
temp_readings = [result.to_mongo().to_dict() for result in query_results]
df = pd.DataFrame(temp_readings)

water_temps = df.loc[df['reading_location'] == 'water']
basking_temps = df.loc[df['reading_location'] == 'bask']

register_matplotlib_converters()
plt.plot(water_temps['reading_time'], water_temps['temp_f'])
plt.plot(basking_temps['reading_time'], basking_temps['temp_f'])

xformatter = DateFormatter('%H:%M')
plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)

plt.title(f'Tank Temperatures {yesterday} to {today}')
plt.legend(['Water Deg F', 'Basking Dock Deg F'])

plt.savefig(f'./tank_graphs/{today}.png')
