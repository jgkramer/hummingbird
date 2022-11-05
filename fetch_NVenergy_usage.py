import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from dataclasses import dataclass

from rate_series import RateSegment, RateSeries, RatePlan
from fetch_seasons import Season
from region import Region

import pdb

from typing import List

USAGE_PATH = "usage_data/Sep21-Aug22energy.csv"

@dataclass
class UsageStats:
    label: str
    kWh: float
    cost: float
    

class NVenergyUsage:
    def __init__(self, usage_path = USAGE_PATH):
        self.table = pd.read_csv(usage_path)
        self.table["startDateTime"] = self.table["startTime"].apply(lambda s: (datetime.strptime(s, "%m/%d/%y %H:%M")))
        self.table["endDateTime"]=  self.table["endTime"].apply(lambda s: (datetime.strptime(s, "%m/%d/%y %H:%M")))
    
        self.table = self.table[["unit", "startDateTime", "endDateTime", "Usage"]]
        self.first_date = min(self.table["startDateTime"])
        self.last_date = max(self.table["startDateTime"])                     

    def print(self, n=96):
        print(self.table.head(n))


    def usage_series_for_days(self, start: datetime, end: datetime, ratesegment = None):
        day_list = [start + timedelta(days = i) for i in range((end - start).days + 1)]
        day_list = [day.date() for day in day_list]

        if ratesegment == None:
            fil = self.table["startDateTime"].apply(lambda x: x.date() in day_list)
        else:
            fil = self.table["startDateTime"].apply(lambda x: (x.date() in day_list) and ratesegment.in_segment(x))
        filtered_table = self.table[fil]
        return zip(filtered_table["startDateTime"], filtered_table["Usage"])

    def usage_series_for_day(self, d: datetime, ratesegment = None):
        return self.usage_series_for_days(d, d, ratesegment)
                
    def stats_by_period(self, rate_plan: RatePlan, start_date: datetime, end_date: datetime = None):
        if(end_date == None): end_date = start_date

        day_list = [start_date + timedelta(days = i) for i in range((end_date - start_date).days + 1)]
        day_list = [day.date() for day in day_list]

        fil = self.table["startDateTime"].apply(lambda x: x.date() in day_list)
        filtered_table = self.table[fil].copy()
        filtered_table["Segment"] = filtered_table["startDateTime"].apply(rate_plan.ratesegment_from_datetime)
        segment_labels = set([s.label for s in filtered_table["Segment"]])
        filtered_table["Cost"] = [(u * r.rate) for u, r in zip(filtered_table["Usage"], filtered_table["Segment"])]
        results = []
        for segment_label in segment_labels:
            usage = sum(u for (u, s) in zip(filtered_table["Usage"], filtered_table["Segment"]) if s.label == segment_label)
            cost = sum(c for (c, s) in zip(filtered_table["Cost"], filtered_table["Segment"]) if s.label == segment_label)
            results.append(UsageStats(label = segment_label, kWh = usage, cost = cost))

        return results
        
if __name__ == "__main__":
    usage = NVenergyUsage()
    states = ["NV"]

    for state in states:
        plans = Region(state).get_rate_plans()

        for plan in plans:
            print(plan)
            d = datetime(2022, 8, 15)
            print("State: " + state, "Plan: " + plan.plan_name)
            print((usage.totals_for_days_by_period(plan, d)))


    
    
