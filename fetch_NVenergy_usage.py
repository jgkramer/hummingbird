import numpy as np
import pandas as pd
from datetime import datetime

USAGE_PATH = "usage_data/Sep21-Aug22energy.csv"


class NVenergyUsage:
    def __init__(self, usage_path = USAGE_PATH):
        self.table = pd.read_csv(usage_path)
        self.table["startDateTime"] = self.table["startTime"].apply(lambda s: (datetime.strptime(s, "%m/%d/%y %H:%M")))
        self.table["endDateTime"]=  self.table["endTime"].apply(lambda s: (datetime.strptime(s, "%m/%d/%y %H:%M")))
    
        self.table = self.table[["unit", "startDateTime", "endDateTime", "Usage"]]
        

    def print(self, n=96):
        print(self.table.head(n))
        
        

if __name__ == "__main__":
    usage = NVenergyUsage()
    print(usage.table.columns)
    usage.print()
    
 #   d = datetime.strptime("9/1/21 0:15", "%m/%d/%y %H:%M")
 #   print(d)
    
    
    
