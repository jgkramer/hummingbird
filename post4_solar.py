
import calendar
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from typing import List

import matplotlib as mpl
import matplotlib.pyplot as plt
from eiaGeneration import EIAGeneration

from periodicCharts import HourlyChart
from monthlyPlots import MonthlyPlots, PlotType

from matplotlib.axis import Axis  
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as pltdates

def keyGenerationStats(hourlyValues):
    stats = {}
    stats["maxGen"] = max(hourlyValues)
    stats["totalGen"] = sum(hourlyValues)
    stats["equivHours"] = stats["totalGen"]/stats["maxGen"]
    stats["activeHours"] = sum([1 if x > 0.1*stats["maxGen"] else 0 for x in hourlyValues])                        
    stats["strongHours"] = sum([1 if x > 0.6*stats["maxGen"] else 0 for x in hourlyValues])                                
    return stats


def prepChart(dims):
    fig, ax = plt.subplots(figsize = dims)
    plt.rcParams.update({'font.size': 8})
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    return fig, ax


TOP_N = 3

def dailyGenerationChart(eiag: EIAGeneration, starts: List[datetime], ends: List[datetime], plot_titles: List[str], path: str):
    plots = len(starts)
    fig, axes = plt.subplots(nrows = 1, ncols = plots, sharey = True, figsize = (8, 3))

    if(plots == 1): axes = [axes]

    plt.rcParams.update({'font.size': 8})
    maxy = 0

    for start, end, ax, title in zip(starts, ends, axes, plot_titles):
        dates, totals = eiag.dailyTotals(start, end)
        dates2, totals2 = eiag.topNOnly(start, end, N=TOP_N)
        if max(totals) > maxy: maxy = max(totals)

        ax.tick_params(axis =  "both", which = "major", labelsize = 7)
        ax.plot(dates, totals, label = "All Days")
        ax.plot(dates2, totals2, label = "Top 3 Days in Month")
        ax.legend()
        
        tick_dates = [datetime(2022, m, 15) for m in range(1, 13)]
        tick_dates_labels = [d.strftime("%b %d") for d in tick_dates]
        ax.set_xticks(tick_dates, labels = tick_dates_labels)

        if(ax == axes[0]):
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
            ax.set_ylabel("Daily NV Power Solar Generation (MWh)", fontsize=8)
            
        ax.set_title(title, fontsize = 8)

        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)

    fig.tight_layout()
    [ax.set_ylim([0, maxy*1.2]) for ax in axes]
    
    plt.savefig(path)
    plt.show()
    plt.close()


def getEIAGeneration(BAname: str, start: datetime, end: datetime) -> EIAGeneration:
    paths = []
    d = start
    while d < end:
        paths.append(f"./generation_data/{BAname}Generation{d.year}_{d.month:02}.csv")
        d = d + relativedelta(months = +1)
    return EIAGeneration(paths)

    
