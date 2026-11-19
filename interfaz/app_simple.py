"""
Invernadero ESP32 - Interfaz SIMPLE (versión para exponer).

Muestra temperatura, humedad y alerta, y permite:
  - cambiar entre modo AUTO y MANUAL
  - en MANUAL: abrir/cerrar la compuerta, prender/apagar el bombillo y silenciar el pitido

La app completa (con gráficas y estadísticas) sigue en app_invernadero.py.
Ejecutar:  python app_simple.py
"""

import asyncio
import json
import time
import uuid

import flet as ft
import paho.mqtt.client as mqtt

# --- Conexión MQTT (los mismos datos que usa el ESP32 en main.py) ---
BROKER = "broker.hivemq.com"
TOPIC_DATOS = "invernadero/telemetria"    # ESP32 -> app
TOPIC_COMANDOS = "invernadero/comandos"   # app -> ESP32

ABIERTA = 0     # ángulo del servo con la compuerta abierta
CERRADA = 145   # ángulo del servo con la compuerta cerrada

datos = {}          # último mensaje recibido del ESP32
hora_datos = 0.0    # cuándo llegó


def al_recibir(client, userdata, msg):
    """Se ejecuta cada vez que el ESP32 envía sus datos (cada 2 s)."""
    global datos, hora_datos
    try:
        datos = json.loads(msg.payload)
        hora_datos = time.time()
    except ValueError:
        pass


cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="app_simple_" + uuid.uuid4().hex[:6])
cliente.on_connect = lambda client, userdata, flags, rc, props: client.subscribe(TOPIC_DATOS)
cliente.on_message = al_recibir


def enviar(comando):
    """Envía una orden al ESP32, por ejemplo {"modo": "MANUAL"}."""
    cliente.publish(TOPIC_COMANDOS, json.dumps(comando))


def tarjeta(titulo, icono, valor):
    """Cuadro con un título, un ícono y un valor grande."""
    return ft.Card(
        expand=True,
        content=ft.Container(
            padding=20,
            content=ft.Column(
                [ft.Row([ft.Icon(icono), ft.Text(titulo, size=16)]), valor],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ),
    )


def main(page: ft.Page):
    page.title = "Invernadero ESP32"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)
    page.padding = 30
    page.window.width = 820
    page.window.height = 620

    # --- Textos que se actualizan con los datos del ESP32 ---
    txt_temp = ft.Text("--", size=36, weight=ft.FontWeight.BOLD)
    txt_hum = ft.Text("--", size=36, weight=ft.FontWeight.BOLD)
    txt_alerta = ft.Text("--", size=36, weight=ft.FontWeight.BOLD)
    txt_estado = ft.Text("Esperando datos del ESP32...", size=16)

    # --- Botones ---
    btn_auto = ft.FilledButton("Modo AUTO", icon=ft.Icons.AUTO_MODE, on_click=lambda e: enviar({"modo": "AUTO"}))
    btn_manual = ft.FilledButton("Modo MANUAL", icon=ft.Icons.PAN_TOOL, on_click=lambda e: enviar({"modo": "MANUAL"}))

    botones_manual = ft.Row(
        [
            ft.OutlinedButton("Abrir compuerta", on_click=lambda e: enviar({"angulo_forzado": ABIERTA})),
            ft.OutlinedButton("Cerrar compuerta", on_click=lambda e: enviar({"angulo_forzado": CERRADA})),
            ft.OutlinedButton("Prender bombillo", on_click=lambda e: enviar({"bombillo": True})),
            ft.OutlinedButton("Apagar bombillo", on_click=lambda e: enviar({"bombillo": False})),
            ft.OutlinedButton("Silenciar pitido", on_click=lambda e: enviar({"silenciar": not datos.get("silenciado")})),
        ],
        wrap=True,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    page.add(
        ft.Text("Invernadero ESP32", size=30, weight=ft.FontWeight.BOLD),
        txt_estado,
        ft.Row(
            [
                tarjeta("Temperatura", ft.Icons.THERMOSTAT, txt_temp),
                tarjeta("Humedad", ft.Icons.WATER_DROP, txt_hum),
                tarjeta("Alerta", ft.Icons.WARNING_AMBER, txt_alerta),
            ]
        ),
        ft.Row([btn_auto, btn_manual], alignment=ft.MainAxisAlignment.CENTER),
        ft.Text("Controles (solo en modo MANUAL):", size=16),
        botones_manual,
    )

    async def actualizar():
        """Cada segundo pasa los datos del ESP32 a la pantalla."""
        while True:
            if datos and time.time() - hora_datos < 8:
                manual = datos["modo"] == "MANUAL"
                angulo = datos["angulo_ventana"]
                compuerta = "Abierta" if angulo == ABIERTA else "Cerrada" if angulo == CERRADA else f"{angulo}°"
                bombillo = "Prendido" if datos.get("bombillo") else "Apagado"

                txt_temp.value = f"{datos['temp_promedio']:.1f} °C"
                txt_hum.value = f"{datos['humedad']:.0f} %"
                alerta = datos["alerta"] != "NORMAL"
                txt_alerta.value = "¡CALOR!" if alerta else "Normal"
                txt_alerta.color = ft.Colors.RED if alerta else ft.Colors.GREEN
                txt_estado.value = f"Modo {datos['modo']}  ·  Compuerta: {compuerta}  ·  Bombillo: {bombillo}"

                botones_manual.disabled = not manual
                botones_manual.controls[4].content = "Activar pitido" if datos.get("silenciado") else "Silenciar pitido"
            else:
                txt_estado.value = "Esperando datos del ESP32..."
                botones_manual.disabled = True
            page.update()
            await asyncio.sleep(1)

    page.run_task(actualizar)


if __name__ == "__main__":
    cliente.connect_async(BROKER, 1883)
    cliente.loop_start()
    ft.run(main)
