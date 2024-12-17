import ujson
from machine import Pin, PWM
import network
import socket
import time

# connect to wifi
ssid = "Playmedia"
password = "160527SF"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Connecting to Wi-Fi...")
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
print("Connected to Wi-Fi")
print("IP address:", wlan.ifconfig()[0])

# socket server
s = socket.socket()
s.bind(('', 80))
s.listen(5)

# servo
Xpin = Pin(4, Pin.OUT)
y1pin = Pin(12, Pin.OUT)
y2pin = Pin(13, Pin.OUT)

Xservo = PWM(Xpin, freq=50)
y1servo = PWM(y1pin, freq=50)
y2servo = PWM(y2pin, freq=50)

def moveServo(axis, angle):
    if axis == 'x':
        angle = 360 - angle if angle > 180 else 180 - angle
        xPos = round( 30 + (angle / 180) * 93)
        Xservo.duty(xPos)
        print('Az move to:', angle)

    elif axis == 'y':
        angle = abs(angle - 90) if angle > 0 else 90 - angle
        yPos = round( 30 + (angle / 180) * 93)
        y1servo.duty(yPos)
        y2servo.duty(yPos)
        print('Alt move to:', angle)

    print('servo rotation:', angle % 180)

while True:
    cl, addr = s.accept()
    print("Client connected from", addr)
    request = str(cl.recv(1024))
    print("Request:", request)

    if "POST" in request:
        _, body = request.split('\r\n\r\n', 1)
        data = ujson.loads(body)

        alt = data.get('altitude', 0)
        az = data.get('azimuth', 0)

        moveServo('x', az)
        moveServo('y', alt)

        response = 'HTTP/1.1 200 OK\n\nData received!'
        cl.send(response)
    else:
        # 404 Not Found
        response = "HTTP/1.1 404 Not Found\n\nRoute Not Found"
        cl.send(response)
    
    cl.close()
    time.delay(1)

