
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

class CumulativePlots:

    def dailyUseVsAverage(hourly: HourlyEnergyUsage, date_list: List[datetime], path: str, cumulative = True):
        fig, ax = plt.subplots(figsize = (7.5, 4))
        fig.tight_layout(pad = 2.0)
        ax.set_xlim([0, 24])
        if(cumulative): 
            ax.set_ylim([-20, 25])
        else:
            ax.set_ylim([0, 4])
        ax.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))

        ax.xaxis.set_major_formatter(format_time)
        ax.xaxis.set_ticks(np.arange(0, 24+1, 3))

        for d in date_list:
            print("working on date: " + str(d))
            times, usage = list(zip(*hourly.usage_series_for_day(d, hoursOnly = False)))

            hours = [(t.hour + t.minute/60) for t in times]
            usage = list(usage)
            print("average for day/hour: " + str(np.average(usage)*4) + " kWh")
            average = [np.average(usage) for u in usage]
            net_usage = [np.average(usage) - u for u in usage]
            daily_cumulative = np.cumsum(net_usage)

            ax.step(hours, usage, where = "post", label = "usage")
            ax.step(hours, average, where = "post", label = "average")
            
            if(cumulative):
                ax.step(hours, daily_cumulative, where = "post", label = "cumulative")

            ax.legend(loc = "upper left")

        plt.show()
        plt.close()

    def periodUseVsAverage(hourly: HourlyEnergyUsage, start: datetime, end: datetime):
        times, usage = list(zip(*hourly.usage_series_for_days(start, end, hoursOnly = True)))
        usage = list(usage)
        period_average = np.average(usage)
        print("average for period/hour: " + str(np.average(usage)) + " kWh")

        net_usage = [period_average - u for u in usage]
        daily_cumulative = np.cumsum(net_usage)

        print("min cumulative " + str(min(daily_cumulative)))
        print("max cumulative " + str(max(daily_cumulative)))


        fig, ax = plt.subplots(figsize = (7.5, 4))
        fig.tight_layout(pad = 2.0)

        ax.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))

#        ax.xaxis.set_major_formatter(format_time)
#        ax.xaxis.set_ticks(np.arange(0, 24+1, 3))


        average = [np.average(usage) for u in usage]
        net_usage = [np.average(usage) - u for u in usage]
        daily_cumulative = np.cumsum(net_usage)

        ax.step(times, usage, where = "post", label = "usage")
        ax.step(times, average, where = "post", label = "average")
        ax.step(times, daily_cumulative, where = "post", label = "cumulative")

        ax.legend(loc = "upper left")

        plt.show()
        plt.close()
 

        


    


