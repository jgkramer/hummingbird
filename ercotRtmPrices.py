
from datetime import datetime
import re
import numpy as np
import pandas as pd
import calendar

import matplotlib.pyplot as plt

# https://www.ercot.com/mp/data-products/data-product-details?id=np6-785-er

class ErcotRtmPrices:

    def __init__(self, filedate: datetime):
        filename = f"rtm_{filedate.month:02}_{filedate.day:02}_{filedate.year}.xlsx"
        path = f"post11_data/{filename}"

        # Read all sheets into a dictionary of DataFrames
        all_sheets = pd.read_excel(path, sheet_name=None)
        months = list(all_sheets.keys())
        self.file_date = filedate
        self.month_names = []
        self.full_data_by_month = {}
        self.monthly_averages = {}

        for month in months:
            sheet_df = all_sheets[month]
            
            # if this month doesn't have any data, ignore it and move on
            if(sheet_df.size == 0): continue

            self.month_names.append(month)

            # this is statewide average            
            settlement_point = "HB_BUSAVG"

            month_prices = (sheet_df[sheet_df["Settlement Point Name"]==settlement_point])[["Delivery Date", "Delivery Hour", "Delivery Interval", "Settlement Point Price"]]
            month_prices = month_prices.rename(columns = {"Delivery Date": "Date", "Settlement Point Price": "Price"})
            month_prices["Hour"] = (month_prices["Delivery Hour"]-1) + (month_prices["Delivery Interval"] - 1)/4
            self.full_data_by_month[month] = month_prices[["Date", "Hour", "Price"]].copy()
            
            hourly_average = month_prices.groupby("Hour")["Price"].mean().reset_index()

            self.monthly_averages[month] = hourly_average

    def get_monthly_average(self, d: datetime):
        month_name = d.strftime("%b")
        # print(f"month name = {month_name}")
        if month_name not in self.month_names: return None
        return self.monthly_averages[month_name].copy()
    
    def get_daily_prices(self, d: datetime):
        month_name = calendar.month_abbr[d.month]
        day_string = d.strftime("%m/%d/%Y")
        
        if month_name not in self.month_names: return None
        month_df = self.full_data_by_month[month_name]
        return month_df[month_df["Date"]==day_string].copy()
    
if __name__ == "__main__":
    e = ErcotRtmPrices(datetime(2024, 10, 6))
    print("Monthly average for May")
    print(e.get_monthly_average("May"))

    print("Getting 5/15/24")
    daily_results = e.get_daily_prices(datetime(2024, 5, 15))
    print(daily_results.size)
    print(daily_results)
