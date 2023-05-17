import numpy as np
import pandas as pd

from dataclasses import dataclass
from datetime import datetime

from fetch_seasons import Season, SeasonsData
from fetch_rates import RatesData
from fetch_times import TimesData

import pdb

# Demand is a class rather than a basic strucutre because this can later be turned into a more complicated formula that may be
# dependent on multiple months worth of prior demands, by having charge be a function rather than a field
@dataclass(frozen = True)
class Demand:
    label: str
    charge: float
    

@dataclass(frozen = True)
class RateSegment:
    start_time: int
    end_time: int
    rate: float
    label: str
    weekend: bool = False
    # datetime .weekday() returns 0-4 for M-F, and 5-6 for Sa-Su

    # this is broken
    def sorter(self):
        return self.start_time

    def is_weekend(d: datetime) -> bool:
        return True if (d.weekday() >= 5) else False
        
    def in_segment(self, d: datetime, confirm_weekday = True) -> bool:
        same_daytype = (self.weekend and RateSegment.is_weekend(d)) or (not self.weekend and not RateSegment.is_weekend(d))
        
        if(confirm_weekday and not same_daytype):
            return False
        
        start_minutes = self.start_time * 60
        end_minutes = self.end_time * 60
        d_minutes = d.hour * 60 + d.minute
        return ((start_minutes <= d_minutes) & (d_minutes < end_minutes))

    def __str__(self):
        return ("Segment: " + self.label + (" Weekend" if self.weekend == True else " Weekday") + ", times=" + str(self.start_time) + " to " + str(self.end_time) + ", rate = " + str(self.rate))
        
# a RateSeries is the specification of rates for a given SEASON in a PLAN in one STATE.
# it contains a list of RateSegments that are times of the day for which different rates apply (e.g., off peak, etc.)
class RateSeries:
    def _add_segments(self):
        segs = []
        rate_dict = self.rd.rate_dictionary(self.state, self.plan_name, self.season.name)
#        print("in _add_segments.  plan name: ", self.plan_name, "season: ", self.season.name, " rate_dict: ", rate_dict)

#        print("period names: ", self.period_names)
        for period_name in self.period_names:
            daytypes = self.td.list_daytypes(self.state, self.plan_type, self.season.name, period_name)
            for daytype in daytypes:
                segments = self.td.list_time_segments(self.state, self.plan_type, self.season.name, period_name, daytype)
                for segment in segments:
                    seg = RateSegment(start_time = segment[0],
                                      end_time = segment[1],
                                      rate = rate_dict[period_name],
                                      label = period_name,
                                      weekend = True if daytype == "Weekend" else False)
                    segs.append(seg)
        return sorted(segs, key = RateSegment.sorter)

    def _add_demand(self):
        demands_raw = self.rd.demand_dictionary(self.state, self.plan_name, self.season.name)
        demands = dict()
        for key in demands_raw.keys():
            demands[key] = Demand(label = key, charge = demands_raw[key])
        return demands
    

    def __init__(self, state: str, season: Season, plan_type: str, plan_name: str, td: TimesData, rd: RatesData, is_demand: bool = False):
        self.state = state
        self.season = season
        self.plan_type = plan_type
        self.plan_name = plan_name
        self.td = td
        self.rd = rd
        self.is_demand = is_demand

        self.period_names = self.td.list_period_names(self.state, self.plan_type, self.season.name)
        if(len(self.period_names) == 0): self.period_names.add("All")    

        self.rate_segments = self._add_segments()

        self.demands = self._add_demand() if self.is_demand else dict()
        print("season: ", self.season.name, " demands:", self.demands)


    def start_times(self, weekend: bool):
        return [seg.start_time for seg in self.rate_segments if seg.weekend == weekend]

    def rates(self, weekend: bool):
        return [seg.rate for seg in self.rate_segments if seg.weekend == weekend]

    def segment_for_datetime(self, d: datetime):
        for seg in self.rate_segments:
            if(seg.in_segment(d)): return seg

 #       print("cannot find datetime: ", d, " in the following segments")
 #       for seg in self.rate_segments:
 #           print(seg)
        raise ValueError("Time is not in any segment in this RateSeries")

    def get_period_names(self):
        return self.period_names

    def __str__(self):
        s = []
        s.append("state = " + str(self.state))
        s.append("season = " + str(self.season))
        s.append("plan type = " + self.plan_type)
        s.append("segments: ")
        for seg in self.rate_segments:
            s.append(str(seg))

        return "\n".join(s)


# fully defines a TOU-based plan.  All seasons in a plan, consists of multiple series.
class RatePlan:
    def __init__(self, state: str, plan_name: str, td: TimesData, rd: RatesData, sd: SeasonsData):
        self.state = state
        self.plan_name = plan_name
        
        self.td = td
        self.rd = rd
        self.sd = sd
        self.rate_series_list = []

        self.plan_type = rd.get_plan_type(state, plan_name)
        
        self.is_demand = rd.is_demand_plan(state, plan_name)

        season_names = rd.seasons_for_plan_type(state, self.plan_type)
        
        seasons = [sd.season_from_name(state, s) for s in season_names]
        self.rate_series_list = [RateSeries(state, season, self.plan_type, self.plan_name, td, rd, self.is_demand) for season in seasons]

        self.periods = set()
        for rs in self.rate_series_list:
            pds = rs.get_period_names()
            self.periods = self.periods.union(set(rs.get_period_names()))

#        print("plan: ", plan_name, ", type: ", self.plan_type, " demand: ", self.is_demand)
#        for s in self.rate_series_list:
#            print(s)
#        print("")

            
    def get_period_names(self):
        return list(self.periods)

    def series(self):
        return self.rate_series_list

    def seasons(self):
        return [rs.season for rs in self.rate_series_list]

    def ratesegment_from_datetime(self, d: datetime):
        for rs in self.rate_series_list:
            if(rs.season.in_season(d)):
                return rs.segment_for_datetime(d)

        raise ValueError("No season in this rate plan for this date")

    
        
            
    

    
