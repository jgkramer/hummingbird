from fetch_NVenergy_usage import NVenergyUsage
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.rrule import rrule, MONTHLY

from typing import List

from rate_series import RateSegment, RateSeries, RatePlan
from fetch_seasons import Season
from region import Region

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


def month_start_ends(start: datetime, end: datetime):
    monthly_starts = list(rrule(freq=MONTHLY, bymonthday = 1, dtstart=start, until=end))
    if(monthly_starts[0].date() != start.date()):
        monthly_starts = [start] + monthly_starts

    monthly_ends = list(rrule(freq=MONTHLY, bymonthday = -1, dtstart=start, until=end))
    if(monthly_ends[-1].date() != end.date()):
        monthly_ends.append(end)

    return monthly_starts, monthly_ends

# return dataframe with "Month" column and "Usage_" and "Cost_" columns for each period
# e.g., "Month", "Usage_Peak", "Cost_Peak", "Usage_Off-Peak", "Cost_Off-Peak"
def get_monthly_table(NVE: NVenergyUsage, plan: RatePlan, start: datetime, end: datetime):

    monthly_starts, monthly_ends = month_start_ends(start, end)
    
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


def format_time(x, _):
    hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
    return hm + ("am" if (x%24)<12 else "pm")


def chart_average_day_by_month(NVE: NVenergyUsage, start: datetime, end: datetime):
    monthly_starts, monthly_ends = month_start_ends(start, end)


    _, full_list = NVE.usage_by_hour_for_period(start, end)
    full_year_average = full_list.sum() / len(full_list)
    print(full_year_average)

    colors = ["lightcoral", "sandybrown", "dimgray", "lightgreen", "lightblue",
              "lightcoral", "lavender", "thistle", "darkgreen",
              "lightgray", "lavender", "thistle"]

    plt.rcParams.update({'font.size': 8})
    fig, ax = plt.subplots(ncols = 1, nrows = 2, figsize = (7.5, 6))
    fig.tight_layout(pad = 3.0)
    ax_summer = ax[0]
    ax_winter = ax[1]
    ax_summer.set_title("Summer Months")
    ax_winter.set_title("Winter Months")

    for a in ax:
        a.set_ylim([0, 10])
        a.spines["right"].set_visible(False)
        a.spines["top"].set_visible(False)

        a.xaxis.set_major_formatter(format_time)
        a.xaxis.set_ticks(np.arange(0, 24, 3))
        a.set_ylabel("avg kWh during this hour")

        hours = range(0, 24)
        a.plot(hours, [full_year_average for h in hours], "-.", color="lightgray")
        a.plot(hours, [full_year_average * 1.5 for h in hours], "-.", color="lightgray")
        

    for month_start, month_end in zip(monthly_starts, monthly_ends):

        hours, avg_usage = NVE.usage_by_hour_for_period(month_start, month_end)

        ax_to_plot = ax_winter
        if(month_start.month in [6, 7, 8, 9]): ax_to_plot = ax_summer
        ax_to_plot.plot(hours, avg_usage, '-o', label = month_start.strftime("%b"), color=colors[month_start.month-1])

        ax_summer.legend(loc = "upper left")
        ax_winter.legend(loc = "upper left")

    
    path = "post2/post2_average_usage_by_hour.png"
    plt.savefig(path)
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


# second part of blog
    s = datetime(2021, 9, 1)
    e = datetime(2022, 8, 31)

    chart_average_day_by_month(NVE, s, e)

# third part of blog post -- print graphs of my monthly usage.
    
    plans = Region("NV").get_rate_plans()

    for plan in plans:
        print(plan.plan_name)
        print_monthly_table(NVE, plan, s, e)



    
    
    
    
