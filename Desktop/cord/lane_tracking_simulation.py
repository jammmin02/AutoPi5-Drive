import cv2
import numpy as np
from tensorflow.keras.models import load_model
import os

# === 데이터 준비 ===
def load_test_data(data_path, image_size):
    """
    데이터와 레이블을 로드하는 함수
    """
    X = []  # 이미지 데이터
    y = []  # 레이블
    file_paths = []  # 파일 경로 저장

    classes = ["left", "straight", "right"]  # 클래스 이름
    class_indices = {cls: idx for idx, cls in enumerate(classes)}
    indices_class = {idx: cls for cls, idx in class_indices.items()}  # 인덱스-클래스 매핑

    for cls in classes:
        cls_path = os.path.join(data_path, cls)
        for img_name in os.listdir(cls_path):
            img_path = os.path.join(cls_path, img_name)
            img = cv2.imread(img_path)
            img_resized = cv2.resize(img, image_size)
            img_normalized = img_resized / 255.0
            X.append(img_normalized)
            y.append(class_indices[cls])
            file_paths.append(img_path)

    return np.array(X), np.array(y), file_paths, indices_class

# === 화살표 그리기 함수 ===
def draw_arrow(image, direction, color):
    """
    주어진 이미지에 방향을 나타내는 화살표를 그림.
    direction: 'left', 'straight', 'right'
    color: (B, G, R)
    """
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    arrow_length = 50

    if direction == "left":
        endpoint = (center[0] - arrow_length, center[1])
    elif direction == "straight":
        endpoint = (center[0], center[1] - arrow_length)
    elif direction == "right":
        endpoint = (center[0] + arrow_length, center[1])
    else:
        return image

    cv2.arrowedLine(image, center, endpoint, color, 3, tipLength=0.3)
    return image

# === 모델 및 데이터 로드 ===
model_path = "/home/pi/AL_CAR/lane_following_model.h5"
data_path = "/home/pi/AL_CAR/images"
image_size = (64, 64)

# 모델 로드
model = load_model(model_path)
print("모델 로드 완료!")

# 테스트 데이터 로드
X_test, y_test, file_paths, indices_class = load_test_data(data_path, image_size)
print(f"테스트 데이터 크기: {X_test.shape}, 라벨 크기: {y_test.shape}")

# === 예측 및 시뮬레이션 ===
output_folder = "/home/pi/AL_CAR/simulation_output"
os.makedirs(output_folder, exist_ok=True)

for i, (image, true_label, file_path) in enumerate(zip(X_test, y_test, file_paths)):
    # 모델 예측
    image_input = np.expand_dims(image, axis=0)
    predictions = model.predict(image_input)
    predicted_label = np.argmax(predictions)

    # 원래 이미지 로드
    original_image = cv2.imread(file_path)
    original_image_resized = cv2.resize(original_image, (256, 256))

    # 실제 방향(파란색) 및 예측 방향(빨간색) 표시
    true_direction = indices_class[true_label]
    predicted_direction = indices_class[predicted_label]

    image_with_arrows = draw_arrow(original_image_resized, true_direction, (255, 0, 0))  # 파란색 화살표 (실제 방향)
    image_with_arrows = draw_arrow(image_with_arrows, predicted_direction, (0, 0, 255))  # 빨간색 화살표 (예측 방향)

    # 결과 이미지 저장
    output_path = os.path.join(output_folder, f"result_{i}_{true_direction}_vs_{predicted_direction}.jpg")
    cv2.imwrite(output_path, image_with_arrows)
    print(f"결과 저장: {output_path}")

    # 화면에 출력 (옵션)
    cv2.imshow("Simulation Result", image_with_arrows)
    if cv2.waitKey(500) & 0xFF == ord('q'):  # q를 누르면 종료
        break

# 리소스 해제
cv2.destroyAllWindows()
print("시뮬레이션 완료!")
