import bluetooth
import time
from ble_simple_peripheral import BLESimplePeripheral
import machine
from machine import Pin

# 距離センサー設定
trigger_pin = 4
echo_pin = 5
trigger = Pin(trigger_pin, Pin.OUT)
echo = Pin(echo_pin, Pin.IN)

def read_distance():
    # トリガーピンをHIGH
    trigger.high()
    time.sleep_us(11)
    trigger.low()

    # echoがHIGHになるまで待つ
    while (echo.value() == 0):
        pass

    lastreadtime = time.ticks_us() 

    # echoがLOWになるまで待つ(パルス継続時間を測定)
    while (echo.value() == 1):
        pass

    echotime = time.ticks_us() - lastreadtime

    # echotimeが大きいときは障害物なしとみなす
    if echotime > 37000:
        return None
    else:
        distance = (echotime * 0.034) / 2
        distance = round(distance, 1)
        return distance

def main():
    ble = bluetooth.BLE()
    peripheral = BLESimplePeripheral(ble, name="お湯溜りボンゴ")

    try:
        while True:
            if peripheral._connections:
                dist = read_distance()

                if dist is None:
                    dist_str = "No obstacle"
                else:
                    dist_str = f"{dist}"

                data_str = f"{dist_str}"
                peripheral.send(data_str.encode())
                print("Data sent:", data_str)
            else:
                print("No connections. Waiting...")

            time.sleep(1)
    except KeyboardInterrupt:
        print("Program interrupted.")

if __name__ == "__main__":
    main()

