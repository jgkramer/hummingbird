import pandas as pd
from datetime import date, datetime, timedelta
from typing import List
from sklearn.linear_model import LinearRegression

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def extract_date(full_string: str):
    date_part = full_string.split(",")[0]
    date_obj = datetime.strptime(date_part, "%m/%d/%Y")
    return date_obj

class EIADemand:
    pass

class EIAGeneration: 
    column_map = {"wind": "Wind Generation (MWh)",
                  "solar": "Solar Generation (MWh)",
                  "hydro": "Hydro Generation (MWh)",
                  "other": "Other Generation (MWh)", 
                  "petroleum": "Petroleum Generation (MWh)",
                  "natural gas": "Natural gas Generation (MWh)",
                  "coal": "Coal Generation (MWh)",
                  "nuclear": "Nuclear Generation (MWh)"}

    def __init__(self, generation_csv_paths: List):
        df_list = []
        for path in generation_csv_paths:
            df_list.append(pd.read_csv(path))
        
        merged_df = pd.concat(df_list, axis = 0)
        merged_df.reset_index(drop = True, inplace = True)
        merged_df['date'] = merged_df["Timestamp (Hour Ending)"].apply(extract_date)
        merged_df.drop(columns=["Timestamp (Hour Ending)"], inplace=True)

        for key, value in EIAGeneration.column_map.items():
            merged_df.rename(columns={value: key}, inplace = True)

        self.df = merged_df
        #print(merged_df.head())

        self.startdate = min(self.df["date"])
        self.enddate = max(self.df["date"])
        print(self.startdate, self.enddate)
       
    def linear_model_by_dates(self, ax, startdate: datetime, enddate: datetime, color: str, fitX: float):
        selected_dates = self.df[self.df["date"].between(startdate, enddate)].copy()
        selected_dates["total"] = selected_dates[["solar", "hydro", "natural gas", "coal", "nuclear"]].sum(axis = 1)
        selected_dates["coal+gas"] = selected_dates[["coal", "natural gas"]].sum(axis = 1)
        
        X = selected_dates[["total"]]/24000
        y = selected_dates["coal+gas"]/24000
        model = LinearRegression().fit(X, y)

        ax.scatter(selected_dates["total"]/24000, y, label = str(startdate.year), s = 10, color = color)

        X_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)  # Generate many points for a smooth line
        y_line = model.predict(X_line)

        prediction = model.predict(np.linspace(fitX, fitX, 1).reshape(-1, 1))[0]

        ax.plot(X_line, y_line, color = color, linestyle = "--")
        ax.legend(loc = "upper left")

        print(f'Coefficients: {model.coef_}')
        print(f'Intercept: {model.intercept_}')
        print(f'R-Squared: {model.score(X, y)}')

        return prediction


    def get_monthly_by_source(self, monthlist: List = None):
        result = self.df.groupby([self.df["date"].apply(lambda d: d.replace(day=1))]).sum().reset_index()
        content_columns = [c for c in result.columns if c != "date"]
        
        result[content_columns] = (result[content_columns]/1e6).round(2) # convert into TWh
        result["total"] = result[content_columns].sum(axis = 1)

        if monthlist is not None:
            result = result[result["date"].dt.month.isin(monthlist)]
        else:
            result = result
        
        #print(result[["date", "wind", "solar", "hydro", "natural gas", "coal", "nuclear", "total"]])
        return result

    def get_total_by_source(self, source: str):
        colsum = self.df[source].sum()
        return colsum

    def stackedbar(self, df, ax, ymax = None, firstplot = True, title = None):
        df = df.copy()
        df["all other"] = df[["wind", "petroleum", "hydro", "other"]].sum(axis = 1)
        df["coal + gas"] = df[["coal", "natural gas"]].sum(axis = 1)
        df = df.drop(columns = ["coal", "natural gas", "wind", "petroleum", "hydro", "other", "total"])
        df = df[["date", "coal + gas", "nuclear", "solar", "all other"]]
        colors = ['sandybrown', 'skyblue', 'yellow', 'lightgray']

        df["date"] = df["date"].dt.strftime("%Y")

        df.set_index('date', inplace=True)
        df = df.sort_index()
        #print(df)
        
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)

        df.index.name = None        
        
        df.plot(kind='bar', stacked=True, ax = ax, color = colors, legend = firstplot)
        ax.set_xlabel(title, fontweight = "bold")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        
        if firstplot: 
            ax.set_ylabel("TWh Generation")
        if not firstplot:
            ax.spines["left"].set_visible(False)
            ax.yaxis.set_visible(False)

        if ymax is not None: 
            ax.set_ylim(0, ymax)

        plt.tight_layout()

        for i, (_, row) in enumerate(df.iterrows()):
            # Coordinates for the labels        
            y_offset = 0
            for col in df.columns:
                value = row[col]
                if col in ['coal + gas', 'nuclear']:
                    # Position the label in the middle of the bar segment
                    ax.text(i, y_offset + value/2, f'{value:.1f}', va='center', ha='center')
                    y_offset += value
        # Label for the total
            total = row.sum()
            ax.text(i, total, f'{total:.1f}', va='bottom', ha='center', fontweight = "bold")
     
if __name__ == "__main__":
    pass




    








        



