import numpy as np
import celesCoor

def eq_altz(lat, dec, ra, ha):
    lat = np.radians(lat)
    dec = np.radians(dec)
    ha = np.radians(ha)
    ra = np.radians(ra)

    alt = np.asin((np.sin(dec) * np.sin(lat)) + (np.cos(dec) * np.cos(lat) * np.cos(ha)))
    # az = np.asin(np.sin(ha) * np.cos(dec) / np.cos(ra))
    az = np.atan2(-np.cos(dec) * np.sin(ha), np.sin(dec) - np.sin(lat) * np.sin(alt))
    az = (np.degrees(az) + 360) % 360

    return celesCoor(np.degrees(alt)), celesCoor(az)