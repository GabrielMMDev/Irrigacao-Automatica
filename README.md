# Sistema de irrigação automática

Neste projeto eu desenvolvi um sistema de automação que monitora a umidade do solo e controla uma bomba de irrigação (simulada por LED) usando **ESP32**, sensor **DHT22** e plataforma **Blynk** via MQTT.

---

## Funcionamento

1. Eu configuro o ESP32 para ler a **temperatura** e a **umidade do solo** pelo sensor DHT22.
2. Sempre que a umidade estiver abaixo do limite que eu defini (Threshold), o LED acende, indicando que a bomba ligaria.
3. Os dados de temperatura, umidade, estado da bomba e limite de umidade são enviados em tempo real para o dashboard do **Blynk**.
4. Eu consigo ajustar o limite de umidade diretamente no Blynk, controlando quando a bomba deve ligar.

---

## Componentes e Pinos

| Componente | Pino ESP32 |
|------------|------------|
| DHT22      | GPIO15     |
| LED        | GPIO2      |

---

## Datastreams no Blynk

| Widget / Datastream | Pin | Função |
|--------------------|-----|--------|
| Temperatura         | V0  | Mostra a temperatura que eu leio |
| Umidade             | V1  | Mostra a umidade do solo |
| Controla Bomba      | V2  | Mostra se a bomba está ligada (LED) |
| Threshold           | V3  | Limite de umidade configurável por mim |

---

## Código e Bibliotecas

No código em **MicroPython**, eu usei:

- `network` → Para conectar o ESP32 ao Wi-Fi  
- `machine.Pin` → Para controlar o LED e o DHT22  
- `dht` → Para ler temperatura e umidade  
- `umqtt.simple` → Para enviar e receber dados via MQTT com o Blynk  

