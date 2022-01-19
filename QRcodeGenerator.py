# QR코드 생성기
# qrcode : https://pypi.org/project/qrcode/

from time import strftime
from qrcode import *
from PIL import Image
from datetime import datetime

# 바코드 형식 : header(6자리) + classification(직원 or 가맹점) + 2021(년) + 11(월) + 4077(전화) + 일련번호(01~20)

# 헤더 = 노원구청 교통행정과 등록팀 (내 QR인지 식별자 역할)
# 가맹점 = Member of Affiliation (직원 = Member of the Staff)
header = "NWTAVR"         # 6
classification = "MS"     # 2

# 1. 년 + 월(월은 다음달)
code_year = datetime.today().strftime("%Y")
code_month = "{:02d}".format((datetime.today().month % 12) + 1 )

# 2. 행정전화
code_name = ["전현호", "박선녕", "정성욱", "이재영", "김재형", "이희영", "신상용", "최미연", "이정선"]  # len(name_list) = 9
code_phone = ["4080", "4079", "4076", "4075", "4077", "4071", "4069", "4068", "4078"]                   # len(phone_list) = 9

#qr.add_data("202111407701 made by Kim Jae Hyoung @ Transportation Administration Division of Nowongu Office")

for person in range(len(code_phone)):       # 한명당(0~8)
    for serialnum in range(1, 20+1):        # 20개씩(1~20)
        qr = QRCode(version=1, error_correction = ERROR_CORRECT_L, box_size=10, border=1)   # border=4(default)
        qr.add_data(code_year + '-' + code_month + '-' + code_phone[person] + '-' + "{:02d}".format(serialnum))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("QR-{}-".format(code_name[person]) + "{:02d}".format(serialnum) + ".png", "PNG")

