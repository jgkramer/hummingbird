import numpy as np
import pandas as pd

SEASON_PATH = "data/season_definitions.csv"
TIER_PATH = "data/tier_definitions.csv"
TIMES_PATH = "data/time_of_use_definitions.csv"

def process_hour_ranges(raw_strings: str):
    #from input like "7-11; 20-24", creates a list of strings with hour ranges like "7-11"
    range_strings = raw_strings.replace(" ", "").split(";")
    
    #for each range, create a tuple of the integer values like (7, 11)
    ranges = [tuple([int(rs.split("-")[0]), int(rs.split("-")[1])])
              for rs in range_strings]
    
    #return a list of tuples corresponding to the original input: [(7, 11), (20, 24)]
    return ranges


if __name__ == "main":
    times_table = pd.read_csv(TIMES_PATH)
    print(times_table["Time Segments"])
    times_table["Time Segments"] = times_table["Time Segments"].apply(process_hour_ranges)
    print(times_table["Time Segments"])
