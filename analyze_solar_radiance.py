import pandas as pd
from datetime import datetime

def make_datetime(row):
    return datetime(int(row["Year"]), int(row["Month"]), int(row["Day"]))

class SolarRadiance():
    def __init__(self, path: str = "post8/vegas_solar_data_2021.csv"):
        self.path = path

        df = pd.read_csv(path, skiprows = [0, 1])
        names = df.columns.tolist()
        
        #   df = df[df["Solar Zenith Angle"] < 93].reset_index(drop = True)
        
        df["Date"] = df.apply(make_datetime, axis = 1)
        cols_to_drop = [col for col in names if "Unnamed" in col] + ["Year", "Month", "Day", "Clearsky DHI", "Clearsky GHI", "Solar Zenith Angle"]
        df = df.drop(columns = cols_to_drop)
        
        table = df.groupby([df['Date'].dt.month, "Hour", "Minute"])["Clearsky DNI"].mean().reset_index()
        table.columns = ["Month", "Hour", "Minute", "DNI"]
        
        self.table = table

    def getRadiance(self, month, hour, minute):
        value = self.table.loc[(self.table["Month"] == month) & (self.table["Hour"] == hour) & (self.table["Minute"] == minute), "DNI"].values[0]
        return value

if "__main__" == __name__:

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    radiance = SolarRadiance()
    print(radiance.getRadiance(12, 12, 0))



