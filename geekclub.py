
from datetime import datetime
from dateutil.relativedelta import relativedelta
import EIA_demand_data, EIA_generation_data
import numpy as np
import pandas as pd
import math
from scipy.stats import linregress
import matplotlib.dates as mdates

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import EIA_demand_data, EIA_generation_data


colors = {
    "NG": "#FF7A0E",
    "SUN": "#FFE278",
    "WND": "#2CA02C",
    "NUC": "#C68ADF",
    "COL": "#B74C1DF0",
    "WAT": "#00BFFF",
    "BAT": "#FF00FF",
    "UES": "#EE0099",
    "OIL":  "brown",
    "PS": "darkgreen"
}

labels = {
    "NG": "Natural Gas",
    "SUN": "Solar",
    "WND": "Wind",
    "NUC": "Nuclear",
    "COL": "Coal",
    "WAT": "Hydro",
    "BAT": "Battery Discharge (Charge)",
    "UES": "Battery Charging",
    "OIL": "Petroleum",
    "PS": "Pumped Storage"
}

def format_time(x, _):
    hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
    return hm + ("am" if (x%24)<12 else "pm")

def texas_daily_chart(region="ISNE", timezone="Eastern", start_date=None, end_date=None, fuels=["NG", "SUN", "NUC"], show_demand=True, show_interchange=True):
    ymin = 0
    ymax = 0
    full_demand = EIA_demand_data.EIA_demand_daily(region = region, 
                                             sub_ba=False,
                                             start_date=start_date,
                                             end_date=end_date,
                                             timezone_str = "Central")
    df = full_demand.demand()
    df.sort_values(by='Date', inplace=True, ignore_index=True)
    df.rename(columns={'value': 'Demand'}, inplace=True)
    df["Demand"] = df["Demand"]/1000    # Convert to GWh 
    

    print(df.head(n=100))
    plt.figure(figsize=(8, 4))
    plt.rcParams.update({'font.size': 8})

    # Plot the series
    plt.plot(df['Date'], df['Demand'], label='Total Demand per Day (GWh)')
    
    # no xlabel, because it is clearly a date
    plt.ylabel('GWh / day')  

    if show_interchange:
        df_interchange = full_demand.interchange()
        df_interchange.sort_values(by='Date', inplace=True, ignore_index=True)
        df_interchange["Interchange"]=df_interchange["Interchange"]/1000
        df = pd.merge(df, df_interchange, on='Date', how='outer')
        plt.plot(df['Date'],-1*df['Interchange'], label='Imports', color='Gray')
        ymax = max(ymax, -1*df['Interchange'].max())
        ymin = min(ymin, -1*df['Interchange'].min())

    for fuel in fuels:
        zoom_fuel = EIA_generation_data.EIA_generation_daily(region = region,
                                                             fuel = fuel,
                                                             start_date=start_date,
                                                             end_date=end_date, 
                                                             timezone_str="Eastern")  
        df_fuel = zoom_fuel.generation()
        df_fuel.sort_values(by='Date', inplace=True, ignore_index=True)
        df_fuel.rename(columns={'value': fuel}, inplace=True)
        df_fuel[fuel] = df_fuel[fuel]/1000  # Convert to GWh

        df = pd.merge(df, df_fuel, on='Date', how='outer')
        
        ymax = max(ymax, df[fuel].max())
        ymin = min(ymin, df[fuel].min())

    if "BAT" in fuels and "UES" in fuels:
        df['BAT'] = df['BAT'] + df['UES']
        fuels = [f for f in fuels if f not in ["UES"]]

    for fuel in fuels:
        plt.plot(df["Date"], df[fuel], label=f'{labels[fuel]}', color=colors[fuel])

    plt.legend(frameon=False, fontsize=8, loc="upper left")

    #formatting
    
    ax = plt.gca()  # Get current axes

    ax.set_ylim(0, (df['Demand'].max()) * 1.1)  # Set y-axis limit to 110% of max demand
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    plt.tight_layout()
    plt.show()

