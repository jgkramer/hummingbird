
from datetime import datetime
from dateutil.relativedelta import relativedelta
import EIA_demand_data, EIA_generation_data
import re
import numpy as np
import pandas as pd
import math

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from ercotStorageReport import StorageData
from ercotRtmPrices import ErcotRtmPrices

import pytz

def format_time(x, _):
    hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
    return hm + ("am" if (x%24)<12 else "pm")


def average_prices(pricing, storage, date_list):
    for curr_date in date_list:
        prices = pricing.get_monthly_average(curr_date)["Price"]
        charges = storage.monthly_average_charging(curr_date)
        charges_15m = [item for item in charges for i in range(4)]
        charging_cost = [0.25 * c * p for (c, p) in zip(charges_15m, prices)]
        discharges = storage.monthly_average_discharging(curr_date)
        discharges_15m = [item for item in discharges for i in range(4)]
        discharging_cost = [0.25 * d * p for (d, p) in zip(discharges_15m, prices)]
        print(f"{curr_date.strftime("%b")}: charging {sum(charges):0.1f} cost {(sum(charging_cost) / sum(charges)):0.2f} discharging {sum(discharges):0.1f} cost {(sum(discharging_cost) / sum(discharges)):0.2f}")


def plot_prices(pricing, storage, date_list, figpath, chargemin = None, chargemax = None, pricemax = None):
    # columns of this DF are Hour and Price, in quarter-hour increments

    ncols = 2
    fig, axes = plt.subplots(figsize = (9, 4), ncols = ncols, nrows = 1)

    month_tables = []

    min_charge = 0 if chargemin == None else chargemin
    max_charge = 0 if chargemax == None else chargemax
    max_price = 0 if pricemax == None else pricemax

    for curr_date in date_list:
        month_table = pricing.get_monthly_average(curr_date)
        
        charges = storage.monthly_average_charging(curr_date)
        charges_15m = [item for item in charges for i in range(4)]
        month_table["Charging"] = charges_15m
        month_table["Charging Price"] = 0.25*month_table["Charging"]*month_table["Price"]

        discharges = storage.monthly_average_discharging(curr_date)
        discharges_15m = [item for item in discharges for i in range(4)]
        month_table["Discharging"] = discharges_15m

        month_table["Net Discharging"] = month_table["Discharging"] - month_table["Charging"]
                  
        month_tables.append(month_table)
      
        if (max(month_table["Net Discharging"]) > max_charge): max_charge = max(month_table["Net Discharging"])
        if (min(month_table["Net Discharging"]) < min_charge): min_charge = min(month_table["Net Discharging"])
        if (max(month_table["Price"]) > max_price): max_price = max(month_table["Price"])
#        print("min charge ", min_charge)
            
    
    for ix, (curr_date, month_table) in enumerate(zip(date_list, month_tables)):
        ax1 = axes[ix]
        ax2 = ax1.twinx()

        ax1.spines["top"].set_visible(False)
        ax2.spines["top"].set_visible(False)

        if(ix == 0):
            ax1.spines["right"].set_visible(False)
            ax2.spines["right"].set_visible(False)
        if(ix == 1):
            ax1.spines["left"].set_visible(False)
            ax2.spines["left"].set_visible(False)

        ax1.step(month_table["Hour"], month_table["Net Discharging"], where="post", color='lightblue', label='Net Discharging (MWh)')
        ax1.fill_between(month_table["Hour"], month_table["Net Discharging"], step="post", alpha = 0.5, color='lightblue')
        
        ax2.plot(month_table["Hour"], month_table["Price"], color = "r", label="Electricity Price ($/MWh)")
        
        ax1.set_ylim(1.1*min_charge, 1.1*max_charge)
        neg_ratio = min_charge/max_charge
        ax2.set_ylim(neg_ratio*1.1*max_price, 1.1*max_price)
        
        # merge the legends for the two axes together
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()

        if(ix == 0): 
            ax1.set_ylabel("MW Net Discharging", color='blue')
            ax1.legend(handles=handles1 + handles2, labels=labels1 + labels2, loc='upper left', frameon = False)
            
            ax1.tick_params(axis='y', labelcolor='blue')
            ax2.tick_params(axis='y', which='both', right=False, labelright=False)

        if(ix == 1): 
            ax2.set_ylabel("Price $/MWh", color='red')
            ax2.tick_params(axis='y', labelcolor='red')
            ax1.tick_params(axis='y', which='both', left=False, labelleft=False)

        ax1.xaxis.set_major_formatter(format_time)
        ax1.xaxis.set_ticks(np.arange(0, 24+1, 4))
        ax1.set_title(f"{curr_date.strftime("%b %Y")}")
    
    fig.tight_layout()
    plt.savefig(figpath, dpi=300)
    plt.show()

