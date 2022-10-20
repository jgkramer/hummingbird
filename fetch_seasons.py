import numpy as np
import pandas as pd

from datetime import datetime
from dataclasses import dataclass

from typing import List

SEASONS_PATH = "data/season_definitions.csv"
JAN_1 = datetime(1900, 1, 1)
DEC_31 = datetime(1900, 12, 31)

@dataclass(frozen = True)
class Season:
    state: str
    name: str
    start_date: datetime
    end_date: datetime

    def on_or_after(test: datetime, reference: datetime):
        return ((test.month > reference.month) |
                ((test.month == reference.month) & (test.day >= reference.day)))
        
    def in_season(self, d: datetime):
        if(Season.on_or_after(self.end_date, self.start_date)):
            return (Season.on_or_after(d, self.start_date) & Season.on_or_after(self.end_date, d))
        else:
            return (Season.on_or_after(d, self.start_date) | Season.on_or_after(self.end_date, d))

    def dates_string(self):
        s = datetime.strftime(self.start_date, "%d-%b") + " to " + datetime.strftime(self.end_date, "%d-%b")
        return s
    
 
class SeasonsData:
    def __init__(self):
        self.table = pd.read_csv(SEASONS_PATH)
        self.table = self.table.drop("Source", axis=1)
        self.table["BeginDateTime"] = self.table["Season_Begin"].apply(
            lambda s: (datetime.strptime(s, "%d-%b")))
        self.table["EndDateTime"] = self.table["Season_End"].apply(
            lambda s: (datetime.strptime(s, "%d-%b")))
        print(self.table.columns)
        print(self.table)
        

    def states_list(self):
        return np.unique(self.table["State"])

    def season_begin(self, state: str, season: str) :
        filter = (self.table["State"]==state) & (self.table["Season"]==season)
        begin = np.unique((self.table[filter])["Season_Begin"])
        if(len(begin) > 0):
            return begin[0]
        else:
            return None

    def season_end(self, state: str, season: str) -> str:
        filter = (self.table["State"]==state) & (self.table["Season"]==season)
        end = np.unique((self.table[filter])["Season_End"])
        if(len(end) > 0):
            return end[0]
        else:
            return None

    def seasons_for_state(self, state: str):
        state_table = self.table[self.table["State"]==state]
        seasons = [Season(state, name, start, end)
                   for name, start, end in zip(state_table["Season"],
                                               state_table["BeginDateTime"],
                                               state_table["EndDateTime"])
                   ]
        return seasons

    def season_from_name(self, state: str, season_name: str):
        if(season_name == "All"): return Season(state, "All", JAN_1, DEC_31)
        seasons = self.seasons_for_state(state)
        for s in seasons:
            if s.name == season_name: return s
        
        raise KeyException("Name not in seasons for state")


if __name__ == "__main__":
    sd = SeasonsData()
    seasons = sd.seasons_for_state("NV")
#    print(seasons)

    today = datetime.today()
    x = [s.in_season(today) for s in seasons]
    for s in seasons:
        s.dates_string()
    
#    print(x)
    
        
    

                                                
        