def texas_zoom_in(region="ERCO", name="", start_date=None, end_date=None, fuels=["NG", "SUN", "NUC"], show_demand=True, show_interchange=True):
    ymax = 0
    ymin = 0
    zoom_demand = EIA_demand_data.EIA_demand(region =region, 
                                             sub_ba=False,
                                             start_date=start_date,
                                             end_date=end_date,
                                             start_offset=-5,
                                             end_offset=-5)

    df_demand = zoom_demand.full_demand()                   
    df_demand['datetime'] = pd.to_datetime(df_demand['Date']) + pd.to_timedelta(df_demand['Hour Starting'], unit='h')
    df_demand.drop(columns=['Date', 'Hour Starting'], inplace=True)
    df = df_demand

    fig = plt.figure(figsize=(8, 5))
    plt.rcParams.update({'font.size': 8})
    if show_demand:
        plt.plot(df['datetime'], df['Demand'], label='Total Demand')
        ymax = df['Demand'].max()


    if show_interchange:
        df_interchange = zoom_demand.full_interchange()
        df_interchange['datetime'] = pd.to_datetime(df_interchange['Date']) + pd.to_timedelta(df_interchange['Hour Starting'], unit='h')
        df_interchange.drop(columns=['Date', 'Hour Starting'], inplace=True)
        df_interchange.sort_values(by='datetime', inplace=True, ignore_index=True)
        df = pd.merge(df, df_interchange, on='datetime', how='outer')
        plt.plot(df['datetime'],-1*df['Interchange'], label='Imports', color='Gray')
        ymax = max(ymax, -1*df['Interchange'].max())
        ymin = min(ymin, -1*df['Interchange'].min())

    for fuel in fuels:
        zoom_fuel = EIA_generation_data.EIA_generation(region = region,
                                                        fuel = fuel,
                                                        start_date=start_date,
                                                        end_date=end_date,
                                                        start_offset=-5,
                                                        end_offset=-5)
    
        df_fuel = zoom_fuel.full_generation()
        df_fuel['datetime'] = pd.to_datetime(df_fuel['Date']) + pd.to_timedelta(df_fuel['Hour Starting'], unit='h')
        df_fuel.drop(columns=['Date', 'Hour Starting'], inplace=True)
        df_fuel.rename(columns={'value': fuel}, inplace=True)
        df_fuel.sort_values(by='datetime', inplace=True, ignore_index=True)
        df = pd.merge(df, df_fuel, on='datetime', how='outer')
        
        ymax = max(ymax, df[fuel].max())
        ymin = min(ymin, df[fuel].min())

    if "BAT" in fuels and "UES" in fuels:
        df['BAT'] = df['BAT'] + df['UES']
        fuels = [f for f in fuels if f not in ["UES"]]

    for fuel in fuels:
        plt.plot(df["datetime"], df[fuel], label=f'{labels[fuel]}', color=colors[fuel])

    ax = plt.gca()  # Get current axes

    ax.set_ylim(ymin * 1.1, ymax * 1.1)  # Set y-axis limit to 110% of max demand
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%-I:%M %p'))
    fig.autofmt_xdate()
    
    plt.ylabel('MWh / hour')  
    plt.title(f"{name}: " + start_date.strftime("%b %d") + " to " + end_date.strftime("%b %d, %Y"))
    plt.tight_layout()
    plt.show()
    plt.show()

    
def texas_hourly_chart(region = "ISNE", start_date=None, end_date=None, interval=1):
    
    full_demand = EIA_demand_data.EIA_demand(region = region, 
                                             sub_ba=False,
                                             start_date=start_date,
                                             end_date=end_date,
                                             start_offset=-5,
                                             end_offset=-5)
    
    df_demand = full_demand.full_demand()
    df_demand['datetime'] = pd.to_datetime(df_demand['Date']) + pd.to_timedelta(df_demand['Hour Starting'], unit='h')
    df_demand.drop(columns=['Date', 'Hour Starting'], inplace=True)
    df_demand.rename(columns={'value': 'Demand'}, inplace=True)
    df_demand.sort_values(by='datetime', inplace=True, ignore_index=True)

   
    plt.figure(figsize=(8, 4))
    plt.rcParams.update({'font.size': 8})

    # Plot the series
    plt.plot(df_demand['datetime'], df_demand['Demand'], label='Total Demand')
    #plt.plot(hourly_demand['datetime'], hourly_demand['Natural Gas Generation'], label='Natural Gas Generation')
    
    # no xlabel, because it is clearly a date
    plt.ylabel('MWh per hour')  # assuming megawatts
    plt.legend()

    #formatting
    
    ax = plt.gca()  # Get current axes

    plt.ylabel('MWh per hour')
    
    ax.set_ylim(0, df_demand['Demand'].max() * 1.1)  # Set y-axis limit to 110% of max demand
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%-d'))  # Unix/Linux/macOS

    plt.tight_layout()
    plt.show()


if "__main__" == __name__:
    #texas_hourly_chart(region = "ISNE", start_date=datetime(2025, 7, 1), end_date=datetime(2025, 7, 15), interval = 3)
    #texas_zoom_in(region = "ISNE", name="New England", start_date=datetime(2025, 1, 28), end_date=datetime(2025, 1, 30), fuels = [], show_interchange=False)
    #texas_zoom_in(region = "ISNE", name="New England", start_date=datetime(2025, 6, 29), end_date=datetime(2025, 7, 1), fuels = ["NG", "SUN", "NUC", "OIL", "PS"], show_interchange=True)
    texas_zoom_in(region = "ERCO", name="Texas", start_date=datetime(2025, 7, 15), end_date=datetime(2025, 7, 17), fuels = ["SUN"], show_interchange=False)
    # texas_zoom_in(region = "ERCO", name="Texas", start_date=datetime(2024, 9, 28), end_date=datetime(2024, 9, 30), fuels = ["SUN", "NG", "NUC", "COL", "WND"], show_demand=True, show_interchange=False)
    #texas_zoom_in(region = "ERCO", name="Texas", start_date=datetime(2025, 7, 15), end_date=datetime(2025, 7, 17), fuels = ["SUN", "NG", "BAT", "UES"], show_demand=False, show_interchange=False)
    
    texas_daily_chart(region = "ISNE", timezone="Eastern", start_date=datetime(2023, 6, 30), end_date=datetime(2025, 6, 30), fuels=["NG", "SUN", "NUC", "OIL"], show_demand=True, show_interchange=True)
    #texas_daily_chart(region = "ERCO", timezone="Central", start_date=datetime(2023, 6, 30), end_date=datetime(2025, 6, 30), fuels=["NG", "SUN", "NUC"], show_demand=True, show_interchange=False)
    