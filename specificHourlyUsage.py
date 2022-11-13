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
    SD_Marshall = "usage_data/Marshall_SanDiego_11-1-2021_11_11-2022_2022.csv"


class NVenergyUsage(HourlyEnergyUsage):
    def process_table(self, usage_path):
        self.table = pd.read_csv(usage_path)
        self.table["startDateTime"] = self.table["startTime"].apply(lambda s: (datetime.strptime(s, "%Y-%m-%d %H:%M:%S")))
    
        self.table = self.table[["startDateTime", "Usage"]]
        self.first_date = min(self.table["startDateTime"])
        self.last_date = max(self.table["startDateTime"])

if __name__ == "__main__":
    NVE = NVenergyUsage()
    NVE.print()
    states = ["NV"]

    s = datetime(2022, 8, 1)
    s2 = datetime(2022, 8, 31)

    print(NVE.usage_by_hour_for_period(s, s2))
    
    
