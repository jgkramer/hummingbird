
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

def demand_generation_df(start_date: datetime, end_date: datetime, include_oil: bool):
    hourly_demand = EIA_demand_data.EIA_demand(region = "ISNE",
                                             sub_ba = False,
                                             start_date = start_date,
                                             end_date= end_date,
                                             start_offset = -4, end_offset = -4).full_demand()


    hourly_demand['datetime'] = pd.to_datetime(hourly_demand['Date']) + pd.to_timedelta(hourly_demand['Hour Starting'], unit='h')
    hourly_demand = hourly_demand.rename(columns={"value": "Demand"})
    hourly_demand.sort_values(by='datetime', inplace=True, ignore_index=True)

    print(hourly_demand.head(n = 40))
    nat_gas_hourly = EIA_generation_data.EIA_generation(region = "ISNE",
                                                        fuel = "NG",
                                                        start_date = start_date,
                                                        end_date= end_date,
                                                        start_offset = -4, end_offset = -4).full_generation()
    
    nat_gas_hourly['datetime'] = pd.to_datetime(nat_gas_hourly['Date']) + pd.to_timedelta(nat_gas_hourly['Hour Starting'], unit='h')
    nat_gas_hourly = nat_gas_hourly.rename(columns={"value": "Natural Gas Generation"})
    nat_gas_hourly.drop(columns=['Date', 'Hour Starting'], inplace=True)
    nat_gas_hourly.sort_values(by='datetime', inplace=True, ignore_index=True)

    print(nat_gas_hourly.head(n = 40))
    hourly_demand = pd.merge(hourly_demand, nat_gas_hourly, on='datetime', how='outer') 

    if(include_oil):
        oil_hourly = EIA_generation_data.EIA_generation(region = "ISNE",
                                                        fuel = "OIL",
                                                        start_date = start_date,
                                                        end_date= end_date,
                                                        start_offset = -4, end_offset = -4).full_generation()
    
        oil_hourly['datetime'] = pd.to_datetime(oil_hourly['Date']) + pd.to_timedelta(oil_hourly['Hour Starting'], unit='h')
        oil_hourly = oil_hourly.rename(columns={"value": "Oil Generation"})
        oil_hourly.drop(columns=['Date', 'Hour Starting'], inplace=True)
        oil_hourly.sort_values(by='datetime', inplace=True, ignore_index=True)
        
        hourly_demand = pd.merge(hourly_demand, oil_hourly, on='datetime', how='outer')

    return hourly_demand

def demand_vs_nat_gas_charts(start_date: datetime, end_date: datetime, y_scale: float, include_oil: bool, path_id: str):

    hourly_demand = demand_generation_df(start_date, end_date, include_oil)
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


def get_nat_gas_report(start_date: datetime, end_date: datetime):
    curr_year = start_date.year
    dfs = []
    while (curr_year <= end_date.year):
        df = pd.read_csv(f"./post12/new_england_natgas_{curr_year}.csv")
        df['Date'] = pd.to_datetime(df['date'])
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date) & (df['Date'].dt.year == curr_year)]
        dfs.append(df)
        curr_year += 1

    data = pd.concat(dfs, ignore_index=True)
    data["Residential-Commercial"] = data["resi_comm"]
    data["Industrial"] = data["industrial"] - data["resi_comm"]
    data["Electric Generation"] = data["electric"] - data["industrial"]
    data.drop(columns=["resi_comm", "industrial", "electric", "date"], inplace=True)
    data.to_csv("./post12/concat.csv", index=False)
    return data


def demand_vs_nat_gas_hourly_regression(start_date: datetime, end_date: datetime):
    df = demand_generation_df(start_date, end_date, include_oil = False)
    results = []

    for date, group in df.groupby('Date'):
        x = group['Demand']
        y = group['Natural Gas Generation']

        if len(x) >= 2:
            slope, intercept, r_value, p_value, std_err = linregress(x, y)
            results.append({'Date': date, 'Slope': slope, 'R2': r_value**2})
        
        else:
            results.append({'Date': date, 'Slope': None, 'R2': None})

    regression_results = pd.DataFrame(results)
    print(regression_results.head(n = 100))
    regression_results.to_csv(f"./post12/demand_natgas_regression_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv", index=False)  

