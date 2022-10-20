import numpy as np
import pandas as pd

from dataclasses import dataclass
from datetime import datetime

from fetch_seasons import Season, SeasonsData
from fetch_rates import RatesData
from fetch_times import TimesData

import pdb

@dataclass(frozen = True)
class RateSegment:
    start_time: int
    end_time: int
    rate: float
    label: str

    def sorter(self):
        return self.start_time

    def in_segment(self, d: datetime) -> bool:
        start_minutes = self.start_time * 60
        end_minutes = self.end_time * 60
        d_minutes = d.hour * 60 + d.minute
        return ((start_minutes <= d_minutes) & (d_minutes < end_minutes))

    def __str__(self):
        return ("Segment: " + self.label +", times=" + str(self.start_time) + " to " + str(self.end_time) + ", rate = " + str(self.rate))
        
# a RateSeries is the specification of rates for a given SEASON in a PLAN in one STATE.
# it contains a list of RateSegments that are times of the day for which different rates apply (e.g., off peak, etc.)
class RateSeries:
    def _add_segments(self):
        segs = []
        rate_dict = self.rd.rate_dictionary(self.state, self.plan_name, self.season.name)
        periods = self.td.time_period_list(self.state, self.plan_type, self.season.name)
        if(len(periods) == 0): periods.append("All")
        for period in periods:
            segments = self.td.time_segments_for_period(self.state, self.plan_type, self.season.name, period)
            for segment in segments:
                seg = RateSegment(segment[0], segment[1], rate_dict[period], period)
                segs.append(seg)
        return sorted(segs, key = RateSegment.sorter)

    def __init__(self, state: str, season: Season, plan_type: str, plan_name: str, td: TimesData, rd: RatesData):
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

    def segment_for_datetime(self, d: datetime):
        for seg in self.rate_segments:
            if(seg.in_segment(d)): return seg

        raise ValueError("Time is not in any segment in this RateSeries")

    def __str__(self):
        s = []
        s.append("state = " + str(self.state))]
        s.append("season = " + str(self.season))
        s.append("plan type = " + self.plan_type)
        s.append("segments: ")
        for seg in self.rate_segments:
            s.append(str(seg))
        return "\n".join(s)



# fully defines a TOU-based plan.  All seasons in a plan, consists of multiple series.
class RatePlan:
    def __init__(self, state: str, plan_type: str, plan_name: str, td: TimesData, rd: RatesData, sd: SeasonsData):
        self.state = state
        self.plan_type = plan_type
        self.plan_name = plan_name
        self.td = td
        self.rd = rd
        self.sd = sd
        self.rate_series_list = []

        season_names = rd.seasons_for_plan(state, plan_name)
        seasons = [sd.season_from_name(state, s) for s in season_names]
        self.rate_series_list = [RateSeries(state, season, plan_type, plan_name, td, rd) for season in seasons]

    def series(self):
        return self.rate_series_list

    def seasons(self):
        return [rs.season for rs in self.rate_series_list]

    def ratesegment_from_datetime(self, d: datetime):
        for rs in self.rate_series_list:
            if(rs.season.in_season(d)):
                return rs.segment_for_datetime(d)

        raise ValueError("No season in this rate plan for this date")

    
        
            
    

    
