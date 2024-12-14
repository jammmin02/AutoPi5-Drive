import RPi.GPIO as GPIO
import time
from pynput import keyboard
import cv2
import numpy as np
import subprocess
import shlex
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
SPEED_INCREMENT = 2  # 속도 증가 단위
MAX_SPEED = 100  # DC 모터 최대 속도

# 각도 범위를 5개로 나눔
ANGLE_RANGES = [(0, 36), (37, 72), (73, 108), (109, 144), (145, 180)]
captured_ranges = set()  # 저장된 각도 범위 추적

# 저장 경로 설정
base_save_path = "/home/pi/AL_CAR/images"

# 폴더 생성
for i in range(len(ANGLE_RANGES)):
    folder_path = os.path.join(base_save_path, f"range_{i}")
    os.makedirs(folder_path, exist_ok=True)

def set_servo_angle(angle):
    duty = 2 + (angle / 18)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)
    servo_pwm.ChangeDutyCycle(0)

def motor_forward():
    global current_speed
    if current_speed < MAX_SPEED:
        current_speed += SPEED_INCREMENT
    current_speed = min(current_speed, MAX_SPEED)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"전진: 속도 {current_speed}%")

def motor_slow_down():
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
    global current_speed
    current_speed = 0
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(0)
    print("모터 정지")

set_servo_angle(current_angle)

def get_angle_range(angle):
    for i, (start, end) in enumerate(ANGLE_RANGES):
        if start <= angle <= end:
            return i
    return -1  # 범위에 없으면 -1 반환

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
            current_angle = min(180, current_angle + ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"서보모터 오른쪽 회전: 각도 {current_angle}도")
        elif key == keyboard.Key.space:
            motor_stop()
        elif key.char == '/':
            current_speed = 40
            GPIO.output(IN1, GPIO.HIGH)
            GPIO.output(IN2, GPIO.LOW)
            dc_motor_pwm.ChangeDutyCycle(current_speed)
            print("DC 모터 속도 설정: 40%")
        elif key.char == '.':
            current_speed = 20
            GPIO.output(IN1, GPIO.HIGH)
            GPIO.output(IN2, GPIO.LOW)
            dc_motor_pwm.ChangeDutyCycle(current_speed)
            print("DC 모터 속도 설정: 20%")
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        print("프로그램 종료")
        return False

# === 카메라 설정 ===
cmd = 'libcamera-vid --inline --nopreview -t 0 --codec mjpeg --width 1280 --height 720 --framerate 15 -o - --camera 0'
process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

capture_interval = 2  # 캡처 간격 (2초)
last_capture_time = time.time()

def capture_images():
    global last_capture_time
    buffer = b""
    while len(captured_ranges) < len(ANGLE_RANGES):
        current_time = time.time()
        if current_time - last_capture_time >= capture_interval:
            buffer += process.stdout.read(4096)
            a = buffer.find(b'\xff\xd8')
            b = buffer.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = buffer[a:b+2]
                buffer = buffer[b+2:]
                bgr_frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                if bgr_frame is not None:
                    # 실시간 영상 표시
                    cv2.imshow("Camera View", bgr_frame)

                    # 캡처 조건: 각도가 특정 범위에 속하고 해당 범위가 캡처되지 않은 경우
                    angle_range = get_angle_range(current_angle)
                    if angle_range != -1:
                        range_folder = os.path.join(base_save_path, f"range_{angle_range}")
                        now = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
                        filename = os.path.join(range_folder, f"{now}.jpg")
                        try:
                            if cv2.imwrite(filename, bgr_frame):
                                print(f"이미지 저장 성공: {filename}")
                                captured_ranges.add(angle_range)  # 저장된 범위 추가
                                last_capture_time = current_time  # 마지막 캡처 시간 업데이트
                            else:
                                print(f"이미지 저장 실패: {filename}")
                        except Exception as e:
                            print(f"이미지 저장 중 에러 발생: {e}")
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
    process.terminate()
    cv2.destroyAllWindows()
    servo_pwm.stop()
    dc_motor_pwm.stop()
    GPIO.cleanup()
    print("프로그램 종료")
