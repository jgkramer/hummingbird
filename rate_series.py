import numpy as np
import pandas as pd
from dataclasses import dataclass

from fetch_rates import RatesData
from fetch_times import TimesData

@dataclass(frozen = True)
class RateSegment:
    start_time: int
    end_time: int
    rate: float
    label: str

class RateSeries:
    def __init__(self, state: str, season: str, plan_type: str, plan_name: str):
        self.state = state
        self.season = season
        self.plan_type = plan_type
        self.plan_name = plan_name
        self.rate_segments = []

    def add_segment(self,
                segment_start: int,
                segment_end: int,
                segment_rate: float,
                segment_label: str):
        self.rate_segments.append(RateSegment(start_time = segment_start,
                                              end_time = segment_end,
                                              rate = segment_rate,
                                              label = segment_label))

    
if __name__ == "__main__":
    rd = RatesData()
    td = TimesData()

    NV_plans = rd.plans_for_state("NV")
    print(NV_plans)
    for plan in NV_plans:
        print(plan)
        seasons = rd.seasons_for_plan("NV", plan)
        for season in seasons:

            rate_series = RateSeries("NV", season, plan, plan) # this is weird

            print(season)
            rate_dict = rd.rate_dictionary("NV", plan, season)
            print(rate_dict)
            periods = td.time_period_list("NV", plan, season)
            if(len(periods) == 0):
                periods.append("All")
            print(periods)
            
            
            
            
    

    
