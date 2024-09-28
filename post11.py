
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

def download_reports():
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
            report_filename = f"./ercot_esr_reports/{name.replace(" ", "_")}.pdf"
            response = requests.get(report_url)
            with open(report_filename, "wb") as file:
                file.write(response.content)

class ReportData:

    # static
    def dateFromFilename(filename):
        #print(filename)
        strings = re.split(r"_|\.", filename)
        date = datetime.strptime(strings[1], "%m-%d-%y")
        return date.date()

    def __init__(self, path, date):
        self.summary_table_rows = []
        self.path = path
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

    def extract_data_from_pdf(self):
        with pdfp.open(self.path) as pdf:
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
                self.installed_discharge_capacity_units = row[1][len(capacity_string):]
            if re.match(pattern2, row[0]):
                capacity_string = re.match(r"[0-9,]+", row[1]).group(0)
                self.installed_charge_capacity = int(capacity_string.replace(",",""))
                self.installed_charge_capacity_units = row[1][len(capacity_string):]

        # PdfPlumber puts the
        reader = PdfReader(self.path)
        page3 = reader.pages[2]
        page3_text = page3.extract_text()


     #   fig, ax = plt.subplots(figsize = (7.5, 3.5))        
     #   fig.tight_layout(pad = 2.0)

        pattern_discharging = r"Actual ESR Discharging Output.*Actual ESR Discharging Output"
        match_discharging = re.search(pattern_discharging, page3_text, re.DOTALL)
        if match_discharging: 
            self.discharging_percents = self.get_percent_series(match_discharging.group(0))
            
        pattern_charging = r"Actual ESR Charging Output.*Actual ESR Charging Output"
        match_charging = re.search(pattern_charging, page3_text, re.DOTALL)
        if match_charging: 
            self.charging_percents = self.get_percent_series(match_charging.group(0))

        self.discharging_mwh = [self.installed_discharge_capacity * p for p in self.discharging_percents]
        
        self.charging_mwh = [self.installed_charge_capacity * p for p in self.charging_percents]
        self.total_discharge = sum(self.discharging_mwh)
        self.total_charge = sum(self.charging_mwh)

if "__main__" == __name__:
    directory = "./ercot_esr_reports/"

    download = False
    if download:
        download_reports()

    # list of filenames that (1) are files and not directories AND (2) have a filename matching ESR integration report
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and re.match(r"^ESRIntegration.*pdf", f, re.DOTALL)]
    print(files)

    datelist = []
    reportlist = []
    for filename in files:
        path = directory + filename
        date = ReportData.dateFromFilename(filename)
        datelist.append(date)
        report_data = ReportData(path, date) 
        report_data.extract_data_from_pdf()
        reportlist.append(report_data)

    sorted_pairs = sorted(zip(datelist, reportlist))
    sorted1, sorted2 = zip(*sorted_pairs)
    datelist = list(sorted1)
    reportlist = list(sorted2)

    print(reportlist[-1].discharging_mwh)
    print(reportlist[-1].charging_mwh)

    discharge_capacity = [r.installed_discharge_capacity for r in reportlist]
    sum_discharge = [r.total_discharge for r in reportlist]
    
    fig, ax = plt.subplots(figsize = (7.5, 3.5))        
    fig.tight_layout(pad = 2.0)
    ax.plot(datelist, discharge_capacity, label = "Installed Discharge Capacity")
    ax.plot(datelist, sum_discharge, label = "Daily Discharge Amount")
    plt.legend()
    plt.show()


    curr_month = datetime(datelist[0].year, datelist[0].month, 1)
    last_month = datetime(datelist[-1].year, datelist[-1].month, 1)
    print(curr_month, last_month)
    
    charging_df = pd.DataFrame()
    discharging_df = pd.DataFrame()

    charging_df["Hour"] = np.arange(1, 25)
    discharging_df["Hour"] = np.arange(1, 25)



    while(curr_month <= last_month):

        monthname = curr_month.strftime("%b %Y")
        print(f"Month is: {monthname}")
        month_hourly_charging = [report.charging_mwh for report in reportlist if report.date.year == curr_month.year and report.date.month == curr_month.month and report.valid_data]
        month_hourly_discharging = [report.discharging_mwh for report in reportlist if report.date.year == curr_month.year and report.date.month == curr_month.month and report.valid_data]
        
        array_charging = np.array(month_hourly_charging)
        average_charging = np.average(array_charging, axis = 0)
        charging_df[monthname] = average_charging

        array_discharging = np.array(month_hourly_discharging)
        average_discharging = np.average(array_discharging, axis = 0)
        discharging_df[monthname] = average_discharging

        print(round(sum(average_charging), 1), 
              round(sum(average_discharging), 1), 
              round(100 * sum(average_discharging) / sum(average_charging), 1), 
              "\n")
        curr_month = curr_month + relativedelta(months = 1)

    pd.set_option('display.float_format', '{:.1f}'.format)    
    print(charging_df)
    print()
    print(discharging_df)
        

        #print(report_data.date, report_data.total_charge, report_data.total_discharge)