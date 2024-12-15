import cv2

# 웹캠 초기화 (기본 장치 ID는 0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

print("웹캠 연결 성공! ESC를 눌러 종료합니다.")

while True:
    ret, frame = cap.read()  # 프레임 읽기
    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break

    cv2.imshow("Webcam Test", frame)  # 영상 출력

    # ESC 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == 27:
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()
