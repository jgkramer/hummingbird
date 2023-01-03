import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from typing import List

import matplotlib.pyplot as plt
import pytz


def timeparse(s):
    dst = True if s.split(". ", 1)[1] == "PDT" else False
    time = datetime.strptime((s.split("m", 1)[0] + "m").replace(".", ""), "%m/%d/%Y %I %p")
    if(dst):
        return time + relativedelta(hours = -2)
    else:
        return time + relativedelta(hours = -1)

def month_of(d: datetime):
    return datetime(d.year, d.month, 1)

class EIAGeneration:

    def averageDayInPeriod(self, start: datetime, end: datetime):
        fil = self.df["Start Time"].apply(lambda d: start <= d and d < end)
        df_filtered = self.df[fil]
        hour_averages = (df_filtered.groupby("Hour"))["Solar Generation (MWh)"].mean(numeric_only = True).reset_index()
        return (hour_averages["Hour"].copy(), hour_averages["Solar Generation (MWh)"].copy())

    def averageDayInPeriodFiltered(self, start: datetime, end: datetime, N: int = None):
        daily_sums = self.dailyTotalsDF(start, end)
        threshold = 0
        if(N == None):
            threshold = np.median(daily_sums["Solar Generation (MWh)"])
        else:
            threshold = np.min((daily_sums.nlargest(N, "Solar Generation (MWh)"))["Solar Generation (MWh)"])
        
        daily_sums["Include"] = daily_sums["Solar Generation (MWh)"].apply(lambda x: x >= threshold)
        include_day = {}
        for day, include in zip(daily_sums["Date"], daily_sums["Include"]):
            include_day[day] = include

        fil = self.df["Start Time"].apply(lambda d: (start <= d and d < end and include_day[d.date()]))
        df_filtered = self.df[fil]
        hour_averages = (df_filtered.groupby("Hour"))["Solar Generation (MWh)"].mean(numeric_only = True).reset_index()
        return (hour_averages["Hour"].copy(), hour_averages["Solar Generation (MWh)"].copy())


    def dailyTotalsDF(self, start: datetime, end: datetime):
        fil = self.df["Start Time"].apply(lambda d: start <= d and d < end)
        df_filtered = self.df[fil]
        daily_sums = (df_filtered.groupby("Date"))["Solar Generation (MWh)"].sum(numeric_only = True).reset_index().copy()
        return daily_sums
    

    def dailyTotals(self, start: datetime, end: datetime):
        ds = self.dailyTotalsDF(start, end)
        ds["Month"] = ds["Date"].apply(month_of)
        monthly_average = (ds.groupby("Month"))["Solar Generation (MWh)"].mean(numeric_only = True).reset_index()
        print("all ")
        print(monthly_average)
        
        return (ds["Date"], ds["Solar Generation (MWh)"])
        

    def topHalfOnly(self, start: datetime, end: datetime):
        ds = self.dailyTotalsDF(start, end)
        ds["Month"] = ds["Date"].apply(month_of)
        month_medians = (ds.groupby("Month"))["Solar Generation (MWh)"].median(numeric_only = True).reset_index().copy()
        
        month_medians_dict = {}
        for month, median in zip(month_medians["Month"], month_medians["Solar Generation (MWh)"]):
            month_medians_dict[month.to_pydatetime()] = median
        
        ds["Include"] = ds.apply(lambda row: (row["Solar Generation (MWh)"] > month_medians_dict[row["Month"]]), axis = 1)

        ds_filtered = ds[ds["Include"]].copy()
        monthly_average = (ds_filtered.groupby("Month"))["Solar Generation (MWh)"].mean(numeric_only = True).reset_index()
        print("top half only")
        print(monthly_average)
        
        return (ds_filtered["Date"], ds_filtered["Solar Generation (MWh)"])
        
    def topNOnly(self, start: datetime, end: datetime, N: int = 3):
        ds = self.dailyTotalsDF(start, end)
        ds["Month"] = ds["Date"].apply(month_of)

        month_top_N = (ds.groupby("Month"))["Solar Generation (MWh)"].nlargest(n = N).reset_index().copy()
        month_Nth_highest = (month_top_N.groupby("Month"))["Solar Generation (MWh)"].min().reset_index().copy()
        print(month_Nth_highest)

        month_Nth_dict = {}
        for month, Nth in zip(month_Nth_highest["Month"], month_Nth_highest["Solar Generation (MWh)"]):
            month_Nth_dict[month.to_pydatetime()] = Nth

        ds["Include"] = ds.apply(lambda row: (row["Solar Generation (MWh)"] >= month_Nth_dict[row["Month"]]), axis = 1)

        ds_filtered = ds[ds["Include"]].copy()
        monthly_average = (ds_filtered.groupby("Month"))["Solar Generation (MWh)"].mean(numeric_only = True).reset_index()
        print("top 3 only")
        print(monthly_average)

        return (ds_filtered["Date"], ds_filtered["Solar Generation (MWh)"])

        

            
    def __init__(self, paths: List[str]):
        dfs = []
        for path in paths:
            df = pd.read_csv(path)
            dfs.append(df)

        self.df = pd.concat(dfs)
        print(self.df.columns)

        self.df["Start Time"] = self.df["Timestamp (Hour Ending)"].apply(timeparse)
        self.df["Hour"] = self.df["Start Time"].apply(lambda d: d.hour)
        self.df["Date"] = self.df["Start Time"].apply(lambda d: d.date())
        

            
if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    

    
        
