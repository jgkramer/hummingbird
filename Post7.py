from specificHourlyUsage import NVenergyUsage, UsagePaths
from hourlyEnergyUsage import HourlyEnergyUsage

from dailyPlots import DailyPlots

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from dateSupplements import DateSupplements

from typing import List

from rate_series import RateSegment, RateSeries, RatePlan
from fetch_seasons import Season
from region import Region

import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, PercentFormatter)

from hourlyEnergyUsage import UsageStats, HourlyEnergyUsage
from specificHourlyUsage import NVenergyUsage

if __name__ == "__main__":
    NVE = NVenergyUsage(UsagePaths.NV_Kramer)

    date_list = [datetime(2022, 8, 16), datetime(2022, 8, 22)]
    
    colors_list = ["steelblue", "blue", "salmon", "red"]
#    colors_list = ['blue', 'dodgerblue', 'steelblue', 'salmon', 'lightpink', 'hotpink', 'red', 'pink', 'indianred', 'deeppink']


    DailyPlots.plot_intraday_usage(NVE, date_list, path = None, colors_list = colors_list)  

    plans = Region("NV").get_rate_plans()
    for plan in plans:
        print("plan: ", plan.plan_name)
        for d in date_list:
            print("date: ", d)
            usage_stats = NVE.stats_by_period(plan, d)
            print(usage_stats)


        

    

        

