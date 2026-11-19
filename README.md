# invernadero-iot-esp32

Este proyecto utiliza un sistema de automatización e IoT para el control microclimático de un invernadero. Su propósito es evitar pérdidas en cultivos mediante el monitoreo de temperatura y humedad, utilizando un ESP32 (simulado en Wokwi y con posiblidad de maquetarlo en la vida real) y sincronización MQTT con una interfaz gráfica para control manual y automático.

## Estructura

| Carpeta | Uso | Diagrama |
| :--- | :--- | :--- |
| Raíz del proyecto | Simulación en Wokwi | `diagram.json` |
| `configuracionESP32_maqueta/` | Placa física (maqueta) | `configuracionESP32_maqueta/diagram.json` |
| `interfaz/` | App en el PC para ver datos y controlar (Flet + MQTT) | — |

El código (`main.py`, `sensores.py`, `actuadores.py`) es el mismo en las dos carpetas. Lo único que cambia es `config.py`, donde están la red Wi-Fi y los pines de cada versión.

## Pines de la simulación (Wokwi)

| Componente | Pin (GPIO) |
| :--- | :---: |
| **Sensor DHT22** | 4 |
| **Botón de Modo** | 14 |
| **Servomotor SG90** | 13 |
| **LED Verde** | 15 |
| **LED Rojo** | 12 |
| **Buzzer** | 27 |
| **Relé (bombillo)** | 26 |

## Pines de la maqueta física

| Componente | Pin (GPIO) | Tipo | Descripción |
| :--- | :---: | :---: | :--- |
| **Sensor DHT22** | 15 | Entrada | Lecturas de temperatura ambiente (°C) y humedad relativa (%). |
| **Botón de Emergencia / Modo** | 13 | Entrada | Pull-Up interno. Alterna entre modo Automático/Manual o silencia alarmas. |
| **Servomotor SG90** | 18 | Salida (PWM) | Regula la apertura de la compuerta de ventilación. |
| **LED Verde** | 4 | Salida | Indica estado climático óptimo. |
| **LED Rojo** | 2 | Salida | Indica alerta por exceso de temperatura o humedad crítica. |
| **Buzzer (Zumbador activo)** | 5 | Salida | Se activa cuando la temperatura supera el umbral crítico. En modo manual se puede silenciar. |
| **Relé SRD-05VDC-SL-C (IN)** | 26 | Salida | Prende el bombillo de 9 V. Activo en bajo: 0 V lo enciende. |

### Conexión del relé y el bombillo (maqueta)

| Relé | Conectar a |
| :--- | :--- |
| VCC (+) | **3V3** del ESP32 (con VIN de 5 V el relé no se apaga) |
| GND (−) | GND del ESP32 |
| IN (S) | GPIO 26 |
| COM | + de la batería de 9 V |
| NO | Un terminal del bombillo (el otro va al − de la batería) |

La batería de 9 V no se conecta al ESP32: el relé separa los dos circuitos. El bombillo debe ser de 9 V.

## Funcionamiento

**Modo AUTO**
- Si la temperatura promedio supera `umbral_temp` (30 °C), la compuerta se abre (0°), se prende el LED rojo y suena el buzzer. Si no, la compuerta se cierra (145°).
- El bombillo se prende solo al llegar a `umbral_bombillo` (25 °C) y se apaga cuando baja 0,5 °C.

**Modo MANUAL**
- La compuerta y el bombillo se controlan desde la interfaz.
- La alerta sigue funcionando, pero el pitido se puede silenciar. Al volver a AUTO vuelve a sonar.

El servo trabaja solo entre **0° (compuerta abierta)** y **145° (compuerta cerrada)**.

## Comandos MQTT

Broker `broker.hivemq.com`. El ESP32 publica su estado en `invernadero/telemetria` cada 2 s y recibe órdenes en `invernadero/comandos`:

```json
{ "modo": "MANUAL" }
{ "angulo_forzado": 0 }
{ "bombillo": true }
{ "silenciar": true }
{ "umbral_temp": 30.0 }
{ "umbral_bombillo": 25.0 }
```

`angulo_forzado`, `bombillo` y `silenciar` solo se aplican en modo MANUAL.

## Interfaz

En `interfaz/` hay una app sencilla hecha con Flet que muestra temperatura, humedad y alerta, y tiene botones para cambiar de modo, abrir/cerrar la compuerta, prender/apagar el bombillo y silenciar el pitido. Se abre con doble clic en `interfaz/abrir_app.bat` (instala las librerías la primera vez) o con:

```bash
cd interfaz
pip install -r requirements.txt
python app_simple.py
```