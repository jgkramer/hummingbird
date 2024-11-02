
import pdfplumber as pdfp
from pypdf import PdfReader
import requests
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

def download_storage_reports(directory: str):
    report_type_id = "23794"
    url = f"https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId={report_type_id}"
    
    response = requests.get(url)
    data = response.json()
    document_list = data["ListDocsByRptTypeRes"]["DocumentList"]
    
    for doc in document_list:
        name = doc["Document"]["FriendlyName"]
        doc_id = doc["Document"]["DocID"]
        print(name, doc_id)

        if doc_id:
            report_url = f"https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={doc_id}"
            report_filename = f"{directory}/{name.replace(" ", "_")}.pdf"
            response = requests.get(report_url)
            with open(report_filename, "wb") as file:
                file.write(response.content)

class DailyStorageReport:
    def __init__(self, date, pdf = True):
        self.summary_table_rows = []
        self.date = date
        self.valid_data = True

    def get_percent_series(self, chart_text):
        hours = r"01\s+02\s+03\s+04\s+05\s+06\s+07\s+08\s+09\s+10\s+11\s+12\s+13\s+14\s+15\s+16\s+17\s+18\s+19\s+20\s+21\s+22\s+23\s+24"
        if not re.search(hours, chart_text, re.DOTALL):
            print(self.date, ": does not have 24 hour buckets")

        chart_text_2 = re.sub(hours, "[hours] ", chart_text)
        #print(chart_text_2)
        percent_pattern = r"([0-9]+\.[0-9]%\s*){24}"
        percent_match = re.search(percent_pattern, chart_text_2, re.DOTALL)
        if not percent_match:
            print(self.date, ": does not have 24 percents")
            chart_text_3 = re.sub(r"([0-9]+\.[0-9]%)(\s\s)", r"\1 0.0% ", chart_text_2) 
            percent_match = re.search(percent_pattern, chart_text_3, re.DOTALL)
            if percent_match:
                print("repair worked!")
            if not percent_match:
                print(self.date, ": repair didn't work")
                self.valid_data = False
                return [0]*24

        percent_str = percent_match.group(0)
        percent_str = re.sub("%", "% ", percent_str)
        percent_str = re.sub(r"\s+", " ", percent_str)
        percent_str = re.sub(r" $", "", percent_str)
        percent_str_list = percent_str.split(" ")
        percent_list = [float(s.rstrip("%")) / 100 for s in percent_str_list]
        return percent_list

    def set_data(self, valid, installed_charge_capacity, installed_discharge_capacity, total_charge, total_discharge, charging_mwh, discharging_mwh):
        self.valid_data = valid
        self.installed_charge_capacity = installed_charge_capacity
        self.installed_discharge_capacity = installed_discharge_capacity
        self.total_charge = total_charge
        self.total_discharge = total_discharge
        self.charging_mwh = charging_mwh
        self.discharging_mwh = discharging_mwh

    def extract_data_from_pdf(self, path):
        with pdfp.open(path) as pdf:
            page1 = pdf.pages[0]
            front_tables = page1.extract_tables()
            
            for ix, table in enumerate(front_tables):
                self.summary_table_rows.extend(table)
        
        pattern1 = "Installed ESR Discharge Capacity"
        pattern2 = "Installed ESR Charge Capacity"
        for row in self.summary_table_rows:    
            if re.match(pattern1, row[0]):
                capacity_string = re.match(r"[0-9,]+", row[1]).group(0)
                self.installed_discharge_capacity = int(capacity_string.replace(",",""))
                #self.installed_discharge_capacity_units = row[1][len(capacity_string):]
            if re.match(pattern2, row[0]):
                capacity_string = re.match(r"[0-9,]+", row[1]).group(0)
                self.installed_charge_capacity = int(capacity_string.replace(",",""))
                #self.installed_charge_capacity_units = row[1][len(capacity_string):]

        # PdfPlumber puts the
        reader = PdfReader(path)
        page3 = reader.pages[2]
        page3_text = page3.extract_text()

        pattern_discharging = r"Actual ESR Discharging Output.*Actual ESR Discharging Output"
        match_discharging = re.search(pattern_discharging, page3_text, re.DOTALL)
        if match_discharging: 
            discharging_percents = self.get_percent_series(match_discharging.group(0))
            
        pattern_charging = r"Actual ESR Charging Output.*Actual ESR Charging Output"
        match_charging = re.search(pattern_charging, page3_text, re.DOTALL)
        if match_charging: 
            charging_percents = self.get_percent_series(match_charging.group(0))

        self.discharging_mwh = [self.installed_discharge_capacity * p for p in discharging_percents]
        self.charging_mwh = [self.installed_charge_capacity * p for p in charging_percents]

        self.total_discharge = sum(self.discharging_mwh)
        self.total_charge = sum(self.charging_mwh)
        
    def get_summary_list(self):
        summary_list = [datetime.strftime(self.date, "%m/%d/%Y"), self.valid_data, self.installed_charge_capacity, self.installed_discharge_capacity, self.total_charge, self.total_discharge]
        summary_list.append(self.charging_mwh)
        summary_list.append(self.discharging_mwh)
        return summary_list


