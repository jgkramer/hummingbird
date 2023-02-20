
from specificHourlyUsage import NVenergyUsage, SDenergyUsage, UsagePaths, EIARegionUsage
from hourlyEnergyUsage import HourlyEnergyUsage

import matplotlib.pyplot as plt
from matplotlib.axis import Tick
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, PercentFormatter, StrMethodFormatter)
from matplotlib.dates import DateFormatter

import math

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import pytz

from typing import List, Callable


class SupplyGenerator:
    def __init__(self, times: List[datetime], usage: List[float]):
        self.times = times
        self.usage = usage
        
    def period_average(self, multiplier = 1.0):
        period_average = np.average(self.usage)
        print(f"period average {period_average:0.1f}") 
        function = [multiplier * period_average for dt in self.times]
        return function

    def percent_of_max(self, multiplier = 1.0):
        period_max = max(self.usage)
        print(f"period max {period_max:0.1f}")
        function = [multiplier * period_max for dt in self.times]
        return function
                       

    def typical_daily_peak(self, multiplier = 1.0, statistic = "median", date_subset: List[datetime] = None):
        print(statistic)
        assert(statistic in ["median", "average"])

        subset_start = self.times[0].date() if date_subset is None else date_subset[0].date()
        subset_end = self.times[-1].date() if date_subset is None else date_subset[1].date()
        
        df = pd.DataFrame({"Date": [t.date() for t in self.times if (subset_start <= t.date() and t.date() <= subset_end)],
                           "Usage": [u for (u, t) in zip(self.usage, self.times) if (subset_start <= t.date() and t.date() <= subset_end)]
                           })
        grouped = df.groupby("Date")["Usage"].max().reset_index()

        average_peak = np.median(grouped["Usage"]) if statistic == "median" else np.mean(grouped["Usage"])
        print(f"average daily peak {average_peak:0.1f}")
        function = [multiplier * average_peak for dt in self.times]
        return function
    

    def top_percentile_days(self, percentile: float = 0.95):
        df = pd.DataFrame({"Time": self.times,
                           "Date": [t.date() for t in self.times],
                           "Usage": self.usage})

        grouped = df.groupby("Date")["Usage"].max().reset_index()
        ndays = len(grouped["Date"])
        top_days = math.ceil((1 - percentile)*len(grouped["Date"]))
        threshold = np.partition(grouped["Usage"], -top_days)[-top_days]
        function = [threshold for dt in self.times]
        return function


    def solar_function(self, path: str, multiplier = 1.0):
        total_usage = sum(self.usage)
        
        df_solar = pd.read_csv(path)

        timezone = pytz.timezone("America/Los_Angeles")
        months = [dt.strftime("%b") for dt in self.times]
        hours = [(dt.hour - (1 if (timezone.localize(dt)).dst() != timedelta(0) else 0)) % 24 for dt in self.times]
        solar_raw = [(df_solar[month])[hour] for (month, hour) in zip(months, hours)]

        total_solar_raw = sum(solar_raw)
        scale = total_usage / total_solar_raw

        function = [multiplier * scale * raw for raw in solar_raw]
        return function


    def blend_fixed_solar(self, path: str, multiplier = 1.0, solar_share: float = 0.5):
        solar = self.solar_function(path, multiplier * solar_share)
        fixed = self.period_average(multiplier * (1-solar_share))
        function = [s + f for s, f in zip(solar, fixed)]
        return function
                    
        
