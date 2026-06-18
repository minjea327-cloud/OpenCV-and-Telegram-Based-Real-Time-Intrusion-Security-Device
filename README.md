# OpenCV and Telegram-Based Real-Time Intrusion Security Device

## 개요
본 실험은 Raspberry Pi와 인공지능(AI) 모델, 텔레그램(Telegram) 메신저를 융합하여 실시간으로 침입자를 감지하고 원격 알림을 보내는 'OpenCV·텔레그램 기반 실시간 침입 보안 디바이스 만들기' 구현을 목적으로 한다.

실시간 웹캠 영상 분석 중 화면 내에서 '사람(person)' 객체가 식별되면, 시스템은 즉시 GPIO 18번 핀을 통해 빨간색 LED를 점등시켜 현장 경보를 울린다. 이와 동시에 텔레그램 봇 API를 활용하여 침입 순간의 스냅샷 사진과 실시간 일시를 사용자의 스마트폰 텔레그램 앱으로 오차 없이 전송한다. 또한, 10초 간격의 중복 전송 방지 알고리즘을 적용하여 무분별한 알림 폭탄을 방지하도록 설계하였다. 본 구현을 통해 임베디드 하드웨어 제어 능력과 텔레그램 기반의 IoT 네트워크 연동 기술을 종합적으로 검증하고자 한다.

## 실험장비
1. Raspberry Pi
2. USB 웹 캠
3. 빨간색 LED
4. 330Ω 저항
5. 브레드보드
6. 점퍼케이블 2개

## 실험절차

1단계: 하드웨어 경보 회로구성
- 빨간색 LED에 $330Ω 저항을 직렬로 연결하였다.
- 이 회로를 라즈베리파이의 GPIO 18번 핀과 GND(그라운드) 핀에 각각 연결하여 물리적인 경보 제어 시스템을 구축하였다.
  
2단계: 개발 환경 설정 및 라이브러리 로드
- Python 개발 환경(Thonny IDE 등)에서 영상 처리 및 통신에 필요한 핵심 라이브러리인 cv2, NumPy, Requests, GPIO Zero, os 등을 임포트(import)하였다.
- gpiozero 라이브러리를 활용하여 제어 코드 내에 GPIO 18번 핀과 매핑되는 경보용 LED 객체를 선언 및 생성하였다.

3단계: 텔레그램 알림 전송 함수 정의
- 웹캠 화면에 침입자가 발생했을 때, 실시간으로 현장 스냅샷 사진과 경고 메시지를 외부로 송신할 수 있도록 소스코드 내에 텔레그램 API 기반의 전송 함수를 정의하였다.
  
4단계: 인공지능(AI) 딥러닝 모델 로드
- 실시간 입력 영상 속 사물을 정확하게 분류 및 판별하기 위하여, 사전 학습된 가벼운 임베디드용 모델인 MobileNet SSD 딥러닝 가중치 파일을 OpenCV DNN(Deep Neural Network) 모듈로 로드하였다.
  
5단계: 웹캠 구동 및 실시간 객체 인식 루프 설계
- 라즈베리파이에 연결된 USB 웹캠을 구동하여 실시간 영상 스트리밍 프레임을 가져왔다.
- 인공지능 모델이 실시간 화면을 연속적으로 분석하여, 신뢰도(Confidence)가 50% 이상인 '사람(person)' 객체만을 정확히 인식하고 추적하도록 내부 while 루프 코드를 설계하였다.
  
6단계: 융합 보안 경보 작동 및 시스템 검증
- 영상 내에서 '사람(person)' 객체가 감지되면 즉시 GPIO 18번 핀을 제어하여 빨간색 LED를 점등시켜 위험을 알리도록 구현하였다.
- 동시에 무분별한 연속 알림을 방지하기 위해 10초 간격의 중복 방지 조건문 알고리즘을 거치도록 하였으며, 조건을 충족할 때 침입 순간의 스냅샷 사진을 촬영 후 텔레그램으로 전송하는 전체 실시간 침입 보안 디바이스의 정상 작동 시스템을 성공적으로 확인하였다.


## 실험내용

Python 프로그램을 활용하여 실시간 영상 분석과 하드웨어 제어가 결합한 물리적 스마트 보안 디바이스를 구현하고,  제한시간 내 하드웨어 및 전송 제어 능력을 습득한다. 더불어 본 실험을 기반으로 향후 OpenCV 및 딥러닝 기반의 객체 인식 기술을 결합하여, AI 기반 방범 시스템으로 확장 가능한 구조를 이해하고자 한다.


## 코드해석
```
import cv2
import numpy as np
import time
import requests
import os
from datetime import datetime
from gpiozero import LED

led = LED(18) 

TELEGRAM_TOKEN = "-----------------------"
CHAT_ID = "------------"

```
- import ... : OpenCV(cv2), 배열 연산(numpy), 시간 제어(time), 웹 통신(requests), 파일 관리(os), 현재 시각 획득(datetime), 하드웨어 제어(gpiozero) 모듈을 로드합니다.

- led = LED(18): 라즈베리파이의 GPIO 18번 핀에 연결된 출력 장치(빨간색 LED)를 제어할 제어 객체를 생성합니다.

- TELEGRAM_TOKEN, CHAT_ID: 보안 원격 알림을 전송할 고유 텔레그램 봇 토큰 값과 사용자의 수신 ID 주소를 정의합니다.
```
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
```
- send_telegram_photo(): 촬영된 현장 스냅샷 사진과 침입 일시 텍스트를 파라미터로 받아 전송하는 함수입니다.

- open(image_path, 'rb'): 저장된 이미지 파일을 바이너리 읽기(rb) 모드로 열어 쪼갠 뒤 네트워크 전송 포맷으로 인코딩합니다.

