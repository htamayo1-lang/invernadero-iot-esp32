import time
import network
import ujson
from machine import Pin
from umqtt.simple import MQTTClient

import config
import sensores
import actuadores

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = "esp32_invernadero_utp"
TOPIC_PUB = b"invernadero/telemetria"
TOPIC_SUB = b"invernadero/comandos"

VENTANA_ABIERTA = 0
VENTANA_CERRADA = 145
PAUSA_ANTIRREBOTE = 0.4
PAUSA_CICLO = 2
HISTERESIS_BOMBILLO = 0.5

boton_modo = Pin(config.PIN_BOTON, Pin.IN, Pin.PULL_UP)

estado_sistema = {
    "temp_actual": 0.0,
    "temp_promedio": 0.0,
    "humedad": 0.0,
    "umbral_temp": 30.0,
    "modo": "AUTO",
    "angulo_ventana": VENTANA_CERRADA,
    "alerta": "NORMAL",
    "bombillo": False,
    "umbral_bombillo": 25.0,
    "silenciado": False
}


def conectar_wifi(tiempo_max=15):
    print("Conectando a Wi-Fi", config.WIFI_SSID, end="")
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    if wifi.isconnected():
        print(" ¡Ya estaba conectado!", wifi.ifconfig()[0])
        return True

    try:
        wifi.disconnect()
    except OSError:
        pass
    time.sleep(0.5)

    wifi.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    inicio = time.time()
    while not wifi.isconnected():
        if time.time() - inicio > tiempo_max:
            print(" No se pudo conectar (revisa config.py).")
            return False
        print(".", end="")
        time.sleep(0.3)

    print(" ¡Conectado!", wifi.ifconfig()[0])
    return True


def conectar_mqtt():
    try:
        cliente = MQTTClient(CLIENT_ID, MQTT_BROKER)
        cliente.set_callback(recibir_comando_mqtt)
        cliente.connect()
        cliente.subscribe(TOPIC_SUB)
        print("Conectado al broker MQTT exitosamente.")
        return cliente
    except Exception as e:
        print("Modo local sin MQTT:", e)
        return None


def mover_ventana(angulo):
    estado_sistema["angulo_ventana"] = actuadores.mover_ventana(angulo)


def encender_bombillo(encender):
    estado_sistema["bombillo"] = actuadores.encender_bombillo(encender)


def poner_modo(modo):
    estado_sistema["modo"] = modo
    if modo == "AUTO":
        estado_sistema["silenciado"] = False  # en AUTO la alarma siempre suena


def recibir_comando_mqtt(topic, msg):
    try:
        datos = ujson.loads(msg.decode())

        if datos.get("modo") in ("AUTO", "MANUAL"):
            poner_modo(datos["modo"])

        if "umbral_temp" in datos:
            estado_sistema["umbral_temp"] = float(datos["umbral_temp"])

        if "angulo_forzado" in datos and estado_sistema["modo"] == "MANUAL":
            mover_ventana(int(datos["angulo_forzado"]))

        if "umbral_bombillo" in datos:
            estado_sistema["umbral_bombillo"] = float(datos["umbral_bombillo"])

        if "bombillo" in datos and estado_sistema["modo"] == "MANUAL":
            encender_bombillo(datos["bombillo"])

        if "silenciar" in datos and estado_sistema["modo"] == "MANUAL":
            estado_sistema["silenciado"] = bool(datos["silenciar"])

        print("Comando MQTT aplicado:", datos)
    except Exception as e:
        print("Error procesando comando MQTT:", e)


def boton_presionado():
    return boton_modo.value() == 0


def cambiar_modo():
    if estado_sistema["modo"] == "AUTO":
        poner_modo("MANUAL")
        mover_ventana(VENTANA_ABIERTA)
    else:
        poner_modo("AUTO")

    print("Modo cambiado por botón físico a:", estado_sistema["modo"])
    time.sleep(PAUSA_ANTIRREBOTE)


def revisar_mensajes(cliente):
    if cliente is None:
        return
    try:
        cliente.check_msg()
    except Exception:
        pass


def esperar_revisando_mensajes(cliente):
    # Espera PAUSA_CICLO segundos, pero revisa MQTT cada 0.1 s
    # para que los comandos de la app se apliquen casi al instante.
    for _ in range(int(PAUSA_CICLO / 0.1)):
        revisar_mensajes(cliente)
        time.sleep(0.1)


def actualizar_lecturas():
    temp_actual, temp_promedio, humedad = sensores.leer_clima()
    estado_sistema["temp_actual"] = temp_actual
    estado_sistema["temp_promedio"] = temp_promedio
    estado_sistema["humedad"] = humedad


def revisar_alerta():
    # La alerta funciona en AUTO y en MANUAL; en MANUAL el pitido se puede silenciar
    hace_calor = estado_sistema["temp_promedio"] > estado_sistema["umbral_temp"]
    estado_sistema["alerta"] = "ALTA_TEMP" if hace_calor else "NORMAL"
    actuadores.actualizar_alertas(hace_calor, not estado_sistema["silenciado"])
    return hace_calor


def control_automatico(hace_calor):
    if hace_calor:
        mover_ventana(VENTANA_ABIERTA)
    else:
        mover_ventana(VENTANA_CERRADA)


def control_bombillo():
    # Se prende al llegar al umbral y se apaga 0.5 grados por debajo (para que no titile)
    temp = estado_sistema["temp_promedio"]
    umbral = estado_sistema["umbral_bombillo"]

    if not estado_sistema["bombillo"] and temp >= umbral:
        encender_bombillo(True)
    elif estado_sistema["bombillo"] and temp < umbral - HISTERESIS_BOMBILLO:
        encender_bombillo(False)


def publicar_telemetria(cliente):
    mensaje = ujson.dumps(estado_sistema)
    print("Telemetría:", mensaje)

    if cliente is None:
        return
    try:
        cliente.publish(TOPIC_PUB, mensaje)
    except Exception:
        pass


def iniciar():
    cliente = None
    if conectar_wifi():
        cliente = conectar_mqtt()
    else:
        print("Modo local sin Wi-Fi ni MQTT.")

    mover_ventana(VENTANA_CERRADA)
    actuadores.actualizar_alertas(False)
    encender_bombillo(False)
    return cliente


cliente = iniciar()

while True:
    if boton_presionado():
        cambiar_modo()

    revisar_mensajes(cliente)
    actualizar_lecturas()
    hace_calor = revisar_alerta()

    if estado_sistema["modo"] == "AUTO":
        control_automatico(hace_calor)
        control_bombillo()

    publicar_telemetria(cliente)
    esperar_revisando_mensajes(cliente)
