import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from dataclasses import dataclass

from abc import ABC, abstractmethod
from monthlyEnergyUsage import MonthlyEnergyUsage

from dateSupplements import DateSupplements


class CT_MonthlyEnergyUsage(MonthlyEnergyUsage):

    def process_table(self, usage_path):
        table = pd.read_csv(usage_path)
        table["Read Date"] = table["Read Date"].apply(lambda s: (datetime.strptime(s, "%m/%d/%y")))
        table.sort_values(by = ["Read Date"], ascending = True, inplace = True)
        table.reset_index(drop=True, inplace = True) # reset index

        self.normalize_table(table)
        

class MA_MonthlyEnergyUsage(MonthlyEnergyUsage):
    def process_table(self, usage_path):
        table = pd.read_csv(usage_path)
        table["Read Date"] = table["END DATE"].apply(lambda s: (datetime.strptime(s, "%m/%d/%y")))
        table["Start Date"] = table["START DATE"].apply(lambda s: (datetime.strptime(s, "%m/%d/%y")))
        table["Usage"] = table["USAGE"]
        table["Usage per Day"] = [u / ((r - s).days + 1)
                                  for (u, r, s) in zip(table["Usage"], table["Read Date"], table["Start Date"])]
        
        table.sort_values(by = ["Read Date"], ascending = True, inplace = True)
        table.reset_index(drop=True, inplace = True) # reset index

        self.normalize_table(table)


if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    ct_path1 = "usage_data/CT_9harding_usage_data.csv"
    test1 = CT_MonthlyEnergyUsage(ct_path1)
    test1.usage_monthly_average(start = datetime(2021, 7, 1))


    ct_path2 = "usage_data/CT_14wp_usage_data.csv"
    test2 = CT_MonthlyEnergyUsage(ct_path2)
    test2.usage_monthly_average()


    ma_path = "usage_data/MA_schaffer.csv"
    test2 = MA_MonthlyEnergyUsage(ma_path)
    test2.usage_monthly_average(end = datetime(2021, 6, 30))
    
    
    

