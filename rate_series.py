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
    def _add_segments(self):
        segs = []
        rate_dict = self.rd.rate_dictionary(self.state, self.plan_name, self.season)
        periods = self.td.time_period_list(self.state, self.plan_type, self.season)
        if(len(periods) == 0): periods.append("All")
        for period in periods:
            segments = self.td.time_segments_for_period(self.state, self.plan_type, self.season, period)
            for segment in segments:
                seg = RateSegment(segment[0], segment[1], rate_dict[period], period)
                segs.append(seg)
        return sorted(segs, key = RateSegment.sorter)

    def __init__(self, state: str, season: str, plan_type: str, plan_name: str, td: TimesData, rd: RatesData):
        self.state = state
        self.season = season
        self.plan_type = plan_type
        self.plan_name = plan_name
        self.td = td
        self.rd = rd
        self.rate_segments = self._add_segments()
        

    def start_times(self):
        return [seg.start_time for seg in self.rate_segments]

    def rates(self):
        return [seg.rate for seg in self.rate_segments]

    def __str__(self):
        s = []
        s.append("state = " + self.state)
        s.append("season = " + self.season)
        s.append("plan type = " + self.plan_type)
        s.append("segments: ")
        for seg in self.rate_segments:
            s.append(str(seg))
        return "\n".join(s)


            
    

    
