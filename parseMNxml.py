import xml.etree.ElementTree as ET
from datetime import datetime

import pandas as pd

path = "./usage_data/lindahl.xml"

tree = ET.parse(path)
root = tree.getroot()

print(root)
                            
results = root.findall(".//{*}IntervalReading")

cost = []
duration = []
starttime = []
usage = []

for result in results:
    cost.append(float(result[0].text))
    duration.append((int(result[1][0].text)))
    epoch = int(result[1][1].text)
    starttime.append(datetime.fromtimestamp(epoch))
    usage.append(result[2].text)


DF = pd.DataFrame(list(zip(cost, duration, starttime, usage)),
                  columns = ["Cost", "Duration", "Start Time", "Usage"])

pd.set_option('display.max_rows', None)
print(DF)
                     

DF.to_csv("lindahl.csv")

    
