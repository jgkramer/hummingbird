from hourlyEnergyUsage import HourlyEnergyUsage

import matplotlib.pyplot as plt
from matplotlib.axis import Tick

from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, PercentFormatter)

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from typing import List

def format_time(x, _):
    hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
    return hm + ("am" if (x%24)<12 else "pm")

class DailyPlots:
    
   def plot_intraday_usage(hourly: HourlyEnergyUsage,
                           date_list: List[datetime],
                           path: str,
                           table_cells = None, table_rows = None, table_columns = None,
                           colors_list: List[str] = None
                           ):
         fig, ax = plt.subplots(figsize = (7.5, 4))
         fig.tight_layout(pad = 2.0)

         ax.set_xlim([0, 24])
         ax.set_ylim([0, 5])
         ax.set_ylabel("kWh consumed (15m windows)")

         ax.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))
         ax.xaxis.set_major_formatter(format_time)
         ax.xaxis.set_ticks(np.arange(0, 24+1, 3))

         if colors_list == None:
             colors_list = [None] * len(date_list)
         
         for d, c in zip(date_list, colors_list):
             times, usage = list(zip(*hourly.usage_series_for_day(d)))
             hours = [(t.hour + t.minute/60) for t in times]
             usage = list(usage)

             hours.append(24)
             usage.append(usage[-1])

             series_label = d.strftime("%a %b %-d, %Y")

             ax.step(hours, usage, where = "post", label = series_label, color = c, linewidth = 1.0)
             ax.legend(loc = "upper left")

         if(path == None):
             plt.show()
         else:
             plt.savefig(path)
         plt.close()

        
class CumulativePlots:
    
    def dailyUseVsAverage(hourly: HourlyEnergyUsage, date_list: List[datetime], path: str):
        fig, ax = plt.subplots(figsize = (7.5, 4))
        fig.tight_layout(pad = 2.0)
        ax.set_xlim([0, 24])
        ax.set_ylim([-20, 20])
        ax.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))

        ax.xaxis.set_major_formatter(format_time)
        ax.xaxis.set_ticks(np.arange(0, 24+1, 3))

        for d in date_list:
            times, usage = list(zip(*hourly.usage_series_for_day(d)))

            hours = [(t.hour + t.minute/60) for t in times]
            usage = list(usage)
            average = [avearge(usage) for u in usage]
            net_usage = [average(usage) - u for u in usage]
            daily_cumulative = np.cumsum(net_usage)

            ax.step(hours, usage, where = "post", label = "usage")
            ax.step(hours, average, where = "post", label = "average")
            ax.step(hours, daily_cumulative, where = "post", label = "cumulative")

            ax.legend(loc = "upper left")

        plt.savefig(path)
        plt.show()
        plt.close()
        
    


