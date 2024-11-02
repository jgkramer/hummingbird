
from datetime import datetime
from dateutil.relativedelta import relativedelta
import EIA_demand_data, EIA_generation_data
import re
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from ercotStorageReport import StorageData
from ercotRtmPrices import ErcotRtmPrices

import pytz

def format_time(x, _):
    hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
    return hm + ("am" if (x%24)<12 else "pm")

def analyze_month(pricing, storage, curr_date: datetime):

    # columns of this DF are Hour and Price, in quarter-hour increments
    month_table = pricing.get_monthly_average(curr_date)

    charges = storage.monthly_average_charging(curr_date)
    print(charges)
    charges_15m = [item for item in charges for i in range(4)]
    month_table["Charging"] = charges_15m

    discharges = storage.monthly_average_discharging(curr_date)
    discharges_15m = [item for item in discharges for i in range(4)]
    month_table["Discharging"] = discharges_15m

    month_table["Net Discharging"] = month_table["Discharging"] - month_table["Charging"]
    month_table["Net Sales"] = 0.25*month_table["Net Discharging"]*month_table["Price"]
    print(month_table)

    print(f"month {curr_date.strftime("%b %Y")}")
    print(f"total charging {sum(month_table["Charging"])}")
    print(f"total discharging {sum(month_table["Discharging"])}")
    print(f"net sales per day {sum(month_table["Net Sales"])}")

    fig, ax1 = plt.subplots()
    ax1.step(month_table["Hour"], month_table["Net Discharging"], where="post", color='lightblue', label='Charging')
    ax1.fill_between(month_table["Hour"], month_table["Net Discharging"], step="post", alpha = 0.5, color='lightblue')

    ax1.set_ylim(1.2*min(month_table["Net Discharging"]), 1.2*max(month_table["Net Discharging"]))
    neg_ratio = min(month_table["Net Discharging"])/max(month_table["Net Discharging"])

    ax1.set_xlabel("Time")
    ax1.set_ylabel("MW Net Discharging", color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2 = ax1.twinx()
    ax2.plot(month_table["Hour"], month_table["Price"], color = "r", label="Price")
    ax2.set_ylabel("Price $/MWh")
    ax2.set_ylim(neg_ratio*1.2*max(month_table["Price"]), 1.2*max(month_table["Price"]))

    ax1.legend()
    ax1.xaxis.set_major_formatter(format_time)
    ax1.xaxis.set_ticks(np.arange(0, 24+1, 3))
    fig.suptitle(f"{curr_date.strftime("%b %Y")}")
    fig.tight_layout()
    plt.show()

def storage_plot_one(storage: StorageData, dt_list):
    n = len(dt_list)
    fig, axes = plt.subplots(ncols = n, figsize = (8, 3), sharex = True, sharey = True)
    plt.rcParams.update({'font.size': 8})

    for i in range(n):
        dt = dt_list[i]
        charging = storage.daily_charging(dt)
        discharging = storage.daily_discharging(dt)
    # this is to make the last item of the bar chart look like a full hour instead of a single point
    
        charging.append(charging[-1])
        discharging.append(discharging[-1])

        axes[i].step(range(24 + 1), charging, where="post", color='orange', label='Charging')
        axes[i].step(range(24 + 1), discharging, where="post", color='mediumblue', label="Discharging")
        axes[i].legend()
        axes[i].spines["right"].set_visible(False)
        axes[i].spines["top"].set_visible(False)
        axes[i].set_ylabel("Charging / Discharging During Hour (MWh)")
        axes[i].xaxis.set_major_formatter(format_time)
        axes[i].xaxis.set_ticks(np.arange(0, 24+1, 3))
   
    fig.tight_layout()
    plt.savefig(f"post11_outputs/storage_example_{dt_list[0].year}_{dt_list[0].month}_{dt_list[0].day}.png")
    plt.show()

def get_utc_offsets(tz: str, start_date, end_date):
    tz = pytz.timezone(tz)
    start_local = tz.localize(start_date)
    start_offset = round(start_local.utcoffset().total_seconds() / 3600)
    end_local = tz.localize(end_date)
    end_offset = round(end_local.utcoffset().total_seconds() / 3600)
    return start_offset, end_offset

if "__main__" == __name__:

    start_date = datetime(2023, 2, 1)
    end_date = datetime.now()


    # this gets the BESS data
    directory = "./ercot_esr_reports/"
    storage_data = StorageData(directory, download = False, load_from_csv = True)

    start_date, end_date = storage_data.get_date_range()
    print(start_date, end_date)

    # finally, we get price data. 
    pricing_2024 = ErcotRtmPrices(datetime(2024, 10, 27))
    #pricing_2023 = ErcotRtmPrices(datetime(2023, 12, 31))

    storage_plot_one(storage_data, [datetime(2024, 7, 15), datetime(2024, 1, 15)])

    exit(1)

    curr_date = datetime(2024, 1, 1)
    while(curr_date < datetime(2024, 10, 31)):
        analyze_month(pricing_2024, storage_data, curr_date)
        curr_date = curr_date + relativedelta(months = 1)

    start_offset, end_offset = get_utc_offsets("US/Central", start_date, end_date)  

    # first we get the demand data for texas
    demand_df = EIA_demand_data.eia_request_data("ERCO", False, start_date, end_date, start_offset = start_offset, end_offset = end_offset)
    demand_df.to_csv("demand.csv")

    # then we get generation data for solar, wind and natural gas
    generation_df = EIA_generation_data.eia_generation_data("ERCO", start_date, end_date, fuel_list = ["SUN", "WND", "NG"], start_offset = start_offset, end_offset = end_offset)
    generation_df.to_csv("generation.csv")

