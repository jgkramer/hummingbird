from fetch_NVenergy_usage import NVenergyUsage
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.rrule import rrule, MONTHLY

from typing import List


from rate_series import RateSegment, RateSeries, RatePlan
from fetch_seasons import Season
from region import Region

from state_usage_stats import Sector, StateUsageStats

import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, PercentFormatter)

def format_time(x, _):
    hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
    return hm + ("am" if (x%24)<12 else "pm")

def get_summer_TOU_peak():
    plans = Region("NV").get_rate_plans()
    plan = ([plan for plan in plans if plan.plan_type == "TOU"])[0]
    rate_series = plan.series()
    summer_rs = ([rs for rs in rate_series
                  if rs.season.name == "Summer"])[0]
    peak_segment = ([seg for seg in summer_rs.rate_segments
                     if (seg.label == "On-Peak" and seg.weekend == False)])[0]
    return peak_segment
    

def plot_usage_chart(NVE: NVenergyUsage,
                     date_list: List[datetime],
                     high_temp_list: List[float],
                     low_temp_list: List[float],
                     path: str):
        
    fig, ax = plt.subplots(figsize = (7.5, 4))
    fig.tight_layout(pad = 2.0)
        
    ax.set_xlim([0, 24])
    ax.set_ylim([0, 4])
    ax.set_ylabel("kWh consumed (15m windows)")
    
    ax.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))

    ax.xaxis.set_major_formatter(format_time)
    ax.xaxis.set_ticks(np.arange(0, 24+1, 3))

    peak = get_summer_TOU_peak()
    
    table_rows = [d.strftime("%b %-d") for d in date_list]
    table_columns = ["Peak", "Off-Peak", "Total (kWh)"]
    cells = []

    for d, ht, lt in zip(date_list, high_temp_list, low_temp_list):
        times, usage = list(zip(*NVE.usage_series_for_day(d)))
        
        hours = [(t.hour + t.minute/60) for t in times]
        usage = list(usage)

        # compute totals
        total_usage = round(sum(usage), ndigits=1)
        peak_usage = round(sum([u if peak.in_segment(t, False) else 0 for (t, u) in zip(times, usage)]), ndigits=1)
        off_peak_usage = round(total_usage - peak_usage, ndigits = 1)
        cells.append([peak_usage, off_peak_usage, total_usage])

        # for the graph only (not computing totals), append one more 
        hours.append(24)
        usage.append(usage[-1])
        
        series_label = d.strftime("%a %b %-d, %Y") + " ({:1.0f}\u00b0 / {:1.0f}\u00b0F)".format(ht, lt)
        ax.step(hours, usage, where = "post", label = series_label)
        ax.legend(loc = "upper left")
        

    table = ax.table(cellText = cells, rowLabels = table_rows, colLabels = table_columns,
                     cellLoc = "center", loc = "upper right")
    table.auto_set_column_width(col=list(range(len(table_columns))))
    table.set_fontsize(9)
    cells = table.get_celld().values()
    for cell in cells:
        cell.set(edgecolor = "lightgray")

    plt.savefig(path)
    plt.close()

# return dataframe with "Month" column and "Usage_" and "Cost_" columns for each period
# e.g., "Month", "Usage_Peak", "Cost_Peak", "Usage_Off-Peak", "Cost_Off-Peak"
def get_monthly_table(NVE: NVenergyUsage, plan: RatePlan, start: datetime, end: datetime):

    monthly_starts = list(rrule(freq=MONTHLY, bymonthday = 1, dtstart=start, until=end))
    if(monthly_starts[0].date() != start.date()):
        monthly_starts = [start] + monthly_starts

    monthly_ends = list(rrule(freq=MONTHLY, bymonthday = -1, dtstart=start, until=end))
    if(monthly_ends[-1].date() != end.date()):
        monthly_ends.append(end)

    #setting up the data frame
    df = pd.DataFrame()
    df["Month"] = [d.strftime("%b %y") for d in monthly_starts]
    for period_name in plan.get_period_names():
        df["Usage_" + period_name] = [0 for d in monthly_starts]
        df["Cost_" + period_name]  = [0 for d in monthly_starts]

    for ix, (month_start, month_end) in enumerate(zip(monthly_starts, monthly_ends)):
        usage_stats = NVE.stats_by_period(plan, month_start, month_end)
        for usage_stat in usage_stats:
            df.loc[ix, "Usage_"+usage_stat.label] = round(usage_stat.kWh, ndigits = 1)
            df.loc[ix, "Cost_"+usage_stat.label] = round(usage_stat.cost, ndigits = 2)

    return df


