import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from dataclasses import dataclass

from abc import ABC, abstractmethod
from dailyEnergyUsage import DailyEnergyUsage

from dateSupplements import DateSupplements


class TX_DailyEnergyUsage(DailyEnergyUsage):

    def process_table(self, usage_path):
        table = pd.read_csv(usage_path)
        table = table.drop(["Meter", "Reading", "Type", "High Temperature", "Low Temperature"], axis = "columns")

        table["Date"] = table["Reading Date"].apply(lambda s: (datetime.strptime(s, "%m/%d/%y")))
        table.sort_values(by = ["Date"], ascending = True, inplace = True)
        table.reset_index(drop=True, inplace = True) # reset index

        table["Usage"] = table["Usage (Kwh)"].copy()

        for ix, raw_u in enumerate(table["Usage (Kwh)"]):
            zeros = 0
            while(ix + zeros + 1 < len(table["Usage (Kwh)"]) and table["Usage (Kwh)"].iloc[ix+zeros+1] == 0):
                zeros = zeros+1
            if(zeros > 0):
                averaged = raw_u/(zeros + 1)
                for i in range(zeros + 1):
                    table["Usage"].iat[ix + i] = averaged

        self.table = pd.DataFrame()
        self.table["Date"] = table["Date"].copy()
        self.table["Usage"] = table["Usage"].copy()

        self.first = min(self.table["Date"])
        self.last = max(self.table["Date"])
        

if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    tx_path = "usage_data/TX_Stewart.csv"
    test = TX_DailyEnergyUsage(tx_path)
    test.usage_by_month()
    test.usage_monthly_average()
    

    

