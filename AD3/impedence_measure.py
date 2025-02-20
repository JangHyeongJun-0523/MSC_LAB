from ctypes import *
from dwfconstants import *
import sys
import math

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

# 보정 데이터 로드
cal_data = (c_double * 5)()
with open("calibration_data.txt", "r") as f:
    for i, line in enumerate(f):
        cal_data[i] = c_double(float(line.strip()))

dwf.FDwfAnalogImpedanceCompSet(hdwf, cal_data)

# 측정 설정
start_freq = 50.0
stop_freq = 25e6
steps = 100
amplitude = 1.0

# 측정 시작
dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(1))  # 1은 측정 시작

# 데이터 수집
freq = (c_double * steps)()
impedance = (c_double * steps)()
phase = (c_double * steps)()
for i in range(steps):
    dwf.FDwfAnalogImpedanceStatus(hdwf, c_int(1), byref(freq[i]), byref(impedance[i]), byref(phase[i]))
    print(f"Frequency: {freq[i]:.2f} Hz, Impedance: {impedance[i]:.2f} Ω, Phase: {phase[i]:.2f} rad")

# 장치 종료
dwf.FDwfDeviceClose(hdwf)
