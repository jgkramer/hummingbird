import numpy as np
import pandas as pd

SEASONS_PATH = "data/season_definitions.csv"

class SeasonsData:

    def __init__(self):
        self.table = pd.read_csv(SEASONS_PATH)

    def states_list(self):
        return np.unique(self.table["State"])

    def seasons_for_state(self, state: str):
        return np.unique((self.table[self.table["State"]==state])["Season"])

    def season_begin(self, state: str, season: str) :
        filter = (self.table["State"]==state) & (self.table["Season"]==season)
        begin = np.unique((self.table[filter])["Season_Begin"])
        if(len(begin) > 0):
            return begin[0]
        else:
            return None

    def season_end(self, state: str, season: str) -> str:
        filter = (self.table["State"]==state) & (self.table["Season"]==season)
        end = np.unique((self.table[filter])["Season_End"])
        if(len(end) > 0):
            return end[0]
        else:
            return None



if __name__ == "__main__":
    sd = SeasonsData()
    seasons = sd.seasons_for_state("CT")
    for season in seasons:
        print(season)
        print(sd.season_begin("CT", season))
        print(sd.season_end("CT", season))

                                                
        

