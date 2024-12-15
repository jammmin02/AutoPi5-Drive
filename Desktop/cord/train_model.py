import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from sklearn.model_selection import train_test_split
import numpy as np
import os
import cv2

# 전처리된 데이터 로드 함수
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
data_path = "/path/to/processed_dataset"
image_size = (64, 64)

# 데이터 로드
X, y = load_processed_data(data_path, image_size)
print(f"데이터 크기: {X.shape}, 라벨 크기: {y.shape}")

# 훈련/검증 데이터 분리
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# 원-핫 인코딩
y_train = tf.keras.utils.to_categorical(y_train, num_classes=3)
y_val = tf.keras.utils.to_categorical(y_val, num_classes=3)

# === 모델 설계 ===
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(3, activation='softmax')  # 3개의 클래스 (left, straight, right)
])

# 모델 컴파일
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# === 모델 훈련 ===
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=10,  # 반복 학습 횟수
    batch_size=32
)

# === 모델 평가 ===
loss, accuracy = model.evaluate(X_val, y_val)
print(f"검증 데이터 손실: {loss:.4f}")
print(f"검증 데이터 정확도: {accuracy * 100:.2f}%")
