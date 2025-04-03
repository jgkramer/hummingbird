
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
    # this gets the BESS data from ERCOT
    directory = "./ercot_esr_reports/"
    storage_data = StorageData(directory, download = True, load_from_csv = False)

    start_date, end_date = storage_data.get_date_range()
    print(start_date, end_date)

    