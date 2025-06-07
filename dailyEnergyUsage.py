import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from dataclasses import dataclass

from abc import ABC, abstractmethod
from timeSeriesEnergyUsage import TimeSeriesEnergyUsage

from dateSupplements import DateSupplements

class DailyEnergyUsage(TimeSeriesEnergyUsage):

    @abstractmethod
    def process_table(self):
        pass

    def __init__(self, path):
        self.process_table(path)

    def usage_by_month(self, start: datetime = None, end: datetime = None):
        if(start == None): start = self.first
        if(end == None): end = self.last

# get a list of complete months
        month_starts, month_ends = DateSupplements.month_starts_ends(start, end, complete_months_only = True)

        start = max(start, month_starts[0])
        end = min(end, month_ends[-1])
       
        days_to_get = [(d >= start and d <= end) for d in self.table["Date"]]

        filtered_table = (self.table[days_to_get]).copy()
        filtered_table["Month"] = [datetime(d.year, d.month, 1) for d in filtered_table["Date"]]

        month_sums = (filtered_table.groupby("Month"))["Usage"].sum().reset_index()
        print(month_sums)
        return month_sums


    def usage_monthly_average(self, start: datetime = None, end: datetime = None):
        usage_df = self.usage_by_month(start, end)
        usage_df["Month Number"] = [d.month for d in usage_df["Month"]]
        averages = usage_df.groupby("Month Number").mean().reset_index()
        print(averages)
        return averages

    
