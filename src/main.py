# main.py - ESP32 (MicroPython) + DHT22 + LED + MQTT (Blynk)
# Projeto: Irrigação Inteligente
# Autor: Gabriel Munhoz Moreira

import network, time
from machine import Pin
import dht

try:
    from umqtt.simple import MQTTClient
except ImportError:
    raise ImportError("Biblioteca umqtt.simple não disponível")

# -------- Configurações de rede --------
SSID = "Wokwi-GUEST"
PWD = ""

# -------- Broker Blynk --------
BROKER = "blynk.cloud"
PORT = 1883
USER = "device"
TOKEN = "r3qD6XAKtJSPGRV9FfCl1XTp_9AKYYU0"

# -------- Datastreams --------
V_TEMP = "V0"
V_SOIL = "V1"
V_PUMP = "V2"
V_LIMIT = "V3"

# -------- GPIO --------
GPIO_DHT = 15  # DHT22 no pino 15
GPIO_LED = 2   # LED no pino 2

# -------- Estado inicial --------
SOIL_LIMIT = 35  # (%) — abaixo disso ativa a bomba
led = Pin(GPIO_LED, Pin.OUT)
sensor = dht.DHT22(Pin(GPIO_DHT))


# -------- Conexão WiFi --------
def connect_wifi():
    net = network.WLAN(network.STA_IF)
    net.active(True)
    try:
        net.config(pm=0xa11140)
    except:
        pass

    if not net.isconnected():
        print("[WiFi] Tentando conexão...")
        net.connect(SSID, PWD)

        for _ in range(120):
            if net.isconnected():
                break
            time.sleep(0.25)

    if not net.isconnected():
        raise RuntimeError("Falha na conexão WiFi.")

    print("[WiFi] Conectado:", net.ifconfig())


# -------- Callback MQTT --------
def callback(topic, msg):
    global SOIL_LIMIT
    tp = topic.decode()
    val = msg.decode().strip().lower()

    if tp.endswith("/" + V_PUMP):
        ativo = val in ("1", "true", "on")
        led.value(1 if ativo else 0)
        print("[MQTT] Pump setado para:", ativo)

    elif tp.endswith("/" + V_LIMIT):
        try:
            SOIL_LIMIT = max(0, min(100, int(float(val))))
            print("[MQTT] Novo limite de umidade:", SOIL_LIMIT)
        except:
            pass


# -------- Conexão MQTT --------
def setup_mqtt():
    cli = MQTTClient(
        client_id="esp32-wokwi",
        server=BROKER,
        port=PORT,
        user=USER,
        password=TOKEN,
        keepalive=45
    )
    cli.set_callback(callback)
    cli.connect()
    cli.subscribe(b"downlink/ds/#")
    print("[MQTT] Conexão estabelecida")
    return cli


def send_data(cli, ds, val):
    cli.publish(b"ds/" + ds.encode(), str(val))


# -------- Loop principal --------
def run():
    connect_wifi()
    cli = setup_mqtt()
    global SOIL_LIMIT

    last_tick = time.ticks_ms()

    while True:
        cli.check_msg()
        now = time.ticks_ms()

        if time.ticks_diff(now, last_tick) > 3000:
            last_tick = now

            try:
                sensor.measure()
                t = sensor.temperature()
                h = sensor.humidity()
            except:
                t, h = 0, 0

            bomba = 1 if h < SOIL_LIMIT else 0
            led.value(bomba)

            send_data(cli, V_TEMP, t)
            send_data(cli, V_SOIL, h)
            send_data(cli, V_LIMIT, SOIL_LIMIT)
            send_data(cli, V_PUMP, bomba)

            print(f"[LOG] T={t}°C | H={h}% | Pump={bomba} | Limit={SOIL_LIMIT}")

        time.sleep_ms(100)


if __name__ == "__main__":
    run()
