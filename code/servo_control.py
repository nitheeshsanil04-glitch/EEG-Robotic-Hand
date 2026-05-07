import RPi.GPIO as GPIO
import time

SERVO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

def move_servo(angle):
    duty = 2 + (angle / 18)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.5)

try:
    while True:
        move_servo(0)
        time.sleep(1)

        move_servo(90)
        time.sleep(1)

except KeyboardInterrupt:
    servo.stop()
    GPIO.cleanup()
