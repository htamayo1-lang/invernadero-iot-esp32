# invernadero-iot-esp32

Este proyecto utiliza un sistema de automatización e IoT para el control microclimático de un invernadero. Su propósito es evitar pérdidas en cultivos mediante el monitoreo de temperatura y humedad, utilizando un ESP32 (simulado en Wokwi y con posiblidad de maquetarlo en la vida real) y sincronización MQTT con una interfaz gráfica para control manual y automático.

## Estructura

| Carpeta | Uso | Diagrama |
| :--- | :--- | :--- |
| Raíz del proyecto | Simulación en Wokwi | `diagram.json` |
| `configuracionESP32_maqueta/` | Placa física (maqueta) | `configuracionESP32_maqueta/diagram.json` |

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

## Pines de la maqueta física

| Componente | Pin (GPIO) | Tipo | Descripción |
| :--- | :---: | :---: | :--- |
| **Sensor DHT22** | 15 | Entrada | Lecturas de temperatura ambiente (°C) y humedad relativa (%). |
| **Botón de Emergencia / Modo** | 13 | Entrada | Pull-Up interno. Alterna entre modo Automático/Manual o silencia alarmas. |
| **Servomotor SG90** | 18 | Salida (PWM) | Regula la apertura de la compuerta de ventilación. |
| **LED Verde** | 4 | Salida | Indica estado climático óptimo. |
| **LED Rojo** | 2 | Salida | Indica alerta por exceso de temperatura o humedad crítica. |
| **Buzzer (Zumbador activo)** | 5 | Salida | Se activa cuando la temperatura supera el umbral crítico. |