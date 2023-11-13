
import pandas as pd
from datetime import datetime, timedelta

from reactorStatus import ReactorStatus

if "__main__" == __name__: 

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    data_path = "./post9/reactorStatus_2Nov23.csv"
    capacity_path = "./post9/SE_nuclear_plants.csv"
    rs = ReactorStatus(data_path, capacity_path)
    rs.plotStatus(individual_path = "./post9/post9_2022_2023_single_plants.png",
                  aggregate_path = "./post9/post9_2022_2023_aggregate.png", 
                  start = datetime(2021, 8, 1), end = datetime(2023, 10, 31), excl_before = {"Vogtle 3": datetime(2023, 8, 1)})



