from flask import Flask, request, render_template, jsonify
from datetime import datetime
from skyfield.api import Topos, load
import numpy as np
import re

app = Flask(__name__)

def degDecimal(deg, min, sec):
    return (deg + min/60 + sec/3600)

# Format celestial coordinate ke seksagesimal (basis 60)
def celesCoor(decimal, hour=False, pnt=2):
    unit = ['°', "'", '"']
    # convert derajat jadi jam (15° = 1h)
    if hour:
        mainComp_h = decimal/15
        decimal = mainComp_h
        unit = ['h', 'm', 's']
    # seksagesimal derajat:
    mainComp = int(decimal)
    min_float = (decimal-mainComp)*60
    min = int(min_float)
    sec = (min_float - min)*60
    return f'{mainComp}{unit[0]}{min}{unit[1]}{sec:.{pnt}f}{unit[2]}'

# cari vektor bulan (x,y,z,r) terhadap koordinat geografis observer
def vectorFrom(object, lat, long, time):
    # Data efemeris posisi
    eph = load('de440.bsp')
    earth = eph['earth']
    surfaceLoc = Topos(latitude=lat, longitude=long)            # posisi observer (lat, long, elevation)

    observerPos = earth + surfaceLoc                            # vektor observer -> earth barycenter (x, y, z)
    targetPos = observerPos.at(time).observe(eph[object]).apparent()  # posisi target terhadap observer di permukaan
    
    x, y, z = targetPos.position.au                             # satuan AU diitung dari permukaan bumi
    r = np.sqrt(x**2 + y**2 + z**2)                             # panjang vektor (jarak)
    return x, y, z, r

# transform vektor ke equatorial
def vec_eq(x, y, z, r, decimal=False):
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

def HA(lst, ra):
    lst = np.radians(lst*15)
    ra = np.radians(ra)
    ha = np.degrees(lst - ra)
    if ha < 0:
        ha += 360
    return ha

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

def toUTC(t):
    ts = load.timescale
    return ts.utc(t[1], t[2], t[3], t[4], t[5], t[6])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
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

        print('target : ', target, flush=True)
        print('Lat  :', latitude, flush=True)
        print('Long  :', longitude, flush=True)
        print('vector:', x, y, z, r, flush=True)
        print('time  :', t, flush=True)
        print('LST  :', lst, flush=True)
        print('HA  :', ha, flush=True)
        print('RA  :', ra, flush=True)
        print('RA frmt:', result['RA'], flush=True)
        print('Dec  :', dec, flush=True)
        print('Dec frmt :', result['Dec'], flush=True)
        print('Alt  :', alt, flush=True)
        print('Az   :', az, flush=True)
        print('latdeg', latDeg)
        print('longdeg', longDeg)
        print('latdir', latDir)
        print('longdir', longDir)

    except Exception as ex:
        result = {'Error':str(ex)}
        
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
    