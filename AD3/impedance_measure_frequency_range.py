"""
   DWF Python 예제 (수정 버전)
   작성자: Digilent, Inc.
   수정일: 2025-02-24

   요구사항: Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import math
import time
import sys
import numpy as np
import matplotlib.pyplot as plt

# OS에 따라 DWF 라이브러리 로드
if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

# 버전 확인
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: " + str(version.value))

# 장치 열기
hdwf = c_int()
szerr = create_string_buffer(512)
print("첫 번째 장치 열기")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    dwf.FDwfGetLastErrorMsg(szerr)
    print("오류:", str(szerr.value))
    print("장치 열기에 실패하였습니다.")
    quit()

# 자동 구성 옵션 설정 (주파수, 진폭 등의 동적 조정을 위해)
dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(3))

# 측정 파라미터 설정
steps = 3755                # 측정 스텝 수
start_freq = 5e1            # 시작 주파수: 50 Hz
stop_freq = 25e6            # 종료 주파수: 25 MHz
reference = 1e3             # 기준 저항: 1 kΩ

print("기준 저항: {} Ω, 주파수 범위: {} Hz ~ {} kHz (nanofarad 커패시터 측정)".format(
    reference, start_freq, stop_freq/1e3))

# 임피던스 측정 초기화 및 설정
dwf.FDwfAnalogImpedanceReset(hdwf)
dwf.FDwfAnalogImpedanceModeSet(hdwf, c_int(8)) 
dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(reference))
dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(start_freq))
dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(1))  # 1V 진폭 (2V 피크 투 피크)
dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(1))  # 측정 시작

# DUT 안정화를 위한 대기 시간
time.sleep(2)

# 결과를 저장할 배열 초기화
rgHz = [0.0] * steps
rgRs = [0.0] * steps
rgXs = [0.0] * steps

# 각 스텝마다 주파수 변경 후 측정 수행
for step in range(steps):
    # 지수적 주파수 스텝 계산
    exponent = (1.0 * step / (steps - 1) - 1)
    hz = stop_freq * pow(10.0, exponent * math.log10(stop_freq / start_freq))
    print("스텝: {}  주파수: {:.2f} Hz".format(step, hz))
    rgHz[step] = hz

    # 주파수 설정
    dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(hz))

    # 측정 준비 상태 확인 (타임아웃 추가: 2초)
    timeout_sec = 2.0
    start_wait = time.time()
    while True:
        if dwf.FDwfAnalogImpedanceStatus(hdwf, byref(c_byte())) == 0:
            dwf.FDwfGetLastErrorMsg(szerr)
            print("오류:", str(szerr.value))
            quit()
        sts = c_byte()
        dwf.FDwfAnalogImpedanceStatus(hdwf, byref(sts))
        if sts.value == 2:
            break
        if time.time() - start_wait > timeout_sec:
            print("스텝 {}에서 타임아웃 발생".format(step))
            break

    # 측정값 읽기 (저항, 리액턴스)
    resistance = c_double()
    reactance = c_double()
    dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceResistance, byref(resistance))
    dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceReactance, byref(reactance))
    rgRs[step] = abs(resistance.value)  # 로그 플롯을 위한 절대값 사용
    rgXs[step] = abs(reactance.value)

    # 채널별 경고 확인 (채널 1과 2)
    for channel in range(2):
        warn = c_int()
        dwf.FDwfAnalogImpedanceStatusWarning(hdwf, c_int(channel), byref(warn))
        if warn.value:
            dOff = c_double()
            dRng = c_double()
            dwf.FDwfAnalogInChannelOffsetGet(hdwf, c_int(channel), byref(dOff))
            dwf.FDwfAnalogInChannelRangeGet(hdwf, c_int(channel), byref(dRng))
            if warn.value & 1:
                print("채널 {}: 입력 전압이 너무 낮음 (최소: {:.2f} V)".format(
                    channel + 1, dOff.value - dRng.value / 2))
            if warn.value & 2:
                print("채널 {}: 입력 전압이 너무 높음 (최대: {:.2f} V)".format(
                    channel + 1, dOff.value + dRng.value / 2))

# 측정 종료 및 장치 닫기
dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(0))  # 측정 중지
dwf.FDwfDeviceClose(hdwf)

# 측정 결과 플롯 (로그 스케일)
plt.plot(rgHz, rgRs, label="Resistance, R")
plt.plot(rgHz, rgXs, label="Reactance, X")
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Freqency (Hz)")
plt.ylabel("Impedance (absolute)")
plt.title("Impedance measure result")
plt.legend()
plt.show()
