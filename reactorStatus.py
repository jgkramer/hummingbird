import pandas as pd
from datetime import datetime, timedelta
from typing import List

class ReactorStatus:

    def __init__(self, path):
        self.df = pd.read_csv(path, index_col = "Date")
        print(self.df)


if "__main__" == __name__:
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    path = "./reactorStatus_21Oct23.csv"
    rs = ReactorStatus(path)


