import plotly.express as px
import pandas as pd
from enum import Enum



# reds, blues    
class StateMap:

    def map_states(df: pd.DataFrame, locationColumn: str, quantityColumn: str, colorscale: str, filepath: str):
        fig = px.choropleth(df,
                            locations = locationColumn,
                            locationmode = 'USA-states',
                            scope = 'usa',
                            color = quantityColumn,
                            color_continuous_scale = colorscale
                            )

        fig.write_image(filepath, width = 000, height = 500, scale = 5)
#        fig.show()

                    
