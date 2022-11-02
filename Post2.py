from fetch_NVenergy_usage import NVenergyUsage
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List


from rate_series import RateSegment, RateSeries, RatePlan
from fetch_seasons import Season
from region import Region


import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

def format_time(x, _):
    hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
    return hm + ("am" if (x%24)<12 else "pm")


def get_summer_TOU_peak():
    plans = Region("NV").get_rate_plans()
    plan = ([plan for plan in plans if plan.plan_type == "TOU"])[0]
    rate_series = plan.series()
    summer_rs = ([rs for rs in rate_series if rs.season.name == "Summer"])[0]
    segments = summer_rs.rate_segments
    peak_segment = ([seg for seg in segments if (
        seg.label == "On-Peak" and seg.weekend == False)])[0]
    return peak_segment
    

def plot_usage_chart(NVE: NVenergyUsage,
                     date_list: List[datetime],
                     high_temp_list: List[float],
                     low_temp_list: List[float],
                     path: str):
        
    fig, ax = plt.subplots(figsize = (7.5, 4.5))
    fig.tight_layout(pad = 3.0)
        
    ax.set_xlim([0, 24])
    ax.set_ylim([0, 4])
    ax.set_ylabel("kWh consumed (15m windows)")
    
    ax.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))

    ax.xaxis.set_major_formatter(format_time)
    ax.xaxis.set_ticks(np.arange(0, 24+1, 3))

    peak = get_summer_TOU_peak()
    print(peak)
    
    
    table_rows = [str(d.date()) for d in date_list]
    table_columns = ["Peak", "Off-Peak", "Total (kWh)"]
    cells = []

    for d, ht, lt in zip(date_list, high_temp_list, low_temp_list):
        times, usage = list(zip(*NVE.usage_series_for_day(d)))
        
        hours = [(t.hour + t.minute/60) for t in times]
        usage = list(usage)

        hours.append(24)
        usage.append(usage[-1])
        
        series_label = d.strftime("%a %b %-d, %Y") + " ({:1.0f}\u00b0 / {:1.0f}\u00b0F)".format(ht, lt)

        ax.step(hours, usage, where = "post", label = series_label)
        ax.legend(loc = "upper left")

        total_usage = round(sum(usage), ndigits=1)
        peak_usage = round(sum([u if peak.in_segment(t, False) else 0 for (t, u) in zip(times, usage)]), ndigits=1)
        off_peak_usage = round(total_usage - peak_usage, ndigits = 1)
        cells.append([peak_usage, off_peak_usage, total_usage])

    table = ax.table(cellText = cells,
                     rowLabels = table_rows,
                     colLabels = table_columns,
                     cellLoc = "center",
                     loc = "upper right")

    table.auto_set_column_width(col=list(range(len(table_columns))))
    table.set_fontsize(9)

    cells = table.get_celld().values()
    for cell in cells:
        cell.set(edgecolor = "lightgray")

                       
    
    
    plt.savefig(path)

    
  
if __name__ == "__main__":
    NVE = NVenergyUsage()

    date_lists = [[datetime(2022, 8, 15), datetime(2022, 8, 31)],  # high
                  [datetime(2022, 2, 1), datetime(2022, 2, 3)],
                  [datetime(2022, 5, 9), datetime(2022, 5, 15)]] #high


    high_temp_lists = [[96, 109],
                      [58, 53],
                      [72, 95]]

    low_temp_lists = [[79, 85],
                      [42, 33],
                      [54, 64]]

    
    # source: https://www.wunderground.com/history/monthly/us/nv/henderson/KLAC/date/2022-8


    base_path = "post2/post2_usage_"

    for date_list, high_temps, low_temps in zip(date_lists, high_temp_lists, low_temp_lists):
        path = base_path + date_list[0].strftime("%b") + ".png"
        plot_usage_chart(NVE, date_list, high_temps, low_temps, path)

        


        

    
    
    
    
