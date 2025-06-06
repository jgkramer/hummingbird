import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from typing import List

import matplotlib.pyplot as plt
import pytz


def timeparse(s):
    dst = True if s.split(". ", 1)[1] in ["PDT", "EDT", "MDT", "CDT"] else False
    time = datetime.strptime((s.split("m", 1)[0] + "m").replace(".", ""), "%m/%d/%Y %I %p")
    if(dst):
        return time + relativedelta(hours = -2)
    else:
        return time + relativedelta(hours = -1)

def month_of(d: datetime):
    return datetime(d.year, d.month, 1)

def dayList(start: datetime, end: datetime):
    ndays = (end-start).days
    l = [start + timedelta(days = i) for i in range(ndays)]
    return l

class EIAGeneration:

    def allHoursInDay(self, my_day: datetime):
        fil = self.df["Start Time"].apply(lambda d: my_day.date() == d.date())
        df_filtered = self.df[fil]
        return df_filtered["Solar Generation (MWh)"].copy()

    def allHoursInDays(self, start: datetime, end: datetime):
        days = dayList(start, end)
        generations = [self.allHoursInDay(d) for d in days]
        return (days, generations)

    def averageDayInPeriod(self, start: datetime, end: datetime):
        fil = self.df["Start Time"].apply(lambda d: start <= d and d < end)
        df_filtered = self.df[fil]
        hour_averages = (df_filtered.groupby("Hour"))["Solar Generation (MWh)"].mean(numeric_only = True).reset_index()
        return (hour_averages["Hour"].copy(), hour_averages["Solar Generation (MWh)"])
        
    def averageDayInPeriodFiltered(self, start: datetime, end: datetime, N: int = 5):
        daily_sums = self.dailyTotalsDF(start, end)
        threshold = np.min((daily_sums.nlargest(N, "Solar Generation (MWh)"))["Solar Generation (MWh)"])
        
        daily_sums["Include"] = daily_sums["Solar Generation (MWh)"].apply(lambda x: x >= threshold)
        include_day = {}
        for day, include in zip(daily_sums["Date"], daily_sums["Include"]):
            include_day[day] = include

        fil = self.df["Start Time"].apply(lambda d: (start <= d and d < end and include_day[d.date()]))
        df_filtered = self.df[fil]
        hour_averages = (df_filtered.groupby("Hour"))["Solar Generation (MWh)"].mean(numeric_only = True).reset_index()
        return (hour_averages["Hour"].copy(), hour_averages["Solar Generation (MWh)"].copy())


    def averageDayInPeriodFilteredHourly(self, start: datetime, end: datetime, N: int = 5):
        fil = self.df["Start Time"].apply(lambda d: start <= d and d < end)
        df_filtered = self.df[fil]
        hour_N_highest = (df_filtered.groupby("Hour"))["Solar Generation (MWh)"].nlargest(n = N).reset_index()
        hour_N_highest_avg = (hour_N_highest.groupby("Hour"))["Solar Generation (MWh)"].mean(numeric_only = True).reset_index().copy()

        __, regular_averages = self.averageDayInPeriod(start, end)
        daily_max = max(regular_averages)


#        night_corrected = [(reg if reg < 0.05*daily_max else peak) for reg, peak in zip(regular_averages, hour_N_highest_avg["Solar Generation (MWh)"])]
       
        return (hour_N_highest_avg["Hour"].copy(), hour_N_highest_avg["Solar Generation (MWh)"])


    def maxOutput(self, N = 1):
        top_N = self.df["Solar Generation (MWh)"].nlargest(n = N)
        results = top_N.mean(numeric_only = True)
        print(f"Max output N = {N}: {results:.1f}")
        return results
        

    def dailyTotalsDF(self, start: datetime, end: datetime):
        fil = self.df["Start Time"].apply(lambda d: start <= d and d < end)
        df_filtered = self.df[fil]
        daily_sums = (df_filtered.groupby("Date"))["Solar Generation (MWh)"].sum(numeric_only = True).reset_index().copy()
        return daily_sums
    

    def dailyTotals(self, start: datetime, end: datetime):
        ds = self.dailyTotalsDF(start, end)
        ds["Month"] = ds["Date"].apply(month_of)
        return (ds["Date"], ds["Solar Generation (MWh)"])
        
      
    def topNOnly(self, start: datetime, end: datetime, N: int = 5):
        ds = self.dailyTotalsDF(start, end)
        ds["Month"] = ds["Date"].apply(month_of)

        month_top_N = (ds.groupby("Month"))["Solar Generation (MWh)"].nlargest(n = N).reset_index().copy()
        month_Nth_highest = (month_top_N.groupby("Month"))["Solar Generation (MWh)"].min().reset_index().copy()

        month_Nth_dict = {}
        for month, Nth in zip(month_Nth_highest["Month"], month_Nth_highest["Solar Generation (MWh)"]):
            month_Nth_dict[month.to_pydatetime()] = Nth

        ds["Include"] = ds.apply(lambda row: (row["Solar Generation (MWh)"] >= month_Nth_dict[row["Month"]]), axis = 1)

        ds_filtered = ds[ds["Include"]].copy()
        monthly_average = (ds_filtered.groupby("Month"))["Solar Generation (MWh)"].mean(numeric_only = True).reset_index()

        return (ds_filtered["Date"], ds_filtered["Solar Generation (MWh)"])


            
    def __init__(self, paths: List[str]):
        dfs = []
        for path in paths:
            df = pd.read_csv(path)
            dfs.append(df)

        self.df = pd.concat(dfs)

        self.df["Start Time"] = self.df["Timestamp (Hour Ending)"].apply(timeparse)
        self.df["Hour"] = self.df["Start Time"].apply(lambda d: d.hour)
        self.df["Date"] = self.df["Start Time"].apply(lambda d: d.date())
        self.df.drop_duplicates(inplace = True)
        

            
if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    

    
        
