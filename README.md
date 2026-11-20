# invernadero-iot-esp32

Este proyecto utiliza un sistema de automatización e IoT para el control microclimático de un invernadero. Su propósito es evitar pérdidas en cultivos mediante el monitoreo de temperatura y humedad, utilizando un ESP32 (simulado en Wokwi y con posiblidad de maquetarlo en la vida real) y sincronización MQTT con una interfaz gráfica para control manual y automático.

## Estructura

| Carpeta | Uso | Diagrama |
| :--- | :--- | :--- |
| Raíz del proyecto | Simulación en Wokwi | `diagram.json` |
| `configuracionESP32_maqueta/` | Placa física (maqueta) | `configuracionESP32_maqueta/diagram.json` |
| `interfaz/` | Interfaz gráfica en el PC (Tkinter), Parcial 3 | — |

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

## Interfaz gráfica (Parcial 3)

Está en `interfaz/app.py`. Es una ventana hecha con **Tkinter**. Si el ESP32 está enviando datos por MQTT, muestra los datos reales de la maqueta; si no, usa **datos simulados**. Se abre con doble clic en `interfaz/abrir_app.bat` (instala `paho-mqtt` la primera vez) o con:

```bash
cd interfaz
pip install -r requirements.txt
python app.py
```

### Qué hace

- Muestra la temperatura y la humedad (con una barra de progreso) y las actualiza cada 2 segundos.
- Muestra el modo, la compuerta, el bombillo y una alarma: verde si la temperatura es normal y roja si pasa el umbral.
- En modo **AUTO** la compuerta se abre sola cuando hace calor. En modo **MANUAL** se controla con los botones.
- Permite cambiar el umbral de alarma. Valida que sea un número entre 20 y 45.
- Guarda en un historial las mediciones y lo que hace el usuario.
- Cada botón también envía la orden al ESP32 por MQTT, así que la maqueta responde a la interfaz.

### Cómo está hecho

| Concepto | Dónde está |
| :--- | :--- |
| POO | Una clase, `AppInvernadero`. Sus atributos guardan el estado (temperatura, modo, umbral...) y cada parte de la ventana se crea en un método `crear_...` |
| Widgets | `LabelFrame`, `Label`, `Button`, `Entry`, `Combobox`, `Progressbar`, `Listbox` |
| Gestores de geometría | `pack` para poner los marcos uno debajo del otro y `grid` (filas y columnas) dentro de Controles y Configuración |
| `command` | Botones: `command=self.mover_compuerta`. La función no recibe nada |
| `bind` | `<Return>` en el Entry y `<<ComboboxSelected>>` en la lista de modo. La función recibe el `evento` |
| Actualización periódica | `self.ventana.after(2000, self.actualizar)`: `actualizar()` se vuelve a llamar sola cada 2 s |
| Datos simulados | `simular_datos()` usa `random`: la temperatura sube poco a poco y baja si la compuerta está abierta |
| Validación | `aplicar_umbral()`: `try/except` para saber si es número y un `if` para el rango |
| Conexión con el ESP32 | `conectar_mqtt()` se conecta al broker. `recibir_datos()` guarda lo que publica el ESP32 en `invernadero/telemetria` y `enviar()` manda órdenes a `invernadero/comandos`. Si no llegan datos en 6 s, `actualizar()` usa datos simulados |
