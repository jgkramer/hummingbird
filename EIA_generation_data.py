import numpy
import pandas as pd
import os
import requests

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import matplotlib as mpl
import math
import os

def data_frame_from_request(url):
    results = requests.get(url)

    if results.status_code >= 400: 
        print(f"Error code: {results.status_code} - {results.reason}")
        print("Error details:", results.text)
        return

    json_data = results.json().get("response").get("data")
    df = pd.DataFrame(json_data)
    return df

def eia_generation_request(region: str, start_date: datetime, end_date: datetime, fuel_list, start_offset, end_offset):
    facets_str = f"facets[respondent][]={region}&"
    for f in fuel_list:
        facets_str = facets_str + f"facets[fueltype][]={f}&"
    
    start_offset_str = f"{start_offset:+03}:00"
    end_offset_str = f"{end_offset:+03}:00"

    print("offsets", start_offset_str, end_offset_str)

    api_key = os.getenv("EIA_API_KEY")

    url_data = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/?frequency=local-hourly&data[0]=value&{}start={}T00{}&end={}T23{}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key={}"

    url_data = url_data.format(facets_str,
                               start_date.strftime("%Y-%m-%d"), 
                               start_offset_str,
                               end_date.strftime("%Y-%m-%d"), 
                               end_offset_str,
                               api_key)
    
    print(url_data)

    df = data_frame_from_request(url_data)
    return df

#fuel list = [] for all fuels
#otherwise, include a subset list of "NG" (natural gas), "SUN" (solar), "WND" (wind), "NUC" (nuclear), "COL" (coal), "WAT" (hydro), "OTH" (other)
def eia_generation_data(region: str, start_date: datetime, end_date: datetime, fuel_list = [], start_offset = 0, end_offset = 0):
    for f in fuel_list:
        print("input ", f)
        if f not in ["NG", "SUN", "WND", "NUC", "COL", "WAT", "OTH"]:
            raise ValueError("Not a valid fuel type")
        
    df_list = []
    nfuels = len(fuel_list) if len(fuel_list) > 0 else 8
    day_bump = math.floor(4900/(24*nfuels))
    print(day_bump)
    
    while(start_date < end_date):
      end_block = min(end_date, start_date + relativedelta(days = day_bump - 1))
      df = eia_generation_request(region, start_date, end_block, fuel_list, start_offset, end_offset)
      df_list.append(df)
      start_date = start_date + relativedelta(days = day_bump)
              
    full_df = pd.concat(df_list, ignore_index = True)
#    full_df.sort_values(by = "period", inplace = True)

    # subtract 1 hour because we want to use "hour starting" convention and EIA data comes as hour ending
    dts = full_df["period"].apply(lambda x: datetime.strptime(x + "00", '%Y-%m-%dT%H%z') + relativedelta(hours = -1))
    full_df["Date"] = [dt.date() for dt in dts]
    full_df["Hour Starting"] = [dt.hour for dt in dts]
    full_df = full_df.drop(columns = ["respondent-name"])
    full_df.sort_values(by = "period", inplace = True)
    return full_df

if __name__ == "__main__":
    df = eia_generation_data("ERCO", start_date = datetime(2024, 8, 1), end_date = datetime(2024, 10, 10), fuel_list = ["SUN", "COL", "WND"])
    df.to_csv("gendata.csv")



    