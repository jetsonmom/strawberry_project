import cv2
import time
import schedule
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import numpy as np

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=30,
    flip_method=0,
    exposure_time=13000,
    gain=(1.0, 2.5),
    saturation=1.5,  # 채도 증가 (기본값: 1.0)
    contrast=1.2,    # 대비 증가 (기본값: 1.0)
    brightness=0.0     # 밝기 조정 (기본값: 0)
):
    return (
        f"nvarguscamerasrc sensor-id={sensor_id} "
        f"exposuretimerange='{exposure_time} {exposure_time}' "
        f"gainrange='{gain[0]} {gain[1]}' "
        f"saturation={saturation} "
        f"contrast={contrast} "
        f"brightness={brightness} "
        f"aeLock=True wbmode=3 ! "
        f"video/x-raw(memory:NVMM), width=(int){capture_width}, height=(int){capture_height}, "
        f"format=(string)NV12, framerate=(fraction){framerate}/1 ! "
        f"nvvidconv flip-method={flip_method} ! "
        f"video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
    )

def enhance_image(image):
    # 이미지 선명도 증가
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(image, -1, kernel)
    
    # 대비 증가
    lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    return enhanced

def send_email(file_path):
    email_address = "jmerrier0910@gmail.com"  # 발신자 겸 수신자 이메일 주소
    app_password = "smvrcqoizxbxmyhy"  # 여기에 생성한 앱 비밀번호를 입력하세요

    # 이메일 메시지 생성
    message = MIMEMultipart()
    message["From"] = email_address
    message["To"] = email_address
    message["Subject"] = "Plant Monitoring Image"

    # 이메일 본문 추가
    body = "식물 모니터링 이미지가 첨부되어 있습니다."
    message.attach(MIMEText(body, "plain"))

    # 이미지 파일 첨부
    with open(file_path, "rb") as image_file:
        image = MIMEImage(image_file.read(), name=os.path.basename(file_path))
        message.attach(image)

    # 이메일 전송
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_address, app_password)
            server.send_message(message)
        print("이메일이 성공적으로 전송되었습니다.")
    except Exception as e:
        print(f"이메일 전송 중 오류 발생: {e}")
        print(f"오류 상세 정보: {type(e).__name__}, {str(e)}")

def capture_image():
    print("사진 촬영 시작...")
    video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    
    if video_capture.isOpened():
        try:
            # 카메라 워밍업을 위해 잠시 대기
            time.sleep(2)
            
            ret_val, frame = video_capture.read()
            if ret_val:
                # 이미지 향상
                enhanced_frame = enhance_image(frame)
                
                # 현재 날짜와 시간으로 파일명 생성
                current_time = datetime.now()
                file_name = current_time.strftime("%Y%m%d_%H%M%S.jpg")
                
                # 날짜별 폴더 생성
                folder_name = current_time.strftime("%Y%m%d")
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                
                # 이미지 저장
                file_path = os.path.join(folder_name, file_name)
                cv2.imwrite(file_path, enhanced_frame)
                print(f"사진이 저장되었습니다: {file_path}")
                
                # 이메일 전송
                send_email(file_path)
            else:
                print("프레임을 읽을 수 없습니다.")
        finally:
            video_capture.release()
    else:
        print("카메라를 열 수 없습니다.")

# 스케줄 설정
schedule.every().day.at("06:00").do(capture_image)
schedule.every().day.at("12:00").do(capture_image)
schedule.every().day.at("18:50").do(capture_image)

if __name__ == "__main__":
    print("식물 모니터링 스크립트가 실행되었습니다.")
    print("매일 오전 6시, 오후 12시, 오후 12시 24분, 오후 5시 50분에 사진을 촬영하고 이메일로 전송합니다.")
    
    # 스크립트 시작 시 즉시 한 번 실행
    capture_image()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("프로그램이 사용자에 의해 중단되었습니다.")
