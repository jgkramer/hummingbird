
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from typing import List

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns


class HourlyChart:

    def format_time(x, _):
        hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
        return hm + ("am" if (x%24)<12 else "pm")
    
    def prepHourlyChart(yrange: List[float], dims):
        plt.rcParams["font.size"] = 8
        fig, ax = plt.subplots(figsize = dims)


        ax.set_xlim([0, 23])
        ax.set_ylim(yrange)

        ax.xaxis.set_ticks(np.arange(0, 24, 3))
        ax.xaxis.set_major_formatter(HourlyChart.format_time)

        if yrange[1] > 10:
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
        else:
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.1f}"))
        
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)

        return fig, ax
                               
    def hourlyLineChart(x_values,
                        y_values_list,
                        y_axis_label: str,
                        series_labels,
                        series_colors,
                        path: str,
                        title: str = None,
                        x_axis_label:str = None,
                        annotate: int = None,
                        ymax = None,
                        series_styles = None,
                        height_scale = 1,
                        table_series: List[int] = None):
        
        maxy = ymax if ymax is not None else 1.125*max([max(l) for l in y_values_list])
        miny = min(0, 1.25*min([min(l) for l in y_values_list]))
        dims = (8, 3*height_scale)

        fig, ax = HourlyChart.prepHourlyChart([miny, maxy], dims)
        
        if series_styles is None: series_styles = ["solid"] * len(y_values_list)
        
        for y_values, label, color, style in zip(y_values_list, series_labels, series_colors, series_styles):
            ax.plot(x_values, y_values, label = label, color = color, linestyle = style)

        if annotate is not None:
            for a, b in zip(x_values, y_values_list[annotate]):
                if b > 0.1*max(y_values_list[annotate]):
                    ax.annotate(f"{int(round(b))}", (a - 0.5 + (a-11)/18, b + 150), size = 8)

        if table_series is not None:
            table_columns = ["Total (MWh)"]
            table_rows = [series_labels[i] for i in table_series]
            cells = [[f"{sum(y_values_list[i]):,.0f} "] for i in table_series]
            
            table = ax.table(cellText = cells, rowLabels = table_rows, colLabels = table_columns,
                             cellLoc = "center", loc = "upper right")
            
            table.auto_set_column_width(col=list(range(len(table_columns))))
            table.set_fontsize(8)
            cells = table.get_celld().values()
            for cell in cells:
                cell.set(edgecolor = "lightgray")
        
        ax.legend(loc = "upper left")
        ax.set_ylabel(y_axis_label)

        if title is not None: ax.set_title(title, fontsize = 8)
        if x_axis_label is not None: ax.set_xlabel(x_axis_label)

        fig.tight_layout(pad = 1.0)
  
        plt.savefig(path)
        plt.show()
        plt.close()

