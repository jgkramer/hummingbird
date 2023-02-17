from specificHourlyUsage import NVenergyUsage, SDenergyUsage, UsagePaths, EIARegionUsage
from hourlyEnergyUsage import HourlyEnergyUsage

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


from energyStorage import SupplyGenerator, StorageAnalyzer

from cumulativePlots import CumulativePlots

if __name__ == "__main__":
    pd.options.display.max_rows = None
    
    hourly = NVenergyUsage(UsagePaths.NV_Kramer)
    start = datetime(2021, 9, 1)
    end = datetime(2021, 9, 30)
    
    analyzer = StorageAnalyzer(hourly, start, end, "kWh")
    analyzer.apply_supply([lambda: analyzer.supplyGenerator.median_daily_peak(1.0)],
                          ["Typical Daily Peak"],
                          path = f"post5/post5_KramerMedianPeak.png")

    path = "post4/NV_ideal_solar_capacity.csv"
    #analyzer.apply_supply([lambda: analyzer.supplyGenerator.solar_function(path, 1.1)])

    jan122 = datetime(2022, 1, 1)
    jan123 = datetime(2023, 1, 1)
    paths = []
    d = jan122
    while d < jan123:
        paths.append(f"./statewide_demand/NVPower_demand_{d.year}_{d.month:02}.csv")
        d = d + relativedelta(months = +1)
    hourly2 = EIARegionUsage(paths)

    analyzer2 = StorageAnalyzer(hourly2, datetime(2022, 11, 1), datetime(2022, 11, 30), hourly2.units)
    analyzer2.apply_supply([lambda: analyzer2.supplyGenerator.median_daily_peak(1.0)])
    


#    analyzer2.apply_supply([lambda: analyzer2.supplyGenerator.solar_function(path, 1.15)])
#    analyzer2.apply_supply([lambda: analyzer2.supplyGenerator.blend_fixed_solar(path, 1.15, solar_share = 0.3)])


#    times, usage, forecast = zip(*list(hourly2.forecast_v_actual(datetime(2022, 1, 1), datetime(2022, 12, 31))))

#    usage = list(usage)
#    forecast = list(forecast)
#    ratio = [(x/y - 1) for (x, y) in zip(usage, forecast)]
#    plt.hist(ratio, bins = 20)
#    plt.show()
    
