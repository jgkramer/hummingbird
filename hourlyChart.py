
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from typing import List

import matplotlib.pyplot as plt

class HourlyChart:

    def format_time(x, _):
        hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
        return hm + ("am" if (x%24)<12 else "pm")
    
    def prepHourlyChart(yrange: List[float])
        fig, ax = plt.subplots(figsize = (7.5, 4))
        fig.tight_layout(pad = 2.0)
        ax.set_xlim([0, 24])
        ax.set_ylim(yrange[0], yrange[1])

        ax.xaxis.set_ticks(np.arange(0, 24+1, 3))

        return fig, ax
        
                               
    def hourlyLineChart(x_values,
                        y_values_list,
                        y_axis_label,
                        series_labels,
                        series_colors,
                        title,
                        path):

        maxy = max([max(l) for l in y_values_list])        
        miny = min([min(l) for l in y_values_list])

        fig, ax = prepHourlyChart([min(0, 1.2*miny), 1.2*maxy])
