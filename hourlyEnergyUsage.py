import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from dataclasses import dataclass

from rate_series import RateSegment, RateSeries, RatePlan
from fetch_seasons import Season
from region import Region

from abc import ABC, abstractmethod

@dataclass
class UsageStats:
    label: str
    kWh: float
    cost: float

class HourlyEnergyUsage(ABC):

    @abstractmethod
    def process_table(self):
        pass

    def __init__(self, path):
        self.table = pd.read_csv(path)
        self.process_table(path)

    def print(self, n=96):
        print(self.table.head(n))

    def get_day_list(self, start: datetime, end: datetime):
        day_list = [start + timedelta(days = i) for i in range((end - start).days + 1)]
        return [day.date() for day in day_list]

    def usage_series_for_days(self, start: datetime, end: datetime, ratesegment = None):
        day_list = self.get_day_list(start, end)
        print(day_list)
        print(type(day_list))
        if ratesegment == None:
            #only get data for the days that are in the list of days we're looking for
            fil = self.table["startDateTime"].apply(lambda x: x.date() in day_list)

            #only get data for days that are in list of days we're looking for AND if it is the rate segment we're looking at
        else:
            fil = self.table["startDateTime"].apply(lambda x: x.date() in day_list) and ratesegment.in_segment(x)

        filtered_table = self.table[fil]
        return zip(filtered_table["startDateTime"].copy(), filtered_table["Usage"].copy())

    def usage_series_for_day(self, d: datetime, ratesegment = None):
        return self.usage_series_for_days(d, d, ratesegment)

    def stats_by_period(self, rate_plan: RatePlan, start: datetime, end: datetime = None):
        if(end == None): end = start

        day_list = self.get_day_list(start, end)
        print(day_list)
        print(type(day_list))
        filtered_table = self.table[self.table["startDateTime"].apply(lambda x: x.date() in day_list)].copy()
        filtered_table["Segment"] = filtered_table["startDateTime"].apply(rate_plan.ratesegment_from_datetime)
        segment_labels = set([s.label for s in filtered_table["Segment"]])
        filtered_table["Cost"] = [(u * r.rate) for u, r in zip(filtered_table["Usage"], filtered_table["Segment"])]
        results = []
        for segment_label in segment_labels:
            usage = sum(u for (u, s) in zip(filtered_table["Usage"], filtered_table["Segment"]) if s.label == segment_label)
            cost = sum(c for (c, s) in zip(filtered_table["Cost"], filtered_table["Segment"]) if s.label == segment_label)
            results.append(UsageStats(label = segment_label, kWh = usage, cost = cost))

        return results

    def usage_by_hour_for_period(self, start: datetime, end: datetime):
        nDays = (end.date()-start.date()).days + 1

        list_of_tuples = list(self.usage_series_for_days(start, end))
        df = pd.DataFrame(list_of_tuples, columns = ["time", "usage"])
        df["hour"] = [t.hour for t in df["time"]]
        df["usage"] = df["usage"].apply(lambda x: x/nDays)
        grouped = df.groupby("hour")["usage"].sum()
        hours = np.unique((df["hour"]))
        return (hours, grouped)


    
        
    
