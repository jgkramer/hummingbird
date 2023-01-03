

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from typing import List

import matplotlib as mpl
import matplotlib.pyplot as plt
from eiaGeneration import EIAGeneration

from hourlyChart import HourlyChart

if __name__ == "__main__":

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    
    start = datetime(2022, 1, 1)
    end = datetime(2022, 12, 31)
    paths = []
    d = start
    while d < end:
        paths.append(f"./generation_data/NVPowerGeneration{d.year}_{d.month:02}.csv")
        d = d + relativedelta(months = +1)

    eiag = EIAGeneration(paths)

    x_values = [x for x in range(0, 24)]
    y_values_list = []
    y_values_list_filtered = []
    series_labels = []

    for month in range(12):
        s = start + relativedelta(months = month)
        e = s + relativedelta(months = +1)
        _, avgs = eiag.averageDayInPeriod(s, e)
        y_values_list.append(avgs)
        
        _, avgs_top = eiag.averageDayInPeriodFiltered(s, e)
        y_values_list_filtered.append(avgs_top)
        
        series_labels.append(s.strftime("%b-%y"))
        
        
    cmap = mpl.cm.get_cmap('Paired')
    series_colors = [cmap(((i)%12)/11) for i in range(12)]

    y_axis_label = "Average MWh"
    title = "title"
    path1 = "test1.png"
    path2 = "test2.png"

    HourlyChart.hourlyLineChart(x_values,
                                y_values_list,
                                y_axis_label,
                                series_labels,
                                series_colors,
                                title,
                                path1)

    HourlyChart.hourlyLineChart(x_values,
                                y_values_list_filtered,
                                y_axis_label,
                                series_labels,
                                series_colors,
                                title,
                                path2)

    dates, totals = eiag.dailyTotals(start, end)
    dates2, totals2 = eiag.topNOnly(start, end, N=5)
    fig, ax = plt.subplots(figsize = (7.5, 4))
    ax.set_ylim([0, max(totals)*1.2])
    ax.plot(dates, totals)
    ax.plot(dates2, totals2)
    plt.show()
    plt.close()
                
#    eiag.topNOnly(start, end)
    
    fig.tight_layout(pad = 2.0)


    
