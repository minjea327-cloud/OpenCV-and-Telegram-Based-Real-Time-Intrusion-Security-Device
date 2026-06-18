import cv2
import numpy as np
import time
import requests
import os
from datetime import datetime
from gpiozero import LED

led = LED(18) 

TELEGRAM_TOKEN = "8727745150:AAH7C66yRBjjcNASPXcB8PgWFTp3TI4qkAw"
CHAT_ID = "8317399107"

def send_telegram_photo(image_path, caption_text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': CHAT_ID,
                'caption': caption_text 
            }
            response = requests.post(url, data=data, files=files)
            if response.status_code == 200:
                print("[알림] 텔레그램으로 사진 전송 성공!")
            else:
                print("[오류] 텔레그램 전송 실패:", response.json())
    except Exception as e:
        print(f"[오류] 파일 전송 중 예외 발생: {e}")


CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

PROTOTXT = "/home/kmj/min/mobileNetSSD_deploy.prototxt"
MODEL = "/home/kmj/min/mobileNetSSD_deploy.caffemodel"

print("[알림] AI 모델을 로드하는 중...")
net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("[알림] 감시 시스템 시작 (텔레그램 연동)...")
last_alert_time = 0  


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("[경고] 카메라 프레임을 읽어올 수 없습니다.")
        break

    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    person_detected = False

    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > 0.5:
            class_id = int(detections[0, 0, i, 1])
            class_name = CLASSES[class_id]

            if class_name == "person":
                person_detected = True
                
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                cv2.putText(frame, f"{class_name}: {confidence * 100:.2f}%", (startX, startY - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    if person_detected:
        current_time = time.time()
        if current_time - last_alert_time > 10: 
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            led.on() 
            
            cv2.imwrite(filename, frame)
            print(f"[경고] 외부인 감지됨! 사진 촬영 완료: {filename}")
            
            alert_msg = f"[보안 경고] 외부인이 감지되었습니다!\n 일시: {now_str}"
            send_telegram_photo(filename, alert_msg)
            
            if os.path.exists(filename):
                os.remove(filename)

            led.off()
                
            last_alert_time = current_time

    cv2.imshow("Smart Security Camera (Telegram)", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
