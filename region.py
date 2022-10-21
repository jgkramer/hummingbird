
from dataclasses import dataclass
from datetime import datetime

from fetch_seasons import Season, SeasonsData
from fetch_times import TimesData
from fetch_rates import RatesData
from rate_series import RateSegment, RateSeries, RatePlan

SD = SeasonsData()
RD = RatesData()
TD = TimesData()

class Region:

    def __init__(self, state: str):
        self.state = state

        plan_names = RD.plans_for_state(self.state)
        self.rate_plans = [RatePlan(self.state, plan, plan, TD, RD, SD) for plan in plan_names]

        self.seasons = SD.seasons_for_state(state)
        

    def get_rate_plans(self):
        return self.rate_plans

    def get_seasons(self):
        return self.seasons

    def get_name(self):
        return self.state
