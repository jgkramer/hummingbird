import numpy
import pandas as pd
import os
import requests

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import pytz

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

    url_data = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/?frequency=local-hourly&data[0]=value&{}start={}T01{}&end={}T00{}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key={}"

    url_data = url_data.format(facets_str,
                               start_date.strftime("%Y-%m-%d"), 
                               start_offset_str,
                               (end_date + timedelta(days=1)).strftime("%Y-%m-%d"), # want hour ending 0th hour on the next day 
                               end_offset_str,
                               api_key)
    
    print(url_data)

    df = data_frame_from_request(url_data)
    return df

#fuel list = [] for all fuels
#otherwise, include a subset list of "NG" (natural gas), "SUN" (solar), "WND" (wind), "NUC" (nuclear), "COL" (coal), "WAT" (hydro), "OTH" (other)
def eia_generation_data(region: str, start_date: datetime, end_date: datetime, fuel, start_offset = 0, end_offset = 0):
    print("input ", fuel)
    if fuel not in ["NG", "SUN", "WND", "NUC", "COL", "WAT", "OTH"]:
        raise ValueError("Not a valid fuel type")
        
    df_list = []
    nfuels = 1
    day_bump = math.floor(4900/(24*nfuels))
    print(day_bump)
    
    while(start_date < end_date):
      end_block = min(end_date, start_date + relativedelta(days = day_bump - 1))
      df = eia_generation_request(region, start_date, end_block, [fuel], start_offset, end_offset)
      df_list.append(df)
      start_date = start_date + relativedelta(days = day_bump)
              
    full_df = pd.concat(df_list, ignore_index = True)

    # subtract 1 hour because we want to use "hour starting" convention and EIA data comes as hour ending
    dts = full_df["period"].apply(lambda x: datetime.strptime(x + "00", '%Y-%m-%dT%H%z') + relativedelta(hours = -1))
    full_df["Hour Starting"] = [dt.hour for dt in dts]

    full_df = full_df.drop(columns = ["respondent-name"])
    full_df["Date"] = [pd.to_datetime(dt.date()) for dt in dts]

    all_dates = pd.date_range(start=full_df["Date"].min(), end=full_df["Date"].max(), freq="D")
    all_hours = pd.DataFrame({"Hour Starting": range(24)})

    all_combinations = pd.merge(pd.DataFrame({"Date": all_dates}), all_hours, how="cross")
    df_complete = pd.merge(all_combinations, full_df, on=["Date", "Hour Starting"], how="left")

    df_complete["value"] = df_complete["value"].fillna(0)
    df_complete["value"] = df_complete["value"].astype(int)

    full_df.sort_values(by = ["Date", "Hour Starting"], inplace = True)
    return df_complete


def get_utc_offsets(tz: str, start_date, end_date):
    tz = pytz.timezone(tz)
    start_local = tz.localize(start_date)
    start_offset = round(start_local.utcoffset().total_seconds() / 3600)
    end_local = tz.localize(end_date)
    end_offset = round(end_local.utcoffset().total_seconds() / 3600)
    return start_offset, end_offset

if __name__ == "__main__":
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2024, 11, 1)
    start_offset, end_offset = get_utc_offsets("US/Central", start_date, end_date)  
    df = eia_generation_data("ERCO", start_date = start_date, end_date = end_date, fuel = "COL", start_offset = start_offset, end_offset = end_offset)
    df.to_csv("gendata.csv")

class EIA_generation:

    def __init__(self, region: str, start_date: datetime, end_date: datetime, fuel: str, start_offset = 0, end_offset = 0):
        self.fuel = fuel
        self.full_df = eia_generation_data(region, start_date, end_date, fuel, start_offset, end_offset)
        self.full_df["value"] = pd.to_numeric(self.full_df["value"])

    def monthly_generation(self, d: datetime):
        slice = self.full_df[(self.full_df["Date"].dt.year == d.year) & (self.full_df["Date"].dt.month == d.month)][["Date", "Hour Starting", "value"]]
        averages = slice.groupby("Hour Starting")["value"].mean().copy().reset_index()
        return averages

    def daily_generation(self, d: datetime):
        slice = self.full_df[self.full_df["Date"].dt.date == d.date()][["Hour Starting", "value"]].copy()
        return slice





    