if __name__ == "__main__":

    if(False):
        demand_vs_nat_gas_charts(start_date = datetime(2025, 6, 1), 
                             end_date = datetime(2025, 7, 5), 
                             y_scale = 1.2, 
                             include_oil = True, 
                             path_id = "summer '25")

    if(False):
        demand_vs_nat_gas_hourly_regression(start_date = datetime(2021, 8, 1), 
                                            end_date = datetime(2025, 7, 1))


    
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
    
    ISO_NE_oil_gen = EIA_generation_data.EIA_generation_daily(region = "ISNE", 
                                                                fuel = "OIL",
                                                                start_date = datetime(2020, 1, 1), 
                                                                end_date = datetime(2025, 7, 1),
                                                                timezone_str = "Eastern").generation()


    df = pd.DataFrame({"Date": ISO_NE_demand["Date"],
                     "Demand": ISO_NE_demand["value"],
                     "NatGas_Gen": ISO_NE_natgas_gen["value"],
                     "Oil_Gen": ISO_NE_oil_gen["value"]})
    

    df['Demand'] = pd.to_numeric(df['Demand'], errors='coerce')/1000 # Convert to GWh
    df['Date'] = pd.to_datetime(df['Date'])
    df['NatGas_Gen'] = pd.to_numeric(df['NatGas_Gen'], errors='coerce')/1000 # Convert to GWh
    df['Oil_Gen'] = pd.to_numeric(df['Oil_Gen'], errors='coerce')/1000 # Convert to GWh

    colors = {"winter": '#1f77b4', "others": '#ff7f0e'}
    df['Color'] = df['Date'].dt.month.apply(lambda m: colors["winter"] if m in [12, 1, 2] else colors["others"])
    
    print(df.head(n = 1000))

    slope, intercept, r_value, _, _ = linregress(df['Demand'], df['NatGas_Gen'])
    reg_y_all_data = slope * df['Demand'] + intercept
    r_squared = r_value**2

    plt.figure(figsize=(7, 4))
    plt.rcParams.update({'font.size': 8})
    plt.scatter(df['Demand'], df['NatGas_Gen'], alpha=0.5, s=10)
    plt.plot(df['Demand'], reg_y_all_data, color='#1a4e85', alpha = 0.75, label=f'y = {slope:.2f}x + {intercept:.1f}, R² = {r_squared:.2f}')
    plt.legend(loc='upper left', fontsize=8, frameon=False)
    plt.xlabel('Daily Electricity Demand (GWh)')
    plt.ylabel('Daily Gas Generation (GWh)')

    #equation_text = f'y = {slope:.2f}x + {intercept:.0f}\n$R^2$ = {r_squared:.2f}'
    #plt.annotate(equation_text, xy=(0.05, 0.95), xycoords='axes fraction', fontsize=8, ha='left', va='top')


    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"./post12/demand_natgas_regression_all_data.png", dpi=300, bbox_inches='tight')
    plt.show()

    winter = df[df['Color'] == colors["winter"]]
    other = df[df['Color'] == colors["others"]]


    # Run regressions
    slope_winter, intercept_winter, r_winter, _, _ = linregress(winter['Demand'], winter['NatGas_Gen'])
    reg_y_winter = slope_winter * winter['Demand'] + intercept_winter

    slope_other, intercept_other, r_other, _, _ = linregress(other['Demand'], other['NatGas_Gen'])
    reg_y_other = slope_other * other['Demand'] + intercept_other

