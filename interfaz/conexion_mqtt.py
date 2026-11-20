import json
import time
import uuid

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

BROKER = "broker.hivemq.com"
PUERTO = 1883
TOPIC_TELEMETRIA = "invernadero/telemetria"
TOPIC_COMANDOS = "invernadero/comandos"
SEGUNDOS_SIN_DATOS = 8


class ConexionMQTT:
    def __init__(self):
        self.cliente = None
        self.conectado = False
        self.estado = None
        self.hora_ultimo_dato = 0.0

    def disponible(self):
        return mqtt is not None

    def descripcion(self):
        conexion = "conectado" if self.conectado else "conectando..."
        if self.conectado and not self.hay_datos_recientes():
            conexion = "conectado, esperando datos del ESP32"
        return f"ESP32 por MQTT ({BROKER}, {conexion})"

    def conectar(self):
        if not self.disponible():
            raise RuntimeError("Falta instalar paho-mqtt: pip install paho-mqtt")

        self.cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="interfaz_" + uuid.uuid4().hex[:6])
        self.cliente.on_connect = self.al_conectar
        self.cliente.on_disconnect = self.al_desconectar
        self.cliente.on_message = self.al_recibir
        self.cliente.connect_async(BROKER, PUERTO)
        self.cliente.loop_start()

    def desconectar(self):
        if self.cliente is not None:
            self.cliente.loop_stop()
            self.cliente.disconnect()
            self.cliente = None
        self.conectado = False
        self.estado = None

    def al_conectar(self, cliente, datos_usuario, banderas, codigo, propiedades):
        self.conectado = not codigo.is_failure
        if self.conectado:
            cliente.subscribe(TOPIC_TELEMETRIA)

    def al_desconectar(self, cliente, datos_usuario, banderas, codigo, propiedades):
        self.conectado = False

    def al_recibir(self, cliente, datos_usuario, mensaje):
        try:
            self.estado = json.loads(mensaje.payload)
            self.hora_ultimo_dato = time.time()
        except ValueError:
            pass

    def hay_datos_recientes(self):
        return self.estado is not None and time.time() - self.hora_ultimo_dato < SEGUNDOS_SIN_DATOS

    def estado_actual(self):
        return dict(self.estado) if self.hay_datos_recientes() else None

    def actualizar(self):
        return self.estado_actual()

    def aplicar_comando(self, comando):
        if self.cliente is not None:
            self.cliente.publish(TOPIC_COMANDOS, json.dumps(comando))
