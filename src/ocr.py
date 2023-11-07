import cv2
from playsound import playsound
import datetime
import cv2
from paddleocr import PaddleOCR
import googletrans
import serial
import time
import re
# 웹캠 열기
cap = cv2.VideoCapture(0)
now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
filename = now + '.png'
ocr = PaddleOCR(lang='korean', use_gpu=False)
address_list = []
name_list = []
number_list = []
dong_list = []

py_serial = serial.Serial(
    # Arduino에 맞는 올바른 포트로 대체하십시오 (예: Linux에서 '/dev/ttyACM0')
    port='/dev/ttyACM0',
    # Arduino의 설정과 일치하는 보드 레이트를 설정하십시오 (예: 9600)
    baudrate=9600
)

while True:
    ret, frame = cap.read()  # 비디오 프레임 읽기
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        # 컨투어 근사화
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        area = cv2.contourArea(contour)
        if len(approx) == 4:
            # 꼭지점이 4개인 경우 컨투어 그리기
            cropped_img = cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            if area > (frame.shape[0]*frame.shape[1]) * 1/2:
                print('인식성공')
                playsound('/home/addinedu/dev_ws/Iot project/qrbarcode_beep.mp3')
                cropped_contour = frame.copy()
                x, y, w, h = cv2.boundingRect(approx)
                cropped_contour = cropped_contour[y:y+h, x:x+w]
                resize_contour = cv2.resize(cropped_contour, (600,384))
                roi_contour = resize_contour[133:268,236:526]
                result = ocr.ocr(roi_contour, cls=True)
                address = ""
                name = ""
                number = ""
                dong = ""
                for idx in range(len(result)):
                    res = result[idx]
                    cnt = 0
                    for line in res:
                        if cnt < 7:
                            address = address + line[1][0]
                        elif cnt >= 7 and cnt < 10:
                            name = name + line[1][0]
                        elif cnt >= 10:
                            number = number + line[1][0]
                        if cnt == 5:
                            dong = dong + line[1][0][:-1]
                        cnt += 1
                reg = re.compile('\d{3}-\d{3,4}-\d{4}')
                number = reg.findall(number)
                print(number)
                number = number[0]
                trans = googletrans.Translator()
                en_address = trans.translate(address, dest = 'en', src='auto')
                en_name = trans.translate(name, dest = 'en', src='auto')
                #trans.를 가지고 오고 translate 함수를 사용하고 ()안 첫번째 인자는 str1은 번역될 대상 두번째인자인 dest는 output언어 src는 input language it's possible set auto also possible set ko
                print("address: ", en_address.text)
                print("name: ", en_name.text)
                print("number: ", number)
                print("dong: ", dong)
                if number_list != []:
                    if number_list[-1] == number:
                        continue
                address_list.append(en_address.text)
                name_list.append(en_name.text)
                number_list.append(number)
                dong_list.append(dong)
                for n in range(4):
                    if n == 0:
                        command = en_address.text
                    elif n == 1:
                        command = en_name.text
                    elif n == 2:
                        command = number
                    elif n == 3:
                        command = dong
                        
                    py_serial.write(command.encode())
                    time.sleep(0.1)
                    if py_serial.in_waiting > 0:
                        # Arduino로부터의 응답을 읽습니다.
                        response = py_serial.readline()
                        # 응답을 디코딩하고 출력합니다 ('\n'을 제거합니다)
                        print(response[:-1].decode())