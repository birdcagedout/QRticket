
import os
import re
import cv2
import sys
import numpy as np
from PIL import Image
from threading import *
from tqdm.auto import tqdm
from pyzbar.pyzbar import *

HOME_PATH = "C:/QRcodePy/2021년11월/"
file_list = os.listdir(HOME_PATH)		# ['1.MOV', '10.MOV', ... '11.MOV', '12.MOV']
num_of_file = len(file_list)			# 동영상 파일 개수 = 쓰레드 개수



# <QR Format>
# 식당: NWTAVR-MA-202111-식당이름
# 직원: 2021-11-4077-01              ==> 다음달부터 NWTAVR-MS-202112-4077-01
# HEADER = 노원구청 교통행정과 등록팀 (내 QR인지 식별자 역할)
# CLASS : 가맹점 = Member of Affiliation / 직원 = Member of Staff
QR_HEADER = "NWTAVR"                  # 6
QR_CLASS_MA = "MA"                    # 2
QR_CLASS_MS = "MS"                    # 2
QR_YEAR = "2021"                      # 4
QR_MONTH = "11"                       # 2
QR_YEAR_MONTH = QR_YEAR + QR_MONTH    # 6
QR_SN = ["0"+str(i) for i in range(1,10)] + list(map(str, range(10, 21)))    # ["01", "02", ... "19", "20"]

affil_list = ["노란코끼리", "어장촌생선구이", "횡성목장", "항도(港都)", "전주콩나루", "옛날칼국수", "칠리사이공", "도나한우", "북경(北京)", "명문식당", "일성스시", "새싹비빔밥", "구내매점"]

code_list =  ["4080",    "4076",    "4079",    "4069",    "4078",    "4071",    "4068",    "4075",    "4077"   ]
name_list =  ["전현호",  "정성욱",  "박선녕",  "신상용",  "이정선",  "이희영",  "최미연",  "이재영",  "김재형" ]
color_list = ["#E32636", "#FFA500", "#FF5511", "#0FF1C3", "#AB3ED8", "#AAEE00", "#1155FF", "#FCE205", "#119617"]

name_by_code =  {"4080":"전현호",  "4076":"정성욱",  "4079":"박선녕",  "4069":"신상용",  "4078":"이정선",  "4071":"이희영",  "4068":"최미연",  "4075":"이재영",  "4077":"김재형"}
color_by_code = {"4080":"#E32636", "4076":"#FFA500", "4079":"#FF5511", "4069":"#0FF1C3", "4078":"#AB3ED8", "4071":"#AAEE00", "4068":"#1155FF", "4075":"#FCE205", "4077":"#119617"}

MA_pattern = re.compile(QR_HEADER + "-" + QR_CLASS_MA + "-" + QR_YEAR_MONTH + "-" + ".+")    # NWTAVR-MA-202111-노란코끼리
MS_pattern = re.compile(QR_YEAR + "-" + QR_MONTH + "-" + "[0-9]{4}-[0-9]{2}")                # 2021-11-4077-01
# MA_pattern = re.compile(QR_HEADER + "-" + QR_CLASS_MS + "-" + QR_YEAR_MONTH + "-" + ".+")  # NWTAVR-MS-202112-4077-01 (12월부터)


class QRDetectionThread(Thread):
	# 초기화
	def __init__(self, file_name):
		super(QRDetectionThread, self).__init__(daemon=True)

		# 내부 변수 초기화
		self.input = HOME_PATH + file_name
		self.cap = cv2.VideoCapture(input)
		if self.cap.isOpened() == False:
			print(f"[쓰레드 오류] VideoCapture 파일읽기 오류 : {file_name}")
			sys.exit(0)

		self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
		self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
		self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
		self.fps = self.cap.get(cv2.CAP_PROP_FPS)

		self.fourcc = cv2.VideoWriter_fourcc(*'DIVX')
		self.out = cv2.VideoWriter(f"{HOME_PATH}+[QR_result]{file_name}.avi", self.fourcc, self.fps, (self.width, self.height))

		self.detected_MA_list = []    # 식당이름
		self.detected_MS_list = []    # 식권QR


	# 쓰레드 실행함수
	def run(self):

		for frame_index in tqdm(range(self.frame_count)):

			# 읽어오지 못한 경우 이 시점에서 success = False
			success, frame = self.cap.read()
			if success == False:
				break
			
			# 프레임에서 QR code 찾기
			result = decode(frame, symbols=[ZBarSymbol.QRCODE])
			num_of_QR = len(result)
			# print(f"[전처리 전] 발견된 QR개수: {num_of_QR}")
			
			
			# 만약 하나도 발견되지 않았다면 다음 Frame
			if num_of_QR == 0:
				print("QR code not detected")
				continue
			
			
			# 프레임 1개에서 발견한 여러개의 QR
			for eachQR in result:
			
				# QR 형식검증 : MS/MA패턴
				eachQR_data = eachQR.data.decode('utf-8')
				match_result_MA = MA_pattern.match(eachQR_data)
				match_result_MS = MS_pattern.match(eachQR_data)

				if match_result_MA is None:
					if match_result_MS is None:
						result.remove(eachQR)
						continue
					else:
						self.detected_MS_list.append(match_result_MS.group())
				else:
					self.detected_MA_list.append(match_result_MA.group())

				# QR 테두리 선그리기
				points = len(eachQR.polygon)     # QR 1개당 인식된 폴리곤 테두리 점의 개수(보통 4각형=4개)

				# 경계선 컬러 설정
				if match_result_MS is not None:
					yyyy, mm, code, sn = eachQR.data.decode('utf-8').split('-')
					color_hex_selected = color_by_code[code]
					color_selected = tuple(int(color_hex_selected[i:i+2], 16) for i in (5, 3, 1))
				else:
					header, classifier, year_month, affil_name = eachQR.data.decode('utf-8').split('-')
					color_selected = (0, 0, 255)    # 식당QR은 빨간색

				# QR 1개당 경계선 그리기
				for point in range(points):
					next_point = (point+1) % points
					cv2.line(frame, tuple(eachQR.polygon[point]), tuple(eachQR.polygon[next_point]), color_selected, 5)    # (B,G,R), 굵기
			
			# num_of_QR_preprocessed = len(result)
			# print("Frame  #{:3}/{:3} 처리 끝    ====>    전처리 전: {:2} \t 전처리 후: {:2}".format(frame_index+1, frame_count, num_of_QR, num_of_QR_preprocessed))
			self.out.write(frame)

		self.cap.release()
		self.out.release()