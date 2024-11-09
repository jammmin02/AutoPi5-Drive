import RPi.GPIO as GPIO
import time

# 핀 번호 설정
IN1 = 17
IN2 = 27
ENA = 18

# GPIO 핀 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# PWM 설정
pwm = GPIO.PWM(ENA, 100)  # ENA 핀에 대해 100Hz 주파수로 PWM 설정
pwm.start(0)  # 처음에는 속도를 0으로 설정

def motor_forward(speed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(speed)

def motor_backward(speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm.ChangeDutyCycle(speed)

def motor_stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        # 앞으로 회전, 속도 75%
        print("모터 앞으로 회전")
        motor_forward(75)
        time.sleep(5)

        # 뒤로 회전, 속도 50%
        print("모터 뒤로 회전")
        motor_backward(50)
        time.sleep(5)

        # 정지
        print("모터 정지")
        motor_stop()
        time.sleep(2)

except KeyboardInterrupt:
    print("프로그램 종료")

finally:
    pwm.stop()
    GPIO.cleanup()                                                                          