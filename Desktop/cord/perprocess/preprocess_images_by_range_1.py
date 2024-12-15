import os
import cv2
import numpy as np

def preprocess_image(image):
    """
    이미지 전처리 함수:
    - 상단 30% 자르기
    - 그레이스케일 변환
    - 가우시안 블러
    - 히스토그램 균등화
    - Adaptive Thresholding
    """
    # 이미지 크기 가져오기
    height, width, _ = image.shape

    # 상단 30% 자르기
    roi = image[int(height * 0.3):, :]  # 상단 30% 제거

    # 그레이스케일 변환
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # 가우시안 블러 적용 (노이즈 제거)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 히스토그램 균등화 (명암비 개선)
    equalized = cv2.equalizeHist(blurred)

    # Adaptive Thresholding 적용 (더 나은 이진화)
    binary = cv2.adaptiveThreshold(
        equalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

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

def main():
    # 원본 이미지 경로 및 저장 경로 설정
    input_path = "C:\\test\\images"  # 원본 이미지 경로
    output_path = "C:\\test\\processed_images"  # 전처리된 이미지 저장 경로
    os.makedirs(output_path, exist_ok=True)

    # 클래스 정의
    classes = ["left", "straight", "right"]  # 클래스 이름

    # 각 클래스 폴더에서 이미지 읽기 및 전처리 수행
    for cls in classes:
        input_dir = os.path.join(input_path, cls)
        output_dir = os.path.join(output_path, cls)
        os.makedirs(output_dir, exist_ok=True)

        for img_name in os.listdir(input_dir):
            img_path = os.path.join(input_dir, img_name)

            # 이미지 읽기
            image = cv2.imread(img_path)
            if image is None:
                print(f"이미지를 읽을 수 없습니다: {img_path}")
                continue

            # 전처리 수행
            processed_image = preprocess_image(image)

            # 전처리된 이미지 저장
            save_preprocessed_image(processed_image, output_path, cls, img_name)

if __name__ == "__main__":
    main()
