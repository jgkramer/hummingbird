
from datetime import datetime
from dateutil.relativedelta import relativedelta
import EIA_demand_data, EIA_generation_data
import numpy as np
import pandas as pd
import math

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from ercotStorageReport import StorageData

import pytz

if __name__ == "__main__":
    ISO_NE_demand  = EIA_demand_data.EIA_demand_daily(region = "ISNE", 
                                                      sub_ba = False, 
                                                      start_date = datetime(2022, 1, 1), 
                                                      end_date = datetime(2024, 12, 31),
                                                      timezone_str = "Eastern")
    
    