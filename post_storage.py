from specificHourlyUsage import NVenergyUsage, SDenergyUsage, UsagePaths, EIARegionUsage, LittlefieldEnergyUsage
from hourlyEnergyUsage import HourlyEnergyUsage

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from region import Region
from rate_series import RateSegment, RateSeries, RatePlan
from dateSupplements import DateSupplements

from energyStorage import SupplyGenerator, StorageAnalyzer

from cumulativePlots import CumulativePlots

def get_monthly_table(NVE: NVenergyUsage, plan: RatePlan, start: datetime, end: datetime, flatten = False):
    monthly_starts, monthly_ends = DateSupplements.month_starts_ends(start, end)
    
    #setting up the data frame
    df = pd.DataFrame()
    df["Month"] = [d.strftime("%b %y") for d in monthly_starts]
    for period_name in plan.get_period_names():
        df["Usage_" + period_name] = [0 for d in monthly_starts]
        df["Cost_" + period_name]  = [0 for d in monthly_starts]

    for ix, (month_start, month_end) in enumerate(zip(monthly_starts, monthly_ends)):
        usage_stats = NVE.stats_by_period(plan, month_start, month_end, daily_average = flatten)
        for usage_stat in usage_stats:
            df.loc[ix, "Usage_"+usage_stat.label] = round(usage_stat.kWh, ndigits = 1)
            df.loc[ix, "Cost_"+usage_stat.label] = round(usage_stat.cost, ndigits = 2)

    return df

if __name__ == "__main__":
    pd.options.display.max_rows = None
    
    kramer_hourly = NVenergyUsage(UsagePaths.NV_Kramer)
    start = datetime(2021, 8, 1)
    end = datetime(2021, 8, 31)

    analyzer_kramer = StorageAnalyzer(kramer_hourly, start, end, "kWh")
    analyzer_kramer.apply_supply([lambda: analyzer_kramer.supplyGenerator.typical_daily_peak(1.0)],
                                 ["Typical Daily Peak"],
                                 path = f"post5/post5_KramerMedianPeak.png",
                                 hourly = True,
                                 print_summary = False,
                                 print_hourly = True)
    
    solar_data_path = "post4/NV_ideal_solar_capacity.csv"
    
    analyzer_kramer.apply_supply([lambda: analyzer_kramer.supplyGenerator.solar_function(solar_data_path, 1.35),
                                  lambda: analyzer_kramer.supplyGenerator.solar_function(solar_data_path, 1.1)],
                                 labels = ["Solar @ 135%", "Solar @ 110%"],
                                 colors = ["coral", "plum"],
                                 path = f"post5/post5_KramerSolar.png",
                                 print_summary = True
                                 )
    

    year_start = datetime(2021, 11, 1)
    year_end = datetime(2022, 11, 1)
    paths = []
    d = year_start
    while d < year_end:
        paths.append(f"./statewide_demand/NVPower_demand_{d.year}_{d.month:02}.csv")
        d = d + relativedelta(months = +1)
    hourly_NV = EIARegionUsage(paths)

    analyzer_NV = StorageAnalyzer(hourly_NV, year_start, year_end, hourly_NV.units)
    analyzer_NV.apply_supply([lambda: analyzer_NV.supplyGenerator.typical_daily_peak(1.0, statistic = "average", date_subset = [datetime(2022, 6, 1), datetime(2022, 9, 30)]),
                              lambda: analyzer_NV.supplyGenerator.top_percentile_days(percentile = 0.95)],
                             labels = ["Avg. Summer Daily Peak (163%)", "95th Percentile Peak (186%)"],
                             colors = ["coral", "plum"],
                             path = f"post5/post5_NV_HighFixed.png",
                             hourly = True,
                             print_summary = True)

    ratio1 = 1.5
    ratio2 = 1.35

    print(f"\n Fixed @ {100*ratio1:.0f}% and {100*ratio2:.0f}%")
    analyzer_NV.apply_supply([lambda: analyzer_NV.supplyGenerator.period_average(ratio1),
                              lambda: analyzer_NV.supplyGenerator.period_average(ratio2)],
                             labels = [f"Fixed @ {100*ratio1:.0f}% average", f"Fixed @ {100*ratio2:.0f}% average"],
                             colors = ["slateblue", "limegreen"],
                             path = f"post5/post5_NV_MediumFixed.png",
                             hourly = False,
                             print_summary = True)


    print(f"\n Solar @ {100*ratio1:.0f}% and {100*ratio2:.0f}%")
    analyzer_NV.apply_supply([lambda: analyzer_NV.supplyGenerator.solar_function(solar_data_path, ratio1),
                              lambda: analyzer_NV.supplyGenerator.solar_function(solar_data_path, ratio2)],
                             labels = [f"Solar @ {100*ratio1:.0f}% average", f"Solar @ {100*ratio2:.0f}% average"],
                             colors = ["slateblue", "limegreen"],
                             path = f"post5/post5_NV_MediumSolar.png",
                             hourly = False,
                             print_summary = True)


    print(f"\n Blend @ {100*ratio1:.0f}%")
    analyzer_NV.apply_supply([lambda: analyzer_NV.supplyGenerator.blend_fixed_solar(solar_data_path, ratio1, solar_share = 0.2)],
                             labels = [f"20% Solar / 80% Fixed @ {100*ratio1:.0f}%"],
                             colors = ["purple"],
                             hourly = False,
                             path = f"post5/post5_NV_80-20.png",
                             print_summary = True)

    
