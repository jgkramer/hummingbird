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
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

def format_time(x, _):
    hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
    return hm + ("am" if (x%24)<12 else "pm")


def get_summer_TOU_peak():
    plans = Region("NV").get_rate_plans()
    plan = ([plan for plan in plans if plan.plan_type == "TOU"])[0]
    rate_series = plan.series()
    summer_rs = ([rs for rs in rate_series if rs.season.name == "Summer"])[0]
    segments = summer_rs.rate_segments
    peak_segment = ([seg for seg in segments if (
        seg.label == "On-Peak" and seg.weekend == False)])[0]
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
#    print(peak)
    
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


def print_monthly_table(NVE: NVenergyUsage, plan: RatePlan, start: datetime, end: datetime):
    assert((start.date() >= NVE.first_date.date()) and (end.date() <= NVE.last_date.date()))

    period_names = plan.get_period_names()

    monthly_starts = list(rrule(freq=MONTHLY, bymonthday = 1, dtstart=start, until=end))
    if(monthly_starts[0].date() != start.date()):
        monthly_starts = [start] + monthly_starts

    monthly_ends = list(rrule(freq=MONTHLY, bymonthday = -1, dtstart=start, until=end))
    if(monthly_ends[-1].date() != end.date()):
        monthly_ends.append(end)

    #setting up the data frame
    df = pd.DataFrame()
    df["Month"] = [d.strftime("%b %Y") for d in monthly_starts]
    for period_name in period_names:
        df["Usage_" + period_name] = [0 for d in monthly_starts]
        df["Cost_" + period_name]  = [0 for d in monthly_starts]

    for ix, (month_start, month_end) in enumerate(zip(monthly_starts, monthly_ends)):
        usage_stats = NVE.stats_by_period(plan, month_start, month_end)
        for usage_stat in usage_stats:
            df.loc[ix, "Usage_"+usage_stat.label] = round(usage_stat.kWh, ndigits = 1)
            df.loc[ix, "Cost_"+usage_stat.label] = round(usage_stat.cost, ndigits = 2)

    plt.rcParams.update({'font.size': 8})
    fig, ax = plt.subplots()

    print(df)
    dfsum = df.sum(axis = 0)
    print(dfsum)
    

    prev = None
    plots = []
    for period_name in period_names:
        if(prev is None):
            plots.append(ax.barh(df["Month"], df["Usage_"+period_name]))
        else:
            plots.append(ax.barh(df["Month"], df["Usage_"+period_name], left = prev))
        prev = df["Usage_"+period_name]

    print(plots[-1])
    ax.bar_label(plots[-1], fmt = "%d", padding = 5)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    plt.gca().invert_yaxis()
    plt.show()

    
if __name__ == "__main__":
    NVE = NVenergyUsage()

# first part of blog post -- plot the graphs for daily usage charts for specific days. 
    date_lists = [[datetime(2022, 8, 15), datetime(2022, 8, 31)],  # high - 8/15/22
                  [datetime(2022, 2, 1), datetime(2022, 2, 3)],
                  [datetime(2022, 5, 9), datetime(2022, 5, 15)]] #high

    high_temp_lists = [[96, 109],
                      [58, 53],
                      [72, 95]]

    low_temp_lists = [[79, 85],
                      [42, 33],
                      [54, 64]]    

    # source: https://www.wunderground.com/history/monthly/us/nv/henderson/KLAC/date/2022-8
    base_path = "post2/post2_usage_"
    for date_list, high_temps, low_temps in zip(date_lists, high_temp_lists, low_temp_lists):
        path = base_path + date_list[0].strftime("%b") + ".png"
        plot_usage_chart(NVE, date_list, high_temps, low_temps, path)


# second part of blog post -- get a table of monthly usage.
    s = datetime(2021, 9, 1)
    e = datetime(2022, 8, 31)

    both_starts, both_usage = list(zip(*NVE.usage_series_for_days(s, e)))
    print(sum(both_usage))

    region = Region("NV")
    plans = region.get_rate_plans()

    for plan in plans:
        print(plan.plan_name)
        print_monthly_table(NVE, plan, s, e)
       
    

    


        

    
    
    
    
