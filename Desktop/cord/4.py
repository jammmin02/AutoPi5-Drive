import cv2
import matplotlib.pyplot as plt

# Haar Cascade 파일 경로 (OpenCV에 기본적으로 포함되어 있음)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 이미지 읽기 및 리사이즈
img = cv2.imread('/home/pi/Downloads/divinetec.jpg')
img = cv2.resize(img, (1200, 800))

# 그레이스케일 변환
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 얼굴 탐지
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

# 탐지된 얼굴에 사각형 그리기
for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 0), 2)

# RGB로 변환 (matplotlib는 RGB 형식 사용)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# 이미지 표시
plt.imshow(img_rgb)
plt.axis('off')  # 축 제거
plt.show()
