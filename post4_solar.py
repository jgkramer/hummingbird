

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from typing import List

import matplotlib as mpl
import matplotlib.pyplot as plt
from eiaGeneration import EIAGeneration

from hourlyChart import HourlyChart

from matplotlib.axis import Axis  
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as pltdates

def keyGenerationStats(hourlyValues):
    stats = {}
    stats["maxGen"] = max(hourlyValues)
    stats["totalGen"] = sum(hourlyValues)
    stats["equivHours"] = stats["totalGen"]/stats["maxGen"]
    stats["activeHours"] = sum([1 if x > 0.1*stats["maxGen"] else 0 for x in hourlyValues])
    stats["strongHours"] = sum([1 if x > 0.6*stats["maxGen"] else 0 for x in hourlyValues])
    print(stats)

def dailyGenerationChart(eiag: EIAGeneration, start: datetime, end: datetime, path: str):
    dates, totals = eiag.dailyTotals(start, end)
    dates2, totals2 = eiag.topNOnly(start, end, N=5)

    plt.rcParams.update({'font.size': 8})
    fig, ax = plt.subplots(figsize = (7.5, 3))

    ax.set_ylim([0, max(totals)*1.2])
    ax.plot(dates, totals, label = "All Days")
    ax.plot(dates2, totals2, label = "Top 5 Days in Month")

    ax.legend()
    ax.xaxis.set_major_formatter(pltdates.DateFormatter("%d-%b-%y"))
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))

    ax.set_ylabel("Daily NV Power Solar Generation (MWh)")

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    fig.tight_layout()

    plt.savefig(path)
    plt.show()
    plt.close()

            

if __name__ == "__main__":

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)


    start = datetime(2022, 1, 1)
    end = datetime(2022, 12, 31)

    # read full year data
    nMonths = 12*(end.year - start.year) + (end.month - start.month) + 1
    paths = []
    d = start
    while d < end:
        paths.append(f"./generation_data/NVPowerGeneration{d.year}_{d.month:02}.csv")
        d = d + relativedelta(months = +1)

    eiag = EIAGeneration(paths)

    # chart 1: motivate focusing on top 5 days

    
    dec_start = datetime(2022, 12, 1)
    dec_end = datetime(2022, 12, 31)
    dailyGenerationChart(eiag, dec_start, dec_end, "post4/post4_december.png")

    # prep: generate the monthly line charts. 
    x_values = [x for x in range(0, 24)]
    y_values_list = []
    y_values_list_filtered = []
    series_labels = []

    for month in range(nMonths):
        s = start + relativedelta(months = month)
        e = s + relativedelta(months = +1)
        _, avgs = eiag.averageDayInPeriod(s, e)
        y_values_list.append(avgs)
        
        _, avgs_top = eiag.averageDayInPeriodFiltered(s, e)
        y_values_list_filtered.append(avgs_top)
        
        series_labels.append(s.strftime("%b-%y"))
        
        
    cmap = mpl.cm.get_cmap('Paired')
    series_colors = [cmap(((i)%12)/11) for i in range(12)]

    # chart 2: first do the december averages
    

    for month in [12, 6]:
       # month_name = datetime(2022, month, 1).strftime("%B")
        HourlyChart.hourlyLineChart(x_values,
                                    [y_values_list[month-1], y_values_list_filtered[month-1]],
                                    "Average Hourly NV Solar Generation (MWh)",
                                    ["Average of all Days", "Average of top 5 Days"],
                                    ["lightblue", "blue"],
                                    f"post4/post4_month{month}_hourly.png",
                                    title = None,
                                    x_axis_label = "Hour Starting (Standard Time)",
                                    annotate = 1)
        
        keyGenerationStats(y_values_list_filtered[month-1])
        keyGenerationStats(y_values_list[month-1])

        
                            
    y_axis_label = "MWh"                            

    HourlyChart.hourlyLineChart(x_values,
                                y_values_list_filtered,
                                y_axis_label,
                                series_labels,
                                series_colors,
                                "post4/post4_all_months_hourly.png",
                                title = None,
                                x_axis_label = "Hour Starting",
                                annotate = None)




    
