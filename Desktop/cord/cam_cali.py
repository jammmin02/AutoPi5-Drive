import numpy as np
import cv2
import glob

# 코너 찾기 알고리즘의 종료 기준 설정
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# 실제 체스보드의 3D 점 설정 (크기: 8x6)
objectpoints = np.zeros((8*6, 3), np.float32)
objectpoints[:, :2] = np.mgrid[0:8, 0:6].T.reshape(-1, 2)

# 3D 및 2D 점 리스트 초기화
worldpoints = []  # 실제 3D 공간에서의 점들
imagepoints = []  # 이미지 상의 2D 점들

# 이미지 파일 경로 설정
images = glob.glob('/home/jungmin/Desktop/cord/date/image/*.jpg')

# 이미지에서 체스보드 코너 찾기
gray = None  # 캘리브레이션 단계에서 사용할 `gray` 초기화
for idx, fname in enumerate(images):
    print("Processing image", idx + 1, ":", fname)
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 체스보드 코너 찾기
    ret, corners = cv2.findChessboardCorners(gray, (8, 6), None)

    if ret:
        print("체스보드 코너를 찾았습니다:", fname)
        worldpoints.append(objectpoints)

        # 코너 점을 더 정확하게 찾기
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imagepoints.append(corners2)

        # 이미지에 체스보드 코너 그리기
        img = cv2.drawChessboardCorners(img, (8, 6), corners2, ret)
    else:
        print("체스보드 코너를 찾지 못했습니다:", fname)

# 이미지가 성공적으로 처리된 경우에만 캘리브레이션 수행
if gray is not None and worldpoints and imagepoints:
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(worldpoints, imagepoints, gray.shape[::-1], None, None)

    # 카메라 매트릭스와 왜곡 계수 출력
    print("Camera matrix:")
    print(mtx)
    print("\nDistortion coefficients:")
    print(dist)
else:
    print("체스보드 코너를 찾은 이미지가 충분하지 않아 캘리브레이션을 수행할 수 없습니다.")

cv2.destroyAllWindows()
