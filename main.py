#
# ダストセンサー動作検証 pi pico microPython
# 2021-05-10  YAMATEC
#
import os
import math
from machine import Pin
import utime

led = Pin(25, Pin.OUT)
sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)

DPIN = 0
dust = Pin(DPIN, Pin.IN)

print("dust sense start")

#パルス幅計測 
def pulseIn(DPIN, sampletime ):
    start_pulse = 0   #low level
    end_pulse = 1     #high level
    pulse_ttl = 0
    st = utime.ticks_ms()
    while utime.ticks_ms()-st < sampletime:
        t_start = st
        while (dust.value() == end_pulse) and (utime.ticks_ms()-st < sampletime):
            t_start = utime.ticks_ms()
        led.value(1)
        t_end = utime.ticks_ms()
        while (dust.value() == start_pulse) and (utime.ticks_ms()-st < sampletime):
            t_end = utime.ticks_ms()
        pulse_ttl += t_end - t_start
        led.value(0)
    return pulse_ttl

#単位をμg/m3に変換
def pcs2ugm3(pcs):
    pi = 3.14159
    density = 1.65 * pow (10, 12)   # 全粒子密度(1.65E12μg/m3)
    r25 = 0.44 * pow (10, -6)       # PM2.5粒子の半径(0.44μm)
    vol25 = (4.0/3.0) * pi * pow (r25, 3)
    mass25 = density * vol25        # μg
    K = 3531.5                      # per m3 
    return pcs * K * mass25         # μg/m^3に変換して返す

#ダスト計測
def get_dust(DPIN):
    t0 = utime.ticks_ms()
    t = 0
    ts = 30 *1000 # サンプリング時間(ms)
    while True:
        t = pulseIn(DPIN, ts)       # LOW状態の時間tを求める
        if (t > ts):
            print("Time over")
            break
        else:
            ratio = (100*t)/ts      # LOWの割合[0-100%]
            concent = 1.1 * pow(ratio,3) - 3.8 * pow(ratio,2) + 520 * ratio + 0.62  # ほこりの濃度を算出
            print(round(concent,2), "[pcs/0.01cf] / ", end="")
            print(round(pcs2ugm3(concent),2), "[ug/m3] / ", end="")
            print(t, "[msec] / ", end="")
            print(round(ratio,2), "[%] / ", end="")
            reading = sensor_temp.read_u16() * conversion_factor
            temperature = 27 - (reading - 0.706)/0.001721
            print(round(temperature,2), "[*C]")
            break

while True:
#    utime.sleep(1.0)
#    led.value(1)
#    utime.sleep(1.0)
#    led.value(0)
    get_dust(DPIN)