def multi_month_net(storage: StorageData, dt_list, path, ylim = None):
    plt.rcParams.update({'font.size': 8})
    fig, axes = plt.subplots(figsize = (7.5, 3))
    
    colors = ["#FFA500", "#0000FF"]  # Start with green, end with blue
    cmap = LinearSegmentedColormap.from_list("red_to_blue", colors)
    color_sequence = cmap(np.linspace(0, 1, len(dt_list)))

    axes.set_xlim(0, 24)
    axes.spines["right"].set_visible(False)
    axes.spines["top"].set_visible(False)
    axes.set_ylabel("Net Discharging (Charging) During Hour (MWh)")
    axes.xaxis.set_major_formatter(format_time)
    axes.xaxis.set_ticks(np.arange(0, 24+1, 3))
    axes.plot(np.arange(0.5, 24.5, 1.0), [0]*24, color="gray", linewidth = 1.0)
    for dt, color in zip(dt_list, color_sequence):
        charging = storage.monthly_average_charging(dt)
        discharging = storage.monthly_average_discharging(dt)
        gw_discharge = sum(discharging)/1000
        gw_charge = sum(charging)/1000
        # stats = f"{gw_discharge:0.2f} GW discharge / {gw_charge:0.2f} GW charge"
        net = [d - c for (d, c) in zip(discharging, charging)]
        axes.plot(np.arange(0.5, 24.5, 1.0), net, color=color, label= datetime.strftime(dt, "%b"), linewidth = 1.0)
    
    if(ylim is not None):
        axes.set_ylim(ylim)

    axes.legend(frameon = False)
    fig.tight_layout()
    plt.savefig(path, dpi=300) 
    plt.show()
    
def bar_charts(storage: StorageData, dt_list, path):
    months = [datetime.strftime(dt, "%b") for dt in dt_list]
    charging = [sum(storage.monthly_average_charging(dt))/1000 for dt in dt_list]
    discharging = [sum(storage.monthly_average_discharging(dt))/1000 for dt in dt_list]
    capacity = [storage.monthly_average_discharge_capacity(dt) / 1000 for dt in dt_list]
    
    fig, ax = plt.subplots(figsize = (7.5, 3))

    bar_width = 0.35
    x = np.arange(len(months))
    ax.bar(x - bar_width / 2, charging, width=bar_width, color='orange', label='Charging')
    ax.bar(x + bar_width / 2, discharging, width=bar_width, color='mediumblue', label='Discharging')
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.set_ylim([0, math.ceil(max(charging))])
    
    
    # Labels and title
    ax.set_ylabel('Average Daily Totals During Month (GWh)')
    ax.set_xticks(x, months)

    for i in range(len(months)):
        label = discharging[i]/charging[i]
        print(f"{datetime.strftime(dt_list[i], "%b")}: ratio {label:0.1%} discharge hours {discharging[i]/capacity[i]:0.2f}, discharging {discharging[i]:0.2f}, capacity {capacity[i]:0.2f}")
        ax.text(i - bar_width / 2, charging[i] + 0.25, f"{charging[i]:0.1f}", ha='center', va='bottom', fontsize = 7, color = "darkorange")
        ax.text(i + bar_width / 2, discharging[i] + 0.25, f"{discharging[i]:0.1f}", ha='center', va='bottom', fontsize = 7, color = "darkblue")

    ax2 = ax.twinx()
    ax2.set_ylim([0, math.ceil(max(charging))])
    ax2.plot(x, capacity, color = "darkgray", label = "Installed Discharge Capacity (GW)")
    ax2.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    handles1, labels1 = ax.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()

    ax.legend(handles=handles1 + handles2, labels=labels1 + labels2, loc='upper left', frameon = False)
    plt.tight_layout()
    # Show the plot
    plt.savefig(path, dpi=300) 
    plt.show()

