import network
import time
import machine
import urequests as requests

# ---------- CONFIG ----------
WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "tYy5VczK725AYic4ybnWvvNwPAxoca6_"
BLYNK_API   = "http://blynk.cloud/external/api"

SERVO_PIN = 13

# ---------- SERVO ----------
servo = machine.PWM(machine.Pin(SERVO_PIN), freq=50)


def set_servo_angle(angle):
    # Limit angle between 0 and 180
    angle = max(0, min(180, angle))

    # Convert angle to duty cycle
    min_duty = 26
    max_duty = 128

    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))

    servo.duty(duty)

    print("Servo angle:", angle)


# ---------- WIFI ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")

while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected!")
print("IP address:", wifi.ifconfig()[0])


# ---------- BLYNK ----------
def read_slider():
    url = f"{BLYNK_API}/get?token={BLYNK_TOKEN}&V1"

    try:
        r = requests.get(url)

        value = int(str(r.text).strip('[]"{}'))

        r.close()

        return value

    except Exception as e:
        print("Blynk error:", e)
        return None


# ---------- MAIN ----------
print("Running servo control...")

while True:

    angle = read_slider()

    if angle is not None:
        set_servo_angle(angle)

    time.sleep(1)