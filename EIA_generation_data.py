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

all_fuels = ["NG", "SUN", "WND", "NUC", "COL", "WAT", "OTH", "OIL", "PS", "BAT", "SNB", "UES"]

def fuel_valid(fuel):
    if fuel not in all_fuels:
        print(f"Fuel {fuel} is not a valid fuel type. Valid types are: {all_fuels}")
        return False
    return True

def data_frame_from_request(url):
    results = requests.get(url)

    if results.status_code >= 400: 
        print(f"Error code: {results.status_code} - {results.reason}")
        print("Error details:", results.text)
        return

    json_data = results.json().get("response").get("data")
    df = pd.DataFrame(json_data)
    return df

def eia_generation_request(region: str, start_date: datetime, end_date: datetime, fuel, start_offset, end_offset):
    facets_str = f"facets[respondent][]={region}&"
    facets_str = facets_str + f"facets[fueltype][]={fuel}&"
    
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
#otherwise, include a subset list of "NG" (natural gas), "SUN" (solar), "WND" (wind), "NUC" (nuclear), "COL" (coal), "WAT" (hydro), "OTH" (other), 
# "OIL" (oil), "PS" (pumped storage), "BAT" (battery), "SNB" (synthetic natural gas)

def eia_generation_data(region: str, start_date: datetime, end_date: datetime, fuel, start_offset = 0, end_offset = 0):
    print("input ", fuel)
    if not fuel_valid(fuel):
        raise ValueError("Not a valid fuel type")
        
    df_list = []
    nfuels = 1
    day_bump = math.floor(4900/(24*nfuels))
    print(day_bump)
    
    while(start_date <= end_date):
      end_block = min(end_date, start_date + relativedelta(days = day_bump - 1))
      df = eia_generation_request(region, start_date, end_block, fuel, start_offset, end_offset)
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

class EIA_generation:
    def __init__(self, region: str, start_date: datetime, end_date: datetime, fuel: str, start_offset = 0, end_offset = 0):
        self.fuel = fuel
        print("Fuel type:", fuel)
        self.full_df = eia_generation_data(region, start_date, end_date, fuel, start_offset, end_offset)
        self.full_df["value"] = pd.to_numeric(self.full_df["value"])
        self.full_df.dropna(inplace=True)

    def monthly_generation(self, d: datetime):
        slice = self.full_df[(self.full_df["Date"].dt.year == d.year) & (self.full_df["Date"].dt.month == d.month)][["Date", "Hour Starting", "value"]]
        averages = slice.groupby("Hour Starting")["value"].mean().copy().reset_index()
        return averages

    def daily_generation(self, d: datetime):
        slice = self.full_df[self.full_df["Date"].dt.date == d.date()][["Hour Starting", "value"]].copy()
        return slice
    
    def full_generation(self):
        return self.full_df[["Date", "Hour Starting", "value"]].copy()
    
class EIA_generation_daily:
    def eia_single_daily_request(self, region: str, fuel, start_date: datetime, end_date: datetime, timezone_str: str):
        api_key = os.getenv("EIA_API_KEY")
        print("API key", api_key)
        facets_str = f"facets[respondent][]={region}&facets[timezone][]={timezone_str}&"
        facets_str = facets_str + f"facets[fueltype][]={fuel}&"
        url_data = "https://api.eia.gov/v2/electricity/rto/daily-fuel-type-data/data/?frequency=daily&data[0]=value&{}start={}&end={}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key={}"
        url_data = url_data.format(facets_str, 
                                   start_date.strftime("%Y-%m-%d"),
                                   end_date.strftime("%Y-%m-%d"),
                                   api_key)        
        print(url_data)
        df = data_frame_from_request(url_data)
        if df is not None:
            print("Got data")
            return df

    def eia_request_daily_data(self, region: str, fuel, start_date: datetime, end_date: datetime, timezone_str: str = "Eastern"):
        df_list = []

        max_months = math.floor(4900 / (31))  # 5000 is the max number of data points returned by EIA, use 4900 to be safe
        month_steps = min(24, max_months)

        while start_date <= end_date:
            request_end = min(start_date + relativedelta(months=month_steps, days=-1), end_date)
            df = self.eia_single_daily_request(region, fuel, start_date, request_end, timezone_str)
            start_date = start_date + relativedelta(months=month_steps)
            df_list.append(df)
        full_df = pd.concat(df_list)
        full_df.sort_values(by="period", inplace=True, ignore_index=True)
        dates = full_df["period"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
        full_df["Date"] = dates
        full_df = full_df.drop(columns = ["period", "respondent-name", "type-name", "timezone-description"]).reindex()
        print(full_df)
        return full_df

    def __init__(self, region: str, fuel, start_date: datetime, end_date: datetime, timezone_str: str = "Eastern"):
        if not fuel_valid(fuel):
            raise ValueError("Not a valid fuel type")
        self.full_df = self.eia_request_daily_data(region, fuel, start_date, end_date)
        self.full_df["value"] = pd.to_numeric(self.full_df["value"])
        self.full_df.dropna(inplace=True)
        
    def generation(self):
        return self.full_df[["Date", "value"]].copy()

if __name__ == "__main__":
    start_date = datetime(2025, 5, 1)
    end_date = datetime(2025, 7, 1)
    gen = EIA_generation_daily("ISNE", fuel = "NG", start_date = start_date, end_date = end_date, timezone_str = "Eastern")

    #display all rows
    pd.set_option('display.max_rows', None)
    print(gen.full_df)
