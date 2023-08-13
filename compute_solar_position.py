
import pandas as pd
from datetime import datetime
import math

def solar_position(lat, long, dt, timezone = -8):
    start_of_year = datetime(dt.year, 1, 1)
    delta = dt - start_of_year
    nth_day = delta.days + 1
    portion_of_day = delta.seconds / (24*60*60)

    yearfrac = 2*math.pi / 365 * (nth_day - 1 + portion_of_day)

    eqtime = 229.18*(0.000075 + 0.001868 * math.cos(yearfrac) - 0.032077 * math.sin(yearfrac) - 0.014615 * math.cos(2*yearfrac) - 0.040849 * math.sin(2 * yearfrac))
    declrad = 0.006918 - 0.399912*math.cos(yearfrac) + 0.070257*math.sin(yearfrac) - 0.006758*math.cos(2*yearfrac) + 0.000907 * math.sin(2*yearfrac) - 0.002697*math.cos(3*yearfrac) + 0.00148 * math.sin(3*yearfrac)

    time_offset = eqtime + 4*long - 60*timezone

    tst = dt.hour*60 + dt.minute + dt.second/60 + time_offset

    ha = (tst / 4) - 180

    harad = ha * math.pi / 180
    latrad = lat * math.pi / 180

    cos_zen = math.sin(latrad) * math.sin(declrad) + math.cos(latrad) * math.cos(declrad) * math.cos(harad)
    zenrad = math.acos(cos_zen)
    thetadeg = 90 - zenrad * 180 / math.pi

    cos_pi_minus_phi = -(math.sin(latrad) * math.cos(zenrad) - math.sin(declrad)) / (math.cos(latrad) * math.sin(zenrad))
    phideg = 180 / math.pi * math.acos(cos_pi_minus_phi)
    if harad > 0:
        phideg = 360 - phideg

    return thetadeg, phideg

if "__main__" == __name__:
    lat = 36.17
    long = -115.14

    for h in range(5, 20):
        dt = datetime(2023, 8, 13, h, 0, 0)
        theta, phi = solar_position(lat, long, dt)
        dt_disp = datetime(2023, 8, 13, h+1, 0, 0)
        print(f"{dt_disp}, azimuth {phi:.1f}, elevation {theta:.1f}")













                     