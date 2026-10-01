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


# ==================================================
# PIN CONFIGURATION
# ==================================================

IR_PIN = 12
SERVO_PIN = 13

TM_CLK = 17
TM_DIO = 16


# ==================================================
# HARDWARE
# ==================================================

ir = Pin(IR_PIN, Pin.IN)

servo = PWM(
    Pin(SERVO_PIN),
    freq=50
)

tm = tm1637.TM1637(
    clk_pin=Pin(TM_CLK),
    dio_pin=Pin(TM_DIO),
    brightness=5
)


# ==================================================
# SERVO FUNCTION
# ==================================================

def set_servo_angle(angle):

    # Keep angle between 0 and 180
    angle = max(0, min(180, angle))

    min_duty = 26
    max_duty = 128

    duty = int(
        min_duty +
        (angle / 180) *
        (max_duty - min_duty)
    )

    servo.duty(duty)

    print("Servo angle:", angle)


# ==================================================
# BLYNK - READ MODE
# ==================================================

def read_mode():

    try:

        url = (
            f"{BLYNK_API}/get?"
            f"token={BLYNK_TOKEN}&V3"
        )

        r = requests.get(url)

        value = int(
            str(r.text).strip('[]"{}')
        )

        r.close()

        return value

    except Exception as e:

        print("Mode read error:", e)

        return 0


# ==================================================
# BLYNK - READ MANUAL SLIDER
# ==================================================

def read_slider():

    try:

        url = (
            f"{BLYNK_API}/get?"
            f"token={BLYNK_TOKEN}&V1"
        )

        r = requests.get(url)

        value = int(
            str(r.text).strip('[]"{}')
        )

        r.close()

        return value

    except Exception as e:

        print("Slider read error:", e)

        return None


# ==================================================
# BLYNK - SEND IR STATUS
# ==================================================

def send_ir_status(status):

    try:

        url = (
            f"{BLYNK_API}/update?"
            f"token={BLYNK_TOKEN}&V0={status}"
        )

        r = requests.get(url)
        r.close()

    except Exception as e:

        print("IR status error:", e)


# ==================================================
# BLYNK - SEND DETECTION COUNT
# ==================================================

def send_count(count):

    try:

        url = (
            f"{BLYNK_API}/update?"
            f"token={BLYNK_TOKEN}&V2={count}"
        )

        r = requests.get(url)
        r.close()

        print("Blynk count:", count)

    except Exception as e:

        print("Count error:", e)


# ==================================================
# WIFI
# ==================================================

wifi = network.WLAN(network.STA_IF)

wifi.active(True)

wifi.connect(
    WIFI_SSID,
    WIFI_PASS
)

print("Connecting to WiFi...")

while not wifi.isconnected():

    time.sleep(1)

print("WiFi connected!")

print(
    "IP address:",
    wifi.ifconfig()[0]
)


# ==================================================
# INITIAL SETTINGS
# ==================================================

# Gate starts closed
set_servo_angle(0)

# Detection counter
count = 0

# tm initial count
tm.show_number(count)

# Send initial count to Blynk
send_count(count)

print("System started")


# ==================================================
# MAIN LOOP
# ==================================================

while True:

    mode = read_mode()
    ir_value = ir.value()

    # ==================================================
    # AUTOMATIC MODE
    # ==================================================

    if mode == 1:

        print("Mode: AUTOMATIC")

        # Object detected
        if ir_value == 0:

            print("Object detected!")

            # Increase detection counter
            count += 1

            # Update TM1637
            tm.show_number(count)

            # Update Blynk count
            send_count(count)

            # Update Blynk IR status
            send_ir_status(0)

            # Open gate
            set_servo_angle(90)

            # Keep gate open
            time.sleep(3)

            # Close gate
            set_servo_angle(0)

            print("Gate closed")

            # --------------------------------------
            # Wait until object leaves
            # --------------------------------------

            while ir.value() == 0:

                time.sleep(1)

            print(
                "Object left - ready "
                "for new detection"
            )

            # Update status
            send_ir_status(0)


        else:

            # No object
            send_ir_status(1)

            time.sleep(1)


    # ==================================================
    # MANUAL MODE
    # ==================================================

    else:

        print("Mode: MANUAL")

        # IR only reports status
        if ir_value == 0:

            print("Obstacle detected")

            send_ir_status(0)

        else:

            print("No obstacle")

            send_ir_status(1)


        # ----------------------------------------------
        # Read Blynk slider
        # ----------------------------------------------

        angle = read_slider()

        if angle is not None:

            set_servo_angle(angle)

        time.sleep(1)