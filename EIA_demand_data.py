
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
    print(df)
    return df

def eia_single_request_other(region: str, start_date: datetime, end_date: datetime):
    api_key = os.getenv("EIA_API_KEY")
    url_data = "https://api.eia.gov/v2/electricity/rto/region-data/data/?frequency=hourly&data[0]=value&facets[respondent][]={}&facets[type][]=D&start={}T00&end={}T23&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key={}"
    
    url_data = url_data.format(region, 
                               start_date.strftime("%Y-%m-%d"),
                               end_date.strftime("%Y-%m-%d"),
                               api_key)
    
    df = data_frame_from_request(url_data)
    df = df[df["type"]=="D"].reset_index()
    df = df[["period", "respondent-name", "value", "value-units"]].copy()
    print(df)
    return df

    
def eia_single_request_subba(region: str, start_date: datetime, end_date: datetime):
    api_key = os.getenv("EIA_API_KEY")
    url_data = "https://api.eia.gov/v2/electricity/rto/region-sub-ba-data/data/?frequency=hourly&data[0]=value&facets[subba][]={}&start={}T00&end={}T23&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key={}"
    
    url_data = url_data.format(region, 
                               start_date.strftime("%Y-%m-%d"),
                               end_date.strftime("%Y-%m-%d"),
                               api_key)
    
    df = data_frame_from_request(url_data)
    print(df)
    df = df[["period", "subba-name", "value", "value-units"]].copy()
    return df


def eia_request_data(region: str, sub_ba: bool, start_date: datetime, end_date: datetime):
    df_list = []
    while(start_date < end_date):
        if(sub_ba):
            df = eia_single_request_subba(region, start_date, start_date + relativedelta(months = 6, days = -1))
        else:
            df = eia_single_request_other(region, start_date, start_date + relativedelta(months = 6, days = -1))
            
        start_date = start_date + relativedelta(months = 6)
        df_list.append(df)
        
    full_df = pd.concat(df_list, ignore_index = True)
    full_df.sort_values(by = "period", inplace = True)
    return full_df






    