import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from typing import List

class DownloadReactorStatus:
    def __init__(self, d: datetime):
        self.date = d
        self.url = f"https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/{d.year}/{d.year}{d.month:02}{d.day:02}ps.html"
        
        response = requests.get(self.url)
        if response.status_code == 200:
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            tables = soup.find_all("table", class_ = "power")
            data = []
            for ix, table in enumerate(tables):
                start = 0 if ix == 0 else 1  # for the first table, grab the header row, for others, skip it
                rows = table.find_all("tr")[start:]
                for row in rows: 
                    cols = row.find_all(["td", "th"])
                    cols = [ele.text.strip() for ele in cols]
                    data.append(cols)

            df = pd.DataFrame(data[1:], columns = data[0]) 
            self.df = df
            self.df.reset_index(inplace = True)
            self.df.set_index("Unit", inplace = True)

        print("Downloaded ", d)

    def check_reactors(self, plants: List[str]):
        return [(p in self.df.index) for p in plants]
    
    def power_dict(self, plants: List[str]):
        powers = {plant: self.df.loc[plant, "Power"] if check else 0 for (plant, check) in zip(plants, self.check_reactors(plants))}
        return powers
                
class DownloadReactorSeries:
    def __init__(self, start: datetime, end: datetime):
        assert(end > start)
        current = start.date()
        self.date_list = []
        while current <= end.date():
            self.date_list.append(current)
            current = current + timedelta(days = 1)

        self.reactor_status_for_dates = [DownloadReactorStatus(d) for d in self.date_list]
    
    def series_for_reactors(self, plants: List[str], path = None):
        powers = {plant: [] for plant in plants}

        for rs in self.reactor_status_for_dates:
            power_dict = rs.power_dict(plants)
            for p in plants: 
                powers[p].append(power_dict[p])
        
        powers["Date"] = self.date_list
        df = pd.DataFrame(powers)
        df.set_index("Date", inplace = True)

        if path is not None:
            df.to_csv(path)

        return df
        
if "__main__" == __name__:
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    d = datetime.now()
    start = datetime(2021, 1, 1)
    end = datetime(d.year, d.month, d.day - 1)
    
    reactorSeries = DownloadReactorSeries(start, end)
    plants = ["Farley 1", "Farley 2", "Hatch 1", "Hatch 2", "Vogtle 1", "Vogtle 2", "Vogtle 3"]

    print(reactorSeries.series_for_reactors(plants, path = "./reactorStatus_21Oct23.csv"))





        

