

import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

import numpy as np

from fetch_rates import RatesData
from fetch_times import TimesData
from rate_series import RateSegment, RateSeries

def format_time(x, _):
    hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
    return hm + ("am" if (x%24)<12 else "pm")

def display_state_charts(state: str, td: TimesData, rd: RatesData):
    fig, ax = plt.subplots(2)
    fig.tight_layout(pad = 3.0)
    summer_axes = ax[0]
    summer_axes.set_title("Summer")

    winter_axes = ax[1]
    winter_axes.set_title("Winter")

    for subplot in ax:
        subplot.set_xlim([0, 24])
        subplot.set_ylim([0, 0.5])
        subplot.yaxis.set_major_formatter(FormatStrFormatter('$%1.2f'))
        subplot.xaxis.set_major_formatter(format_time)
        subplot.xaxis.set_ticks(np.arange(0, 24+1, 4))
        subplot.set_ylabel("$ per kWh")
    
    state_plans = rd.plans_for_state(state)
    for plan in state_plans:
        seasons = rd.seasons_for_plan(state, plan)
        for season in seasons:
            rs = RateSeries(state, season, plan, plan, td, rd) # double plan is weird
            x = rs.start_times()
            x.append(24)
            y = rs.rates()
            y.append(y[0])

            if(season == "Summer" or season == "All"):
                summer_axes.step(x, y, where = "post", label = plan)
                for a,b in zip(x,y):
                    if(a<24): summer_axes.annotate(f" ${b}", (a,b))
                    
            if(season == "Winter" or season == "All"):
                winter_axes.step(x, y, where = "post", label = plan)
                for a,b in zip(x,y):
                    if(a<24): winter_axes.annotate(f" ${b}", (a,b))


    summer_axes.legend(loc = 'upper left')
    winter_axes.legend(loc = 'upper left')
    plt.show()

if __name__ == "__main__":
    rd = RatesData()
    td = TimesData()
    states = ["NV", "CT"]
    for state in states:
        display_state_charts(state, td, rd)





    
            
