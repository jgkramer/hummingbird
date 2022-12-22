
from specificHourlyUsage import NVenergyUsage, SDenergyUsage, UsagePaths
from hourlyEnergyUsage import HourlyEnergyUsage

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta


from cumulativePlots import CumulativePlots

if __name__ == "__main__":
    NVE = NVenergyUsage(UsagePaths.NV_Kramer)

    start = datetime(2022, 8, 1)
    end = datetime(2022, 8, 31)

    days = NVE.get_day_list(start, end)
    for day in days:
        d = datetime(day.year, day.month, day.day)
        time, usage = list(zip(*NVE.usage_series_for_day(d, hoursOnly = False)))
        print(str(day) + " " + str(max(usage)))

    CumulativePlots.dailyUseVsAverage(NVE, [datetime(2022, 8, 1)], "test.png", cumulative = False)
    
