
from datetime import datetime
from dateutil.relativedelta import relativedelta
import EIA_demand_data, EIA_generation_data
import numpy as np
import pandas as pd
import math
from scipy.stats import linregress
import matplotlib.dates as mdates

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from ercotStorageReport import StorageData

import pytz


def demand_vs_nat_gas_charts(start_date: datetime, end_date: datetime, y_scale: float, include_oil: bool, path_id: str):

    hourly_demand = EIA_demand_data.EIA_demand(region = "ISNE",
                                             sub_ba = False,
                                             start_date = start_date,
                                             end_date= end_date,
                                             start_offset = -4, end_offset = -4).full_demand()


    hourly_demand['datetime'] = pd.to_datetime(hourly_demand['Date']) + pd.to_timedelta(hourly_demand['Hour Starting'], unit='h')
    hourly_demand = hourly_demand.rename(columns={"value": "Demand"})
    hourly_demand.drop(columns=["Date", "Hour Starting"], inplace=True)
    hourly_demand.sort_values(by='datetime', inplace=True, ignore_index=True)

    print(hourly_demand.head(n = 40))
    nat_gas_hourly = EIA_generation_data.EIA_generation(region = "ISNE",
                                                        fuel = "NG",
                                                        start_date = start_date,
                                                        end_date= end_date,
                                                        start_offset = -4, end_offset = -4).full_generation()
    
    nat_gas_hourly['datetime'] = pd.to_datetime(nat_gas_hourly['Date']) + pd.to_timedelta(nat_gas_hourly['Hour Starting'], unit='h')
    nat_gas_hourly = nat_gas_hourly.rename(columns={"value": "Natural Gas Generation"})
    nat_gas_hourly.drop(columns=["Date", "Hour Starting"], inplace=True)
    nat_gas_hourly.sort_values(by='datetime', inplace=True, ignore_index=True)

    print(nat_gas_hourly.head(n = 40))

    oil_hourly = EIA_generation_data.EIA_generation(region = "ISNE",
                                                        fuel = "OIL",
                                                        start_date = start_date,
                                                        end_date= end_date,
                                                        start_offset = -4, end_offset = -4).full_generation()
    
    oil_hourly['datetime'] = pd.to_datetime(oil_hourly['Date']) + pd.to_timedelta(oil_hourly['Hour Starting'], unit='h')
    oil_hourly = oil_hourly.rename(columns={"value": "Oil Generation"})
    oil_hourly.drop(columns=["Date", "Hour Starting"], inplace=True)
    oil_hourly.sort_values(by='datetime', inplace=True, ignore_index=True)

    hourly_demand = pd.merge(hourly_demand, nat_gas_hourly, on='datetime', how='outer') 
    hourly_demand = pd.merge(hourly_demand, oil_hourly, on='datetime', how='outer') 
    
    hourly_demand = hourly_demand[(hourly_demand['Demand'] != 0) & (hourly_demand['Natural Gas Generation'] != 0)]
    print(hourly_demand.head(n = 100))

    hourly_demand.to_csv(f"./post12/demand_natgas_{path_id}.csv", index=False)

    plt.figure(figsize=(8, 4))
    plt.rcParams.update({'font.size': 8})

    # Plot the series
    plt.plot(hourly_demand['datetime'], hourly_demand['Demand'], label='Total Demand')
    plt.plot(hourly_demand['datetime'], hourly_demand['Natural Gas Generation'], label='Natural Gas Generation')
    if(include_oil):
        plt.plot(hourly_demand['datetime'], hourly_demand['Oil Generation'], label='Oil Generation')


    # no xlabel, because it is clearly a date
    plt.ylim(top=y_scale * hourly_demand['Demand'].max())
    plt.ylabel('MWh')  # assuming megawatts
    plt.title('New England Electricity Demand and Generation - Hourly', fontsize=9)
    plt.legend()

    #formatting
    
    ax = plt.gca()  # Get current axes
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%-d'))  # Unix/Linux/macOS

    plt.tight_layout()
    plt.savefig(f"./post12/demand_natgas_{path_id}.png", dpi=300, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":

    if(False):
        demand_vs_nat_gas_charts(start_date = datetime(2025, 6, 1), 
                             end_date = datetime(2025, 7, 5), 
                             y_scale = 1.2, 
                             include_oil = True, 
                             path_id = "summer '25")


    ISO_NE_demand  = EIA_demand_data.EIA_demand_daily(region = "ISNE", 
                                                      sub_ba = False, 
                                                      start_date = datetime(2020, 1, 1), 
                                                      end_date = datetime(2025, 7, 1),
                                                      timezone_str = "Eastern").demand()
    
    
    ISO_NE_natgas_gen = EIA_generation_data.EIA_generation_daily(region = "ISNE", 
                                                                fuel = "NG",
                                                                start_date = datetime(2020, 1, 1), 
                                                                end_date = datetime(2025, 7, 1),
                                                                timezone_str = "Eastern").generation()

    df = pd.DataFrame({"Date": ISO_NE_demand["Date"],
                     "Demand": ISO_NE_demand["value"],
                     "NatGas_Gen": ISO_NE_natgas_gen["value"]})
    

    df['Demand'] = pd.to_numeric(df['Demand'], errors='coerce')
    df['NatGas_Gen'] = pd.to_numeric(df['NatGas_Gen'], errors='coerce')

    df['Color'] = df['Date'].dt.month.apply(lambda m: 'red' if m in [12, 1, 2] else 'blue')
    
    print(df)

    plt.scatter(df['Demand'], df['NatGas_Gen'], alpha=0.5)
    plt.xlabel('Total Electricity Demand (MWh)')
    plt.ylabel('Natural Gas Generation (MWh)')
    plt.title('Scatterplot: Demand vs. Natural Gas Generation')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    winter = df[df['Color'] == 'red']
    other = df[df['Color'] == 'blue']

    # Run regressions
    slope_red, intercept_red, r_red, _, _ = linregress(winter['Demand'], winter['NatGas_Gen'])
    slope_blue, intercept_blue, r_blue, _, _ = linregress(other['Demand'], other['NatGas_Gen'])

    print(f"Winter Regression: y = {slope_red:.2f}x + {intercept_red:.2f}, R^2 = {r_red**2:.2f}")
    print(f"Other Seasons Regression: y = {slope_blue:.2f}x + {intercept_blue:.2f}, R^2 = {r_blue**2:.2f}")

    plt.scatter(df['Demand'], df['NatGas_Gen'], c=df['Color'], alpha=0.5)
    plt.xlabel('Total Electricity Demand (MWh)')
    plt.ylabel('Natural Gas Generation (MWh)')
    plt.title('Scatterplot: Demand vs. Natural Gas Generation')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    