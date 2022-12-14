from specificHourlyUsage import NVenergyUsage, SDenergyUsage, UsagePaths
from hourlyEnergyUsage import HourlyEnergyUsage
from monthlyEnergyUsage import MonthlyEnergyUsage
from specificMonthlyUsage import CT_MonthlyEnergyUsage
from dailyEnergyUsage import DailyEnergyUsage
from specificDailyUsage import TX_DailyEnergyUsage

from timeSeriesEnergyUsage import TimeSeriesEnergyUsage

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List

from state_usage_stats import Sector, StateUsageStats

import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, PercentFormatter)

from rate_series import RateSegment, RateSeries, RatePlan
from region import Region

from monthlyPlots import MonthlyPlots
from statemap import StateMap

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



def print_comp_graphs(susses: List[StateUsageStats], individuals: List[TimeSeriesEnergyUsage], labels: List[str], start: datetime, end: datetime, name: str):
    x_axis = [datetime(2022, n, 1).strftime("%b") for n in range(1, 13)]

    y_values_list = [(sus.usage_monthly_average(start, end, Sector.RESIDENTIAL)["Usage"])/sum((sus.usage_monthly_average(start, end, Sector.RESIDENTIAL)["Usage"]))
                         for sus in susses]
    
                                                                                                                         
#    state_resi_fraction = [x / sum(state_residential["Usage"]) for x in state_residential["Usage"]]
    y_values_list = y_values_list + [(meu.usage_monthly_average())["Usage"]/sum((meu.usage_monthly_average())["Usage"]) for meu in individuals]

    series_colors = ["orange", "blue", "lightblue"]
    filepath = f"post3/post3_{name}_line.png"

    MonthlyPlots.monthlyUsageLineChart(x_axis,
                                       y_values_list,
                                       labels,
                                       series_colors,
                                       title = "Each Month's % of Annual Electricity Consumption",
                                       path = filepath)

    

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

    filepath = "post3/post3_Kramer_vs_NV.png"

    MonthlyPlots.monthlyUsageLineChart(x_axis,
                                       y_values_list,
                                       series_labels,
                                       series_colors,
                                       title = "Each Month's % of Annual Electricity Consumption",
                                       path = filepath)


def key_months(state: str, df: pd.DataFrame):
    d = dict()

    d["Min month"] = df["Month Number"].iloc[df["Usage"].idxmin()]
    d["Min usage"] = min(df["Usage"])

    local_maxes = [1 if (month > next_month and month > prev_month) else 0
                   for (month, next_month, prev_month)
                   in zip(df["Usage"], np.roll(df["Usage"], 1), np.roll(df["Usage"], -1))]
    
    df["Local maxes"] = [is_max * use for (is_max, use) in zip(local_maxes, df["Usage"])]

    df_summer = df[ [ m in range(5, 11) for m in df["Month Number"]] ]
    df_winter = df[ [ m not in range(5, 11) for m in df["Month Number"]] ]

    d["Winter peak month"] = df["Month Number"].iloc[df_winter["Local maxes"].idxmax()]
    d["Winter peak usage"] = df["Local maxes"].iloc[df_winter["Local maxes"].idxmax()]
    assert(d["Winter peak usage"] != 0)
                         

    d["Summer peak month"] = df["Month Number"].iloc[df_summer["Local maxes"].idxmax()]
    d["Summer peak usage"] = df["Local maxes"].iloc[df_summer["Local maxes"].idxmax()]
    assert(d["Summer peak usage"] != 0)

#    print(d)

    return d

def get_ratios(s: datetime, e: datetime):
    states = StateUsageStats.list_all_states()
    winter_peaks = []
    winter_peaks_ratio = []
    summer_peaks = []
    summer_peaks_ratio = []
    min_usage = []
    for state in states:
        dictionary = key_months(state, StateUsageStats(state).usage_monthly_average(s, e, Sector.RESIDENTIAL))
        winter_peaks.append(dictionary["Winter peak usage"])
        summer_peaks.append(dictionary["Summer peak usage"])
        min_usage.append(dictionary["Min usage"])
        
        winter_peaks_ratio.append(dictionary["Winter peak usage"]/dictionary["Min usage"])
        summer_peaks_ratio.append(dictionary["Summer peak usage"]/dictionary["Min usage"])        

    df_map = pd.DataFrame(list(zip(states, winter_peaks_ratio, summer_peaks_ratio)),
                          columns = ["State", "Winter Peak", "Summer Peak"])

    df_csv = pd.DataFrame(list(zip(states, winter_peaks, summer_peaks, min_usage)),
                          columns = ["State", "Winter Peak Month (TWh)", "Summer Peak Month (TWh)", "Lowest Usage Month (TWh)"])

    StateMap.map_states(df_map, "State", "Summer Peak", "reds", "post3/post3_summer_map.png")
    StateMap.map_states(df_map, "State", "Winter Peak", "blues", "post3/post3_winter_map.png")

    map_csv_path = "post3/post3_map.csv"
    df_csv.to_csv(map_csv_path, float_format = "%.2f")

    

def print_summary_stats(sus: StateUsageStats, s: datetime, e: datetime):
    years = (e.year - s.year) + (e.month - s.month + 1)/12
    print("\nState: ", sus.state)
    print(f"All sectors: {sus.total_for_period(s, e, Sector.TOTAL)/years:.1f} TWh")
    print(f"Residential: {sus.total_for_period(s, e, Sector.RESIDENTIAL)/years:.1f} TWh")

    avgs = sus.usage_monthly_average(s, e, Sector.RESIDENTIAL)
    d = key_months(sus.state, avgs)
    print("Winter peak: ", f"{d['Winter peak usage'] / d['Min usage']:.2f}x")
    print("Summer peak: ", f"{d['Summer peak usage'] / d['Min usage']:.2f}x")
    print(f"% of Consumption in Summer: {100*(avgs['Usage'].iloc[5:8]).sum() / avgs['Usage'].sum():.1f}%")
    print(f"% of Consumption in Winter: {100*(avgs['Usage'].iloc[[0,1,11]]).sum() / avgs['Usage'].sum():.1f}%")
    

if __name__ == "__main__":
    NVE = NVenergyUsage(UsagePaths.NV_Kramer)

    s = datetime(2019, 9, 1)
    e = datetime(2022, 8, 31)

# line chart: NV house vs. NV total
    print_normalized_graphs(NVE, s, e)

# first part of blog post -- print statewide graphs NV
    states = ["NV", "CT", "FL", "AK"]
    for state in states:
        sus = StateUsageStats(state)
        print_state_table(sus, s, e, filepath = f"post3/post3_{state}_statewide.png")
        print_summary_stats(sus, s, e)


# line chart: CT aggregate vs. two houses
    CTkramer = CT_MonthlyEnergyUsage("usage_data/CT_14wp_usage_data.csv")
    CTharding = CT_MonthlyEnergyUsage("usage_data/CT_9harding_usage_data.csv")
    print_comp_graphs([StateUsageStats("CT")],
                    [CTkramer, CTharding],
                    ["CT Total Residential", "House 1: Electric heat pump", "House 2: Natural gas heated"],
                    s, e, "CT_individual")

    susFL = StateUsageStats("FL")
    susAK = StateUsageStats("AK")
    print_comp_graphs([susFL, susAK], [], ["FL Total Residential", "AK Total Residential"], s, e, "FLandAK")

# and the US map!
    get_ratios(s, e)
    
#https://plotly.com/python/getting-started/


