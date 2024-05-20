import numpy as np
import pandas as pd
import os
import requests


import EIA_demand_data

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import statistics

import os



def to_percent(y, position):
    return f"{100 * y:.0f}%"

def replace_outlier(df, outliers, index):
    start = max(0, index - 50)
    end = min(len(df), index + 51)
    valid_data = df["value"][start:end].where(~outliers[start:end])
    return valid_data.mean()

def process_data(df):
    df["dt"] = pd.to_datetime(df["period"], format ='%Y-%m-%dT%H')
    df["value"] = pd.to_numeric(df["value"])
    df["value"] = pd.to_numeric(df["value"])
    df.reset_index(inplace = True)

    outliers = df["value"] > 100 * df["value"].mean()
    for index in df[outliers].index:
        df.at[index, "value"] = replace_outlier(df, outliers, index)

    df.set_index("dt", inplace = True, drop = False)

    return df

def get_data(region: str, subba: bool, path: str, new_download = True):
    if(new_download):
        start_date = datetime(2019, 1, 1)
        today = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
        full_df = EIA_demand_data.eia_request_data(region, subba, start_date, today)
        full_df.to_csv(path)

    else:
        full_df = pd.read_csv(path)
    
    df = process_data(full_df)

    monthly_avg = df["value"].resample("ME").mean()

    pd.set_option("display.max_rows", None)

    monthly_avg.index = pd.MultiIndex.from_arrays([monthly_avg.index.year, monthly_avg.index.month], names=["year", "month"])
    print("monthly average in column")

    yoy_increase_pct = [(this/last - 1) for last, this in zip(monthly_avg[0:len(monthly_avg-12)], monthly_avg[12:len(monthly_avg)])]
    print("YoY increase %: Mean ", statistics.mean(yoy_increase_pct), "  Stdev ", statistics.stdev(yoy_increase_pct))

    yoy_increase_abs = [(this - last) for last, this in zip(monthly_avg[0:len(monthly_avg-12)], monthly_avg[12:len(monthly_avg)])]
    print("YoY increase MW: Mean ", statistics.mean(yoy_increase_abs), "  Stdev ", statistics.stdev(yoy_increase_abs))

    reshaped_df = monthly_avg.unstack(level=-1)
    
    output_path = "" + region + "test_output.csv"
    reshaped_df.to_csv(output_path)
    return reshaped_df


def annual_growth_stats(df, percent = True):

    if(percent == True):
        df = df / df.loc[2019]
        growth_df = df - 1

    else: 
        growth_df = df - df.loc[2019]
    
    return growth_df


data_centers = [1421, 1808, 2302, 2767, 3375, 4066]
def plot_growth_vs_datacenters(growth_df, path = "a.png"):
    plt.figure(figsize=(6, 3.5))
    annual_growth = growth_df.mean(axis = 1)
    df = pd.DataFrame(annual_growth, columns = ["Demand Growth"])
    df["Data Centers GW"] = [x/1000 - data_centers[0]/1000 for x in data_centers]

    mpl.rcParams['font.size'] = 8
    plt.gca().spines["right"].set_visible(False)
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["left"].set_visible(False)
    plt.gca().set_yticklabels([])
    plt.gca().set_yticks([])

    plt.ylim([-1, 3.0])
    plt.plot(df.index, df["Demand Growth"], label = "Dominion Virginia Electricity Demand", marker = "x", color = "slategrey", lw = 0.75)
    plt.plot(df.index, df["Data Centers GW"], marker = "x", ls = "--", color = "darkorange", lw = 0.75)
    plt.plot(df.index[:-1], df["Data Centers GW"][:-1], marker = "x", label = "Dominion Data Center Electricity Usage", color = "darkorange", lw = 0.75)

    for i in df.index:
        est = " (est.)" if i == 2024 else ""
        ytd = " (ytd)" if i == 2024 else ""
        plt.annotate(f'{df["Demand Growth"][i]:0.2f}' + ytd, (i, df["Demand Growth"][i]), textcoords="offset points", xytext=(0,-17), ha='center', color = "slategrey", fontweight = "bold")
        plt.annotate(f'{df["Data Centers GW"][i]:0.2f}' + est, (i, df["Data Centers GW"][i]), textcoords="offset points", xytext=(0,+10), ha='center', color = "darkorange", fontweight = "bold")

    plt.gca().set_title("Growth (in GW) since 2019", loc = "center", pad = -10, fontsize = 8) 
    plt.legend(loc = "lower right", frameon=False)
    plt.tight_layout()
    plt.savefig(path)
    plt.show()


