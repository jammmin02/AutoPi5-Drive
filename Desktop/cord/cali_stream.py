import cv2
import numpy as np
import subprocess
import shlex

# 새로운 Camera Matrix와 Distortion Coefficients 설정
camera_matrix = np.array([[2121.31966, 0.00000000, 102.826483],
                          [0.00000000, 2093.10952, 229.730186],
                          [0.00000000, 0.00000000, 1.00000000]])

dist_coeffs = np.array([[1.02050823, -6.54281478, -0.00515584852, -0.103680850]])

# 카메라 스트리밍 명령어 설정
cmd = 'libcamera-vid --inline --nopreview -t 0 --codec mjpeg --width 640 --height 480 --framerate 30 -o - --camera 0'
process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 창 설정
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
cv2.resizeWindow('frame', 640, 360)

try:
    buffer = b""
    while True:
        buffer += process.stdout.read(4096)
        a = buffer.find(b'\xff\xd8')
        b = buffer.find(b'\xff\xd9')

        if a != -1 and b != -1:
            jpg = buffer[a:b+2]
            buffer = buffer[b+2:]

            bgr_frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            if bgr_frame is not None:
                h, w = bgr_frame.shape[:2]
                # 새로운 카메라 매트릭스를 얻고 왜곡을 보정
                new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))
                calibrated_frame = cv2.undistort(bgr_frame, camera_matrix, dist_coeffs, None, new_camera_matrix)

                # ROI로 이미지를 자르기
                x, y, w, h = roi
                calibrated_frame = calibrated_frame[y:y+h, x:x+w]

                cv2.imshow('frame', calibrated_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
finally:
    process.terminate()
    cv2.destroyAllWindows()
