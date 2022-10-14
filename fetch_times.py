import numpy as np
import pandas as pd

TIMES_PATH = "data/time_of_use_definitions.csv"

class TimesData:

    def __init__(self):
        self.table = pd.read_csv(TIMES_PATH)
        self.table["Time Segments"] = self.table["Time Segments"].apply(TimesData.process_hour_ranges)

    def process_hour_ranges(raw_strings: str):
        #from input like "7-11; 20-24", creates a list of strings with hour ranges like "7-11"
        range_strings = raw_strings.replace(" ", "").split(";")

        #for each range, create a tuple of the integer values like (7, 11)
        ranges = [tuple([int(rs.split("-")[0]), int(rs.split("-")[1])])
                  for rs in range_strings if rs != ""]

        #return a list of tuples corresponding to the original input: [(7, 11), (20, 24)]
        return ranges

    def print_key_columns(self):
        print(self.table[["State", "Season", "Plan Type", "Time Period", "Time Segments"]])

    def states_list(self):
        return np.unique(self.table["State"])

    def plans_for_state(self, state: str):
        return np.unique((self.table[self.table["State"]==state])["Plan Type"])
        
    def seasons_for_state(self, state: str):
        return np.unique((self.table[self.table["State"]==state])["Season"])

    def time_period_list(self, state: str, plan_type: str, season: str):
        filter = (self.table["State"]==state) & (self.table["Plan Type"]==plan_type) & (self.table["Season"]==season)
        return ((self.table[filter])["Time Period"]).tolist()

    def time_segments_for_period(self, state: str, plan_type: str, season: str, period_name: str):
        if(period_name == "All"):
            return [tuple([0, 24])]                                     
        filter = (self.table["State"]==state) & (self.table["Plan Type"]==plan_type) & (self.table["Season"]==season) & (self.table["Time Period"]==period_name)
        #index zero because each item in Time Segments is a list.
        return ((self.table[filter])["Time Segments"]).tolist()[0]
        

if __name__ == "__main__":
    td = TimesData()

    print(td.states_list())

    periods = td.time_period_list("NV", "TOU", "Summer")
    print(periods)

    for period in periods:
        print(period)
        l = td.time_segments_for_period("NV", "TOU", "Summer", period)    
        print(l)

          
    
