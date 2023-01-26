

import matplotlib.pyplot as plt
from matplotlib.axis import Tick

from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, PercentFormatter)

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

from typing import List

from enum import Enum


class PlotType(Enum):
    PERCENT = 1
    OTHER = 2

class MonthlyPlots:

    def monthlyUsageBarChart(x_values, y_values_list, y_axis_label, series_labels, series_colors, fmt_str, title, path,
                             show_y_axis = False):

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

        if not show_y_axis: ax.spines["left"].set_visible(False)

        ax.tick_params(left = False, labelleft = False)
        ax.set_ylabel(y_axis_label)

#       ax.get_yaxis().set_visible(False)


        ax.legend(loc = "upper right")

        ax.set_title(title)
        plt.savefig(path)
        plt.show()
        plt.close()
        

    

    def monthlyUsageLineChart(x_values,
                              y_values_list,
                              series_labels,
                              series_colors,
                              title,
                              path,
                              show_average:bool = True,
                              text_label_list: List[str] = None,
                              plottype = PlotType.PERCENT,
                              y_axis_label = None):
        
        plt.rcParams.update({'font.size': 8})
        fig, ax = plt.subplots(figsize = (7.5, 3.5))
        fig.tight_layout(pad = 2.0)

        maxy = max([max(l) for l in y_values_list])
        ax.set_ylim([0, 1.2*maxy])

        for y_values, series_label, series_color in zip(y_values_list, series_labels, series_colors):
            ax.plot(x_values, y_values, '-D', label = series_label, color = series_color)
            
        if show_average:
            ax.plot(x_values, [sum(y_values_list[0])/len(x_values) for x in x_values], '-', color = "lightgray")

        if text_label_list is not None:
            for (text_labels, y_values, color) in zip(text_label_list, y_values_list, series_colors):
                if text_labels is None: continue
                for(x, y, label) in zip(x_values, y_values, text_labels):
                    ax.text(x, y - 0.1*maxy, label, color = color)
                    
        ax.legend()

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        if plottype == PlotType.PERCENT:
            ax.yaxis.set_major_formatter(PercentFormatter(xmax = 1, decimals=0))

        if y_axis_label is not None:
            ax.set_ylabel(y_axis_label)
        
        if title is not None:
            ax.set_title(title)
        
        plt.savefig(path)
        plt.show()
        plt.close()

            
    


