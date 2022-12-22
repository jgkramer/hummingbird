import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from dataclasses import dataclass

from rate_series import RateSegment, RateSeries, RatePlan
from fetch_seasons import Season
from region import Region
from dateSupplements import DateSupplements

from abc import ABC, abstractmethod
from timeSeriesEnergyUsage import TimeSeriesEnergyUsage

@dataclass
class UsageStats:
    label: str
    kWh: float
    cost: float

class HourlyEnergyUsage(TimeSeriesEnergyUsage):

    @abstractmethod
    def process_table(self):
        pass

    def __init__(self, path):
        self.process_table(path)

    def print(self, n=96):
        print(self.table.head(n))

    def get_day_list(self, start: datetime, end: datetime):
        day_list = [start + timedelta(days = i) for i in range((end - start).days + 1)]
        return [day.date() for day in day_list]

    def usage_series_for_days(self, start: datetime, end: datetime, hoursOnly = False, ratesegment = None):
        day_list = self.get_day_list(start, end)
        if ratesegment == None:
            #only get data for the days that are in the list of days we're looking for
            fil = self.table["startDateTime"].apply(lambda x: x.date() in day_list)

            #only get data for days that are in list of days we're looking for AND if it is the rate segment we're looking at
        else:
            fil = self.table["startDateTime"].apply(lambda x: x.date() in day_list) and ratesegment.in_segment(x)

        filtered_table = self.table[fil]
        if(not hoursOnly):
            return zip(filtered_table["startDateTime"].copy(), filtered_table["Usage"].copy())
        
        else:
            filtered_table["HourOnly"] = filtered_table["startDateTime"].apply(
                lambda d: datetime(d.year, d.month, d.day, d.hour))
            hour_sums = (filtered_table.groupby("HourOnly"))["Usage"].sum(numeric_only = True).reset_index()
            return zip(hour_sums["HourOnly"].copy(), hour_sums["Usage"].copy())

                                          
    def usage_series_for_day(self, d: datetime, hoursOnly = False, ratesegment = None):
        return self.usage_series_for_days(d, d, hoursOnly, ratesegment)

    def stats_by_period(self, rate_plan: RatePlan, start: datetime, end: datetime = None):
        if(end == None): end = start

        day_list = self.get_day_list(start, end)
        print(day_list)
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
        grouped = df.groupby("hour")["usage"].sum(numeric_only = True)
        hours = np.unique((df["hour"]))
        return (hours, grouped)

    def usage_by_month(self, start: datetime = None, end: datetime = None):
        if(start == None): start = self.first_date
        if(end == None): end = self.last_date

        month_starts, month_ends = DateSupplements.month_starts_ends(start, end, complete_months_only = True)

        start = max(start, month_starts[0])
        end = min(end, month_ends[-1])
       
        days_to_get = [(d >= start and d <= end) for d in self.table["startDateTime"]]

        filtered_table = (self.table[days_to_get]).copy()
        filtered_table["Month"] = [datetime(d.year, d.month, 1) for d in filtered_table["startDateTime"]]

        month_sums = (filtered_table.groupby("Month"))["Usage"].sum(numeric_only = True).reset_index()
        return month_sums

    def usage_monthly_average(self, start: datetime = None, end: datetime = None):
        usage_df = self.usage_by_month(start, end)
        usage_df["Month Number"] = [d.month for d in usage_df["Month"]]
        averages = usage_df.groupby("Month Number").mean(numeric_only = True).reset_index()
        return averages



    
        
    
