import numpy as np

def HA(lst, ra):
    """Returns Hour Angle, an angle of a celestial object
    measured from meridian to the west at a given LST (Local Siderial Time)
    and RA (Right Ascension). Simply HA = LST - HA"""

    lst = np.radians(lst*15)
    ra = np.radians(ra)
    ha = np.degrees(lst - ra)
    if ha < 0:
        ha += 360
    return ha