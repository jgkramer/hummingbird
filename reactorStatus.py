import pandas as pd
from datetime import datetime, timedelta
from typing import List

from reactorStatusChart import DailyChart

class ReactorStatus:
    def __init__(self, path):
        self.df = pd.read_csv(path, index_col = "Date")
        #self.df.apply(pd.to_numeric, errors="coerce")
        
        strdates = self.df.index.tolist()
    
        self.df.index = [datetime.strptime(s, "%Y-%m-%d") for s in strdates]
        self.date_list = self.df.index
        #print(self.df.index)
        #print(self.df)

    def plotStatus(self):
        y_values_list = [self.df[column].tolist() for column in self.df.columns]
        y_values_labels = self.df.columns.tolist()

        DailyChart.dailyLineChart(self.date_list,
                                  y_values_list,
                                  "Reactor Power (%)",
                                  y_values_labels,
                                  "./test_chart.png")
        
                                  
if "__main__" == __name__:
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    path = "./reactorStatus_21Oct23.csv"
    rs = ReactorStatus(path)
    rs.plotStatus()



