import pandas as pd
from datetime import datetime, timedelta
from typing import List

from reactorStatusChart import DailyChart

class ReactorStatus:
    def __init__(self, data_path, capacity_path):
        self.percent_df = pd.read_csv(data_path, index_col = "Date")
        self.percent_df.apply(pd.to_numeric, errors="coerce")

        self.reactors = self.percent_df.columns

        strdates = self.percent_df.index.tolist()
        self.percent_df.index = [datetime.strptime(s, "%Y-%m-%d") for s in strdates]
        self.date_list = self.percent_df.index.to_list()

        self.capacity_df = pd.read_csv(capacity_path, index_col = "Unit")
        self.capacity_dict = self.capacity_df.to_dict()["Capacity"]

        self.powers_df = self.percent_df.copy()
        constants = [self.capacity_dict[column] / 100 for column in self.powers_df.columns]
        self.powers_df = self.powers_df.mul(constants)
        
        #print(self.df.index)
        #print(self.df)

    def computeTotal(self, df_filtered, excl_before = dict()):
        df_copy = df_filtered.copy()
        for col, excl_date in excl_before.items():
            df_copy.loc[df_copy.index <= excl_date, col] = 0
        sums = df_copy.sum(axis = 1).to_list()
        return sums

    def plotStatus(self, start: datetime = None, end: datetime = None, excl_before = dict()):

        if start is None: start = self.date_list[0]
        if end is None: end = self.date_list[-1]

        in_range = [(start <= d) and (d <= end) for d in self.date_list]
        dates_in_range = [d for d in self.date_list if (start <= d) and (d <= end)]
        df_filtered = self.powers_df[in_range]

        y_values_list = [(df_filtered[column]).tolist() for column in df_filtered.columns]
        y_values_labels = self.powers_df.columns.tolist()

        totals = self.computeTotal(df_filtered, excl_before)

        date_breakpoints = sorted([d for d in excl_before.values() if d in pd.date_range(start, end)] + [start, end + timedelta(days = 1)])
        date_ranges = [(s, e + timedelta(days = -1)) for (s, e) in zip(date_breakpoints[:-1], date_breakpoints[1:])]

        averages = []
        capacities = []

        for date_range in date_ranges:
            date_range_list = pd.date_range(date_range[0], date_range[1])
            print(date_range)
            total_in_range = sum([t if d in date_range_list else 0 for t, d in zip(totals, dates_in_range)])
            average_in_range = total_in_range / len(date_range_list)
            averages = averages + ([average_in_range] * len(date_range_list))
            capacity_in_range = sum([self.capacity_dict[r] for r in self.reactors if r not in excl_before.keys() or date_range[0] >= excl_before[r]])
            capacities = capacities + ([capacity_in_range] * len(date_range_list))
            
        colors = ["mediumpurple", "purple", "orangered", "red", "steelblue", "navy", "limegreen"]
        styles = ["solid", "dashed", "solid", "dashed", "solid", "dashed", "dashed"]
        width = [1, 1, 1, 1, 1, 1, 2]
        second_axis = [False] * len(y_values_labels)
        second_axis[-1] = True

        DailyChart.dailyLineChart(dates_in_range,
                                  y_values_list,
                                  "Reactor Power (MW)",
                                  y_values_labels,
                                  "./post9_2022_2023_single_plants.png", 
                                  series_colors = colors,
                                  series_styles = styles, 
                                  series_width = width)
        
        DailyChart.dailyLineChart(dates_in_range,
                                  [totals, averages, capacities],
                                  "MW Generation Online",
                                  ["Daily", "Average of Active Fleet", "Capacity of Active Fleet"],
                                  "./post9_2022_2023_aggregate.png",    
                                  series_colors = ["gray", "blue", "gray"], 
                                  series_styles = ["solid", "solid", "dashed"])
        
                                  
if "__main__" == __name__:
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    data_path = "./post9/reactorStatus_2Nov23.csv"
    capacity_path = "./post9/SE_nuclear_plants.csv"
    rs = ReactorStatus(data_path, capacity_path)
    #rs.plotStatus(start = datetime(2022, 1, 1), end = datetime(2022, 12, 31))
    #rs.plotStatus(start = datetime(2021, 1, 1), end = datetime(2021, 12, 31), excl_before = {"Vogtle 3": datetime(2023, 8, 1)})
    #rs.plotStatus(start = datetime(2022, 1, 1), end = datetime(2022, 12, 31), excl_before = {"Vogtle 3": datetime(2023, 8, 1)})
    rs.plotStatus(start = datetime(2022, 1, 1), end = datetime(2023, 10, 31), excl_before = {"Vogtle 3": datetime(2023, 8, 1)})



