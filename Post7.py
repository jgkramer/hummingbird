from specificHourlyUsage import NVenergyUsage, UsagePaths, SDenergyUsage
from hourlyEnergyUsage import HourlyEnergyUsage

from dailyPlots import DailyPlots

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from dateSupplements import DateSupplements

from typing import List

from rate_series import RateSegment, RateSeries, RatePlan
from fetch_seasons import Season
from region import Region

import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, PercentFormatter)

from hourlyEnergyUsage import UsageStats, HourlyEnergyUsage
from specificHourlyUsage import NVenergyUsage


def plot_demand(demand_costs: List, energy_costs: List, labels: List, path = None):

    ndays = 30
    max_demand = max(demand_costs)
    ymax = np.ceil((max_demand / (ndays * 1.5)) /.05) * 0.05

    plt.rcParams.update({'font.size': 8})
    fig, ax = plt.subplots(figsize = (7, 3.5))

    ax.set_xlim([0, 24])
    ax.set_xticks(range(0, 28, 4))
    ax.set_xlabel("Energy Consumption, in Avg. Hours per Day at Peak Demand")

    ax.set_ylim([0, ymax])
    ax.set_ylabel("Blended Cost of Energy per kWh", labelpad = 5)

    ax.yaxis.set_major_formatter(FormatStrFormatter('$%1.2f'))


    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout(pad = 0.75)

    
    hours = [(i+1)/4 for i in range(24*4)]
    for (d, e, l) in zip(demand_costs, energy_costs, labels):
        costs = [e + d/(h*ndays) for h in hours]
        ax.plot(hours, costs, label = l)

    ax.legend(loc = "upper right", frameon=False)
    if path == None:
        plt.show()
    else:
        plt.savefig(path)
    plt.close()


if __name__ == "__main__":
    NVE = NVenergyUsage(UsagePaths.NV_Kramer)
    SDE = SDenergyUsage(UsagePaths.SD_Marshall)

    date_list = [datetime(2022, 8, 16), datetime(2022, 8, 22)]
    
    colors_list = ["steelblue", "blue", "salmon", "red"]
    # colors_list = ['blue', 'dodgerblue', 'steelblue', 'salmon', 'lightpink', 'hotpink', 'red', 'pink', 'indianred', 'deeppink']


    DailyPlots.plot_intraday_usage(NVE, date_list, path = "post7/post7_august_comparison.png", colors_list = colors_list, data_labels_max = True)

    plans = Region("NV").get_rate_plans()
    for plan in plans:
        if not plan.has_demand(): continue
        print("plan: ", plan.plan_name)
        for d in date_list:
            print("date: ", d)
            usage_stats = NVE.stats_by_period(plan, d)

            print(usage_stats)

            ndays = 30
            
            summary = pd.DataFrame()
            summary["Period"] = [u.label for u in usage_stats]
            summary["kWh"] = [ndays * u.kWh for u in usage_stats]
            summary["kWh cost"] = [ndays * u.cost for u in usage_stats]
            summary["Peak Demand"] = [u.peak_demand for u in usage_stats]
            summary["Demand Charge"] = [u.demand_charge for u in usage_stats]

            print(summary)
            sums = summary[["kWh cost", "Demand Charge"]].sum()
            print(sums, "\n total: ", round(sum(sums), 2), "\n")


    date_list2 = []
    for i in range(6):
        date_list2.append(datetime(2022, 10, 4) + timedelta(days = i))
    
    DailyPlots.plot_intraday_usage(SDE,
                                   date_list2,
                                   path = "post7/post7_overlap.png",
                                   colors_list = ["purple", "orange", "green", "red", "pink", "blue"],
                                   data_labels_max = False,
                                   ymax = 3.25)


    print("Marshall 10/6/22 only: ", SDE.stats_by_period(plans[0], datetime(2022, 10, 6)))
    print("Marshall full week: ", SDE.stats_by_period(plans[0], date_list2[0], date_list2[-1]))

    plot_demand([7.69, 11.29, 15.33],
                [0.114, 0.068, 0.041],
                ["NV Non-TOU (\$7.69 / \$0.114)", "FL Non-TOU (\$11.29 / \$0.068)", "VA Large--Peak (\$15.33 / \$0.041)"],
                path = "post7/post7_blended_kWh.png")
    
    

        

