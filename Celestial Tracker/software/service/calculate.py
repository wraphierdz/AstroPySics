from flask import request
from skyfield.api import load
from utils import degDecimal, celesCoor, vectorFrom, vec_eq, HA, eq_altz


def calculate():
    # Target input
    target = (request.form['target']).lower()

    # Location input
    loc = ['latDeg', 'latMin', 'latSec', 'latDir', 'longDeg', 'longMin', 'longSec', 'longDir']
    lats = [request.form.get(i) for i in loc[:4]]
    longs = [request.form.get(i) for i in loc[4:]]

    latDeg, latMin, latSec = map(float, lats[:-1])
    longDeg, longMin, longSec = map(float, longs[:-1])
    latDir, longDir = lats[-1], longs[-1]

    latitude = degDecimal(latDeg, latMin, latSec)
    longitude = degDecimal(longDeg, longMin, longSec)

    if latDir == "S":
        latitude = -latitude
    if longDir == "W":
        longitude = -longitude

    # Time input
    observeTime = request.form.get("observeTime")
    date, time = observeTime.split('T')
    yr, mon, d = map(int, date.split('-'))
    h, mins = map(int, time.split(':'))
    h -= longitude//15 # convert ke utc

    # Let's calculate
    try:
        ts = load.timescale()
        t = ts.utc(yr, mon, d, h, mins)
        lst = (t.gast + longitude / 15) % 24

        x, y, z, r = vectorFrom(target, latitude, longitude, t)
        ra, dec = vec_eq(x, y, z, r, decimal=True)
        ha = HA(lst, ra)
        alt, az = eq_altz(latitude, dec, ra, ha)

        result = {
            'Target': target,
            'Latitude': celesCoor(latitude),
            'Longitude': celesCoor(longitude),
            'Time': (t.utc_datetime()).strftime('%d-%m-%Y %H-%M-%S'),
            'RA': celesCoor(ra, hour=True),
            'Dec': celesCoor(dec),
            'Altitude': alt,
            'Azimuth': az
        }
    except Exception as ex:
        result = {'Error':str(ex)}