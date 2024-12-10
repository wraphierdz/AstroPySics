from skyfield.api import Topos, load
import numpy as np

def vectorFrom(object, lat, long, time):
    """Convert solar barycentric vector of the object target to 
    observer-centered vector, 3 positional vector and 1 distance vector (x, y, z, r)
    in AU (Astronomical Unit)"""

    eph = load('de440.bsp')
    earth = eph['earth']
    surfaceLoc = Topos(latitude=lat, longitude=long)                    # posisi observer (lat, long, elevation)

    observerPos = earth + surfaceLoc                                    # vektor observer -> earth barycenter (x, y, z)
    targetPos = observerPos.at(time).observe(eph[object]).apparent()    # posisi target terhadap observer di permukaan
    
    x, y, z = targetPos.position.au                                     # satuan AU diitung dari permukaan bumi
    r = np.sqrt(x**2 + y**2 + z**2)                                     # panjang vektor (jarak)
    return x, y, z, r