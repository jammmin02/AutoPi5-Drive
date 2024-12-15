import cv2
import numpy as np
from tensorflow.keras.models import load_model
import RPi.GPIO as GPIO
import time

# === GPIO 설정 ===
SERVO_PIN = 12  # 서보모터 핀 번호
IN1 = 17        # DC 모터 IN1 핀 번호
IN2 = 27        # DC 모터 IN2 핀 번호
ENA = 18        # DC 모터 ENA 핀 번호

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)
dc_motor_pwm = GPIO.PWM(ENA, 100)
servo_pwm.start(0)
dc_motor_pwm.start(0)

# === 서보모터 및 DC 모터 제어 함수 ===
current_angle = 30  # 초기 서보모터 각도 (직진)
ANGLE_INCREMENT = 15  # 좌우 회전 각도
SPEED = 20  # 모터 속도 (20으로 설정)

def set_servo_angle(angle):
    """서보모터 각도 설정"""
    duty = 2 + (angle / 18)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)
    servo_pwm.ChangeDutyCycle(0)

def motor_forward(speed=SPEED):
    """DC 모터 전진"""
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(speed)

def motor_stop():
    """DC 모터 정지"""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(0)

# === 모델 및 전처리 ===
model = load_model("/home/pi/AL_CAR/lane_following_model.h5")
print("모델 로드 완료!")

def preprocess_frame(frame):
    """카메라 프레임을 모델 입력 크기로 전처리"""
    frame = cv2.resize(frame, (64, 64))
    frame = frame / 255.0  # 정규화
    return np.expand_dims(frame, axis=0)

# === 카메라 설정 ===
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break

        # 프레임 전처리
        processed_frame = preprocess_frame(frame)

        # 모델 예측
        predictions = model.predict(processed_frame)
        direction = np.argmax(predictions)  # 0: left, 1: straight, 2: right

        # 방향 제어
        if direction == 0:  # 좌회전
            current_angle = max(0, current_angle - ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"좌회전: 각도 {current_angle}도")
            motor_forward()

        elif direction == 1:  # 직진
            current_angle = 30  # 기본 직진 각도
            set_servo_angle(current_angle)
            print(f"직진: 각도 {current_angle}도")
            motor_forward()

        elif direction == 2:  # 우회전
            current_angle = min(60, current_angle + ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"우회전: 각도 {current_angle}도")
            motor_forward()

        # 종료 조건 (q 키를 누르면 정지)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("종료 키 입력됨. 프로그램 종료 중...")
            break

finally:
    # 리소스 정리
    print("모터 정지 및 GPIO 정리...")
    motor_stop()
    cap.release()
    cv2.destroyAllWindows()
    servo_pwm.stop()
    dc_motor_pwm.stop()
    GPIO.cleanup()
    print("프로그램 종료")
