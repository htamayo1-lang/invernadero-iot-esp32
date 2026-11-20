import random

VENTANA_ABIERTA = 0
VENTANA_CERRADA = 145
MAX_LECTURAS = 5
HISTERESIS_BOMBILLO = 0.5
TEMP_MINIMA = 15.0
TEMP_MAXIMA = 40.0


class SimuladorInvernadero:
    def __init__(self):
        self.temperatura = 24.0
        self.humedad = 60.0
        self.historial_temp = []
        self.estado = {
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

    def descripcion(self):
        return "Datos simulados (sin ESP32)"

    def estado_actual(self):
        return dict(self.estado)

    def actualizar(self):
        self.leer_sensores()
        hace_calor = self.revisar_alerta()

        if self.estado["modo"] == "AUTO":
            self.control_automatico(hace_calor)
            self.control_bombillo()

        return self.estado_actual()

    def leer_sensores(self):
        cambio = random.uniform(-0.2, 0.8)
        if self.estado["angulo_ventana"] == VENTANA_ABIERTA:
            cambio -= 1.0

        self.temperatura = max(TEMP_MINIMA, min(self.temperatura + cambio, TEMP_MAXIMA))
        self.humedad = max(30.0, min(self.humedad - cambio + random.uniform(-1.5, 1.5), 90.0))

        self.historial_temp.append(self.temperatura)
        if len(self.historial_temp) > MAX_LECTURAS:
            self.historial_temp.pop(0)
        promedio = sum(self.historial_temp) / len(self.historial_temp)

        self.estado["temp_actual"] = round(self.temperatura, 1)
        self.estado["temp_promedio"] = round(promedio, 1)
        self.estado["humedad"] = round(self.humedad, 1)

    def revisar_alerta(self):
        hace_calor = self.estado["temp_promedio"] > self.estado["umbral_temp"]
        self.estado["alerta"] = "ALTA_TEMP" if hace_calor else "NORMAL"
        return hace_calor

    def control_automatico(self, hace_calor):
        self.estado["angulo_ventana"] = VENTANA_ABIERTA if hace_calor else VENTANA_CERRADA

    def control_bombillo(self):
        temp = self.estado["temp_promedio"]
        umbral = self.estado["umbral_bombillo"]

        if not self.estado["bombillo"] and temp >= umbral:
            self.estado["bombillo"] = True
        elif self.estado["bombillo"] and temp < umbral - HISTERESIS_BOMBILLO:
            self.estado["bombillo"] = False

    def aplicar_comando(self, comando):
        if comando.get("modo") in ("AUTO", "MANUAL"):
            self.estado["modo"] = comando["modo"]
            if comando["modo"] == "AUTO":
                self.estado["silenciado"] = False

        if "umbral_temp" in comando:
            self.estado["umbral_temp"] = float(comando["umbral_temp"])

        if "umbral_bombillo" in comando:
            self.estado["umbral_bombillo"] = float(comando["umbral_bombillo"])

        if self.estado["modo"] != "MANUAL":
            return

        if "angulo_forzado" in comando:
            self.estado["angulo_ventana"] = max(VENTANA_ABIERTA, min(int(comando["angulo_forzado"]), VENTANA_CERRADA))

        if "bombillo" in comando:
            self.estado["bombillo"] = bool(comando["bombillo"])

        if "silenciar" in comando:
            self.estado["silenciado"] = bool(comando["silenciar"])
