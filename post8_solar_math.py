import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
import math
import itertools
 
import matplotlib as mpl
import matplotlib.pyplot as plt
from periodicCharts import HourlyChart

from compute_solar_position import SolarPosition
from analyze_solar_radiance import SolarRadiance

def plot_solar_capacity(df_solar):
    cmap = mpl.cm.get_cmap('tab20c')
    #gray for winter (16), green spring(8), blue summer(0), reds fall (5)
    series_color_nums = [16, 16, 9, 9, 9, 0, 0, 0, 5, 5, 5, 16]  
    series_colors = [cmap(x/20) for x in series_color_nums]
    series_styles = ["dashed", "dotted", "solid"] * 4

    x_values = range(24)
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
 

def cosine_beta(azimuth_deg, elevation_deg):
    if elevation_deg < 0:
        return 0

    cos_azimuth = math.cos(math.radians(azimuth_deg))
    cos_elevation = math.cos(math.radians(elevation_deg))
    
    return math.sqrt(1 - (cos_elevation * cos_azimuth)**2)


if __name__ == "__main__":
    pd.options.display.max_rows = None

    # the solar generation data from post 4
    solar_data_path = "post4/NV_ideal_solar_capacity.csv"
    df_solar_raw = pd.read_csv(solar_data_path)

    # strip out the minimum overnight generation from each month - likely thermal solar
    df_solar = df_solar_raw.apply(lambda col: col - col.min())

    print(df_solar["Jun"])
    plot_solar_capacity(df_solar)

    vegasSolarPosition = SolarPosition(lat = 36.17, long = -115.14, timezone = -8)

    dfs = dict()
    months = [4, 6, 8, 10, 12]

    radiance = SolarRadiance()

    ymax = 0

    for m in months:
        dfs[m] = vegasSolarPosition.solar_position_series([datetime(2023, m, 15, h // 2, 30 * (h%2), 0) for h in range(24*2)])
        (dfs[m])["cos beta"] = dfs[m].apply(lambda row: cosine_beta(row["azimuth"], row["elevation"]), axis = 1)
        radlist = [radiance.getRadiance(m, h // 2, 30 * (h%2)) for h in range(24*2)]
        (dfs[m])["radiance"] = radlist
        (dfs[m])["output"] = dfs[m]["radiance"] * dfs[m]["cos beta"]
        ymax = max(ymax, max(dfs[m]["output"]))


    cmap = mpl.cm.get_cmap('tab20c')
    #gray for winter (16), green spring(8), blue summer(0, 1, 2), reds fall (4, 5, 6)
    series_color_nums = [16, 16, 9, 9, 9, 0, 0, 0, 5, 5, 5, 16]  
    series_colors = [cmap(x/20) for x in [series_color_nums[m-1] for m in months]]

    styles_all = ["dashed", "dotted", "solid"] * 4
    series_styles = [styles_all[m-1] for m in months]

    HourlyChart.hourlyLineChart(np.arange(0, 24, 0.5),
                                [dfs[m]["radiance"] for m in months],
                                "Las Vegas \"Clearsky\" DNI (W/m^2)",
                                [calendar.month_abbr[m] for m in months],
                                series_colors,
                                path = "post8/post8_NV_dni_by_month.png",
                                series_styles = series_styles)

    HourlyChart.hourlyLineChart(np.arange(0, 24, 0.5),
                                [np.array(dfs[m]["output"]) * 1/ymax for m in months],
                                "Modeled Output (scaled to max)",
                                [calendar.month_abbr[m] for m in months],
                                series_colors,
                                path = "post8/post8_NV_modeled_by_month.png", 
                                x_axis_label = "Time of Day (Standard Time)",
                                ymax = 1.2,
                                series_styles = series_styles, 
                                height_scale = 1.25)
    
    for m in [6, 9, 12]:
        df = vegasSolarPosition.solar_position_series([datetime(2023, m, 15, h, 0, 0) for h in [8, 10, 12, 14, 16]])
        #print(" ".join(list(df["datetime"])))
        print("<td>", "</td><td>".join([str(round(x, 1)) + "&deg;" for x in list(df["elevation"])]), "</td>")
        print("<td>", "</td><td>".join([str(round(x, 1)) + "&deg;" for x in list(df["azimuth"])]), "</td>")



print(dfs[4][["datetime", "cos beta", "radiance"]])
print(dfs[8][["datetime", "cos beta", "radiance"]])










    
        
