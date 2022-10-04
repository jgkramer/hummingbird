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
        return (self.table[filter])["Season"]

        
    def rate_list(self, state: str, plan_type: str, season: str, tier: str = "All"):
        filter = (self.table["State"]==state) & (self.table["Plan Type"]==plan_type) & (self.table["Season"]==season) & (self.table["Tier"] == tier)
        return zip((self.table[filter])["Time Period"], (self.table[filter])["Rate"])

    
if __name__ == "__main__":
    td = RatesData()
    td.print_key_columns()

    print(td.states_list())
    print(td.plans_for_state("NV"))
    for tupe in td.rate_list("NV", "TOU", "Summer"):
        print(tupe)
    for tupe in td.rate_list("NV", "TOU", "Winter"):
        print(tupe)
    for tupe in td.rate_list("NV", "Fixed", "All"):
        print(tupe)
        



    
    
