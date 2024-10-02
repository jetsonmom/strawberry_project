#pip3 install schedule
#sudo systemctl restart nvargus-daemon
#sudo usermod -a -G video jetson
#sudo dpkg-reconfigure tzdata
import cv2
import time
import schedule
from datetime import datetime
import os

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=1920,
    display_height=1080,
    framerate=30,
    flip_method=0,
):
    return (
        f"nvarguscamerasrc sensor-id={sensor_id} ! "
        f"video/x-raw(memory:NVMM), width=(int){capture_width}, height=(int){capture_height}, framerate=(fraction){framerate}/1 ! "
        f"nvvidconv flip-method={flip_method} ! "
        f"video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
    )

def capture_image():
    print("사진 촬영 시작...")
    video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    
    if video_capture.isOpened():
        try:
            # 카메라 워밍업을 위해 잠시 대기
            time.sleep(2)
            
            ret_val, frame = video_capture.read()
            if ret_val:
                # 현재 날짜와 시간으로 파일명 생성
                current_time = datetime.now()
                file_name = current_time.strftime("%Y%m%d_%H%M%S.jpg")
                
                # 날짜별 폴더 생성
                folder_name = current_time.strftime("%Y%m%d")
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                
                # 이미지 저장
                file_path = os.path.join(folder_name, file_name)
                cv2.imwrite(file_path, frame)
                print(f"사진이 저장되었습니다: {file_path}")
            else:
                print("프레임을 읽을 수 없습니다.")
        finally:
            video_capture.release()
    else:
        print("카메라를 열 수 없습니다.")

# 스케줄 설정
schedule.every().day.at("10:17").do(capture_image)
schedule.every().day.at("18:30").do(capture_image)

print("식물 모니터링 스크립트가 실행되었습니다.")
print("매일 오전 10시 30분과 오후 6시 30분에 사진을 촬영합니다.")

# 메인 루프
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("프로그램이 사용자에 의해 중단되었습니다.")
