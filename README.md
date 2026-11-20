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

Aplicación de escritorio hecha con **Tkinter** para ver el estado del invernadero y controlarlo. Por defecto funciona con **datos simulados**, así que no necesita el ESP32. Desde la lista desplegable *Fuente de datos* se puede cambiar a **ESP32 por MQTT** para usar los datos reales.

### Cómo abrirla

Doble clic en `interfaz/abrir_app.bat`, o:

```bash
cd interfaz
python app.py
```

Tkinter viene incluido con Python. Solo el modo MQTT necesita `pip install -r requirements.txt` (paho-mqtt).

### Qué tiene

| Sección | Qué muestra o hace | Widgets |
| :--- | :--- | :--- |
| Encabezado | Título y selector de fuente de datos | `Label`, `Combobox` |
| Variables | Temperatura actual, promedio y humedad | `Label`, `Progressbar` |
| Estado del sistema | Modo, compuerta, bombillo, pitido, umbrales y alarma que parpadea | `Label` con colores |
| Controles | Modo AUTO/MANUAL, abrir/cerrar compuerta, bombillo, silenciar | `Button` |
| Configuración | Umbral de alarma y del bombillo, con validación | `Entry`, `Button` |
| Historial | Tabla de mediciones y lista de eventos | `Notebook`, `Treeview`, `Listbox`, `Scrollbar` |
| Barra inferior | Fuente, última lectura, número de lecturas y tiempo de uso | `Label` |

### Archivos

| Archivo | Contenido |
| :--- | :--- |
| `app.py` | Clase `AppInvernadero` (hereda de `tk.Tk`): arma la ventana, une los paneles y repite `actualizar()` cada 2 s con `after()` |
| `panel_variables.py` | Clase `PanelVariables` |
| `panel_estado.py` | Clase `PanelEstado` (indicadores y alarma) |
| `panel_controles.py` | Clase `PanelControles` |
| `panel_configuracion.py` | Clase `PanelConfiguracion` |
| `panel_historial.py` | Clase `PanelHistorial` |
| `validacion.py` | Función `validar_numero()` |
| `simulador.py` | Clase `SimuladorInvernadero`: genera datos con la misma lógica del firmware |
| `conexion_mqtt.py` | Clase `ConexionMQTT`: recibe la telemetría y envía órdenes al ESP32 |

### Conceptos usados

- **POO:** cada panel es una clase que hereda de `ttk.LabelFrame` y tiene su método `mostrar(estado)`. `SimuladorInvernadero` y `ConexionMQTT` tienen los mismos métodos (`actualizar`, `estado_actual`, `aplicar_comando`), así que la ventana trabaja igual con cualquiera de las dos fuentes.
- **Gestores de geometría:** `grid` para la ventana principal y los paneles con filas y columnas, y `pack` dentro de los paneles de controles e historial.
- **`command`:** en los botones (por ejemplo `command=self.abrir_compuerta`). La función se llama sin argumentos.
- **`bind`:** `<Return>` en los `Entry` aplica los umbrales y `<<ComboboxSelected>>` cambia la fuente de datos. La función recibe el `evento`.
- **Actualización periódica:** `after(2000, self.actualizar)` pide datos nuevos cada 2 s, y `after(500, self.parpadear)` hace parpadear la alarma.
- **Validación:** el campo no puede estar vacío, debe ser un número (acepta coma o punto), debe estar dentro del rango, y el umbral del bombillo debe ser menor que el de alarma. Los errores se muestran en rojo y quedan en el historial de eventos.
- **Datos simulados:** la temperatura sube poco a poco y baja cuando la compuerta está abierta, así que en modo AUTO se ve cómo se activa y se apaga la alarma.