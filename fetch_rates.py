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
        return np.unique((self.table[self.table["State"]==state])["Plan Name"])

    def seasons_for_plan_type(self, state: str, plan_type: str):
        filter = (self.table["State"]==state) & (self.table["Plan Type"]==plan_type)
        return np.unique((self.table[filter])["Season"])

    def get_plan_type(self, state: str, plan_name: str):
        filter = (self.table["State"]==state) & (self.table["Plan Name"]==plan_name)

        # make sure that each plan has a unique plan type
        assert len(np.unique(list((self.table[filter])["Plan Type"]))) == 1
        
        return list((self.table[filter])["Plan Type"])[0]

    def is_demand_plan(self, state: str, plan_name: str):
        filter = (self.table["State"]==state) & (self.table["Plan Name"]==plan_name)

        # make sure that each plan has a unique "demand" type
        assert len(np.unique(list((self.table[filter])["Demand"]))) == 1
        if "Yes" == list((self.table[filter])["Demand"])[0]:
            return True
        else:
            return False
        

    def rate_dictionary(self, state: str, plan_name: str, season: str, tier: str = "All"):
        dictionary = dict()
        filter = (self.table["State"]==state) & (self.table["Plan Name"]==plan_name) & (self.table["Season"]==season) & (self.table["Tier"] == tier)
        Z = zip((self.table[filter])["Time Period"], (self.table[filter])["Rate"])
        for time, rate in Z:
            dictionary[time] = rate
        return dictionary

    def demand_dictionary(self, state: str, plan_name: str, season: str, tier: str = "All"):
        dictionary = dict()
        filter = (self.table["State"]==state) & (self.table["Plan Name"]==plan_name) & (self.table["Season"]==season) & (self.table["Tier"] == tier)
        Z = zip((self.table[filter])["Time Period"], (self.table[filter])["Demand Charge"])
        for time, demand in Z:
            dictionary[time] = demand if (demand != "") else 0
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



    
    
