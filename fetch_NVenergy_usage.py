import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from rate_series import RateSegment, RateSeries, RatePlan
from fetch_seasons import Season
from region import Region

import pdb

USAGE_PATH = "usage_data/1Sep22energy.csv"


class UsageStats:
    label: str
    kWh: float
    cost: float

class NVenergyUsage:
    def __init__(self, usage_path = USAGE_PATH):
        self.table = pd.read_csv(usage_path)
        print(self.table.head(12))
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
        filtered_table = self.table[fil].copy()

#        times = filtered_table["startDateTime"]
#        usage = filtered_table["Usage"]


        filtered_table["Segment"] = filtered_table["startDateTime"].apply(rate_plan.ratesegment_from_datetime)
        filtered_table["SegmentLabel"] = [s.label for s in filtered_table["Segment"]]
        filtered_table["Cost"] = [(u * r.rate) for u, r in zip(filtered_table["Usage"], filtered_table["Segment"])]

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
    
#        print(filtered_table[["startDateTime", "SegmentLabel", "Usage", "Cost"]])

        grouped = filtered_table.groupby("SegmentLabel")
        print(grouped.sum())
        
#        print((zip(usage, rateSegments)))
        
        return sum(filtered_table["Cost"])
        

if __name__ == "__main__":
    usage = NVenergyUsage()

    states = ["NV"]

    for state in states:
        region = Region(state)
        plans = region.get_rate_plans()

        for plan in plans:
            d = datetime(2022, 9, 1).date()
            d2 = datetime(2022, 9, 1).date()
            print("State: " + state)
            print("Plan: " + plan.plan_name)
            print("Cost: " + str(usage.total_cost_for_days(plan, d, d2)))


    
    
