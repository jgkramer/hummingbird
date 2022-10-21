import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

import numpy as np

from fetch_seasons import SeasonsData, Season
from rate_series import RateSegment, RateSeries, RatePlan
from region import Region

def format_time(x, _):
    hm = "{:d}:{:02d}".format((int(((x-1)%12)+1)), int((x%1)*60))
    return hm + ("am" if (x%24)<12 else "pm")

def display_state_charts(state: str):
    state = Region(state)
    state_seasons = state.get_seasons()
    fig, ax = plt.subplots(len(state_seasons))
    fig.tight_layout(pad = 3.0)

    # subplots returns a list if >1,  but a single item if = 1, so this makes it a list for consistency
    if(len(state_seasons) == 1): ax = [ax]

    # this dictionary will come in handy later, when we have a season NAME, it will tell us which subplot belongs to that name
    seasons_dict = {}
    for i, state_season in enumerate(state_seasons):
        seasons_dict[state_season.name] = i
        ax[i].set_title(state_season.name + " (" + state_season.dates_string() + ")")

    # formatting the plots
    for subplot in ax:
        subplot.set_xlim([0, 24])
        subplot.set_ylim([0, 0.5])
        subplot.yaxis.set_major_formatter(FormatStrFormatter('$%1.2f'))
        subplot.xaxis.set_major_formatter(format_time)
        subplot.xaxis.set_ticks(np.arange(0, 24+1, 4))
        subplot.set_ylabel("$ per kWh")
    
    # go through each plan (i.e., TOU) that the state has
    state_plans = state.get_rate_plans()

    for plan in state_plans:
        if(plan.plan_name != "Fixed" and plan.plan_name != "TOU"):
            continue  #right now we're just doing Fixed and Standard TOU plans. 

        # for each season(series) in the plan:
        rate_series = plan.series()  
        for rs in rate_series:
            x = rs.start_times()
            y = rs.rates()           
            x.append(24) #make sure we have a data point at end of day to finish plot
            y.append(y[0]) # make sure midnight (end of day) matches midnight (start of day) value

            seasons_to_plot = [rs.season.name] if rs.season.name != "All" else [s.name for s in state_seasons]
            subplots = [ax[seasons_dict[s]] for s in seasons_to_plot]
            for subplot in subplots:
                subplot.step(x, y, where = "post", label = plan.plan_name)
                for a,b in zip(x,y):
                    if(a<24): subplot.annotate(f" ${b: 1.3f}", (a,b))
                subplot.legend(loc = 'upper left')

    path = "post1/output_" + state.get_name() + ".png"
    plt.savefig(path)

if __name__ == "__main__":
    states = ["NV", "CT", "MD"]
    for state in states:
        display_state_charts(state)



            
