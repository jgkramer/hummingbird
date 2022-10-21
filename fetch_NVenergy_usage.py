import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from rate_series import RateSegment, RateSeries, RatePlan
from fetch_seasons import Season
from region import Region

USAGE_PATH = "usage_data/Sep21-Aug22energy.csv"


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
        return sum(cost)
        

if __name__ == "__main__":
    usage = NVenergyUsage()

    region = Region("NV")
    plans = region.get_rate_plans()
    
    for plan in plans:
        d = datetime(2021, 9, 1).date()
        d2 = datetime(2021, 9, 15).date()
        print("Plan: " + plan.plan_name)
        print("Cost: " + str(usage.total_cost_for_days(plan, d, d2)))


    
    
