from specificHourlyUsage import NVenergyUsage, SDenergyUsage, UsagePaths
from hourlyEnergyUsage import HourlyEnergyUsage

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta


from cumulativePlots import CumulativePlots

if __name__ == "__main__":
    NVE = NVenergyUsage(UsagePaths.NV_Kramer)
    date_list = [datetime(2022, 8, 15)]
    CumulativePlots.dailyUseVsAverage(NVE, date_list, "test.png")
  #  CumulativePlots.dailyUseVsAverage(SDE, date_list, "test2.png", cumulative = False)

    start = datetime(2021, 9, 1)
    end = datetime(2021, 9, 30)
    
    CumulativePlots.periodUseVsAverage(NVE, start, end)
    
