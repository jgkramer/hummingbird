import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from dataclasses import dataclass

from rate_series import RateSegment, RateSeries, RatePlan
from fetch_seasons import Season
from region import Region

from hourlyEnergyUsage import HourlyEnergyUsage, UsageStats

import pdb

from typing import List

@dataclass(frozen = True)
class UsagePaths:
    NV_Kramer = "usage_data/Aug21-Oct22energy.csv"
    SD_Marshall = "usage_data/Marshall_SanDiego_11-1-2021_11-11-2022_2022.csv"


class NVenergyUsage(HourlyEnergyUsage):
    def process_table(self, usage_path):
        table = pd.read_csv(usage_path)
        table["startDateTime"] = table["startTime"].apply(lambda s: (datetime.strptime(s, "%Y-%m-%d %H:%M:%S")))
    
        self.table = table[["startDateTime", "Usage"]].copy()
        self.first_date = min(self.table["startDateTime"])
        self.last_date = max(self.table["startDateTime"])


class SDenergyUsage(HourlyEnergyUsage):
    def process_table(self, usage_path):
        table = pd.read_csv(usage_path)
        combined_start = [" ".join([d, t]) for d, t in zip(table["Date"], table["Start Time"])]
        combined_start = [datetime.strptime(s, "%m/%d/%y %I:%M %p") for s in combined_start]
        self.table = pd.DataFrame({"startDateTime": combined_start,
                                   "Usage": table["Consumption"]})

        self.first_date = min(self.table["startDateTime"])
        self.last_date = max(self.table["startDateTime"])


if __name__ == "__main__":
    NVE = NVenergyUsage(UsagePaths.NV_Kramer)
#    NVE.print()
    states = ["NV"]


    s = datetime(2022, 2, 1)
    s2 = datetime(2022, 8, 31)

    print(NVE.usage_by_month())
    print(NVE.usage_monthly_average())

#    SDE = SDenergyUsage(UsagePaths.SD_Marshall)
#    print(SDE.usage_by_month())
#    print(SDE.usage_monthly_average())

    
    
    
    
