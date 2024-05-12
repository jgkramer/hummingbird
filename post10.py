import numpy as np
import pandas as pd
import os
import requests


import EIA_demand_data

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

import matplotlib as mpl
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
        print(full_df)
        full_df.to_csv(path)

    else:
        full_df = pd.read_csv(path)
        print(full_df)
    
    df = process_data(full_df)

    monthly_avg = df["value"].resample("ME").mean()

    pd.set_option("display.max_rows", None)

    monthly_avg.index = pd.MultiIndex.from_arrays([monthly_avg.index.year, monthly_avg.index.month], names=["year", "month"])
    print("monthly average in column")
    
    print(monthly_avg)

    yoy_increase = [(this/last - 1) for last, this in zip(monthly_avg[0:len(monthly_avg-12)], monthly_avg[12:len(monthly_avg)])]
    
    print("YoY increase")
    #print(yoy_increase)
    print("Mean ", statistics.mean(yoy_increase), "  Stdev ", statistics.stdev(yoy_increase))


    reshaped_df = monthly_avg.unstack(level=-1)
    print(reshaped_df)
    print(reshaped_df.columns)
    print(reshaped_df.index)
    
    output_path = "" + region + "test_output.csv"
    reshaped_df.to_csv(output_path)
    return reshaped_df


def annual_growth_stats(df):
    normalized_df = df / df.loc[2019]
    years_since_2019 =  normalized_df.index - 2019
    transformed_df = normalized_df.apply(lambda x: np.power(x, 1/years_since_2019) - 1, axis = 0)
    last_non_nan_values = transformed_df.apply(lambda column: column.dropna().iloc[-1] if not column.dropna().empty else None)
    print(last_non_nan_values)
    cum_growth_df = normalized_df - 1
    return cum_growth_df


def visualize(df, cumulative_growth = True):
    
    df = df.reset_index().melt(id_vars = "year", var_name ="month", value_name = "value")
    print(df)

    colors = plt.cm.Reds(np.linspace(0, 1, 2+len(df['year'].unique())))

    mpl.rcParams['font.size'] = 8
    plt.figure(figsize=(9, 3.5))

    for i, year in enumerate(sorted(df["year"].unique())):
        subset = df[df["year"]==year]
        plt.plot(subset["month"], subset["value"], color=colors[i+2], label=f"{year}", marker = "x", lw=0.2*(i+1), ls="-")
                    
    if not cumulative_growth:
        plt.ylim([0, 1.2*max(df["value"])])
        plt.ylabel("Average Demand During Month (GW)")    
    if cumulative_growth:
       plt.ylim([-0.2, 0.4])
       plt.ylabel("Demand % Change Since 2019")
       plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))

    plt.xlabel("Month")
    plt.xticks(range(1, 13))
    plt.legend(loc = "upper left", ncol = 2)
    plt.tight_layout()
    plt.gca().spines["right"].set_visible(False)
    plt.gca().spines["top"].set_visible(False)

    plt.show()

regions = ["DOM", "CPLE", "DUK", "TEN", "CAR"]
region_subba = [True, False, False, False, False]

if __name__ == "__main__":
    index = 0
    df = get_data(regions[index], region_subba[index], "" + regions[index] + "_2018_2024.csv", new_download = False)/1000
    visualize(df, cumulative_growth = False)
    cum_growth_df = annual_growth_stats(df)
    visualize(cum_growth_df, cumulative_growth = True)



    