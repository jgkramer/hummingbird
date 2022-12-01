
import numpy as np
import pandas as pd
from datetime import datetime, date
from enum import Enum

# source
# https://www.eia.gov/electricity/data/eia861m/xls/sales_revenue.xlsx

USAGE_PATH = "usage_data/monthly_statewide_usage_MWh.csv"


class Sector(Enum):
    RESIDENTIAL = 0
    COMMERCIAL = 1
    INDUSTRIAL = 2
    TRANSPORTATION = 3
    TOTAL = 4

class StateUsageStats:
    MasterTable = pd.read_csv(USAGE_PATH)
    MasterTable["Month"] = [datetime(y, m, 1) for y, m in zip(MasterTable["Year"], MasterTable["Month"])]
    MasterTable.drop("Year", axis = 1, inplace = True)
    
    def list_all_states():
        states = list(pd.unique(StateUsageStats.MasterTable["State"]))
        return states

    def __init__(self, state, usage_path = USAGE_PATH):

        self.state = state

        table = StateUsageStats.MasterTable
        self.first = min(table["Month"])
        self.last = max(table["Month"])

        fil = (table["State"] == state)
        self.table = table[fil].copy()
        
    def usage_by_month(self, start_date: datetime = None, end_date: datetime = None, sector: Sector = Sector.TOTAL):
        if start_date == None: start_date = self.first
        if end_date == None: end_date = self.last
        
        fil = [(start_date.date() <= d.date()) and d.date() <= end_date.date() for d in self.table["Month"]]

        df = pd.DataFrame()
        df["Month"] = (self.table[fil])["Month"].copy()
        df["Usage"] = (self.table[fil])[sector.name.capitalize()].apply(lambda x: int(x.replace(",", ""))/1e6)
        df.sort_values(by = ["Month"], ascending = True, inplace = True)
        df.reset_index(drop=True, inplace = True) # reset index
        
        return df

    def usage_monthly_average(self, start_date: datetime = None, end_date: datetime = None, sector: Sector = Sector.TOTAL):
        usage_df = self.usage_by_month(start_date, end_date, sector)
        usage_df["Month Number"] = [d.month for d in usage_df["Month"]]
        averages = usage_df.groupby("Month Number").mean(numeric_only = True).reset_index()
        return averages

    def total_for_period(self, start_date: datetime = None, end_date: datetime = None, sector: Sector = Sector.TOTAL):
        df = self.usage_by_month(start_date, end_date, sector)
        return (df["Usage"]).sum()
        
    
if __name__ == "__main__":
    pass
#    l = StateUsageStats.list_all_states()
#    print(len(l))   
#    sus = StateUsageStats(state = "NV")
#    print(sus.usage_by_month(sector = Sector.TOTAL, start_date = datetime(2019, 9, 1)))
#    print(sus.usage_monthly_average(sector = Sector.TOTAL, start_date = datetime(2019, 9, 1)))

        
