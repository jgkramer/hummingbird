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

    def computeCapacityFactor(self, in_range: List, excl: List[str] = None):
        included_reactors = [reactor for reactor in self.reactors if reactor not in excl]
        print(included_reactors)
        df_filtered = self.powers_df[in_range]
        total_capacity = sum([self.capacity_dict[reactor] for reactor in included_reactors])
        capacity_factor = (df_filtered[included_reactors].sum(axis = 1) / total_capacity).to_list()
        return capacity_factor

    def plotStatus(self, start: datetime = None, end: datetime = None):

        if start is None: start = self.date_list[0]
        if end is None: end = self.date_list[-1]

        in_range = [(start <= d) and (d <= end) for d in self.date_list]
        dates_in_range = [d for d in self.date_list if (start <= d) and (d <= end)]
        df_filtered = self.powers_df[in_range]

        y_values_list = [(df_filtered[column]).tolist() for column in df_filtered.columns]
        y_values_labels = self.powers_df.columns.tolist()

        capacity_factor = self.computeCapacityFactor(in_range, ["Vogtle 3"])
        y_values_list.append(capacity_factor)
        y_values_labels.append("% Capacity")

        colors = ["mediumpurple", "purple", "orangered", "red", "steelblue", "navy", "royalblue", "gray"]
        styles = ["solid", "dashed", "solid", "dashed", "solid", "dashed", "dotted", "solid"]
        width = [1, 1, 1, 1, 1, 1, 2, 1]
        second_axis = [False] * len(y_values_labels)
        second_axis[-1] = True

        DailyChart.dailyLineChart(dates_in_range,
                                  y_values_list,
                                  "Reactor Power (MW)",
                                  y_values_labels,
                                  "./test_chart.png", 
                                  series_colors = colors,
                                  series_styles = styles, 
                                  series_width = width)
        
                                  
if "__main__" == __name__:
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    data_path = "./reactorStatus_21Oct23.csv"
    capacity_path = "./post9/SE_nuclear_plants.csv"
    rs = ReactorStatus(data_path, capacity_path)
    rs.plotStatus(start = datetime(2022, 1, 1), end = datetime(2022, 12, 31))



