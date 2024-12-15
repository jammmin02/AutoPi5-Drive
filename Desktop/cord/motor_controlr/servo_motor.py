import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
from pynput import keyboard

# I2라C 설정
i2c = busio.I2C(SCL, SDA)

# PCA9685 초기화
pca = PCA9685(i2c)
pca.frequency = 50


# 서보모터 채널 설정 (예: 채널 0)
servo_channel = pca.channels[0]

# 서보모터 각도 계산 함수 (0도에서 180도 사이)
def set_servo_angle(channel, angle):
    # 각도를 PWM 신호로 변환
    min_pulse = 1638    # 0도에 해당하는 최소 펄스
    max_pulse = 8192    # 180도에 해당하는 최대 펄스
    pulse = int(min_pulse + (angle / 180.0) * (max_pulse - min_pulse))
    channel.duty_cycle = pulse

# 초기 각도 설정 (90도)
current_angle = 90
set_servo_angle(servo_channel, current_angle)

# 각도 변화량 설정
ANGLE_INCREMENT = 5

# 키보드 입력 처리 함수
def on_press(key):
    global current_angle
    try:
        if key == keyboard.Key.left:
            # 왼쪽 방향키를 눌렀을 때 각도 감소
            current_angle = max(0, current_angle - ANGLE_INCREMENT)
            set_servo_angle(servo_channel, current_angle)
            print(f"왼쪽: 각도 {current_angle}도")
        elif key == keyboard.Key.right:
            # 오른쪽 방향키를 눌렀을 때 각도 증가
            current_angle = min(180, current_angle + ANGLE_INCREMENT)
            set_servo_angle(servo_channel, current_angle)
            print(f"오른쪽: 각도 {current_angle}도")
    except AttributeError:
        pass

# 키보드 리스너 시작
listener = keyboard.Listener(on_press=on_press)
listener.start()

# 메인 루프 (서보모터 제어)
try:
    while True:
        time.sleep(0.1)  # 루프 대기 (반복 실행 유지)
except KeyboardInterrupt:
    pass
finally:
    # 프로그램 종료 시 PCA9685 정리
    pca.deinit()

