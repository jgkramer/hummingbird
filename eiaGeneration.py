import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from typing import List

import matplotlib.pyplot as plt
import pytz


def timeparse(s):
    dst = True if s.split(". ", 1)[1] == "PDT" else False
    time = datetime.strptime((s.split("m", 1)[0] + "m").replace(".", ""), "%m/%d/%Y %I %p")
    if(dst):
        return time + relativedelta(hours = -2)
    else:
        return time + relativedelta(hours = -1)

class EIAGeneration:
    def __init__(self, paths: List[str]):
        dfs = []
        for path in paths:
            df = pd.read_csv(path)
            dfs.append(df)

        self.df = pd.concat(dfs)
        print(self.df.columns)

        self.df["Start Time"] = self.df["Timestamp (Hour Ending)"].apply(timeparse)
        print(self.df[["Timestamp (Hour Ending)", "Start Time"]])



            
if __name__ == "__main__":

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    
    d = datetime(2021, 12, 1)
    end = datetime(2022, 11, 1)
    paths = []
    while d <= end:
        paths.append(f"./generation_data/NVPowerGeneration{d.year}_{d.month:02}.csv")
        d = d + relativedelta(months = +1)
    print(paths)

    eiag = EIAGeneration(paths)

    
        
