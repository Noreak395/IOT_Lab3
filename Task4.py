import network
import time
import machine
import urequests as requests
from machine import Pin, PWM
import tm1637


# ---------- CONFIG ----------
WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "tYy5VczK725AYic4ybnWvvNwPAxoca6_"
BLYNK_API   = "http://blynk.cloud/external/api"


# ---------- PINS ----------
IR_PIN = 12
SERVO_PIN = 15

TM_CLK = 17
TM_DIO = 16


# ---------- HARDWARE ----------
ir = Pin(IR_PIN, Pin.IN)

servo = PWM(Pin(SERVO_PIN), freq=50)

tm = tm1637.TM1637(
    clk_pin=Pin(TM_CLK),
    dio_pin=Pin(TM_DIO),
    brightness=5
)


# ---------- SERVO FUNCTION ----------
def set_servo_angle(angle):

    angle = max(0, min(180, angle))

    min_duty = 26
    max_duty = 128

    duty = int(
        min_duty +
        (angle / 180) * (max_duty - min_duty)
    )

    servo.duty(duty)


# ---------- BLYNK FUNCTION ----------
def send_count(count):

    url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&V2={count}"

    try:
        r = requests.get(url)
        r.close()

        print("Blynk count:", count)

    except Exception as e:
        print("Blynk error:", e)


# ---------- WIFI ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")

while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected!")
print("IP address:", wifi.ifconfig()[0])


# ---------- INITIAL SETUP ----------

# Gate starts closed
set_servo_angle(0)

# Counter starts at 0
count = 0

# Show 0 on TM1637
tm.show_number(count)

# Send 0 to Blynk
send_count(count)

print("IR + Servo + TM1637 + Blynk started")


# ---------- MAIN LOOP ----------
while True:

    value = ir.value()

    # ---------- NEW OBJECT DETECTED ----------
    if value == 0:

        # Increase counter ONCE
        count += 1

        print("New object detected!")
        print("Detection count:", count)

        # Update TM1637
        tm.show_number(count)

        # Update Blynk
        send_count(count)

        # Open gate
        set_servo_angle(90)
        print("Gate opened")

        # Keep gate open for 3 seconds
        time.sleep(3)

        # Close gate
        set_servo_angle(0)
        print("Gate closed")

        # ---------- WAIT FOR OBJECT TO LEAVE ----------
        while ir.value() == 0:
            time.sleep(1)

        print("Object left")
        print("Ready for next detection")

    else:

        time.sleep(1)