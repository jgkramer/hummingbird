
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from typing import List

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import matplotlib.colors as mcolors


import seaborn as sns

class DailyChart:

    def prepDailyChart(xrange: List[datetime], yrange: List[float], dims):

        plt.rcParams["font.size"] = 8
        fig, ax = plt.subplots(figsize = dims)

        ax.set_xlim(xrange)
        ax.set_ylim(yrange)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%y"))
        plt.xticks(rotation = 45)

        if yrange[1] > 10:
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
        else:
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.1f}"))
        
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)

        return fig, ax
    

    def dailyLineChart(date_list,
                        y_values_list,
                        y_axis_label: str,
                        series_labels,
                        path: str,
                        series_colors = None,
                        ymax = None,
                        title = None,
                        series_styles = None, 
                        series_width = None, 
                        second_axis: List[bool] = None):
        
#        print(y_values_list[0])

        if second_axis is None: second_axis = [False] * len(y_values_list)

        maxy = ymax if ymax is not None else 1.125*max([max(l) for l in y_values_list])
        miny = 0
        dims = (9, 3)

        fig, ax = DailyChart.prepDailyChart([date_list[0], date_list[-1]], [miny, maxy], dims)
        

        if series_styles is None: series_styles = ["solid"] * len(y_values_list)        
        if series_colors is None: series_colors = list(mcolors.TABLEAU_COLORS.values())[:len(y_values_list)]
        if series_width is None: series_width = [1] * len(y_values_list)



        for y_values, label, color, style, width, second in zip(y_values_list, series_labels, series_colors, series_styles, series_width, second_axis):
            ax.plot(date_list, y_values, label = label, color = color, linestyle = style, linewidth = width)

        ax.legend(loc = "lower left", ncol = 2)
        ax.set_ylabel(y_axis_label)
        ax.tick_params(axis='x', labelsize=7)

        if title is not None: ax.set_title(title, fontsize = 8)
        
        fig.tight_layout(pad = 1.0)
  
        plt.savefig(path)
        plt.show()
        plt.close()