if __name__ == "__main__":

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    BAname = "NVPower" # "DukeEast" "NVPower" "ERCOT" "DukeFL"
    StateName = "NV"
    ymax = 2250 if BAname == "NVPower" else None

    start = datetime(2022, 1, 1)
    end = datetime(2023, 1, 1)

    # read full year data for NV
    eiag = getEIAGeneration(BAname, start, end)



    # chart 1: every day vs. top 3 days in each month
    daily_starts = [datetime(2022, 1, 1)]
    daily_ends = [datetime(2022, 12, 31)]
    dailyGenerationChart(eiag, daily_starts, daily_ends, ["2022 Generation"], f"post4/post4_{BAname}DailyChart.png")

    # chart 2: let's get daily line charts for JULY only
    july1 = datetime(2022, 7, 1)
    aug1 = datetime(2022, 8, 1)

    days, generations = eiag.allHoursInDays(july1, aug1)
    _, avgs = eiag.averageDayInPeriod(july1, aug1)
    _, avgs_top = eiag.averageDayInPeriodFiltered(july1, aug1, TOP_N)
    _, avgs_hour = eiag.averageDayInPeriodFilteredHourly(july1, aug1, TOP_N)

    print(avgs)
    print(avgs_top)
    print(avgs_hour)
    
    y_values = generations + [avgs, avgs_top, avgs_hour]
    
    legends = ["July 1-10"] + [None]*9 + ["July 11-20"] + [None]*9 + ["July 21-31"] + [None]*(len(days) - 21) + ["Avg (All Days)", "Top 3 (Day)", "Top 3 (Hour)"]
    colors =  ["lightblue"]*10 + ["lightgreen"]*10 + ["lightgray"]*(len(days)-20) + ["purple", "red", "black"]

    
    hours = range(24)
    HourlyChart.hourlyLineChart(hours,
                                y_values,
                                "NV Power Hourly Solar Generation (MWh)",
                                legends,
                                colors,
                                path = f"post4/post4_{BAname}JulyDays.png",
                                title = None,
                                x_axis_label = "Hour Starting (Standard Time)",
                                annotate = len(y_values) - 1,
                                ymax = ymax,
                                table_series = [len(y_values) - 3, len(y_values) - 2, len(y_values)-1])
                                

    # chart 3: generate the monthly line charts. 
    x_values = [x for x in range(0, 24)]
    y_values_list = []
    y_values_list_top = []
    series_labels = []

    dates_by_month = []
    totals_by_month = []

    df = pd.DataFrame()
    df["Hour Start"] = range(0, 24)

    nMonths = 12*(end.year - start.year) + (end.month - start.month)
    for month in range(nMonths):
        s = start + relativedelta(months = month)
        e = s + relativedelta(months = +1)
        _, avgs = eiag.averageDayInPeriod(s, e)
        y_values_list.append(avgs)
        
        _, avgs_hour = eiag.averageDayInPeriodFilteredHourly(s, e, TOP_N)
        y_values_list_top.append(avgs_hour)

        df[s.strftime("%b")] = avgs_hour

        series_labels.append(s.strftime("%b-%y"))

        # this is the list for each month of the daily totals, will use this later
        dates, totals = eiag.dailyTotals(s, e)
        dates_by_month.append(dates)
        totals_by_month.append(totals)

    df.to_csv("post4/NV_ideal_solar_capacity.csv", index = False)

        
    cmap = mpl.cm.get_cmap('tab20c')
    #gray for winter (16), green spring(8), blue summer(0, 1, 2), reds fall (4, 5, 6)
    series_color_nums = [16, 16, 9, 9, 9, 0, 0, 0, 5, 5, 5, 16]  
    series_colors = [cmap(x/20) for x in series_color_nums]

    series_styles = ["dashed", "dotted", "solid"] * 4
               

    # chart 4: line chart for every month
    y_axis_label = f"{StateName} Ideal Solar Generation by Hour of Day(MWh)"                            

    HourlyChart.hourlyLineChart(x_values,
                                y_values_list_top, ## HOURS!
                                y_axis_label,
                                series_labels,
                                series_colors,
                                f"post4/post4_{BAname}_all_hourly.png",
                                title = None,
                                x_axis_label = "Hour Starting (Standard Time)",
                                annotate = None,
                                ymax = ymax,
                                series_styles = series_styles,
                                height_scale = 1.25)

 # chart 5: HTML table for June and December Data
    
    max_hour = eiag.maxOutput(3)

 
    for month in [3, 6, 12]:
        capacity_stats = keyGenerationStats(y_values_list_top[month-1])
        active_hours = sum([1 if g >= 0.1*capacity_stats["maxGen"] else 0 for g in y_values_list_top[month-1]])

        row_html = ["<tr>\n"]
        row_html.append(f'  <th scope="col" style="background-color: #D6EEEE">{datetime(2022, month, 1).strftime("%B")}</th>\n') #Month
        row_html.append(f' <td>{capacity_stats["totalGen"]:,.0f}</td>') #DailyGenerationCapacity (MWh)
        row_html.append(f'<td>{capacity_stats["maxGen"]:,.0f}</td>') #Max Hourly Rate (MWh)
        row_html.append(f'<td>{active_hours:,.0f}</td>') #Active Hours (> 10%)
        row_html.append(f'<td>{capacity_stats["equivHours"]:.1f}</td>') #Hours of Full Generation
        row_html.append(f'<td>{capacity_stats["totalGen"]/max_hour:,.1f}</td>')
        row_html.append('</tr>\n')
        
        print("".join(row_html))

    row_html = ["<tr>\n"]
    row_html.append('<th scope="col" style="background-color: #D6EEEE">24h x Max. Physical Output</th>/n')
    row_html.append(f'<td>{24*max_hour:,.0f}</td> <td>{max_hour:,.0f}</td><td>-</td><td>-</td><td>24</td>')
    row_html.append('</tr>\n')
    print("".join(row_html))

    # chart 6: capacity vs. actual by month
    months = [datetime(2023, month, 1).strftime("%b") for month in range(1, 13)]
    capacities_by_month = [sum(l)/max_hour for l in y_values_list_top]
    actuals_by_month = [sum(l)/max_hour for l in y_values_list]

    actuals_labels = [f"{(a/c*100):.0f}%" for (a, c) in zip(actuals_by_month, capacities_by_month)]

    MonthlyPlots.monthlyUsageLineChart(months,
                                       [capacities_by_month, actuals_by_month],
                                       ["Month's Ideal Solar Generation", "2022 Actual (% of Month's Capacity)"],
                                       ["lightblue", "blue"],
                                       None,
                                       f"post4/post4_{BAname}_monthly.png",
                                       show_average = False,
                                       text_label_list = [None, actuals_labels],
                                       plottype = PlotType.OTHER,
                                       y_axis_label = "Hours of Max. Output per Day")
                                    

    # output totals
    total_capacity = sum([capacities_by_month[month] * calendar.monthrange(start.year, month+1)[1] for month in range(12)])/365
    total_actual = sum([actuals_by_month[month] * calendar.monthrange(start.year, month+1)[1] for month in range(12)])/365
    print(f"total capacity: {total_capacity:.2f} hours, total actual: {total_actual:.2f}")
                                                  
    # loop over multiple states

    BAs = ["NVPower", "DukeEast", "ERCOT", "DukeFL"]
    States = ["Nevada", "NC", "Texas", "Florida"]

    nMonths = 12*(end.year - start.year) + (end.month - start.month)
    month_names = [(start + relativedelta(months = month)).strftime("%b") for month in range(nMonths)]

    absolute_max = dict()
    capacities_lists = dict()
    actuals_lists = dict()
    
    capacity_by_month = dict()
    actual_by_month = dict()
    total_capacity = dict()
    total_actual = dict()

    for BA in BAs:

        eiag = getEIAGeneration(BA, start, end)
        
        absolute_max[BA] = eiag.maxOutput(3)

        capacity_by_month[BA] = []
        actual_by_month[BA] = []

        actuals_lists[BA] = list()
        capacities_lists[BA] = list()

        #read data for this state

        for month in range(nMonths):
            s = start + relativedelta(months = month)
            e = s + relativedelta(months = +1)
            _, avgs = eiag.averageDayInPeriod(s, e)
            _, avgs_top = eiag.averageDayInPeriodFilteredHourly(s, e, TOP_N)
            actuals_lists[BA].append(avgs)
            capacities_lists[BA].append(avgs_top)
            
            if max(avgs_top) > absolute_max[BA]: absolute_max[BA] = max(avgs_top)

        print("\nMax. Physical Output for " + BA + " " + str("{:,.2f}".format(absolute_max[BA])))
        capacity_by_month[BA] = [sum(l)/absolute_max[BA] for l in capacities_lists[BA]]
        print("capacity by month is:")
        print(" ".join("{:.2f}".format(x) for x in capacity_by_month[BA]))

        actual_by_month[BA] = [sum(l)/absolute_max[BA] for l in actuals_lists[BA]]
        print("actual by month is:")
        print(" ".join("{:.2f}".format(x) for x in actual_by_month[BA]))

        total_capacity[BA] = sum([(capacity_by_month[BA])[month] * calendar.monthrange(start.year, month+1)[1] for month in range(12)])/365
        total_actual[BA] = sum([(actual_by_month[BA])[month] * calendar.monthrange(start.year, month+1)[1] for month in range(12)])/365
        

    MonthlyPlots.monthlyUsageLineChart(months,
                                       [capacity_by_month[BA] for BA in BAs],
                                       States,
                                       ["lightblue", "blue", "green", "purple"],
                                       "Ideal Solar Generation by Month and Locale",
                                       f"post4/post4_multi_state.png",
                                       show_average = False,
                                       text_label_list = None,
                                       plottype = PlotType.OTHER,
                                       y_axis_label = "Hours of Max. Output per Day")


    JUNE = 5 # June

    normalized_hourlies = [np.divide((capacities_lists[BA])[JUNE], max((capacities_lists[BA])[JUNE])) for BA in BAs]
    above_75 = [f"{sum([1 if x >= 0.9 else 0 for x in normalized_hourly]):.2f}" for normalized_hourly in normalized_hourlies]
    print("Hours generating at least 75% of max power:")
    print(BAs, above_75)
    
    HourlyChart.hourlyLineChart(x_values,
                                normalized_hourlies, 
                                "Ideal Generation by Hour of Day (normalized)",
                                States,
                                ["lightblue", "blue", "green", "purple"],
                                f"post4/post4_multi_state_june_hours.png",
                                title = "June 2022",
                                x_axis_label = "Hour Starting (Standard Time)",
                                annotate = None,
                                ymax = None,
                                series_styles = None,
                                height_scale = 1.0)
    


    #ugh a bar chart
    fig, ax = prepChart(dims = (7, 3.5))
    plots = []
    plots.append(ax.bar(States, [total_capacity[BA] for BA in BAs], label = "Ideal Solar Generation", color = "lightblue"))
    #ax.bar_label(plots[-1], fmt = fmt_str, padding = 5)

    plots.append(ax.bar(States, [total_actual[BA] for BA in BAs], label = "Actual (% of Ideal)", color = "slategray"))
    ax.bar_label(plots[-1],
                 labels = [f"{total_actual[BA]/total_capacity[BA]*100:.0f}%" for BA in BAs],
                 padding = -15,
                 color = "white",
                 fontweight = "bold")

    print("ideal solar generation " + str(total_capacity))
    print("actual generation " + str(total_actual))
    
                 
    ax.set_ylim([0, 1.2*max(total_capacity.values())])
    ax.set_ylabel("Avg. Hours of Max. Output per Day")
    ax.legend(loc = "upper right")
    fig.tight_layout(pad = 1.0)

    plt.savefig(f"post4/post4_multi_state_bar.png")
    plt.show()
    plt.close()


    

    


        

