from specificHourlyUsage import NVenergyUsage, SDenergyUsage, UsagePaths
from hourlyEnergyUsage import HourlyEnergyUsage

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from state_usage_stats import Sector, StateUsageStats

import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, PercentFormatter)

from rate_series import RateSegment, RateSeries, RatePlan
from region import Region


from monthlyPlots import MonthlyPlots

def print_state_table(sus: StateUsageStats, s: datetime, e: datetime, filepath:str):
    
    nv_residential = sus.usage_monthly_average(s, e, Sector.RESIDENTIAL)
    nv_total = sus.usage_monthly_average(s, e, Sector.TOTAL)

    x_axis = [datetime(2022, n, 1).strftime("%b") for n in nv_residential["Month Number"]]
    y_values_list = [nv_total["Usage"], nv_residential["Usage"]]
    series_labels = ["Total", "Residential"]
    series_colors = ["peachpuff", "orange"]
    
    MonthlyPlots.monthlyUsageBarChart(x_axis,
                                      y_values_list,
                                      "TWh / month",
                                      series_labels,
                                      series_colors,
                                      fmt_str = "%1.1f",
                                      title = f"Electricity Consumed in {sus.state} by Month (3y Average)",
                                      path = filepath)


def process(use: float, month: str, may: float, aug: float):
    if(month == 6): return 0.5*(may + aug)
    if(month == 7): return aug
    return use

def print_normalized_graphs(NVE: NVenergyUsage, start: datetime, end: datetime):
        
    kramer_df = NVE.usage_monthly_average()
    sus = StateUsageStats("NV")
        
    kramer_fraction = kramer_df["Usage"]/sum(kramer_df["Usage"])

    # adjust June and July
    Kramer_may = kramer_df.where(kramer_df["Month Number"] == 5)["Usage"].sum(skipna = True)
    Kramer_aug = kramer_df.where(kramer_df["Month Number"] == 8)["Usage"].sum(skipna = True)
    kramer_df["Adjusted_Usage"] = [ process(use, month, Kramer_may, Kramer_aug)
                                     for (use, month) in zip(kramer_df["Usage"], kramer_df["Month Number"])]
    kramer_adjusted_fraction = kramer_df["Adjusted_Usage"]/sum(kramer_df["Adjusted_Usage"])


    nv_residential = sus.usage_monthly_average(start, end, Sector.RESIDENTIAL)
    nv_resi_fraction = [x/sum(nv_residential["Usage"]) for x in nv_residential["Usage"]]

    nv_total = sus.usage_monthly_average(start, end, Sector.TOTAL)
    nv_total_fraction = [x/sum(nv_total["Usage"]) for x in nv_total["Usage"]]

    x_axis = [datetime(2022, n, 1).strftime("%b") for n in kramer_df["Month Number"]]
    y_values_list = [kramer_fraction, kramer_adjusted_fraction, nv_resi_fraction, nv_total_fraction]
    series_labels = ["My House (Unadjusted)", "My House", "NV Residential", "NV Total"]
    series_colors = ["lightblue", "blue", "orange", "peachpuff"]
    filepath = "post3/percent_of_total.png"

    MonthlyPlots.monthlyUsageLineChart(x_axis,
                                       y_values_list,
                                       series_labels,
                                       series_colors,
                                       title = "Each Month's % of Annual Electricity Consumption",
                                       path = filepath)


if __name__ == "__main__":
    NVE = NVenergyUsage(UsagePaths.NV_Kramer)

    s = datetime(2019, 9, 1)
    e = datetime(2022, 8, 31)

# first part of blog post -- print statewide graphs NV
    susNV = StateUsageStats("NV")
    print_state_table(susNV, s, e, filepath = f"post3/post3_NV_statewide.png")
    print("Total NV: ", susNV.total_for_period(s, e, Sector.TOTAL))
    print("Residential NV: ", susNV.total_for_period(s, e, Sector.RESIDENTIAL))
    print("Months: ", 12*(e.year - s.year) + (e.month - s.month + 1))
    
        

#    sus2 = StateUsageStats("AK")
#    print_state_table(sus2, s, e)

# part of blog post 2 -- normalize my house vs. state resi vs. state total

    print_normalized_graphs(NVE, s, e)

