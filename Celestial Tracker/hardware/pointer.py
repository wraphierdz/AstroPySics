import network
import urequests
import time
from machine import Pin, PWM
import ujson

ssid = 'Playmedia'
password = '160527SF'

azPin = Pin(4, Pin.OUT)
altPin1 = Pin(12, Pin.OUT)
altPin2 = Pin(13, Pin.OUT)

azServo = PWM(azPin, freq=50)
altServo1 = PWM(altPin1, freq=50)
altServo2 = PWM(altPin2, freq=50)

def connectWifi():
    print('Connecting to WiFi...')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)
        print('.')
    print('Connected to WiFi')
    print('IP Adddress:', wlan.ifconfig()[0])

def testConnection():
    url = "http://192.168.1.10:5000/"
    try:
        response = urequests.get(url)
        print('Server reachable:', response.status_code)
    except Exception as ex:
        print('Connection error:', ex)

def getAltz():
    url = r"http://192.168.1.10:5000/getAltz?target=moon&latDeg=7&latMin=16&latSec=11&latDir=S&longDeg=112&longMin=46&longSec=57&longDir=E&observeTime=2024-12-15T18:00"
    try:
        response = urequests.get(url)
        if response.status_code == 200:
            data = response.json()
            print('received data:', data)

            if 'az' in data and 'alt' in data:
                return data['az'], data['alt']
            else:
                print('Required keys not found in the data')
                return None
        else:
            print('failed to get data, status code:', response.status_code)
            return None
    except Exception as ex:
        print('Error:', ex)
        return None

def Yservo(y):
    if y > 0:
        servo = abs(y - 90 )
    else:
        servo = 90 - y
    return servo

def moveServo(x, y):
    xPos = round( 30 + ((x % 180) / 180) * 93)
    yPos = round( 30 + ((Yservo(y)) / 180) * 93)

    azServo.duty(xPos)
    altServo1.duty(yPos)
    altServo2.duty(yPos)
    print('Az move to:', x)
    print('Alt move to:', y)
    print('servo rotation:', x%180)

def main():
    connectWifi()
    testConnection()
    moveServo(0,0)

    while True:
        data = getAltz()

        if data:
            try:
                azimuth, altitude = data
                moveServo(azimuth, altitude)
            except Exception as ex:
                print('Error parsing data:', ex)
        
        time.sleep(2.5)

main()
