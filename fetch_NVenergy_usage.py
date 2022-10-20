import numpy as np
import pandas as pd
from datetime import datetime

from typing import List
from rate_series import RateSegment, RateSeries, RatePlan
from fetch_rates import RatesData
from fetch_times import TimesData
from fetch_seasons import Season, SeasonsData

USAGE_PATH = "usage_data/Sep21-Aug22energy.csv"


class NVenergyUsage:
    def __init__(self, usage_path = USAGE_PATH):
        self.table = pd.read_csv(usage_path)
        self.table["startDateTime"] = self.table["startTime"].apply(lambda s: (datetime.strptime(s, "%m/%d/%y %H:%M")))
        self.table["endDateTime"]=  self.table["endTime"].apply(lambda s: (datetime.strptime(s, "%m/%d/%y %H:%M")))
    
        self.table = self.table[["unit", "startDateTime", "endDateTime", "Usage"]]

    def print(self, n=96):
        print(self.table.head(n))

    def total_cost_for_day(self, rate_plan: RatePlan, d: datetime = None):
        print(d)
        fil = self.table["startDateTime"].apply(lambda x: x.date() == d.date())
        filtered_table = self.table[fil]
        print(filtered_table)

        times = filtered_table["startDateTime"]
        apply = filtered_table["startDateTime"].apply(rate_plan.ratesegment_from_datetime)
        for t, a in zip(times, apply):
            print(t)
            print(a)       


if __name__ == "__main__":
    usage = NVenergyUsage()
    print(usage.table.columns)
#    usage.print()

    sd = SeasonsData()
    rd = RatesData()
    td = TimesData()

    plans = rd.plans_for_state("NV")
    for plan in plans:
        rate_plan = RatePlan("NV", plan, plan, td, rd, sd)
        d = datetime(2022, 8, 31)
        print(d)
        usage.total_cost_for_day(rate_plan, d)
        

## NEXT - RATESERIES NEEDS TO REPLACE SEASON STR with SEASON OBJECT                


    
    