- requests.post(url, ...): HTTP POST 요청을 통해 텔레그램 오픈 API 웹 서버 주소로 사진 스트림 데이터와 텍스트 메시지를 포함하여 실시간 클라이언트 요청을 송신합니다. status_code == 200을 통해 전송 성공 유무를 디버깅합니다.
```
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
```
- CLASSES: 가벼운 딥러닝 인공지능 모델인 MobileNet SSD가 판별할 수 있도록 사전 정의된 21개의 객체 범주 목록입니다.

- cv2.dnn.readNetFromCaffe(): 인공지능 신경망 구조 파일(.prototxt)과 학습된 가중치 파일(.caffemodel)을 OpenCV의 DNN 모듈 인터페이스로 연동하여 로드합니다.

- cv2.VideoCapture(0): 라즈베리파이에 연결된 기본 USB 웹캠(0번)을 구동하고 화면 프레임 해상도를 비디오 표준 크기인 640x480으로 셋팅합니다.

- last_alert_time = 0: 무분별한 실시간 연속 알림 폭탄을 방지하기 위해 직전 알림이 발생한 시점의 시간을 저장하는 초기 제어 변수입니다.
```
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
```
- cap.read(): 카메라 렌즈로부터 실시간 1프레임 영상을 주기적으로 캡처하여 배열 형태로 가져옵니다.

- cv2.dnn.blobFromImage(): AI 모델에 프레임을 집어넣기 위한 필수 전처리 단계입니다. 원본 영상 크기를 모델 규격인 300x300 해상도로 강제 리사이즈하고, 픽셀 강도를 보정(스케일링 및 평균 차감)하여 다차원 배열(Blob) 데이터로 변환합니다.

- net.forward(): 전처리된 데이터를 인공신경망 피드포워드(순방향 연산)를 실행시켜 화면 속 사물들의 분석 예측 결과 행렬(detections)을 최종 산출합니다.
```
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
```
- if confidence > 0.5:: 분석된 사물의 매칭 확률(신뢰도)이 50%를 초과하는 유효한 데이터만 필터링합니다.

- if class_name == "person":: 감지된 객체명이 CLASSES 배열 중 "person(사람)"일 경우에만 보안 위협 상황으로 인지하여 person_detected 변수를 True(참)로 전환합니다.

- cv2.rectangle() / cv2.putText(): 검출된 침입자 격자 좌표값에 원본 해상도(w, h)를 곱해 복원한 뒤, 화면상 침입자 주변에 빨간색 사각형 안내선(Bounding Box)을 드로잉하고 상단에 확률 값을 텍스트로 오버레이 시각화합니다.
```
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
```
- if current_time - last_alert_time > 10:: 현재 시간과 마지막 경보 전송 시간의 차이를 계산하여 10초가 지난 상태일 때만 내부 경보를 수행하는 중복 트래픽 제한 조건문입니다.

- led.on() / led.off(): 침입 차단 이벤트 발령과 동시에 GPIO 핀의 전압을 제어하여 브레드보드에 연결된 빨간색 LED를 즉시 점등하고, 작업이 끝나면 소등합니다.

- cv2.imwrite(): 침입자가 레이블링된 상태의 현재 640x480 실시간 화면 프레임을 고유 날짜 파일명(.jpg)을 생성하여 로컬 저장소에 스냅샷으로 저장합니다.

- os.remove(filename): 텔레그램 네트워크 전송 API 함수가 완료되면, 디스크 용량이 작은 라즈베리파이의 메모리 과부하를 막기 위해 임시 저장했던 스냅샷 이미지 파일을 저장소에서 자동 완전 삭제(자원 관리 최적화)합니다.
```
    cv2.imshow("Smart Security Camera (Telegram)", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```
- cv2.imshow(): 딥러닝 분석 바운딩 박스가 씌워진 모니터링 화면을 라즈베리파이 GUI 디스플레이 화면에 실시간으로 출력합니다.

- cv2.waitKey(1) ... ord('q'): 매 프레임 키보드 입력을 감지하다가 사용자가 키보드 'q' 키를 누르면 루프(while)를 강제 탈출합니다.

- cap.release() / destroyAllWindows(): 루프 종료 후 사용했던 웹캠 카메라 하드웨어 자원을 시스템에 다시 안전하게 반환하고, 띄워져 있던 GUI 모니터링 윈도우 창을 메모리 상에서 모두 깨끗하게 닫아 프로세스를 안전하게 종료합니다.
  
## 웹 API 기반의 실시간 네트워크 연동 원리

인공지능을 통해 감지된 침입 정보는 HTTP 통신 프로토콜과 텔레그램 API(Application Programming Interface)를 통해 외부 스마트폰으로 실시간 전송된다. API는 서로 다른 소프트웨어(라즈베리파이의 파이썬 프로그램과 텔레그램 서버)가 안전하게 데이터를 주고받을 수 있도록 규격화된 통신 창구 역할을 한다. 라즈베리파이 내부에서 사람이 식별되는 이벤트가 발생하면, 파이썬의 requests 라이브러리는 고유한 인증 열쇠인 토큰(TOKEN)과 목적지 주소인 사용자 아이디(CHAT_ID)를 결합하여 텔레그램 서버 주소로 전송 요청(HTTP POST Request)을 보낸다. 이때 로컬 디스크에 임시 저장된 침입자의 스냅샷 이미지 파일은 바이너리 데이터 스트림 형태로 패킹되어 네트워크망을 통해 전송된다. 텔레그램 웹 서버가 이 요청을 수신하면 사용자의 고유 계정을 찾아 푸시 알림(Push Notification) 형태로 스마트폰 앱에 사진과 메시지를 밀어내어 발송하는 원리로 작동한다.

----
유튜브 데모영상 : https://youtu.be/H0ZokqdttXM
