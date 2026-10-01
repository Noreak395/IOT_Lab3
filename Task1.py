import network
import time
import machine
import urequests as requests

# ---------- CONFIG ----------
WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "tYy5VczK725AYic4ybnWvvNwPAxoca6_"
BLYNK_API   = "http://blynk.cloud/external/api"

IR_PIN = 12

# ---------- HARDWARE ----------
ir = machine.Pin(IR_PIN, machine.Pin.IN)

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
def send_ir_status(status):
    url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&V0={status}"

    try:
        r = requests.get(url)
        r.close()
    except Exception as e:
        print("Blynk error:", e)


# ---------- MAIN ----------
print("Running IR sensor control...")

while True:

    value = ir.value()

    if value == 0:
        print("Obstacle detected")

        # Send 0 to Blynk when obstacle is detected
        send_ir_status(0)

    else:
        print("No obstacle")

        # Send 1 to Blynk when no obstacle
        send_ir_status(1)

    time.sleep(1)