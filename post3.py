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

def print_state_table(s: datetime, e: datetime):
    path = "post3/statewide_usage.png"
    
    sus = StateUsageStats("NV")
    nv_residential = sus.usage_by_month(s, e, Sector.RESIDENTIAL)
    nv_total = sus.usage_by_month(s, e, Sector.TOTAL)

    fig, ax = plt.subplots(figsize = (7.5, 3.5))
    ax.set_ylim([0, 5])
    fig.tight_layout(pad = 2.0)

    x_axis = [d.strftime("%b %y") for d in nv_total["Month"]]

    plots = []
    plots.append(ax.bar(x_axis, nv_total["Usage"], label = "Total", color = "peachpuff"))
    ax.bar_label(plots[-1], fmt = "%1.1f", padding = 5)
    plots.append(ax.bar(x_axis, nv_residential["Usage"], label = "Residential", color = "orange"))
    ax.bar_label(plots[-1], fmt = "%1.1f", padding = 5)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.get_yaxis().set_visible(False)

    ax.set_title('Electricity (TerraWatt Hours) Consumed in NV by Month')

    ax.invert_xaxis()
    plt.savefig(path)
    plt.close()


def process(use: float, month: str, may: float, aug: float):
    if(month == "Jun"): return 0.5*(may + aug)
    if(month == "Jul"): return aug
    return use

def print_normalized_graphs(NVE: NVenergyUsage, start: datetime, end: datetime):
    fig, ax = plt.subplots(figsize = (7.5, 3.5))
    fig.tight_layout(pad = 2.0)
    ax.set_ylim([0, .18])
        
    df = NVE.usage_monthly_average()
    df["Month"] = df["Month Number"].apply(lambda n: datetime(2022, n, 1).strftime("%b"))
    df["Kramer"] = df["Usage"]/sum(df["Usage"])

    sus = StateUsageStats("NV")
    nv_residential = sus.usage_monthly_average(start, end, Sector.RESIDENTIAL)
    nv_residential["Fraction"] = [x/sum(nv_residential["Usage"]) for x in nv_residential["Usage"]]

    nv_total = sus.usage_monthly_average(start, end, Sector.TOTAL)
    nv_total["Fraction"] = [x/sum(nv_total["Usage"]) for x in nv_total["Usage"]]

    df["NV Residential"] = nv_residential["Fraction"]
    df["NV Total"] = nv_total["Fraction"]

    ax.plot(df["Month"], df["Kramer"], '-D', label = "My House", color = "blue")
    ax.plot(df["Month"], df["NV Residential"], '-D', label = "NV Residential", color = "orange")
    ax.plot(df["Month"], df["NV Total"], '-D', label = "NV Total", color = "peachpuff")
    ax.plot(df["Month"], [1/12 for x in df["Month Number"]], '-', color = "lightgray")
    ax.legend()

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.yaxis.set_major_formatter(PercentFormatter(xmax = 1, decimals=0))
    ax.set_title("Each Month's % of Annual Electricity Consumption")
    
    path1 = "post3/percent_of_total.png"

    plt.savefig(path1)
    plt.show()
    plt.close()

    fig, ax = plt.subplots(figsize = (7.5, 3.5))
    fig.tight_layout(pad = 2.0)
    ax.set_ylim([0, 0.18])
    
    Kramer_may = df.where(df["Month"] == "May")["Usage"].sum(skipna = True)
    Kramer_aug = df.where(df["Month"] == "Aug")["Usage"].sum(skipna = True)
    df["Adjusted_Usage"] = [ process(use, month, Kramer_may, Kramer_aug)
                             for (use, month) in zip(df["Usage"], df["Month"])]
    df["Kramer_Adjusted"] = df["Adjusted_Usage"]/sum(df["Adjusted_Usage"])

    ax.plot(df["Month"], df["Kramer_Adjusted"], '-D', label = "My House", color = "blue")
    ax.plot(df["Month"], df["NV Residential"], '-D', label = "NV Residential", color = "orange")
    ax.plot(df["Month"], df["NV Total"], '-D', label = "NV Total", color = "peachpuff")
    ax.plot(df["Month"], [1/12 for x in df["Month"]], '-', color = "lightgray")
    ax.legend()

    fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
    

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.yaxis.set_major_formatter(PercentFormatter(xmax = 1, decimals=0))
    ax.set_title("Each Month's % of Annual Electricity Consumption (June-July Hypothetical)")
    
    path2 = "post3/percent_of_total_adjusted.png"

    plt.savefig(path2)
    plt.show()
    plt.close()


if __name__ == "__main__":
    NVE = NVenergyUsage(UsagePaths.NV_Kramer)

    s = datetime(2021, 1, 1)
    e = datetime(2021, 12, 31)

    plans = Region("NV").get_rate_plans()

# first part of blog post -- print statewide graphs NV
    print_state_table(s, e)

# part of blog post 2 -- normalize my house vs. state resi vs. state total
    for plan in plans:
        if(plan.plan_name == "Fixed"):
            print_normalized_graphs(NVE, s, e)

