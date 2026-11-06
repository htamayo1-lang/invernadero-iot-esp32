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

VENTANA_CERRADA = 0
VENTANA_ABIERTA = 90
PAUSA_ANTIRREBOTE = 0.4
PAUSA_CICLO = 2

boton_modo = Pin(config.PIN_BOTON, Pin.IN, Pin.PULL_UP)

estado_sistema = {
    "temp_actual": 0.0,
    "temp_promedio": 0.0,
    "humedad": 0.0,
    "umbral_temp": 30.0,
    "modo": "AUTO",
    "angulo_ventana": VENTANA_CERRADA,
    "alerta": "NORMAL"
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


def recibir_comando_mqtt(topic, msg):
    try:
        datos = ujson.loads(msg.decode())

        if "modo" in datos:
            estado_sistema["modo"] = datos["modo"]

        if "umbral_temp" in datos:
            estado_sistema["umbral_temp"] = float(datos["umbral_temp"])

        if "angulo_forzado" in datos and estado_sistema["modo"] == "MANUAL":
            mover_ventana(int(datos["angulo_forzado"]))

        print("Comando MQTT aplicado:", datos)
    except Exception as e:
        print("Error procesando comando MQTT:", e)


def boton_presionado():
    return boton_modo.value() == 0


def cambiar_modo():
    if estado_sistema["modo"] == "AUTO":
        estado_sistema["modo"] = "MANUAL"
        mover_ventana(VENTANA_ABIERTA)
    else:
        estado_sistema["modo"] = "AUTO"

    print("Modo cambiado por botón físico a:", estado_sistema["modo"])
    time.sleep(PAUSA_ANTIRREBOTE)


def revisar_mensajes(cliente):
    if cliente is None:
        return
    try:
        cliente.check_msg()
    except Exception:
        pass


def actualizar_lecturas():
    temp_actual, temp_promedio, humedad = sensores.leer_clima()
    estado_sistema["temp_actual"] = temp_actual
    estado_sistema["temp_promedio"] = temp_promedio
    estado_sistema["humedad"] = humedad


def control_automatico():
    hace_calor = estado_sistema["temp_promedio"] > estado_sistema["umbral_temp"]

    if hace_calor:
        mover_ventana(VENTANA_ABIERTA)
        estado_sistema["alerta"] = "ALTA_TEMP"
    else:
        mover_ventana(VENTANA_CERRADA)
        estado_sistema["alerta"] = "NORMAL"

    actuadores.actualizar_alertas(hace_calor)


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
    return cliente


cliente = iniciar()

while True:
    if boton_presionado():
        cambiar_modo()

    revisar_mensajes(cliente)
    actualizar_lecturas()

    if estado_sistema["modo"] == "AUTO":
        control_automatico()

    publicar_telemetria(cliente)
    time.sleep(PAUSA_CICLO)
