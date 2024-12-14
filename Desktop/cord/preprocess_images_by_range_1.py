import os
import cv2
import numpy as np

# 데이터 경로 설정
input_path = "C:\\test\\images"  # 원본 이미지 경로
output_path = "C:\\test\\processed_images"  # 전처리된 이미지 저장 경로
os.makedirs(output_path, exist_ok=True)

# 이미지 크기와 클래스 정의
image_size = (64, 64)  # 이미지 크기
classes = ["left", "straight", "right"]  # 클래스 이름

# 전처리 및 저장
for cls in classes:
    input_dir = os.path.join(input_path, cls)
    output_dir = os.path.join(output_path, cls)
    os.makedirs(output_dir, exist_ok=True)

    for img_name in os.listdir(input_dir):
        img_path = os.path.join(input_dir, img_name)
        img = cv2.imread(img_path)

        if img is None:
            print(f"이미지 읽기 실패: {img_path}")
            continue

        # 이미지 크기 조정 및 정규화
        img_resized = cv2.resize(img, image_size)
        img_normalized = img_resized / 255.0

        # 저장
        save_path = os.path.join(output_dir, img_name)
        cv2.imwrite(save_path, (img_normalized * 255).astype(np.uint8))  # 정규화 후 다시 [0, 255]로 저장
        print(f"전처리 완료 및 저장: {save_path}")
