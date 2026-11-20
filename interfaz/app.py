import json
import random
import time
import tkinter as tk
from tkinter import ttk

import paho.mqtt.client as mqtt

UMBRAL_MIN = 20
UMBRAL_MAX = 45

BROKER = "broker.hivemq.com"
TOPIC_DATOS = "invernadero/telemetria"
TOPIC_COMANDOS = "invernadero/comandos"
SEGUNDOS_SIN_DATOS = 6
VENTANA_ABIERTA = 0
VENTANA_CERRADA = 145


class AppInvernadero:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Invernadero IoT")
        self.ventana.geometry("520x620")

        self.temperatura = 25.0
        self.humedad = 60.0
        self.umbral = 30.0
        self.modo = "AUTO"
        self.compuerta_abierta = False
        self.bombillo_prendido = False

        self.datos_esp32 = None
        self.hora_datos_esp32 = 0
        self.fuente = ""

        self.crear_variables()
        self.crear_estado()
        self.crear_controles()
        self.crear_configuracion()
        self.crear_historial()

        self.conectar_mqtt()
        self.actualizar()

    def conectar_mqtt(self):
        self.cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.cliente.on_connect = self.al_conectar
        self.cliente.on_message = self.recibir_datos
        self.cliente.connect_async(BROKER, 1883)
        self.cliente.loop_start()

    def al_conectar(self, cliente, userdata, flags, codigo, propiedades):
        cliente.subscribe(TOPIC_DATOS)

    def recibir_datos(self, cliente, userdata, mensaje):
        try:
            self.datos_esp32 = json.loads(mensaje.payload)
            self.hora_datos_esp32 = time.time()
        except ValueError:
            pass

    def enviar(self, comando):
        self.cliente.publish(TOPIC_COMANDOS, json.dumps(comando))

    def hay_datos_esp32(self):
        return self.datos_esp32 is not None and time.time() - self.hora_datos_esp32 < SEGUNDOS_SIN_DATOS

    def usar_datos_esp32(self):
        datos = self.datos_esp32
        self.temperatura = datos["temp_promedio"]
        self.humedad = datos["humedad"]
        self.modo = datos["modo"]
        self.umbral = datos["umbral_temp"]
        self.compuerta_abierta = datos["angulo_ventana"] == VENTANA_ABIERTA
        self.bombillo_prendido = datos["bombillo"]

    def crear_variables(self):
        marco = tk.LabelFrame(self.ventana, text="Variables", padx=10, pady=10)
        marco.pack(fill="x", padx=10, pady=5)

        self.lbl_temperatura = tk.Label(marco, text="Temperatura: --", font=("Arial", 14))
        self.lbl_temperatura.pack(anchor="w")

        self.lbl_humedad = tk.Label(marco, text="Humedad: --", font=("Arial", 14))
        self.lbl_humedad.pack(anchor="w")

        self.barra_humedad = ttk.Progressbar(marco, maximum=100)
        self.barra_humedad.pack(fill="x", pady=5)

    def crear_estado(self):
        marco = tk.LabelFrame(self.ventana, text="Estado", padx=10, pady=10)
        marco.pack(fill="x", padx=10, pady=5)

        self.lbl_fuente = tk.Label(marco, text="--", font=("Arial", 10, "bold"))
        self.lbl_fuente.pack(anchor="w")

        self.lbl_estado = tk.Label(marco, text="--")
        self.lbl_estado.pack(anchor="w")

        self.lbl_alarma = tk.Label(marco, text="--", font=("Arial", 14, "bold"), fg="white", bg="gray")
        self.lbl_alarma.pack(fill="x", pady=5)

    def crear_controles(self):
        marco = tk.LabelFrame(self.ventana, text="Controles", padx=10, pady=10)
        marco.pack(fill="x", padx=10, pady=5)

        tk.Label(marco, text="Modo:").grid(row=0, column=0, sticky="w")
        self.combo_modo = ttk.Combobox(marco, values=["AUTO", "MANUAL"], state="readonly", width=10)
        self.combo_modo.set("AUTO")
        self.combo_modo.grid(row=0, column=1, sticky="w", pady=3)
        self.combo_modo.bind("<<ComboboxSelected>>", self.cambiar_modo)

        tk.Button(marco, text="Abrir / cerrar compuerta", command=self.mover_compuerta).grid(row=1, column=0, padx=3, pady=3)
        tk.Button(marco, text="Prender / apagar bombillo", command=self.cambiar_bombillo).grid(row=1, column=1, padx=3, pady=3)

    def crear_configuracion(self):
        marco = tk.LabelFrame(self.ventana, text="Configuración", padx=10, pady=10)
        marco.pack(fill="x", padx=10, pady=5)

        tk.Label(marco, text="Umbral de alarma (°C):").grid(row=0, column=0)
        self.entry_umbral = tk.Entry(marco, width=8)
        self.entry_umbral.insert(0, str(self.umbral))
        self.entry_umbral.grid(row=0, column=1, padx=5)
        self.entry_umbral.bind("<Return>", self.aplicar_umbral)
        tk.Button(marco, text="Aplicar", command=self.aplicar_umbral).grid(row=0, column=2)

        self.lbl_mensaje = tk.Label(marco, text="")
        self.lbl_mensaje.grid(row=1, column=0, columnspan=3, sticky="w")

    def crear_historial(self):
        marco = tk.LabelFrame(self.ventana, text="Historial", padx=10, pady=10)
        marco.pack(fill="both", expand=True, padx=10, pady=5)

        self.lista_historial = tk.Listbox(marco)
        self.lista_historial.pack(fill="both", expand=True)

    def simular_datos(self):
        self.temperatura += random.uniform(-0.3, 0.8)
        if self.compuerta_abierta:
            self.temperatura -= 1.2
        self.temperatura = max(15, min(self.temperatura, 40))
        self.humedad = random.uniform(50, 70)

    def actualizar(self):
        if self.hay_datos_esp32():
            self.usar_datos_esp32()
            fuente = "ESP32 (maqueta)"
        else:
            self.simular_datos()
            if self.modo == "AUTO":
                self.compuerta_abierta = self.temperatura > self.umbral
            fuente = "simulados (sin ESP32)"

        if fuente != self.fuente:
            self.fuente = fuente
            self.agregar_historial(f"Usando datos {fuente}")

        self.mostrar_datos()
        self.agregar_historial(f"Temp: {self.temperatura:.1f} °C   Hum: {self.humedad:.0f} %")
        self.ventana.after(2000, self.actualizar)

    def mostrar_datos(self):
        self.lbl_temperatura.config(text=f"Temperatura: {self.temperatura:.1f} °C")
        self.lbl_humedad.config(text=f"Humedad: {self.humedad:.0f} %")
        self.barra_humedad["value"] = self.humedad
        self.lbl_fuente.config(text=f"Datos: {self.fuente}")
        self.combo_modo.set(self.modo)

        compuerta = "Abierta" if self.compuerta_abierta else "Cerrada"
        bombillo = "Prendido" if self.bombillo_prendido else "Apagado"
        self.lbl_estado.config(text=f"Modo: {self.modo}   |   Compuerta: {compuerta}   |   Bombillo: {bombillo}")

        if self.temperatura > self.umbral:
            self.lbl_alarma.config(text="ALERTA: temperatura alta", bg="red")
        else:
            self.lbl_alarma.config(text="Temperatura normal", bg="green")

    def agregar_historial(self, texto):
        hora = time.strftime("%H:%M:%S")
        self.lista_historial.insert(0, f"{hora}   {texto}")

    def cambiar_modo(self, evento):
        self.modo = self.combo_modo.get()
        self.enviar({"modo": self.modo})
        self.agregar_historial(f"Modo cambiado a {self.modo}")
        self.mostrar_datos()

    def mover_compuerta(self):
        if self.modo != "MANUAL":
            self.agregar_historial("Cambia a modo MANUAL para mover la compuerta")
            return

        self.compuerta_abierta = not self.compuerta_abierta
        angulo = VENTANA_ABIERTA if self.compuerta_abierta else VENTANA_CERRADA
        self.enviar({"angulo_forzado": angulo})
        self.agregar_historial("Compuerta abierta" if self.compuerta_abierta else "Compuerta cerrada")
        self.mostrar_datos()

    def cambiar_bombillo(self):
        if self.modo != "MANUAL":
            self.agregar_historial("Cambia a modo MANUAL para usar el bombillo")
            return

        self.bombillo_prendido = not self.bombillo_prendido
        self.enviar({"bombillo": self.bombillo_prendido})
        self.agregar_historial("Bombillo prendido" if self.bombillo_prendido else "Bombillo apagado")
        self.mostrar_datos()

    def aplicar_umbral(self, evento=None):
        try:
            valor = float(self.entry_umbral.get())
        except ValueError:
            self.lbl_mensaje.config(text="Error: escribe un número", fg="red")
            return

        if valor < UMBRAL_MIN or valor > UMBRAL_MAX:
            self.lbl_mensaje.config(text=f"Error: el umbral debe estar entre {UMBRAL_MIN} y {UMBRAL_MAX}", fg="red")
            return

        self.umbral = valor
        self.enviar({"umbral_temp": valor})
        self.lbl_mensaje.config(text=f"Umbral guardado: {valor} °C", fg="green")
        self.agregar_historial(f"Umbral cambiado a {valor} °C")
        self.mostrar_datos()


if __name__ == "__main__":
    ventana = tk.Tk()
    app = AppInvernadero(ventana)
    ventana.mainloop()
