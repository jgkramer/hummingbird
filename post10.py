
import numpy
import pandas
import os
import requests


from datetime import datetime, timedelta

import matplotlib as mpl

import os

def get_data():
    url_data = "https://api.eia.gov/v2/electricity/rto/region-sub-ba-data/data/?frequency=local-hourly&data[0]=value&facets[subba][]=DOM&start=2024-01-01T00:00:00-05:00&end=2024-02-01T00:00:00-05:00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"


if __name__ == "__main__":
    api_key = os.getenv("EIA_API_KEY")
    api = eia.API(api_key)

    