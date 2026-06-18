import cv2
import numpy as np
import time
import requests
import os
from datetime import datetime
from gpiozero import LED

led = LED(18) # GPIO 18번 핀에 연결된 LED 객체 생성 (경고등 역할)

# 텔레그램 봇 API 토큰 및 수신할 사용자/그룹의 Chat ID 설정
TELEGRAM_TOKEN = "-----------------------"
CHAT_ID = "------------"

def send_telegram_photo(image_path, caption_text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        # 이미지 파일을 바이너리 읽기(rb) 모드로 열기
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': CHAT_ID,
                'caption': caption_text # 사진과 함께 보낼 텍스트 메시지
            }
            # 텔레그램 서버로 POST 요청 전송
            response = requests.post(url, data=data, files=files)
            
            # 전송 결과 확인
            if response.status_code == 200:
                print("[알림] 텔레그램으로 사진 전송 성공!")
            else:
                print("[오류] 텔레그램 전송 실패:", response.json())
    except Exception as e:
        print(f"[오류] 파일 전송 중 예외 발생: {e}")

# MobileNet SSD 모델이 감지할 수 있는 21개 클래스 목록
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# 딥러닝 모델 파일 경로 설정 (prototxt: 네트워크 구조, caffemodel: 학습된 가중치)
PROTOTXT = "/home/kmj/min/mobileNetSSD_deploy.prototxt"
MODEL = "/home/kmj/min/mobileNetSSD_deploy.caffemodel"

print("[알림] AI 모델을 로드하는 중...")
# OpenCV의 DNN 모듈을 사용하여 Caffe 모델 로드
net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)

# 기본 카메라(0번) 연결 및 해상도 설정 (640x480)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("[알림] 감시 시스템 시작 (텔레그램 연동)...")
last_alert_time = 0   # 마지막으로 경고를 보낸 시간을 저장하는 변수 (중복 알림 방지용)

# 카메라가 정상적으로 열려 있는 동안 반복 수행
while cap.isOpened():
    ret, frame = cap.read() # 카메라로부터 프레임 한 장 읽기
    if not ret:
        print("[경고] 카메라 프레임을 읽어올 수 없습니다.")
        break
        
    # 프레임의 세로(h), 가로(w) 크기 취득
    (h, w) = frame.shape[:2]

    # 모델 입력 형식에 맞게 이미지 크기 조절(300x300) 및 픽셀 값 스케일링 (Blob 생성)
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob) # 신경망에 입력 설정
    detections = net.forward() # 객체 감지(추론) 실행

    person_detected = False # 이번 프레임에서 사람이 감지되었는지 여부 플래그

    # 감지된 객체들을 순회하며 확인
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2] # 감지된 객체들을 순회하며 확인

        # 신뢰도가 50% 이상인 경우에만 처리
        if confidence > 0.5:
            class_id = int(detections[0, 0, i, 1]) # 감지된 객체의 클래스 ID
            class_name = CLASSES[class_id]  # 클래스 이름 매칭

            # 감지된 객체가 "person(사람)"일 경우
            if class_name == "person":
                person_detected = True # 사람 감지 플래그 True 설정

                # 감지된 사각형 박스 좌표 계산 (원본 이미지 크기에 맞게 스케일링)
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # 화면의 사람 위치에 빨간색(0, 0, 255) 사각형 그리기
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                # 사각형 위에 클래스 이름과 신뢰도 퍼센트 텍스트 표시
                cv2.putText(frame, f"{class_name}: {confidence * 100:.2f}%", (startX, startY - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # 사람이 감지되었을 때의 처리 로직
    if person_detected:
        current_time = time.time()
        # 마지막 알림 전송 후 10초가 지났는지 확인 (도배 방지용)
        if current_time - last_alert_time > 10: 
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # 메시지용 시간 문자열
            filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg" # 저장할 이미지 파일명
            
            led.on()  # 외부인 감지 시 경고 LED 켜기

            # 현재 프레임을 이미지 파일로 임시 저장
            cv2.imwrite(filename, frame)
            print(f"[경고] 외부인 감지됨! 사진 촬영 완료: {filename}")

            # 텔레그램으로 보낼 메시지 작성 및 사진 전송 함수 호출
            alert_msg = f"[보안 경고] 외부인이 감지되었습니다!\n 일시: {now_str}"
            send_telegram_photo(filename, alert_msg)

            # 전송 완료 후 라즈베리파이 저장 공간 확보를 위해 임시 이미지 파일 삭제
            if os.path.exists(filename):
                os.remove(filename)

            led.off() # 처리 완료 후 경고 LED 끄기
                
            last_alert_time = current_time # 마지막 알림 시간 업데이트

    # "Smart Security Camera (Telegram)"라는 이름의 윈도우 창에 실시간 영상 출력
    cv2.imshow("Smart Security Camera (Telegram)", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'): # 키보드 입력 대기 (1ms), 'q' 키를 누르면 루프 종료
        break

# 프로그램 종료 프로세스: 카메라 자원 해제 및 모든 OpenCV 창 닫기
cap.release()
cv2.destroyAllWindows()
