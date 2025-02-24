"""
   DWF Python 예제 (GUI 버튼 적용, 고정 주파수 측정)
   작성자: Digilent, Inc.
   수정일: 2025-02-24

   요구사항: Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import math
import time
import sys
import threading
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# ---------------------------
# DWF 라이브러리 초기화
# ---------------------------
if sys.platform.startswith("win"):
    dwf = cdll.LoadLibrary("dwf.dll")
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

# 버전 출력
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version:", version.value.decode())

# 장치 열기
hdwf = c_int()
szerr = create_string_buffer(512)
print("첫 번째 장치 열기")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
if hdwf.value == hdwfNone.value:
    dwf.FDwfGetLastErrorMsg(szerr)
    print("오류:", szerr.value.decode())
    print("장치 열기에 실패하였습니다.")
    sys.exit(1)

# 자동 구성 옵션 (동적 조정)
dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(3))

# 고정 주파수 측정 파라미터
fixed_freq = 10.0       # 측정 주파수 (10Hz)
reference = 1e3         # 기준 저항: 1 kΩ

# 임피던스 측정 초기 설정 (한번만 설정)
dwf.FDwfAnalogImpedanceReset(hdwf)
dwf.FDwfAnalogImpedanceModeSet(hdwf, c_int(0))                   # 모드 0: W1-C1-DUT-C2-R-GND
dwf.FDwfAnalogImpedanceReferenceSet(hdwf, c_double(reference))     # 기준 저항 설정
dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(fixed_freq))      # 고정 주파수 설정
dwf.FDwfAnalogImpedanceAmplitudeSet(hdwf, c_double(1))             # 1V 진폭 (2V 피크 투 피크)
dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(1))                   # 측정 시작

# DUT 안정화를 위한 대기
time.sleep(2)

# ---------------------------
# 전역 변수 및 스레드 제어
# ---------------------------
running = False         # 측정 반복 제어 플래그
meas_thread = None      # 측정 스레드 객체

# ---------------------------
# 그래프 및 버튼 설정 (R vs X)
# ---------------------------
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)  # 버튼 영역 확보

ax.set_xlabel("R, Resistance  (Ω)")
ax.set_ylabel("X, Reactance (Ω)")
ax.set_title("Impedance measurement (R vs X)")
ax.grid(True)

# 초기 빈 데이터 리스트 (측정 결과 저장)
data_R = []
data_X = []

# 버튼 영역 생성 (버튼을 그래프 하단 가운데 정렬)
# 전체 버튼 영역의 가로 길이: 0.4, 왼쪽 여백: 0.3, 버튼 간 간격: 0.05, 버튼 폭: 0.1
ax_start = plt.axes([0.3, 0.1, 0.1, 0.075])
ax_stop  = plt.axes([0.45, 0.1, 0.1, 0.075])
ax_reset = plt.axes([0.6, 0.1, 0.1, 0.075])

btn_start = Button(ax_start, 'Start')
btn_stop  = Button(ax_stop, 'Stop')
btn_reset = Button(ax_reset, 'Reset')

# ---------------------------
# 측정 함수 (한 번의 측정)
# ---------------------------
def measure_once():
    # 고정 주파수 재설정 (필요시)
    dwf.FDwfAnalogImpedanceFrequencySet(hdwf, c_double(fixed_freq))
    
    # 측정 준비 상태 확인 (타임아웃 1초)
    sts = c_byte()
    timeout_sec = 1.0
    start_wait = time.time()
    while True:
        if dwf.FDwfAnalogImpedanceStatus(hdwf, byref(sts)) == 0:
            dwf.FDwfGetLastErrorMsg(szerr)
            print("오류:", szerr.value.decode())
            return None, None
        if sts.value == 2:
            break
        if time.time() - start_wait > timeout_sec:
            print("측정 준비 타임아웃")
            break
    
    # 임피던스 측정 (저항과 리액턴스)
    resistance = c_double()
    reactance = c_double()
    dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceResistance, byref(resistance))
    dwf.FDwfAnalogImpedanceStatusMeasure(hdwf, DwfAnalogImpedanceReactance, byref(reactance))
    
    # 절대값 (로그 스케일 표시 등을 고려)
    return abs(resistance.value), abs(reactance.value)

# ---------------------------
# 측정 반복 스레드 함수
# ---------------------------
def measurement_loop():
    global running, data_R, data_X
    while running:
        R, X = measure_once()
        if R is not None and X is not None:
            data_R.append(R)
            data_X.append(X)
            # 그래프에 'X' 마커 추가
            ax.plot(R, X, marker='x', color='red', markersize=8)
            fig.canvas.draw_idle()
            print("측정 결과 - R: {:.3f} Ω, X: {:.3f} Ω".format(R, X))
        # 측정 주기 (예: 1초 간격)
        time.sleep(1)

# ---------------------------
# 버튼 콜백 함수
# ---------------------------
def start_callback(event):
    global running, meas_thread
    if not running:
        print("Start measurement")
        running = True
        # 측정 스레드 생성 및 시작
        meas_thread = threading.Thread(target=measurement_loop)
        meas_thread.daemon = True
        meas_thread.start()

def stop_callback(event):
    global running, meas_thread
    if running:
        print("Puse measurement")
        running = False
        # 스레드 종료를 기다림 (필요시 join)
        if meas_thread is not None:
            meas_thread.join()
            meas_thread = None

def reset_callback(event):
    global data_R, data_X
    print("Graph initialize")
    data_R = []
    data_X = []
    ax.cla()  # 현재 축 내용 삭제
    # 축 제목 및 레이블 재설정
    ax.set_xlabel("R, Resistance  (Ω)")
    ax.set_ylabel("X, Reactance (Ω)")
    ax.set_title("Impedance measurement (R vs X)")
    ax.grid(True)
    fig.canvas.draw_idle()

# 버튼에 콜백 함수 연결
btn_start.on_clicked(start_callback)
btn_stop.on_clicked(stop_callback)
btn_reset.on_clicked(reset_callback)

# ---------------------------
# matplotlib 이벤트 루프 실행
# ---------------------------
plt.show()

# ---------------------------
# 측정 종료 후 정리
# ---------------------------
# 측정 중이라면 중지 처리
if running:
    running = False
    if meas_thread is not None:
        meas_thread.join()

# 측정 종료 (장치 닫기)
dwf.FDwfAnalogImpedanceConfigure(hdwf, c_int(0))  # 측정 중지
dwf.FDwfDeviceClose(hdwf)
