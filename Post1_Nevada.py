

import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

import numpy as np

from fetch_rates import RatesData
from fetch_times import TimesData
from fetch_seasons import SeasonsData
from rate_series import RateSegment, RateSeries

def format_time(x, _):
    hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
    return hm + ("am" if (x%24)<12 else "pm")

def display_state_charts(state: str, td: TimesData, rd: RatesData, sd: SeasonsData):

    state_seasons = list(sd.seasons_for_state(state))
    fig, ax = plt.subplots(len(state_seasons))
    fig.tight_layout(pad = 3.0)

    # subplots returns a list if >1,  but a single item if = 1, so this makes it a list for consistency
    if(len(state_seasons) == 1): ax = [ax]

    # this dictionary will come in handy later, when we have a season NAME, it will tell us which subplot belongs to that name
    seasons_dict = {}
    for i, state_season in enumerate(state_seasons):
        seasons_dict[state_season] = i
        ax[i].set_title(state_season)

    for subplot in ax:
        subplot.set_xlim([0, 24])
        subplot.set_ylim([0, 0.5])
        subplot.yaxis.set_major_formatter(FormatStrFormatter('$%1.2f'))
        subplot.xaxis.set_major_formatter(format_time)
        subplot.xaxis.set_ticks(np.arange(0, 24+1, 4))
        subplot.set_ylabel("$ per kWh")
    
    state_plans = rd.plans_for_state(state)
    for plan in state_plans:
        if(plan == "EV"): continue  #right now we're just doing straight up TOU plans. 
        
        seasons = list(rd.seasons_for_plan(state, plan))
        for season in seasons:
            rs = RateSeries(state, season, plan, plan, td, rd) # double plan is weird
            x = rs.start_times()
            y = rs.rates()
            
            x.append(24) #make sure we have a data point at end of day to finish plot
            y.append(y[0]) # make sure midnight (end of day) matches midnight (start of day) value

            seasons_to_plot = [season] if season != "All" else state_seasons
            for plot_season in seasons_to_plot:
                subplot = ax[seasons_dict[plot_season]]
                subplot.step(x, y, where = "post", label = plan)
                for a,b in zip(x,y):
                    if(a<24): subplot.annotate(f" ${b: 1.3f}", (a,b))
                subplot.legend(loc = 'upper left')

    path = "output_" + state + ".png"
    plt.savefig(path)
    plt.show()

if __name__ == "__main__":
    rd = RatesData()
    td = TimesData()
    sd = SeasonsData()
    states = ["NV", "CT", "MD"]
    for state in states:
        display_state_charts(state, td, rd, sd)





    
            
