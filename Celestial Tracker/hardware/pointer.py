import machine
import time

# Inisialisasi pin untuk PWM
servo1 = machine.Pin(4, machine.Pin.OUT)
pwm = machine.PWM(servo1)

# Set frekuensi PWM ke 50 Hz
pwm.freq(50)

# while True:
#     pwm.duty(70)
#     time.sleep(1)

# Uji berbagai posisi servo
while True:
    print("Servo ke sudut 0°")
    pwm.duty(30)  # Sesuaikan nilai ini jika servo tidak bergerak
    time.sleep(1)


    print("Servo ke sudut 90°")
    pwm.duty(77)  # Sesuaikan nilai ini jika servo tidak bergerak
    time.sleep(1)

    print("Servo ke sudut 180°")
    pwm.duty(123)  # Sesuaikan nilai ini jika servo tidak bergerak
    time.sleep(1)


# ampy --port COM7 run pointer.py
# esptool --port COM7 erase_flash
# esptool --port COM7 write_flash -z 0x1000 ESP32_GENERIC-20241129-v1.24.1.bin