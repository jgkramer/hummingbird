import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from dataclasses import dataclass

from abc import ABC, abstractmethod
from timeSeriesEnergyUsage import TimeSeriesEnergyUsage

from dateSupplements import DateSupplements

class MonthlyEnergyUsage(TimeSeriesEnergyUsage):

    @abstractmethod
    def process_table(self):
        pass

    def __init__(self, path):
        self.process_table(path)


    def normalize_table(self, table: pd.DataFrame):

        earliest_read = min(table["Read Date"])
        self.first = datetime(earliest_read.year, earliest_read.month, 1)
        self.last = max(table["Read Date"])
        
        starts, ends = DateSupplements.month_starts_ends(self.first,
                                                         self.last,
                                                         complete_months_only = True)
#        print(table)

        self.table = pd.DataFrame()
        self.table["Month Start"] = starts
        self.table["Month End"] = ends
        bills = list(table["Read Date"].iloc[0:-1])

        days_before = [((bill - start).days + 1) for (bill, start) in zip(bills, starts)]
        days_after = [((end - bill).days) for (end, bill) in zip(ends, bills)]

        usage_before = list(table["Usage per Day"].iloc[0:-1])
        usage_after = list(table["Usage per Day"].iloc[1:])        

        self.table["Monthly Usage"] = [(db * ub + da * ua) for (db, da, ub, ua)
                                       in zip(days_before, days_after, usage_before, usage_after)]

    def usage_by_month(self, start: datetime = None, end: datetime = None):
        if(start == None): start = self.first
        if(end == None): end = self.last
        months_to_get = [(ms >= start and ms <= end) for ms in self.table["Month Start"]]
        months = list((self.table["Month Start"])[months_to_get])
        usage = list((self.table["Monthly Usage"])[months_to_get])

        df = pd.DataFrame(list(zip(months, usage)), columns = ["Month", "Usage"])

#        print(df)
        return df


    def usage_monthly_average(self, start: datetime = None, end: datetime = None):
        usage_df = self.usage_by_month(start, end)
        usage_df["Month Number"] = [d.month for d in usage_df["Month"]]
        averages = usage_df.groupby("Month Number").mean(numeric_only = True).reset_index()
#        print(averages)
        return averages
    
        
        
        
        
    
        
                

    
