import machine
import time

# ---------- PINS ----------
IR_PIN = 12
SERVO_PIN = 13

# ---------- HARDWARE ----------
ir = machine.Pin(IR_PIN, machine.Pin.IN)

servo = machine.PWM(machine.Pin(SERVO_PIN), freq=50)


# ---------- SERVO FUNCTION ----------
def set_servo_angle(angle):

    # Limit angle between 0 and 180
    angle = max(0, min(180, angle))

    min_duty = 26
    max_duty = 128

    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))

    servo.duty(duty)


# ---------- INITIAL POSITION ----------
# Gate starts closed
set_servo_angle(0)

print("IR + Servo Gate System Started")


# ---------- MAIN ----------
while True:

    value = ir.value()

    # Object detected
    if value == 0:

        print("Object detected!")

        # Open gate
        set_servo_angle(90)
        print("Gate opened")

        # Keep gate open for 3 seconds
        time.sleep(3)

        # Close gate
        set_servo_angle(0)
        print("Gate closed")

        # Wait until object leaves
        while ir.value() == 0:
            time.sleep(1)

        print("Object left - ready for new detection")

    else:
        # No object
        time.sleep(1)