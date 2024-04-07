
import numpy
import pandas as pd
import os
import requests

from datetime import datetime, timedelta

import matplotlib as mpl

import os

def get_data():
    api_key = os.getenv("EIA_API_KEY")
    print(api_key)
    url_data = "https://api.eia.gov/v2/electricity/rto/region-sub-ba-data/data/?api_key={}&frequency=local-hourly&data[0]=value&facets[subba][]=DOM&start=2024-01-01T00:00:00-05:00&end=2024-01-3T00:00:00-05:00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
    url_data = url_data.format(api_key)
    print(url_data)
    results = requests.get(url_data)
    
    if results.status_code >= 400: 
        print(f"Error code: {results.status_code} - {results.reason}")
        print("Error details:", results.text)
        return
    
 
    json_data = results.json().get("response").get("data")
    print(json_data)
    df = pd.DataFrame(json_data)
    print(df)

    

if __name__ == "__main__":
    get_data()


    