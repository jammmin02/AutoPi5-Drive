import cv2
import os

def preprocess_and_save_images(base_input_path, base_output_path, target_size=(64, 64), crop_percentage=0.3):
    # 각 range_{i} 폴더를 순회
    for folder_name in os.listdir(base_input_path):
        input_folder = os.path.join(base_input_path, folder_name)
        output_folder = os.path.join(base_output_path, folder_name)

        # 폴더 확인 및 생성
        if not os.path.isdir(input_folder):
            continue
        os.makedirs(output_folder, exist_ok=True)

        for filename in os.listdir(input_folder):
            if filename.endswith(".jpg"):
                img_path = os.path.join(input_folder, filename)
                img = cv2.imread(img_path)

                if img is None:
                    print(f"이미지를 불러올 수 없습니다: {img_path}")
                    continue

                # 위쪽 30% 제거
                height, width, _ = img.shape
                crop_height = int(height * crop_percentage)
                cropped_img = img[crop_height:, :]  # [crop_height:전체 높이, 모든 너비]

                # 크기 조정
                resized_img = cv2.resize(cropped_img, target_size)

                # 전처리된 이미지 저장
                output_path = os.path.join(output_folder, filename)
                cv2.imwrite(output_path, resized_img)
                print(f"저장 완료: {output_path}")
