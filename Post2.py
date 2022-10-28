from fetch_NVenergy_usage import NVenergyUsage
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

def format_time(x, _):
    hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
    return hm + ("am" if (x%24)<12 else "pm")

if __name__ == "__main__":
    NVE = NVenergyUsage()

    fig, ax = plt.subplots(nrows = 1, ncols = 3)
    
    
    date_lists = [[datetime(2022, 8, 25), datetime(2022, 8, 31)],  # high
                  [datetime(2022, 2, 14), datetime(2022, 2, 15)],
                  [datetime(2022, 5, 9), datetime(2022, 5, 23)]] #high 

    for ix, date_list in enumerate(date_lists):

        sub = ax[ix]
        sub.set_xlim([0, 24])
        sub.set_ylim([0, 4])
        sub.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))
        sub.xaxis.set_major_formatter(format_time)
        sub.xaxis.set_ticks(np.arange(0, 24+1, 4))
        
        for d in date_list:
            
            print(str(d) + " day of week " + str(d.weekday()))
            times, usage = list(zip(*NVE.usage_series_for_day(d)))
            print("total usage " + str(sum(usage)))
            hours = [(t.hour + t.minute/60) for t in times]
            sub.step(hours, usage, where = "post", label = str(d.date()))
            sub.legend(loc = "upper left")
            
    plt.show()

    
    
    
    
