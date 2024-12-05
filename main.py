import bluetooth
import time
from ble_simple_peripheral import BLESimplePeripheral
import machine



sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / 65535

    

def main():
    # BLE初期化
    ble = bluetooth.BLE()
    peripheral = BLESimplePeripheral(ble, name="お湯溜りボンゴ")

    try:
        while True:
            if peripheral._connections:
                reading = sensor_temp.read_u16() * conversion_factor
                temp = 27 - (reading - 0.706)/0.001721
                temp = round(temp, 1)
                print(temp)
                peripheral.send(str(temp).encode())  # データをバイト列に変換して送信
                print("Data sent.")
            else:
                print("No connections. Waiting...")
            time.sleep(1) # 5秒ごとに送信
    except KeyboardInterrupt:
        print("Program interrupted.")

if __name__ == "__main__":
    main()

