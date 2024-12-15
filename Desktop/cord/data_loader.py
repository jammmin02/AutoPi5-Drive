import tensorflow as tf
import numpy as np
import os
import cv2  # OpenCV 모듈 임포트
# 전처리된 데이터 로드
def load_processed_data(data_path, image_size):
    X = []  # 이미지 데이터
    y = []  # 레이블

    classes = ["left", "straight", "right"]  # 클래스 이름
    class_indices = {cls: idx for idx, cls in enumerate(classes)}

    for cls in classes:
        cls_path = os.path.join(data_path, cls)
        for img_name in os.listdir(cls_path):
            img_path = os.path.join(cls_path, img_name)
            img = cv2.imread(img_path)
            img = cv2.resize(img, image_size)  # 크기 조정
            img = img / 255.0  # 정규화
            X.append(img)
            y.append(class_indices[cls])

    return np.array(X), np.array(y)

# 데이터 경로와 크기 설정
data_path = "//home//pi//AL_CAR//processed_images"
image_size = (64, 64)

# 데이터 로드
X, y = load_processed_data(data_path, image_size)
print(f"데이터 크기: {X.shape}, 라벨 크기: {y.shape}")

# 훈련/검증 데이터 분리
from sklearn.model_selection import train_test_split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# 원-핫 인코딩
y_train = tf.keras.utils.to_categorical(y_train, num_classes=3)
y_val = tf.keras.utils.to_categorical(y_val, num_classes=3)