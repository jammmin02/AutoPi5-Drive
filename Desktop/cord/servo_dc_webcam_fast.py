import RPi.GPIO as GPIO
import time
from pynput import keyboard
import cv2
import numpy as np
import datetime
import os
import threading

# === GPIO 설정 ===
SERVO_PIN = 12  # 서보모터 핀 번호
IN1 = 17        # DC 모터 IN1 핀 번호
IN2 = 27        # DC 모터 IN2 핀 번호
ENA = 18        # DC 모터 ENA 핀 번호

GPIO.setmode(GPIO.BCM)  # BCM 핀 번호 사용
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 서보모터: 50Hz PWM
dc_motor_pwm = GPIO.PWM(ENA, 100)   # DC 모터: 100Hz PWM

servo_pwm.start(0)
dc_motor_pwm.start(0)

current_angle = 30  # 서보모터 초기 각도
current_speed = 0   # DC 모터 초기 속도

ANGLE_INCREMENT = 5  # 서보모터 각도 변화량
SPEED_INCREMENT = 2   # 속도 증가 단위
MAX_SPEED = 100       # DC 모터 최대 속도

# === 새로운 각도 범위 설정 ===
ANGLE_RANGES = {
    "left": (0, 20),         # 좌회전
    "straight": (21, 40),    # 직진
    "right": (41, 60)        # 우회전
}

# 저장 경로 설정
base_save_path = "/home/pi/AL_CAR/images"

# 폴더 생성
for direction in ANGLE_RANGES.keys():
    folder_path = os.path.join(base_save_path, direction)
    os.makedirs(folder_path, exist_ok=True)

def set_servo_angle(angle):
    """서보모터 각도를 설정합니다."""
    duty = 2 + (angle / 18)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)  # 신호 유지 시간 증가
    servo_pwm.ChangeDutyCycle(0)

def motor_forward():
    """DC 모터 전진."""
    global current_speed
    if current_speed < MAX_SPEED:
        current_speed += SPEED_INCREMENT
    current_speed = min(current_speed, MAX_SPEED)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"전진: 속도 {current_speed}%")

def motor_slow_down():
    """DC 모터 감속."""
    global current_speed
    if current_speed > 0:
        current_speed -= SPEED_INCREMENT
    current_speed = max(current_speed, 0)
    if current_speed == 0:
        motor_stop()
    else:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        dc_motor_pwm.ChangeDutyCycle(current_speed)
        print(f"속도 감소: 속도 {current_speed}%")

def motor_stop():
    """DC 모터 정지."""
    global current_speed
    current_speed = 0
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(0)
    print("모터 정지")

set_servo_angle(current_angle)

def get_direction(angle):
    """현재 각도에 따라 좌회전, 직진, 우회전 반환."""
    for direction, (start, end) in ANGLE_RANGES.items():
        if start <= angle <= end:
            return direction
    return None  # 범위에 없으면 None 반환

def on_press(key):
    global current_angle
    global current_speed
    try:
        if key == keyboard.Key.up:
            motor_forward()
        elif key == keyboard.Key.down:
            motor_slow_down()
        elif key == keyboard.Key.left:
            current_angle = max(0, current_angle - ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"서보모터 왼쪽 회전: 각도 {current_angle}도")
        elif key == keyboard.Key.right:
            current_angle = min(60, current_angle + ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"서보모터 오른쪽 회전: 각도 {current_angle}도")
        elif key == keyboard.Key.space:
            motor_stop()
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        print("프로그램 종료")
        return False

# === 웹캠 캡처 설정 ===
cap = cv2.VideoCapture(0)  # USB 웹캠 연결 (0은 기본 웹캠 ID)
if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

capture_interval = 0.1  # 캡처 간격
burst_capture_count = 3  # 한 번에 저장할 이미지 수
burst_interval = 0.05  # 버스트 캡처 간격

def capture_images():
    global last_capture_time
    last_capture_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            print("웹캠에서 프레임을 읽을 수 없습니다.")
            break

        current_time = time.time()
        if current_time - last_capture_time >= capture_interval:
            direction = get_direction(current_angle)
            if direction:
                range_folder = os.path.join(base_save_path, direction)
                for i in range(burst_capture_count):
                    burst_time = datetime.datetime.now().strftime('%y%m%d_%H%M%S_%f')
                    filename = os.path.join(range_folder, f"{direction}_{burst_time}_burst{i}.jpg")
                    if cv2.imwrite(filename, frame):
                        print(f"이미지 저장 성공 ({direction}): {filename}")
                    else:
                        print(f"이미지 저장 실패: {filename}")
                    time.sleep(burst_interval)
            last_capture_time = current_time
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

# === 프로그램 실행 ===
try:
    threading.Thread(target=capture_images, daemon=True).start()
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    listener.join()
except KeyboardInterrupt:
    pass
finally:
    cap.release()
    cv2.destroyAllWindows()
    servo_pwm.stop()
    dc_motor_pwm.stop()
    GPIO.cleanup()
    print("프로그램 종료")