class StorageData:
    # static
    def dateFromFilename(filename):
        #print(filename)
        strings = re.split(r"_|\.", filename)
        date = datetime.strptime(strings[1], "%m-%d-%y")
        return date.date()

    # returns a data frame with columns Date, Charge, Discharge
    def daily_totals(self):
        sum_charge = [r.total_charge for r in self.reportlist]
        sum_discharge = [r.total_discharge for r in self.reportlist]
        df = pd.DataFrame({"Date": self.datelist, "Charge (MWh)": sum_charge, "Discharge (MWh)": sum_discharge})
        return df

    def get_date_range(self):
        return self.start_date, self.end_date    

    # returns a 24-element list with the charging MW for each hour of the day, averaged across all the dates of the month of curr_month
    def monthly_average_charging(self, curr_month: datetime):
        print("monthly average charging for", curr_month)
        month_hourly_charging = [self.reports[d].charging_mwh for d in self.datelist if d.year == curr_month.year and d.month == curr_month.month and self.reports[d].valid_data]
        print(month_hourly_charging)
        # for the i'th of the month, the i'th element of this array contains the 24-long series of hourly charging / discharging for that day
        array_charging = np.array(month_hourly_charging)
        
        # this computes the average across all days, resulting in a 24-hour long array)
        average_charging = np.average(array_charging, axis = 0)
        print(average_charging)
        return average_charging
    
    def monthly_average_discharging(self, curr_month: datetime):
        month_hourly_discharging = [self.reports[d].discharging_mwh for d in self.datelist if d.year == curr_month.year and d.month == curr_month.month and self.reports[d].valid_data]
        array_discharging = np.array(month_hourly_discharging)
        average_discharging = np.average(array_discharging, axis = 0)
        return average_discharging

    def save_down(self):
        columns = ["Date", "Valid", "Installed_Charge_Capacity", "Installed_Discharge_Capacity", "Total_Charge", "Total_Discharge", "Hourly_Charging", "Hourly_Discharging"]
        df = pd.DataFrame(columns = columns)
        for d in self.datelist:
            report = self.reports[d]
            row = report.get_summary_list()
            df.loc[len(df)] = row
            
        print(df)
        df.to_csv("storage.csv")

    def load_saved(self):
        datelist = []
        df = pd.read_csv("storage.csv")
        for row in df.itertuples(index=True, name="Row"):
            d = datetime.strptime(row.Date, "%m/%d/%Y").date()
            valid = True
            installed_charge_capacity = float(row.Installed_Charge_Capacity)
            installed_discharge_capacity = float(row.Installed_Discharge_Capacity)
            total_charge = float(row.Total_Charge)
            total_discharge = float(row.Total_Discharge)
            hourly_charging_strs = row.Hourly_Charging.strip("[]").split(", ")
            hourly_charging_list = [float(s) for s in hourly_charging_strs]
            hourly_discharging_strs = row.Hourly_Discharging.strip("[]").split(", ")
            hourly_discharging_list = [float(s) for s in hourly_discharging_strs]

            report = DailyStorageReport(d, pdf = False)
            report.set_data(valid,
                            installed_charge_capacity, 
                            installed_discharge_capacity,
                            total_charge,
                            total_discharge,
                            hourly_charging_list,
                            hourly_discharging_list)
            
            datelist.append(d)
            self.reports[d] = report
        
        self.datelist = sorted(datelist)

    def daily_charging(self, dt):
        return self.reports[dt.date()].charging_mwh
    
    def daily_discharging(self, dt):
        return self.reports[dt.date()].discharging_mwh

    def __init__(self, directory, download = False, load_from_csv = True):

        datelist = []
        self.reports = {}

        if(download):
            download_storage_reports(directory)

        if(load_from_csv == False):
            # list of filenames that (1) are files and not directories AND (2) have a filename matching ESR integration report
            files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and re.match(r"^ESRIntegration.*pdf", f, re.DOTALL)]
            for filename in files:
                path = directory + filename
                date = StorageData.dateFromFilename(filename)
                datelist.append(date)
                report = DailyStorageReport(date)
                report.extract_data_from_pdf(path)
                self.reports[date] = report
                self.datelist = sorted(datelist)   
            self.save_down()     
            
        else: 
            self.load_saved()

        self.start_date = self.datelist[0]
        self.end_date = self.datelist[-1]
        


        
            