class StorageAnalyzer():

    def plotStorageAnalysis(self,
                            supply_series: List,
                            storage_balance_series: List,
                            labels: List[str] = None,
                            colors: List = None,
                            legend_position: str = "upper left",
                            path: str = None):

        if colors is None:
            colors = (["red", "purple", "green", "orange"])[0:len(supply_series)]

        if labels is None:
            labels = ([None] * len(supply_series))


        # set up the plot
        plt.rcParams.update({'font.size': 8, })
        fig, ax = plt.subplots(ncols = 1, nrows = 2, figsize = (8, 4.5),
                               gridspec_kw = {"height_ratios": [2, 1]})
        fig.tight_layout(pad = 2.5)

        max_supply = max([max(x) for x in supply_series])
        ax[0].set_ylim((0,1.2*max(max(self.usage), max_supply)))
        ax[0].set_xlim(self.times[0], self.times[-1])
        ax[1].set_xlim(self.times[0], self.times[-1])
                        
        
        ax[0].spines["right"].set_visible(False)
        ax[0].spines["top"].set_visible(False)

        ax[1].spines["right"].set_visible(False)
        ax[1].spines["top"].set_visible(False)

        ax[0].yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
        ax[0].set_ylabel(self.units)
            
        ax[1].yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
        ax[1].set_ylabel(self.units)

        ax[0].xaxis.set_major_formatter(DateFormatter('%-m/%-d/%y'))
#        ax[0].xaxis.set_major_locator(plt.MaxNLocator(6))

        ax[1].xaxis.set_major_formatter(DateFormatter('%-m/%-d/%y'))
#        ax[1].xaxis.set_major_locator(plt.MaxNLocator(6))


        # plot usage once, applies to all

        for supply, storage_balance, color, label in zip(supply_series, storage_balance_series, colors, labels):
            ax[0].step(self.times, supply, where = "post", label = label, color = color, linewidth=1)
            ax[1].step(self.times, storage_balance, where = "post", color = color, linewidth=1)

        ax[0].step(self.times, self.usage, where = "post", label = "Usage", color = "blue", linewidth=1)

        ax[0].legend(loc = legend_position)
        ax[0].set_title("Hourly Supply/Usage", fontsize = 8)
        ax[1].set_title("Storage Drawdown from Maximum", fontsize = 8)

        if path is not None:
            plt.savefig(path)
        plt.show()
        plt.close()
    
    def __init__(self, heu: HourlyEnergyUsage, start: datetime, end: datetime, units: str):
        self.start = start
        self.end = end
        times, usage = list(zip(*heu.usage_series_for_days(start, end, hoursOnly = True)))
        self.times = list(times)

        usage = list(usage)
        if(max(usage) > 7000):
            self.usage = [u / 1000 for u in usage]
            self.units = "GWh" if units == "MWh" else "MWh"
        else:
            self.usage = usage
            self.units = units                
        self.supplyGenerator = SupplyGenerator(list(self.times), list(self.usage))

    def apply_supply(self,
                     generator_functions: List[Callable],
                     labels: List[str] = None,
                     legend_position = "upper left",
                     path: str = None,
                     colors: List[str] = None,
                     print_series = False):
        supply_series = []
        storage_balance_series = []
        for generator_function in generator_functions:
            supply = generator_function()
            net_to_storage = [s - u for (s, u) in zip(supply, self.usage)]
            storage_balance = [0] * len(supply)
            
            for i in range(len(self.times)):
                prev = 0 if i == 0 else storage_balance[i-1]
                storage_balance[i] = min(0, prev + net_to_storage[i])

            supply_series.append(supply)
            storage_balance_series.append(storage_balance)
            

            if print_series:
                df = pd.DataFrame({"Times": self.times,
                                   "Date": [t.date() for t in self.times],
                                   "Usage": self.usage,
                                   "Supply": supply,
                                   "Storage Balance": storage_balance})
                
                grouped =  df.groupby("Date")["Usage"].sum(numeric_only = True).reset_index()
                print(grouped[["Date", "Usage"]])

            print(f"Largest Storage Drawdown: {min(storage_balance):.1f} {self.units} ")
            print(f"Sum usage: {sum(self.usage):,.1f} {self.units}")
            print(f"Max usage: {max(self.usage):,.1f} {self.units}")
            print(f"Sum supply: {sum(supply):,.1f} {self.units}")
            print(f"Average supply: {np.average(supply):,.1f} {self.units}")


        self.plotStorageAnalysis(supply_series,
                                 storage_balance_series,
                                 labels = labels,
                                 legend_position = legend_position,
                                 path = path,
                                 colors = colors)

  


             

    
    


