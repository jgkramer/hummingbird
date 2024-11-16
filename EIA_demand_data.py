
import numpy
import pandas as pd
import os
import requests

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import matplotlib as mpl

import os


def data_frame_from_request(url):
    results = requests.get(url)

    if results.status_code >= 400: 
        print(f"Error code: {results.status_code} - {results.reason}")
        print("Error details:", results.text)
        return

    json_data = results.json().get("response").get("data")
    df = pd.DataFrame(json_data)
    # print(df)
    return df

def eia_single_request_other(region: str, start_date: datetime, end_date: datetime, start_offset, end_offset):
    api_key = os.getenv("EIA_API_KEY")
    start_offset_str = f"{start_offset:+03}:00"
    end_offset_str = f"{end_offset:+03}:00"

    url_data = "https://api.eia.gov/v2/electricity/rto/region-data/data/?frequency=local-hourly&data[0]=value&facets[respondent][]={}&facets[type][]=D&start={}T00{}&end={}T23{}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key={}"
    
    url_data = url_data.format(region, 
                               start_date.strftime("%Y-%m-%d"),
                               start_offset_str,
                               end_date.strftime("%Y-%m-%d"),
                               end_offset_str,
                               api_key)
    
    df = data_frame_from_request(url_data)
    df = df[df["type"]=="D"].reset_index()
    df = df[["period", "respondent-name", "value", "value-units"]].copy()
    return df


def eia_single_request_subba(region: str, start_date: datetime, end_date: datetime, start_offset, end_offset):
    start_offset_str = f"{start_offset:+03}:00"
    end_offset_str = f"{end_offset:+03}:00"

    api_key = os.getenv("EIA_API_KEY")
    url_data = "https://api.eia.gov/v2/electricity/rto/region-sub-ba-data/data/?frequency=local-hourly&data[0]=value&facets[subba][]={}&start={}T00{}&end={}T23{}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key={}"
    
    url_data = url_data.format(region, 
                               start_date.strftime("%Y-%m-%d"),
                               start_offset_str,
                               end_date.strftime("%Y-%m-%d"),
                               end_offset_str,
                               api_key)
    
    df = data_frame_from_request(url_data)
    # print(df)
    df = df[["period", "subba-name", "value", "value-units"]].copy()
    return df

def eia_request_data(region: str, sub_ba: bool, start_date: datetime, end_date: datetime, start_offset = 0, end_offset = 0):
    df_list = []
    while(start_date < end_date):
        if(sub_ba):
            df = eia_single_request_subba(region, start_date, start_date + relativedelta(months = 6, days = -1), start_offset, end_offset)
        else:
            df = eia_single_request_other(region, start_date, start_date + relativedelta(months = 6, days = -1), start_offset, end_offset)
            
        start_date = start_date + relativedelta(months = 6)
        df_list.append(df)
        
    full_df = pd.concat(df_list, ignore_index = True)
    full_df.sort_values(by = "period", inplace = True)

# subtract 1 hour because we want to use "hour starting" convention and EIA data comes as hour ending
    dts = full_df["period"].apply(lambda x: datetime.strptime(x + "00", '%Y-%m-%dT%H%z') + relativedelta(hours=-1))
    full_df["Hour Starting"] = [dt.hour for dt in dts]

    # need to convert it to date to get rid of the offset, and then back to datetime to store (dates are annoying to work with later)
    full_df["Date"] = [pd.to_datetime(dt.date()) for dt in dts]
    full_df = full_df.drop(columns = ["respondent-name"])

    return full_df

class EIA_demand:

    def __init__(self, region: str, sub_ba: bool, start_date: datetime, end_date: datetime, start_offset = 0, end_offset = 0):
        self.full_df = eia_request_data(region, sub_ba, start_date, end_date, start_offset, end_offset)
        self.full_df["value"] = pd.to_numeric(self.full_df["value"])

    def monthly_demand(self, d: datetime):
        slice = self.full_df[(self.full_df["Date"].dt.year == d.year) & (self.full_df["Date"].dt.month == d.month)][["Date", "Hour Starting", "value"]].copy()
        averages = slice.groupby("Hour Starting")["value"].mean().reset_index()
        print(averages)

    def daily_demand(self, d: datetime):
        slice = self.full_df[self.full_df["Date"].dt.date == d.date()][["Hour Starting", "value"]].copy()
        print(slice)






    