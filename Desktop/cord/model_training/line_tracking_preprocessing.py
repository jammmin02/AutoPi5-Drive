import cv2
import os
import datetime
import numpy as np

def preprocess_image(image):
    """
    이미지 전처리 함수
    - 상단 30% 자르기
    - 그레이스케일 변환
    - 가우시안 블러
    - 이진화
    """
    # 이미지 크기 가져오기
    height, width, _ = image.shape

    # 위쪽 30% 자르기
    roi = image[int(height * 0.3):, :]

    # 그레이스케일 변환
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # 가우시안 블러 적용
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 이진화 (Thresholding)
    _, binary = cv2.threshold(blurred, 128, 255, cv2.THRESH_BINARY_INV)

    return binary

def save_preprocessed_image(image, save_path, folder_name, image_name):
    """
    전처리된 이미지를 저장하는 함수
    """
    folder_path = os.path.join(save_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    filename = f"processed_{image_name}"
    full_path = os.path.join(folder_path, filename)

    if cv2.imwrite(full_path, image):
        print(f"전처리된 이미지 저장 성공: {full_path}")
    else:
        print(f"이미지 저장 실패: {full_path}")

# 메인 함수
def main():
    # 원본 이미지 경로 및 저장 경로 설정
    base_image_path = r"C:\\test\\images"
    save_path = r"C:\\test\\processed_images"

    # 각 폴더에서 이미지 읽기 및 전처리 수행
    for folder_name in os.listdir(base_image_path):
        folder_path = os.path.join(base_image_path, folder_name)
        if os.path.isdir(folder_path):
            print(f"Processing folder: {folder_name}")
            image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            print(f"Found {len(image_files)} image(s) in folder {folder_name}")
            for image_name in image_files:
                image_path = os.path.join(folder_path, image_name)

                # 이미지 읽기
                image = cv2.imread(image_path)
                if image is None:
                    print(f"이미지를 읽을 수 없습니다: {image_path}")
                    continue

                # 전처리 수행
                processed_image = preprocess_image(image)

                # 전처리된 이미지 저장
                save_preprocessed_image(processed_image, save_path, folder_name, image_name)

if __name__ == "__main__":
    main()
