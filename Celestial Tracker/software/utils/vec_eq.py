import numpy as np
import celesCoor

def vec_eq(x, y, z, r, decimal=False):
    """Converts x, y, z, r target vector from observer position
    to equatorial coordinate system (Right Acension α, Declination δ)"""

    # Format desimal
    dec = np.degrees(np.asin(z/r))      # sin δ = z/r
    ra = np.degrees(np.atan2(y, x))     # tan α = y/x
    # Make sure RA di range 0 - 360°
    if ra < 0:
        ra += 360
    # Format celestial coordinate
    if decimal == False:
        return celesCoor(dec), celesCoor(ra, hour=True)
    return ra, dec