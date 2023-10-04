import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

class ReactorStatus:

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
            

            print(df.columns)
            print(df[["Unit", "Power", "Down"]])

            df.reset_index(inplace = True)
            df.set_index("Unit", inplace = True)
            print(df.index.name)

            print(df.loc[["Farley 1", "Farley 2", "Hatch 1", "Hatch 2", "Vogtle 1", "Vogtle 2", "Vogtle 3"],["Power", "Reason or Comment"]])


if "__main__" == __name__:
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    d = datetime.now()
    rs = ReactorStatus(datetime(d.year, d.month - 2, d.day, 0, 0, 0))




        

