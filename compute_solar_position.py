
import pandas as pd
from datetime import datetime
import math

class SolarPosition:

    def __init__(self, lat, long, timezone = -8):
        self.lat = lat
        self.long = long
        self.timezone = timezone

    def solar_position(self, dt: datetime):
        start_of_year = datetime(dt.year, 1, 1)
        delta = dt - start_of_year
        nth_day = delta.days + 1
        portion_of_day = delta.seconds / (24*60*60)

        yearfrac = 2*math.pi / 365 * (nth_day - 1 + portion_of_day)

        eqtime = 229.18*(0.000075 + 0.001868 * math.cos(yearfrac) - 0.032077 * math.sin(yearfrac) - 0.014615 * math.cos(2*yearfrac) - 0.040849 * math.sin(2 * yearfrac))
        declrad = 0.006918 - 0.399912*math.cos(yearfrac) + 0.070257*math.sin(yearfrac) - 0.006758*math.cos(2*yearfrac) + 0.000907 * math.sin(2*yearfrac) - 0.002697*math.cos(3*yearfrac) + 0.00148 * math.sin(3*yearfrac)

        time_offset = eqtime + 4*self.long - 60*self.timezone

        tst = dt.hour*60 + dt.minute + dt.second/60 + time_offset

        ha = (tst / 4) - 180

        harad = ha * math.pi / 180
        latrad = self.lat * math.pi / 180

        cos_zen = math.sin(latrad) * math.sin(declrad) + math.cos(latrad) * math.cos(declrad) * math.cos(harad)
        zenrad = math.acos(cos_zen)
        elev_deg = 90 - zenrad * 180 / math.pi

        cos_pi_minus_azi = -(math.sin(latrad) * math.cos(zenrad) - math.sin(declrad)) / (math.cos(latrad) * math.sin(zenrad))
        azi_deg = 180 / math.pi * math.acos(cos_pi_minus_azi)
        if harad > 0:
            azi_deg = 360 - azi_deg

        return elev_deg, azi_deg
    
    def solar_position_series(self, dt_list):
        L = [(dt, self.solar_position(dt)[0], self.solar_position(dt)[1]) for dt in dt_list]
        return pd.DataFrame(L, columns = ["datetime", "elevation", "azimuth"])

if "__main__" == __name__:

    vegasSolarPosition = SolarPosition(lat = 36.17, long = -115.14, timezone = -8)

    DTL = [datetime(2023, 12, 15, h, 0, 0) for h in range(5, 20)]
    df = vegasSolarPosition.solar_position_series(DTL)
    print(df)



    

