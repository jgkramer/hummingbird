
import pandas as pd
from datetime import datetime, timedelta

import matplotlib as mpl
import matplotlib.pyplot as plt

from reactorStatus import ReactorStatus
from EIADailyFiles import EIAGeneration


def bars_for_months(eiag: EIAGeneration, path: str):
    fig, axes = plt.subplots(1, 4, figsize = (9, 4))
    
    for ax, month, firstplot, monthname in zip(axes, [8, 9, 10, 11], [True, False, False, False], ["August", "September", "October", "November"]):
        result = eiag.get_monthly_by_source(monthlist = [month])
        # print(result)
        eiag.stackedbar(result, ax, ymax = 28, firstplot = firstplot, title = monthname)
    plt.savefig(path)
    plt.show()

def linear_regression_plot(eiag: EIAGeneration, path: str):
    fig, ax = plt.subplots(figsize = (8, 4))

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.set_ylabel("Daily Avg. Coal + Natural Gas Generation (GW)")
    ax.set_xlabel("Daily Avg. Total Generation (GW)")
    plt.tight_layout()

    fit = dict()

    print("\n2023 linear regression")
    fit[2023] = eiag.linear_model_by_dates(ax = ax, startdate = datetime(2023, 8, 1), enddate = datetime(2023, 11, 30), color = "blue", fitX = 29)

    print("\n2022 linear regression")
    fit[2022] = eiag.linear_model_by_dates(ax = ax, startdate = datetime(2022, 8, 1), enddate = datetime(2022, 11, 30), color = "green", fitX = 29)

    print("\n2021 linear regression")
    fit[2021] = eiag.linear_model_by_dates(ax = ax, startdate = datetime(2021, 8, 1), enddate = datetime(2021, 11, 30), color = "violet", fitX = 29)

    table_data = [["", "Regression at 29 GW"]]
    for year in [2021, 2022, 2023]:
        table_data.append([year, f"{fit[year]:0.2f} GW"])

    table = ax.table(cellText=table_data, colWidths=[0.05, 0.18], loc='lower right', cellLoc = 'center')
    # Change all borders to gray
    for _, cell in table.get_celld().items():
        cell.set_edgecolor("white")
        cell.set_fontsize(9)

    plt.savefig(path)
    plt.show()


if "__main__" == __name__: 

    plt.rcParams.update({'font.size': 8})

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    data_path = "./post9/reactorStatus_3Dec23.csv"
    capacity_path = "./post9/SE_nuclear_plants.csv"
    rs = ReactorStatus(data_path, capacity_path)
    rs.plotStatus(individual_path = "./post9/post9_2022_2023_single_plants.png",
                  aggregate_path = "./post9/post9_2022_2023_aggregate.png", 
                  start = datetime(2021, 8, 1), end = datetime(2023, 11, 30), excl_before = {"Vogtle 3": datetime(2023, 8, 1)})

    generation_path_list = [f"./post9/SE_daily_generation_{year}.csv" for year in [2021, 2022, 2023]]
    eiag = EIAGeneration(generation_path_list)

    barchartpath = "./post9/post9_monthbars.png"
    bars_for_months(eiag, barchartpath)

    linregpath = "./post9/post9_linreg.png"
    linear_regression_plot(eiag, linregpath)

    print("nat gas ", eiag.get_total_by_source("natural gas"))
    print("coal ", eiag.get_total_by_source("coal"))


