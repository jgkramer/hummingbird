

import matplotlib.pyplot as plt
from matplotlib.axis import Tick

from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, PercentFormatter)

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from typing import List

class MonthlyPlots:

    def monthlyUsageBarChart(x_values, y_values_list, y_axis_label, series_labels, series_colors, fmt_str, title, path):

        plt.rcParams.update({'font.size': 8})
        fig, ax = plt.subplots(figsize = (7.5, 3.5))

        maxy = max([max(l) for l in y_values_list])
        ax.set_ylim([0, 1.2*maxy])
        
        fig.tight_layout(pad = 2.0)

        plots = []
        for y_values, series_label, series_color in zip(y_values_list, series_labels, series_colors):
            plots.append(ax.bar(x_values, y_values, label = series_label, color = series_color))
            ax.bar_label(plots[-1], fmt = fmt_str, padding = 5)
            
            
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)

        ax.tick_params(left = False, labelleft = False)
        ax.set_ylabel(y_axis_label)

#        ax.get_yaxis().set_visible(False)


        ax.legend(loc = "upper right")

        ax.set_title(title)
        plt.savefig(path)
        plt.show()
        plt.close()
        

    def monthlyUsageLineChart(x_values, y_values_list, series_labels, series_colors, title, path, show_average:bool = True):
        plt.rcParams.update({'font.size': 8})
        fig, ax = plt.subplots(figsize = (7.5, 3.5))
        fig.tight_layout(pad = 2.0)

        maxy = max([max(l) for l in y_values_list])
        ax.set_ylim([0, 1.2*maxy])

        for y_values, series_label, series_color in zip(y_values_list, series_labels, series_colors):
            ax.plot(x_values, y_values, '-D', label = series_label, color = series_color)
            
        if show_average:
            ax.plot(x_values, [1/12 for x in x_values], '-', color = "lightgray")
            

        ax.legend()

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.set_major_formatter(PercentFormatter(xmax = 1, decimals=0))
        
        ax.set_title(title)
        plt.savefig(path)
        plt.show()
        plt.close()

            
    


