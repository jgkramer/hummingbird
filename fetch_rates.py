import numpy as np
import pandas as pd

RATES_PATH = "data/electricity_rates.csv"

class RatesData:

    def __init__(self):
        self.table = pd.read_csv(RATES_PATH)

    def print_key_columns(self):
        print(self.table[["State", "Plan Type", "Plan Name", "Season", "Time Period", "Tier", "Rate"]])
    
    def states_list(self):
        return np.unique(self.table["State"])

    def plans_for_state(self, state: str):
        return np.unique((self.table[self.table["State"]==state])["Plan Type"])

    def seasons_for_plan(self, state: str, plan_type: str):
        filter = (self.table["State"]==state) & (self.table["Plan Type"]==plan_type)
        return np.unique((self.table[filter])["Season"])

    def rate_dictionary(self, state: str, plan_type: str, season: str, tier: str = "All"):
        dictionary = dict()
        filter = (self.table["State"]==state) & (self.table["Plan Type"]==plan_type) & (self.table["Season"]==season) & (self.table["Tier"] == tier)
        Z = zip((self.table[filter])["Time Period"], (self.table[filter])["Rate"])
        for time, rate in Z:
            dictionary[time] = rate
        return dictionary
        

    
if __name__ == "__main__":
    rd = RatesData()
#   rd.print_key_columns()

    print(rd.states_list())
    plans = rd.plans_for_state("NV")
    for plan in plans:
        print(plan)
        seasons = rd.seasons_for_plan("NV", plan)
        print(seasons)
        for season in seasons:
            print(season)
            rate_dict = rd.rate_dictionary("NV", plan, season)
            print(rate_dict)



    
    
