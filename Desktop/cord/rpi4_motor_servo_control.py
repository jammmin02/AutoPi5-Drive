import RPi.GPIO as GPIO
import time
from pynput import keyboard

# GPIO 핀 설정
SERVO_PIN = 12  # 서보모터 핀 번호
IN1 = 17        # DC 모터 IN1 핀 번호
IN2 = 27        # DC 모터 IN2 핀 번호
ENA = 18        # DC 모터 ENA 핀 번호

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)  # BCM 핀 번호 사용
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# PWM 설정
servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 서보모터: 50Hz PWM
dc_motor_pwm = GPIO.PWM(ENA, 100)   # DC 모터: 100Hz PWM

# PWM 시작
servo_pwm.start(0)
dc_motor_pwm.start(0)

# 초기값 설정
current_angle = 90  # 서보모터 기본 각도
current_speed = 0   # DC 모터 기본 속도

# 서보모터 각도 설정 함수
def set_servo_angle(angle):
    """
    서보모터의 각도를 설정합니다.
    :param angle: 0~180도 사이의 각도 값
    """
    duty = 2 + (angle / 18)  # 각도 -> 듀티 사이클 변환
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)
    servo_pwm.ChangeDutyCycle(0)  # 과열 방지를 위해 PWM 신호 차단

# DC 모터 전진 함수
def motor_forward():
    """
    DC 모터를 전진시킵니다. 속도는 5%씩 증가합니다.
    """
    global current_speed
    if current_speed < 100:  # 최대 속도 제한
        current_speed += 5
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"전진: 속도 {current_speed}%")

# DC 모터 속도 감소 함수
def motor_slow_down():
    """
    DC 모터의 속도를 감소시킵니다. 속도는 5%씩 감소합니다.
    """
    global current_speed
    if current_speed > 0:  # 최소 속도 제한
        current_speed -= 5
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"속도 감소: 속도 {current_speed}%")

# 모터 정지 함수
def motor_stop():
    """
    DC 모터를 정지합니다.
    """
    global current_speed
    current_speed = 0
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(0)
    print("모터 정지")

# 초기 서보모터 각도 설정
set_servo_angle(current_angle)

# 각도 변화량 설정
ANGLE_INCREMENT = 5  # 서보모터 각도 변화량 (단위: 도)

# 키 입력 처리 함수
def on_press(key):
    """
    키 입력을 처리합니다.
    """
    global current_angle
    try:
        if key == keyboard.Key.up:  # 위쪽 방향키: DC 모터 전진
            motor_forward()
        elif key == keyboard.Key.down:  # 아래쪽 방향키: DC 모터 속도 감소
            motor_slow_down()
        elif key == keyboard.Key.left:  # 왼쪽 방향키: 서보모터 왼쪽 회전
            current_angle = max(0, current_angle - ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"서보모터 왼쪽 회전: 각도 {current_angle}도")
        elif key == keyboard.Key.right:  # 오른쪽 방향키: 서보모터 오른쪽 회전
            current_angle = min(180, current_angle + ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"서보모터 오른쪽 회전: 각도 {current_angle}도")
        elif key == keyboard.Key.space:  # Space 키: 모터 정지
            motor_stop()
    except AttributeError:
        pass

def on_release(key):
    """
    키가 릴리즈될 때 호출됩니다. ESC 키로 종료합니다.
    """
    if key == keyboard.Key.esc:
        print("프로그램을 종료합니다.")
        return False

# 키보드 리스너 시작
print("키 입력을 기다리는 중입니다...")
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# 메인 루프
try:
    listener.join()  # 키보드 리스너가 종료될 때까지 대기
except KeyboardInterrupt:
    pass
finally:
    # 프로그램 종료 시 GPIO 핀 초기화
    servo_pwm.stop()
    dc_motor_pwm.stop()
    GPIO.cleanup()
    print("프로그램을 종료합니다.")