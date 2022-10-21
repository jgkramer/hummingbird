import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

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


    def total_cost_for_days(self, rate_plan: RatePlan, start_date: date, end_date: date):

        end_datetime = datetime(end_date.year, end_date.month, end_date.day)
        start_datetime = datetime(start_date.year, start_date.month, start_date.day)

        day_list = [start_date + timedelta(days = i) for i in range((end_date - start_date).days + 1)]

        fil = self.table["startDateTime"].apply(lambda x: x.date() in day_list)
        filtered_table = self.table[fil]

        times = filtered_table["startDateTime"]
        usage = filtered_table["Usage"]
        rateSegments = filtered_table["startDateTime"].apply(rate_plan.ratesegment_from_datetime)
        cost = [(u * r.rate) for u, r in zip(usage, rateSegments)]
        print(len(cost))
#       print(cost)
        print(sum(cost))
        return sum(cost)
        

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
        d = datetime(2021, 9, 1, 5).date()
        d2 = datetime(2022, 8, 31, 4).date()
        print(type(d))
        usage.total_cost_for_days(rate_plan, d, d2)


## NEXT - RATESERIES NEEDS TO REPLACE SEASON STR with SEASON OBJECT                


    
    
