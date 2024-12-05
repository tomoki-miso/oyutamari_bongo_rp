import bluetooth
from micropython import const
from machine import Pin
from ble_advertising import advertising_payload

# キャラクタリスティックのフラグ
_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_WRITE = const(0x0008)

# BLE UUID 定義
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

# IRQ イベントコード
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)


class BLESimplePeripheral:
    def __init__(self, ble, name="mpy-uart"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        
        # サービスとキャラクタリスティックを登録
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))

        self._led = Pin("LED", Pin.OUT)  # LED ピンの初期化
        self._led.value(0)  # 初期状態は消灯

        self._payload = advertising_payload(name=name)
        self._connections = set()
        self._advertise()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("Connected", conn_handle)
            self._connections.add(conn_handle)
            self._led.value(1)  # LED を点灯
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            self._led.value(0)  # LED を消灯
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._handle_rx:  # 書き込みキャラクタリスティック
                value = self._ble.gatts_read(self._handle_rx).decode('utf-8')
                print(f"Received data: {value}")

                if value == 'CCC':
                    print("Disconnecting client:", conn_handle)
                    self._connections.remove(conn_handle)
                    self._led.value(0)  # LED を消灯
                    self._advertise()

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def send(self, data):
        """
        接続中のすべてのデバイスにデータを送信します。
        """
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)
        print(f"Sent data: {data}")

