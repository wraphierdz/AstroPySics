from flask import Flask, request, render_template
from skyfield.api import Topos, load
import numpy as np
import requests

app = Flask(__name__)

# IP ESP32 untuk komunikasi HTTP
ESP32_SERVER_URL = "http://192.168.1.15/servo"

def degDecimal(deg, arcmin, arcsec):
    return deg + (arcmin / 60) + (arcsec / 3600)

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
    eph = load('de421.bsp')
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

def eq_altz(lat, dec, ra, ha, decimal=False):
    lat = np.radians(lat)
    dec = np.radians(dec)
    ha = np.radians(ha)
    ra = np.radians(ra)

    alt = np.asin((np.sin(dec) * np.sin(lat)) + (np.cos(dec) * np.cos(lat) * np.cos(ha)))
    # az = np.asin(np.sin(ha) * np.cos(dec) / np.cos(ra))
    az = np.atan2(-np.cos(dec) * np.sin(ha), np.sin(dec) - np.sin(lat) * np.sin(alt))
    az = (np.degrees(az) + 360) % 360

    if decimal == False:
        return celesCoor(np.degrees(alt)), celesCoor(az)
    return np.degrees(alt), az

def sendCoordinate(alt, az):
    """Mengirim data Altitude dan Azimuth ke ESP32"""
    try:
        response = requests.post(ESP32_SERVER_URL, json={"altitude": alt, "azimuth": az})
        return response.status_code == 200
    except Exception as e:
        print(f"Error mengirim data ke ESP32: {e}")
        return False

@app.route("/")
def index():
    """Halaman input HTML"""
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    """Menerima input, hitung koordinat, dan kirim ke ESP32"""
    # Ambil data input dari form
    target = request.form["target"].lower()
    latDeg = int(request.form["latDeg"])
    latMin = int(request.form["latMin"])
    latSec = float(request.form["latSec"])
    latDir = request.form["latDir"]
    longDeg = int(request.form["longDeg"])
    longMin = int(request.form["longMin"])
    longSec = float(request.form["longSec"])
    longDir = request.form["longDir"]
    observeTime = request.form["observeTime"]
    
    # Konversi latitude dan longitude ke desimal
    latitude = degDecimal(latDeg, latMin, latSec)
    longitude = degDecimal(longDeg, longMin, longSec)
    
    if latDir == "S":
        latitude = -latitude
    if longDir == "W":
        longitude = -longitude

    # Time input
    date, time = observeTime.split('T')
    yr, mon, d = map(int, date.split('-'))
    h, mins = map(int, time.split(':'))
    h -= longitude//15 # convert ke utc

    ts = load.timescale()
    t = ts.utc(yr, mon, d, h, mins)
    lst = (t.gast + longitude / 15) % 24

    x, y, z, r = vectorFrom(target, latitude, longitude, t)
    ra, dec = vec_eq(x, y, z, r, decimal=True)
    ha = HA(lst, ra)
    alt, az = eq_altz(latitude, dec, ra, ha, decimal=True)
    
    # Kirim koordinat ke ESP32
    if sendCoordinate(alt, az):
        return f"<h1>Data berhasil dikirim ke ESP32! Altitude: {alt}°, Azimuth: {az}°</h1>"
    else:
        return "<h1>Gagal mengirim data ke ESP32</h1>"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
