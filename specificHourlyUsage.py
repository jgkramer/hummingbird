import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from dataclasses import dataclass

from rate_series import RateSegment, RateSeries, RatePlan
from fetch_seasons import Season
from region import Region

from hourlyEnergyUsage import HourlyEnergyUsage, UsageStats

import pdb


@dataclass(frozen = True)
class UsagePaths:
    NV_Kramer = "usage_data/NV_Kramer_22Nov.csv"
    NV_Kramer_23May = "usage_data/NV_Kramer_22Nov.csv"
    SD_Marshall = "usage_data/Marshall_SanDiego_11-1-2021_11-11-2022_2022.csv"
    MA_Littlefield = "usage_data/Wellesley-30_Bellevue-15MIN.csv"


class NVenergyUsage(HourlyEnergyUsage):
    def process_table(self, usage_path):
        table = pd.read_csv(usage_path)
        table["startDateTime"] = table["startTime"].apply(lambda s: (datetime.strptime(s, "%m/%d/%y %H:%M")))
    
        self.table = table[["startDateTime", "Usage"]].copy()
        self.first_date = min(self.table["startDateTime"])
        self.last_date = max(self.table["startDateTime"])
        self.units = "kWh"
        self.minutes = 15


class SDenergyUsage(HourlyEnergyUsage):
    def process_table(self, usage_path):
        table = pd.read_csv(usage_path)
        combined_start = [" ".join([d, t]) for d, t in zip(table["Date"], table["Start Time"])]
        combined_start = [datetime.strptime(s, "%m/%d/%y %I:%M %p") for s in combined_start]
        self.table = pd.DataFrame({"startDateTime": combined_start,
                                   "Usage": table["Consumption"]})

        self.first_date = min(self.table["startDateTime"])
        self.last_date = max(self.table["startDateTime"])
        self.units = "kWh"
        self.minutes = 15

class LittlefieldEnergyUsage(HourlyEnergyUsage):
    def process_table(self, usage_path):
        table = pd.read_csv(usage_path)
        table["startDateTime"] = table["Time Bucket (America/New_York)"].apply(lambda s: (datetime.strptime(s, "%m/%d/%y %H:%M")))
        table["Usage"] = table["30 Bellevue-Mains_A (kWatts)"] + table["30 Bellevue-Mains_B (kWatts)"] - table["30 Bellevue-Electric Vehicle/RV-Tesla Charger (kWatts)"]
        self.table = table[["startDateTime", "Usage"]].copy()
        self.units = "kWh"


class EIARegionUsage(HourlyEnergyUsage):

    def timeparse(s):
        # we'll stick with local time because we're not being super precise about times of day
        
        # dst = True if s.split(". ", 1)[1] == "PDT" else False
        time = datetime.strptime((s.split("m", 1)[0] + "m").replace(".", ""), "%m/%d/%Y %I %p")
        # because these CSV files specify the end of the hour rather than beginning
        return time + relativedelta(hours = -1)
    
    def process_table(self, usage_paths):
        assert isinstance(usage_paths, list)
        dfs = []
        for path in usage_paths:
            df = pd.read_csv(path)
            dfs.append(df)
        
        table = pd.concat(dfs)
        table["startDateTime"] = table["Timestamp (Hour Ending)"].apply(EIARegionUsage.timeparse)
        table["Usage"] = table["Demand (MWh)"]
        table["Forecast"] = table["Demand Forecast (MWh)"]
        table.drop_duplicates(subset = ["startDateTime"], inplace = True)
        self.table = table[["startDateTime", "Usage", "Forecast"]].copy()
        self.first_date = min(self.table["startDateTime"])
        self.last_date = max(self.table["startDateTime"])
        self.units = "MWh"

    def forecast_v_actual(self, start: datetime, end: datetime):
        fil = self.table["startDateTime"].apply(lambda d: start <= d and d < end)
        filtered = self.table[fil]


        return zip(filtered["startDateTime"].copy(), filtered["Usage"].copy(), filtered["Forecast"].copy())


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

    
    
    
    