#    print(f"Winter Regression: y = {slope_winter:.2f}x + {intercept_winter:.2f}, R^2 = {r_winter**2:.2f}")
#    print(f"Other Seasons Regression: y = {slope_other:.2f}x + {intercept_other:.2f}, R^2 = {r_other**2:.2f}")

    plt.figure(figsize=(7, 4))
    plt.rcParams.update({'font.size': 8})
    plt.scatter(df['Demand'], df['NatGas_Gen'], c=df['Color'], alpha=0.4, s=10)
    plt.plot(winter['Demand'], reg_y_winter, color='#1a4e85', alpha = 0.75, label=f'Winter Months: {slope_winter:.2f}x + {intercept_winter:.1f}, R² = {r_winter**2:.2f}')
    plt.plot(other['Demand'], reg_y_other, color='#e65c00', alpha = 0.75, label=f'Other Months: {slope_other:.2f}x + {intercept_other:.1f}, R² = {r_other**2:.2f}')
    plt.xlabel('Daily Electricity Demand (GWh)')
    plt.ylabel('Daily Gas Generation (GWh)')
    plt.legend(loc='upper left', fontsize=8, frameon=False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"./post12/demand_natgas_regression_seasonal.png", dpi=300, bbox_inches='tight')
    plt.show()




       # last year Natural Gas Usage

    df_gas_1y = get_nat_gas_report(start_date = datetime(2024, 5, 1), end_date = datetime(2025, 5, 1))
    df_gas_1y = df_gas_1y.sort_values('Date')
    fig, ax = plt.subplots(1, 1, figsize=(8, 4))

    ax.plot(df_gas_1y['Date'], df_gas_1y['Electric Generation'], label='Electricity Generation')
    ax.plot(df_gas_1y['Date'], df_gas_1y['Residential-Commercial'], label='Residential-Commercial')
    ax.plot(df_gas_1y['Date'], df_gas_1y['Industrial'], label='Industrial')

    ax.set_ylabel('Natural Gas Consumption (bcf / day)')
    ax.text(0.5, 0.98, 'Natural Gas Consumption by Sector',   #this is the title of the top chart
         transform=ax.transAxes,
         fontsize=10,
         color='#505050',
         fontweight='bold',
         ha='center', va='top',
         bbox=dict(facecolor='white', edgecolor='none', boxstyle='square,pad=0.5', alpha=0.8))
    
    ax.legend(loc='upper left', fontsize=8, frameon=False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.grid(True, color='lightgray', alpha=0.3)

    # Formatting
    plt.tight_layout()
    plt.savefig(f"./post12/gas_graph.png", dpi=300, bbox_inches='tight')
    plt.show()



    df["NatGas_Shortfall"] = df["NatGas_Gen"] - (slope_other * df['Demand'] + intercept_other)
    df2 = df[df["Date"] >= datetime(2022, 5, 1)]
    df_shortfall = df2[df2["Date"] <= datetime(2025, 5, 1)]
    
    df_natgas = get_nat_gas_report(start_date = datetime(2022, 5, 1), end_date = datetime(2025, 5, 1))
    
    df_shortfall = df_shortfall.sort_values('Date')
    df_natgas = df_natgas.sort_values('Date')

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    # --- Top chart: NatGas shortfall ---
    ax1.plot(df_shortfall['Date'], df_shortfall['NatGas_Shortfall'], label='Natural Gas Electricity Generation vs. Regression')
    ax1.plot(df_shortfall['Date'], df_shortfall['Oil_Gen'], label='Oil Generation', color='dimgray')
    ax1.set_ylabel('(GWh per Day)')
    ax1.set_ylim(-150, 150)
    ax1.legend(loc='upper left', fontsize=8, frameon=False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.text(0.5, 0.98, 'Electricity Generation',   #this is the title of the top chart
         transform=ax1.transAxes,
         fontsize=10,
         color='#505050',
         fontweight='bold',
         ha='center', va='top',
         bbox=dict(facecolor='white', edgecolor='none', boxstyle='square,pad=0.5', alpha=0.8))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.grid(True, color='lightgray', alpha=0.3)


    # --- Bottom chart: Sectoral NatGas Usage ---
    ax2.plot(df_natgas['Date'], df_natgas['Electric Generation'], label='Electricity Generation')
    ax2.plot(df_natgas['Date'], df_natgas['Residential-Commercial'], label='Residential-Commercial')
    ax2.plot(df_natgas['Date'], df_natgas['Industrial'], label='Industrial')

    ax2.set_ylabel('Natural Gas Consumption (bcf / day)')
    ax2.text(0.5, 0.98, 'Natural Gas Consumption',   #this is the title of the top chart
         transform=ax2.transAxes,
         fontsize=10,
         color='#505050',
         fontweight='bold',
         ha='center', va='top',
         bbox=dict(facecolor='white', edgecolor='none', boxstyle='square,pad=0.5', alpha=0.8))
    
    ax2.legend(loc='upper left', fontsize=8, frameon=False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax2.grid(True, color='lightgray', alpha=0.3)

    # Formatting
    plt.tight_layout()
    plt.savefig(f"./post12/combined_graph.png", dpi=300, bbox_inches='tight')
    plt.show()