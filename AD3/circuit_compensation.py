from ctypes import *
from dwfconstants import *
import sys

# 라이브러리 로드
if sys.platform.startswith("win"):
    dwf = cdll.dwf
else:
    dwf = cdll.LoadLibrary("libdwf.so")

# 장치 열기
hdwf = c_int()
if dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf)) != 1:
    print("장치 연결 실패")
    quit()

# 참조 저항 설정 (1kΩ)
reference = 1000.0
dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(reference))

# 보정 초기화
dwf.FDwfAnalogImpedanceCompReset(hdwf)

# Open 보정
print("DUT를 분리하고 Enter를 누르세요...")
input()
dwf.FDwfAnalogImpedanceCompReset(hdwf)  # Open 보정 초기화
dwf.FDwfAnalogImpedanceCompSet(hdwf, c_double(0), c_double(0), c_double(0), c_double(0))  # Open 보정 수행

# Short 보정
print("DUT를 단락시키고 Enter를 누르세요...")
input()
dwf.FDwfAnalogImpedanceCompReset(hdwf)  # Short 보정 초기화
dwf.FDwfAnalogImpedanceCompSet(hdwf, c_double(0), c_double(0), c_double(0), c_double(0))  # Short 보정 수행

# 보정 데이터 저장
open_resistance = c_double()
open_reactance = c_double()
short_resistance = c_double()
short_reactance = c_double()
dwf.FDwfAnalogImpedanceCompGet(hdwf, byref(open_resistance), byref(open_reactance), byref(short_resistance), byref(short_reactance))

with open("calibration_data.txt", "w") as f:
    f.write(f"{open_resistance.value}\n")
    f.write(f"{open_reactance.value}\n")
    f.write(f"{short_resistance.value}\n")
    f.write(f"{short_reactance.value}\n")

print("보정 완료 및 데이터 저장")

# 장치 종료
dwf.FDwfDeviceClose(hdwf)
