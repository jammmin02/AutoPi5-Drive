import cv2
import numpy as np
import subprocess
import shlex
import datetime
import time

# 카메라 스트리밍 명령어 설정
cmd = 'libcamera-vid --inline --nopreview -t 0 --codec mjpeg --width 640 --height 480 --framerate 30 -o - --camera 0'

# 명령어 실행
process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 캡처 간격 및 시간 초기화
capture_interval = 3
last_capture_time = time.time()

# OpenCV 창 설정
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
cv2.resizeWindow('frame', 640, 360)

# 절대 경로 설정
save_path = "/home/jungmin/Desktop/cord/date/"

# 테스트 이미지 저장
test_image = np.zeros((480, 640, 3), dtype=np.uint8)  # 검은색 이미지 생성
if cv2.imwrite(save_path + "test.jpg", test_image):
    print("테스트 이미지 저장 성공")
else:
    print("테스트 이미지 저장 실패")

try:
    buffer = b""
    while True:
        current_time = time.time()

        # 버퍼에 데이터 추가
        buffer += process.stdout.read(4096)
        a = buffer.find(b'\xff\xd8')
        b = buffer.find(b'\xff\xd9')

        # JPEG 이미지가 버퍼에 있으면 디코딩
        if a != -1 and b != -1:
            jpg = buffer[a:b+2]
            buffer = buffer[b+2:]

            bgr_frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            # 이미지 표시
            if bgr_frame is not None:
                cv2.imshow('frame', bgr_frame)

                # 지정된 간격으로 이미지 저장
                if current_time - last_capture_time >= capture_interval:
                    now = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
                    print("take picture :", now)
                    
                    # 예외 처리로 저장 성공 여부 출력
                    try:
                        if cv2.imwrite(save_path + now + ".jpg", bgr_frame):
                            print("이미지 저장 성공:", now)
                        else:
                            print("이미지 저장 실패:", now)
                    except Exception as e:
                        print("이미지 저장 중 에러 발생:", e)
                    
                    last_capture_time = current_time

                # 'q' 키 입력 시 종료
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

finally:
    process.terminate()
    cv2.destroyAllWindows()

