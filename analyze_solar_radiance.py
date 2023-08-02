
import pandas as pd


def readRadiance(path: str):
    df = pd.read_csv(path, skiprows = [0, 1])
    names = df.columns.tolist()
    cols_to_drop = [col for col in names if "Unnamed" in col]
 #   df = df.drop(columns = cols_to_drop)
 #   df = df[df["Solar Zenith Angle"] < 93].reset_index(drop = True)
    print(df.head)



if "__main__" == __name__:
    path = "post8/vegas_solar_data_2021.csv"
    readRadiance(path)
