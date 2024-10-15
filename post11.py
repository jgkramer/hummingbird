

from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from ercotStorageReport import StorageData
import ercotRtmPrices

if "__main__" == __name__:
    directory = "./ercot_esr_reports/"
    data_set = StorageData(directory, download = False)

    start_date, end_date = data_set.get_date_range()
    print(start_date, end_date)

    #print(report_data.date, report_data.total_charge, report_data.total_discharge)