from io import BytesIO
from datetime import datetime
from barcode import EAN13
from barcode.writer import ImageWriter

# 바코드 형식(12자리) : 2021(년) + 11(월) + 4077(전화) + 일련번호(01~20)

# 1. 년 + 월(월은 다음달)
year_month = datetime.today().year + (datetime.today().month + 1)

# 2. 행정전화
name_list = ["전현호", "박선녕", "정성욱", "이재영", "김재형", "이희영", "신상용", "최미연", "이정선"]
phone_list = ["4080", "4079", "4076", "4075", "4077", "4071", "4069", "4068", "4078"]


# print to a file-like object:
#rv = BytesIO()
#EAN13(str(100000902922), writer=ImageWriter()).write(rv)


# 이미지 파일로 출력
with open("식권바코드.png", 'wb') as f:
    EAN13('202111407701', writer=ImageWriter()).write(f)