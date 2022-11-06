
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
    def __init__(self, state, usage_path = USAGE_PATH):
        self.table = pd.read_csv(usage_path)
        self.table["Month"] = [datetime(y, m, 1) for y, m in zip(self.table["Year"], self.table["Month"])]
        self.table.drop("Year", axis = 1, inplace = True)

        fil = (self.table["State"] == state)
        self.table = self.table[fil].copy()
        
    def time_series(self, start_date: datetime, end_date: datetime, sector: Sector = Sector.TOTAL):
        print(start_date.date(), end_date.date())
        fil = [(start_date.date() <= d.date()) and d.date() <= end_date.date() for d in self.table["Month"]]
        dictionary = dict()
        dictionary["Month"] = list((self.table[fil])["Month"])
        
        dictionary["Usage"] = list((self.table[fil])[sector.name.capitalize()].apply(lambda x: int(x.replace(",", ""))/1e6))
        if(dictionary["Month"][0] > dictionary["Month"][-1]):
            dictionary["Month"].reverse()
            dictionary["Usage"].reverse()
        
        return dictionary


if __name__ == "__main__":
    sus = StateUsageStats(state = "NV")
    print(sus.time_series(datetime(2022, 1, 15), datetime(2022, 3, 2), Sector.TOTAL))

        