def print_monthly_table(NVE: NVenergyUsage, plan: RatePlan, start: datetime, end: datetime):
    df = get_monthly_table(NVE, plan, start, end)

    plt.rcParams.update({'font.size': 8})
    fig, ax = plt.subplots(figsize = (7.5, 3.5))
    fig.tight_layout(pad = 2.0)
    ax.set_ylim([0, 5000])

    dfsum = df.sum(axis = 0)
    
    path = "post2/post2_monthly_usage_" + plan.plan_name + ".png"
    
    prev = None
    plots = []
    for period_name in plan.get_period_names():
        if(prev is None):
            plots.append(ax.bar(df["Month"], df["Usage_"+period_name], label = period_name))
        else:
            plots.append(ax.bar(df["Month"], df["Usage_"+period_name], bottom = prev, label = period_name))
        prev = df["Usage_"+period_name]

    ax.bar_label(plots[-1], fmt = "%d", padding = 5)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_title('Electricity (kWh) Consumed by Month')
    ax.legend()
    plt.savefig(path)
    plt.close()

def print_state_table(s: datetime, e: datetime):
    path = "post2/statewide_usage.png"
    
    sus = StateUsageStats("NV")
    nv_residential = sus.time_series(s, e, Sector.RESIDENTIAL)
    nv_total = sus.time_series(s, e, Sector.TOTAL)

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
    if(month == "Jun 22"): return 0.5*(may + aug)
    if(month == "Jul 22"): return aug
    return use

def print_normalized_graphs(NVE: NVenergyUsage, plan: RatePlan, start: datetime, end: datetime):
    fig, ax = plt.subplots(figsize = (7.5, 3.5))
    fig.tight_layout(pad = 2.0)
    ax.set_ylim([0, .18])
        
    df = get_monthly_table(NVE, plan, start, end)
    df["Kramer"] = df["Usage_All"]/sum(df["Usage_All"])

    sus = StateUsageStats("NV")
    nv_residential = sus.time_series(start, end, Sector.RESIDENTIAL)
    nv_residential["Fraction"] = [x/sum(nv_residential["Usage"]) for x in nv_residential["Usage"]]

    nv_total = sus.time_series(start, end, Sector.TOTAL)
    nv_total["Fraction"] = [x/sum(nv_total["Usage"]) for x in nv_total["Usage"]]

    df["NV Residential"] = nv_residential["Fraction"]
    df["NV Total"] = nv_total["Fraction"]

    ax.plot(df["Month"], df["Kramer"], '-D', label = "My House", color = "blue")
    ax.plot(df["Month"], df["NV Residential"], '-D', label = "NV Residential", color = "orange")
    ax.plot(df["Month"], df["NV Total"], '-D', label = "NV Total", color = "peachpuff")
    ax.plot(df["Month"], [1/12 for x in df["Month"]], '-', color = "lightgray")
    ax.legend()

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.yaxis.set_major_formatter(PercentFormatter(xmax = 1, decimals=0))
    ax.set_title("Each Month's % of Annual Electricity Consumption")
    
    path1 = "post2/percent_of_total.png"

    plt.savefig(path1)
    plt.show()
    plt.close()

    fig, ax = plt.subplots(figsize = (7.5, 3.5))
    fig.tight_layout(pad = 2.0)
    ax.set_ylim([0, 0.18])
    
    Kramer_may = df.where(df["Month"] == "May 22")["Usage_All"].sum(skipna = True)
    Kramer_aug = df.where(df["Month"] == "Aug 22")["Usage_All"].sum(skipna = True)
    df["Adjusted_Usage"] = [ process(use, month, Kramer_may, Kramer_aug)
                             for (use, month) in zip(df["Usage_All"], df["Month"])]
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
    

    path2 = "post2/percent_of_total_adjusted.png"

    plt.savefig(path2)
    plt.show()
    plt.close()

    

if __name__ == "__main__":
    NVE = NVenergyUsage()

# first part of blog post -- plot the graphs for daily usage charts for specific days. 
    date_lists = [[datetime(2022, 8, 15), datetime(2022, 8, 31)],  # high - 8/15/22
                  [datetime(2022, 2, 1), datetime(2022, 2, 3)],
                  [datetime(2022, 5, 9), datetime(2022, 5, 15)]] #high

    high_temp_lists = [[96, 109], # august
                      [58, 53],   # feb
                      [72, 95]]   # may

    low_temp_lists = [[79, 85],   # aug
                      [42, 33],   # feb
                      [54, 64]]  # may
    # source: https://www.wunderground.com/history/monthly/us/nv/henderson/KLAC/date/2022-8
    
    base_path = "post2/post2_usage_"
    for date_list, high_temps, low_temps in zip(date_lists, high_temp_lists, low_temp_lists):
        path = base_path + date_list[0].strftime("%b") + ".png"
        plot_usage_chart(NVE, date_list, high_temps, low_temps, path)


# second part of blog post -- print graphs of my monthly usage.
    s = datetime(2021, 9, 1)
    e = datetime(2022, 8, 31)

    plans = Region("NV").get_rate_plans()

    for plan in plans:
        print(plan.plan_name)
        print_monthly_table(NVE, plan, s, e)

# third part of blog post -- print statewide graphs
    print_state_table(s, e)

# third part of blog post 2 -- normalize my house vs. state resi vs. state total
    for plan in plans:
        if(plan.plan_name == "Fixed"):
            print_normalized_graphs(NVE, plan, s, e)

    

    


        

    
    
    
    
