import cv2
import schedule
import time
from datetime import datetime, timedelta

def capture_image():
    # 카메라 열기
    cap = cv2.VideoCapture(0)  # 0은 기본 카메라 장치 ID입니다.
    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    # 사진 촬영
    ret, frame = cap.read()
    if ret:
        # 현재 시간으로 파일명 설정 (한국 시간)
        kst_now = datetime.utcnow() + timedelta(hours=9)  # UTC에 9시간 추가
        filename = kst_now.strftime("%Y%m%d_%H%M%S.jpg")
        cv2.imwrite(filename, frame)  # 이미지 저장
        print(f"사진 저장됨: {filename}")
    else:
        print("사진 촬영 실패.")

    # 카메라 해제
    cap.release()

# 스케줄 설정 (한국 시간 기준)
schedule.every().day.at("07:00").do(capture_image)
schedule.every().day.at("13:00").do(capture_image)
schedule.every().day.at("18:00").do(capture_image)

print("스케줄러 시작됨.")
while True:
    schedule.run_pending()
    time.sleep(1)  # CPU 사용량을 줄이기 위해 대기

