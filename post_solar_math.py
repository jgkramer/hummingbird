import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
 
import matplotlib as mpl
import matplotlib.pyplot as plt
from periodicCharts import HourlyChart

def plot_solar_capacity(df_solar):
    
    cmap = mpl.cm.get_cmap('tab20c')
    #gray for winter (16), green spring(8), blue summer(0, 1, 2), reds fall (4, 5, 6)
    series_color_nums = [16, 16, 9, 9, 9, 0, 0, 0, 5, 5, 5, 16]  
    series_colors = [cmap(x/20) for x in series_color_nums]
    series_styles = ["dashed", "dotted", "solid"] * 4

    x_values = [h for h in range(0, 24)]
    y_values_list = []
    series_labels = []
    y_axis_label = f"NV Ideal Solar Generation by Hour of Day (MWh)"

    ymax = 0
    for col_name, col in df_solar.items():
        if col_name in list(calendar.month_abbr[1:]):
            y_values_list.append(list(col))
            series_labels.append(col_name)
            if(max(col) > ymax): ymax = max(col)

    print(ymax)

    HourlyChart.hourlyLineChart(x_values,
                                y_values_list,
                                y_axis_label,
                                series_labels,
                                series_colors,
                                path = "post8/NV_solar_by_month.png",
                                title = None,
                                x_axis_label = "Hour Starting (Standard Time)",
                                annotate = None,
                                ymax = ymax*1.2,
                                series_styles = series_styles,
                                height_scale = 1.25)
                                
                                
if __name__ == "__main__":
    pd.options.display.max_rows = None

    # the solar generation data from post 4
    solar_data_path = "post4/NV_ideal_solar_capacity.csv"
    df_solar_raw = pd.read_csv(solar_data_path)

    # strip out the minimum overnight generation from each month - likely thermal solar
    df_solar = df_solar_raw.apply(lambda col: col - col.min())

    print(df_solar["Jun"])
    plot_solar_capacity(df_solar)
    
        