def storage_plot_one(storage: StorageData, dt_list):
    n = len(dt_list)
    plt.rcParams.update({'font.size': 8})
    fig, axes = plt.subplots(ncols = n, figsize = (9, 3), sharex = True, sharey = True)
    if(n == 1):
        axes = [axes]
    
    for i in range(n):
        dt = dt_list[i]
        charging = storage.daily_charging(dt)
        discharging = storage.daily_discharging(dt)
        print("Total Charge:", sum(charging))
        print("Total Discharge:", sum(discharging))
        print("Ratio", sum(discharging)/sum(charging))
    # this is to make the last item of the bar chart look like a full hour instead of a single point
    
        charging.append(charging[-1])
        discharging.append(discharging[-1])

        axes[i].set_xlim([0, 24])
        axes[i].step(range(24 + 1), charging, where="post", color='orange', label='Charging')
        axes[i].step(range(24 + 1), discharging, where="post", color='mediumblue', label="Discharging")
        
        axes[i].spines["right"].set_visible(False)
        axes[i].spines["top"].set_visible(False)
        axes[i].set_title(dt.strftime("%-d-%b-%y"), fontsize=8, pad = -100)
        if(i == 0):
            axes[i].set_ylabel("Charging / Discharging During Hour (MWh)")
            axes[i].legend(frameon = False)
        else: 
            axes[i].yaxis.set_visible(False)
            axes[i].spines["left"].set_visible(False)

        axes[i].xaxis.set_major_formatter(format_time)
        axes[i].xaxis.set_ticks(np.arange(0, 24+1, 4))
   
    fig.tight_layout()
    plt.savefig(f"post11_outputs/storage_example_{dt_list[0].year}_{dt_list[0].month}_{dt_list[0].day}.png", dpi=300)
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

    storage_plot_one(storage_data, [datetime(2024, 1, 1), datetime(2024, 7, 15)])

    months1 = [datetime(2024, m, 1) for m in [1, 2, 3, 4, 5]]
    multi_month_net(storage_data, months1, "post11_outputs/months1.png", ylim = [-1500, 2000])

    months2 = [datetime(2024, m, 1) for m in [6, 7, 8, 9, 10, 11]]
    multi_month_net(storage_data, months2, "post11_outputs/months2.png", ylim = [-2000, 2500])

    bar_charts(storage_data, [datetime(2024, m+1, 1) for m in range(11)], "post11_outputs/monthly_bars.png")

    # finally, we get price data. 
    pricing_2024 = ErcotRtmPrices(datetime(2024, 11, 10))
    #pricing_2023 = ErcotRtmPrices(datetime(2023, 12, 31))

    date_list = [datetime(2024, m, 1) for m in [1, 3]]
    plot_prices(pricing_2024, storage_data, date_list, "post11_outputs/price1.png", chargemin = -1250, chargemax = 2000, pricemax = 150/1.1)

    date_list = [datetime(2024, m, 1) for m in [7, 9]]
    plot_prices(pricing_2024, storage_data, date_list, "post11_outputs/price2.png", chargemin = -1250, chargemax = 2000, pricemax = 150/1.1)

    average_prices(pricing_2024, storage_data, [datetime(2024, m, 1) for m in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]])
#    date_list = [datetime(2024, m, 1) for m in [9, 11]]
#    analyze_month(pricing_2024, storage_data, date_list, "post11_outputs/price3.png", chargemin = -1250, chargemax = 2000, pricemax = 150/1.1)
    
    start_offset, end_offset = get_utc_offsets("US/Central", start_date, end_date)  

    # first we get the demand data for texas
    demand = EIA_demand_data.EIA_demand("ERCO", False, start_date, end_date, start_offset = start_offset, end_offset = end_offset)
    demand.daily_demand(datetime(2024, 10, 15))
    demand.monthly_demand(datetime(2024, 10, 15))

    # then we get generation data for solar, wind and natural gas
#    generation_df = EIA_generation_data.eia_generation_data("ERCO", start_date, end_date, fuel_list = ["SUN", "WND", "NG"], start_offset = start_offset, end_offset = end_offset)
#    generation_df.to_csv("post11_data/generation.csv")

