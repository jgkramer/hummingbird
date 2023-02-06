
from specificHourlyUsage import NVenergyUsage, SDenergyUsage, UsagePaths
from hourlyEnergyUsage import HourlyEnergyUsage

import matplotlib.pyplot as plt
from matplotlib.axis import Tick
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, PercentFormatter)

import math

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from typing import List, Callable


class SupplyGenerator:
    def __init__(self, times: List[datetime], usage: List[float]):
        self.times = times
        self.usage = usage
        
    def period_average(self, multiplier = 1.0):
        period_average = np.average(self.usage)
        function = [multiplier * period_average for dt in self.times]
        return function

    def percent_of_max(self, multiplier = 1.0):
        period_max = max(self.usage)
        function = [multiplier * period_max for dt in self.times]
        return function
                       

    def top_percentile_days(self, percentile: float = 0.95):
        df = pd.DataFrame({"Time": self.times,
                           "Date": [t.date() for t in self.times],
                           "Usage": self.usage})

        grouped = df.groupby("Date")["Usage"].max().reset_index()
        print(grouped)
        ndays = len(grouped["Date"])
        top_days = math.ceil((1 - percentile)*len(grouped["Date"]))
        threshold = np.partition(grouped["Usage"], -top_days)[-top_days]
        function = [threshold for dt in self.times]
        return function
        
class StorageAnalyzer():

    def plotStorageAnalysis(self, supply, net_to_storage, storage_balance):
        plt.rcParams.update({'font.size': 8})
        fig, ax = plt.subplots(ncols = 1, nrows = 2, figsize = (7.5, 5),
                               gridspec_kw = {"height_ratios": [2, 1]})
        fig.tight_layout(pad = 2.0)

        ax[0].step(self.times, self.usage, where = "post", label = "Usage")
        ax[0].step(self.times, supply, where = "post", label = "Supply")
#        ax[0].step(self.times, net_to_storage, where = "post", label = "Net to (from) Storage")
        ax[0].spines["right"].set_visible(False)
        ax[0].spines["top"].set_visible(False)
        ax[0].legend(loc = "upper left")

        ax[1].step(self.times, storage_balance, where = "post", label = "Storage Balance")
        ax[1].legend(loc = "upper left")
        ax[1].spines["right"].set_visible(False)
        ax[1].spines["top"].set_visible(False)


        ax[0].yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))
        ax[1].yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))
        
        plt.show()
        plt.close()
    
    def __init__(self, heu: HourlyEnergyUsage, start: datetime, end: datetime):
        self.heu = heu
        self.start = start
        self.end = end
        times, usage = list(zip(*heu.usage_series_for_days(start, end, hoursOnly = True)))
        self.times = list(times)
        self.usage = list(usage)
        self.supplyGenerator = SupplyGenerator(list(self.times), list(self.usage))

    def apply_supply(self, generator_function: Callable):
        supply = generator_function()
        net_to_storage = [s - u for (s, u) in zip(supply, self.usage)]
        storage_balance = [0] * len(supply)

        for i in range(len(self.times)):
            prev = 0 if i == 0 else storage_balance[i-1]
            storage_balance[i] = min(0, prev + net_to_storage[i])

        df = pd.DataFrame({"Time": self.times,
                           "Supply": supply,
                           "Usage": self.usage,
                           "Net to Storage": net_to_storage,
                           "Storage Balance": storage_balance})
    
        print(df)
        self.plotStorageAnalysis(supply, net_to_storage, storage_balance)
  

if __name__ == "__main__":
    pd.options.display.max_rows = None
    
    hourly = NVenergyUsage(UsagePaths.NV_Kramer)

    start = datetime(2021, 9, 1)
    end = datetime(2021, 9, 15)
    
    analyzer = StorageAnalyzer(hourly, start, end)
    analyzer.apply_supply(lambda: analyzer.supplyGenerator.percent_of_max(0.70)) 