def visualize(df_list, cumulative_growth = True, title_list = [], path = "a.png"):

    fig, axes = plt.subplots(nrows = 1, ncols = len(df_list), figsize = (9, 3.5))
    axes = np.atleast_1d(axes) # this makes sure that it is a list, rather than a single object

    mpl.rcParams['font.size'] = 8

    for index, df, ax, title in zip(range(len(df_list)), df_list, axes, title_list):
        df = df.reset_index().melt(id_vars = "year", var_name ="month", value_name = "value")
        
        colors = plt.cm.Reds(np.linspace(0, 1, 2+len(df['year'].unique())))
        
        for i, year in enumerate(sorted(df["year"].unique())):
            subset = df[df["year"]==year]
            ax.plot(subset["month"], subset["value"], color=colors[i+2], label=f"{year}", marker = "x", lw=0.2*(i+1), ls="-")
                    
        if not cumulative_growth:
            ax.set_ylim([0, 1.2*max(df["value"])])
            if(index == 0): ax.set_ylabel("Average Demand During Month (GW)", fontsize = 8)

        if cumulative_growth:
            ax.set_ylim([-0.2, 0.4])
            if(index == 0): ax.set_ylabel("Demand % Change Since 2019", fontsize = 8)
            ax.yaxis.set_major_formatter(FuncFormatter(to_percent))
            
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        ax.tick_params(axis="both", labelsize = 8)
        
        legend_loc = "upper left" if cumulative_growth else "lower left"
        if(index == 0): ax.legend(loc = legend_loc, ncol = 2, frameon=False)
    
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)

        ax.set_title(title, loc = "center", pad = -10, fontsize = 8)
    
    plt.tight_layout()
    plt.savefig(path)
    plt.show()
   
regions = ["DOM", "TEN", "CAR", "AEP", "BC"]
sub_ba =  [True, False, False, True, True]
fullname = ["Dominion Virginia", "Tennessee", "Carolinas", "American Electric Power", "Baltimore"]

if __name__ == "__main__":
    download = False

    #Virginia
    index = 0
    df = get_data(regions[index], sub_ba[index], "./" + regions[index] + "_2018_2024.csv", new_download = download)/1000
    visualize([df], cumulative_growth = False, title_list = [fullname[index]], path = f"./post10/post10_{regions[index]}_GW_demand.png")

    growth_percentage_df = annual_growth_stats(df, True)
    visualize([growth_percentage_df], cumulative_growth = True, title_list = [fullname[index]], path = f"./post10/post10_{regions[index]}_growth.png")


    dfList = [get_data(regions[index], sub_ba[index], "./" + regions[index] + "_2018_2024.csv", new_download = download)/1000 for index in [1, 2]]
    dfList2 = [annual_growth_stats(df, True) for df in dfList]

    visualize(dfList, cumulative_growth = False, title_list = fullname[1:3], path = f"./post10/post10_multi_GW_demand_1.png")

    dfList = [get_data(regions[index], sub_ba[index], "./" + regions[index] + "_2018_2024.csv", new_download = download)/1000 for index in [3, 4]]
    dfList2 = [annual_growth_stats(df, True) for df in dfList]

    visualize(dfList, cumulative_growth = False, title_list = fullname[3:5], path = f"./post10/post10_multi_GW_demand_2.png")


    #TEN, CAR, AEP

    if regions[index] == "DOM":
        growth_df = annual_growth_stats(df, False)
        plot_growth_vs_datacenters(growth_df, path = f"./post10/post10_data_center_comparison.png")





    
    