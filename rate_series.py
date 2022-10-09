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

    def sorter(self):
        return self.start_time

class RateSeries:
    def __init__(self, state: str, season: str, plan_type: str, plan_name: str):
        self.state = state
        self.season = season
        self.plan_type = plan_type
        self.plan_name = plan_name
        self.rate_segments = []

    def add_segment(self, seg: RateSegment):
        self.rate_segments.append(seg)

    def sort(self):
        self.rate_segments = sorted(self.rate_segments, key=RateSegment.sorter)

    def __str__(self):
        s = []
        s.append("state = " + self.state)
        s.append("season = " + self.season)
        s.append("plan type = " + self.plan_type)
        s.append("segments: ")
        for seg in self.rate_segments:
            s.append(str(seg))
        return "\n".join(s)


    
if __name__ == "__main__":
    rd = RatesData()
    td = TimesData()

    NV_plans = rd.plans_for_state("NV")
    print(NV_plans)
    for plan in NV_plans:
        print("\nplan " + plan)
        seasons = rd.seasons_for_plan("NV", plan)
        for season in seasons:
            print("\nseason " + season + "\n")

            rate_series = RateSeries("NV", season, plan, plan) # this is weird
            rate_dict = rd.rate_dictionary("NV", plan, season)

            periods = td.time_period_list("NV", plan, season)
            if(len(periods) == 0):
                periods.append("All")

            rs = RateSeries("NV", season, plan, plan)

            for period in periods:
                segments = td.time_segments_for_period("NV", plan, season, period)

                for segment in segments:
                    seg = RateSegment(segment[0], segment[1], rate_dict[period], period)
                    rs.add_segment(seg)
                    
            rs.sort()
            print(rs)
            
            
            
            
    

    
