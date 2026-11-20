import time
import tkinter as tk
from tkinter import ttk, messagebox

from simulador import SimuladorInvernadero
from conexion_mqtt import ConexionMQTT
from panel_variables import PanelVariables
from panel_estado import PanelEstado, texto_compuerta
from panel_controles import PanelControles
from panel_historial import PanelHistorial
from panel_configuracion import PanelConfiguracion

INTERVALO_MS = 2000
FUENTE_SIMULADA = "Datos simulados"
FUENTE_MQTT = "ESP32 por MQTT"


class AppInvernadero(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Invernadero IoT - Panel de control")
        self.geometry("980x720")
        self.minsize(900, 640)
        self.state("zoomed")

        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("TButton", padding=3)

        self.simulador = SimuladorInvernadero()
        self.mqtt = ConexionMQTT()
        self.fuente = self.simulador
        self.estado_anterior = None
        self.lecturas = 0
        self.hora_ultima_lectura = "--"
        self.hora_inicio = time.time()

        self.crear_encabezado()
        self.crear_paneles()
        self.crear_barra_estado()

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.registrar_evento("Interfaz iniciada con datos simulados")
        self.actualizar()

    def crear_encabezado(self):
        encabezado = ttk.Frame(self, padding=(15, 6))
        encabezado.grid(row=0, column=0, columnspan=2, sticky="ew")

        ttk.Label(encabezado, text="Invernadero IoT", font=("Segoe UI", 18, "bold")).pack(side="left")

        self.combo_fuente = ttk.Combobox(encabezado, values=[FUENTE_SIMULADA, FUENTE_MQTT], state="readonly", width=18)
        self.combo_fuente.set(FUENTE_SIMULADA)
        self.combo_fuente.bind("<<ComboboxSelected>>", self.cambiar_fuente)
        self.combo_fuente.pack(side="right")
        ttk.Label(encabezado, text="Fuente de datos:").pack(side="right", padx=5)

    def crear_paneles(self):
        self.panel_variables = PanelVariables(self)
        self.panel_variables.grid(row=1, column=0, sticky="nsew", padx=10, pady=3)

        self.panel_estado = PanelEstado(self)
        self.panel_estado.grid(row=1, column=1, sticky="nsew", padx=10, pady=3)

        self.panel_controles = PanelControles(self, self.enviar_comando)
        self.panel_controles.grid(row=2, column=0, sticky="nsew", padx=10, pady=3)

        self.panel_configuracion = PanelConfiguracion(self, self.enviar_comando, self.registrar_evento)
        self.panel_configuracion.grid(row=2, column=1, sticky="nsew", padx=10, pady=3)

        self.panel_historial = PanelHistorial(self)
        self.panel_historial.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=3)

    def crear_barra_estado(self):
        self.lbl_info = ttk.Label(self, text="Iniciando...", relief="sunken", padding=(10, 3))
        self.lbl_info.grid(row=4, column=0, columnspan=2, sticky="ew")

    def actualizar(self):
        estado = self.fuente.actualizar()
        if estado:
            self.lecturas += 1
            self.hora_ultima_lectura = time.strftime("%H:%M:%S")
            self.mostrar(estado)
            self.panel_historial.agregar_medicion(estado)
        else:
            self.panel_variables.mostrar_sin_datos()
            self.panel_controles.mostrar(None)
            self.panel_estado.mostrar_sin_datos()

        self.actualizar_info()
        self.after(INTERVALO_MS, self.actualizar)

    def mostrar(self, estado):
        self.panel_variables.mostrar(estado)
        self.panel_estado.mostrar(estado)
        self.panel_controles.mostrar(estado)
        self.detectar_cambios(estado)
        self.estado_anterior = estado

    def detectar_cambios(self, estado):
        anterior = self.estado_anterior
        if anterior is None:
            return

        if estado["modo"] != anterior["modo"]:
            self.registrar_evento(f"Modo cambiado a {estado['modo']}")

        if estado["alerta"] != anterior["alerta"]:
            if estado["alerta"] == "NORMAL":
                self.registrar_evento("Temperatura normalizada")
            else:
                self.registrar_evento(f"ALERTA: temperatura alta ({estado['temp_promedio']:.1f} °C)")

        if estado["angulo_ventana"] != anterior["angulo_ventana"]:
            self.registrar_evento(f"Compuerta: {texto_compuerta(estado['angulo_ventana'])}")

        if estado["bombillo"] != anterior["bombillo"]:
            self.registrar_evento("Bombillo prendido" if estado["bombillo"] else "Bombillo apagado")

        if estado["silenciado"] != anterior["silenciado"]:
            self.registrar_evento("Pitido silenciado" if estado["silenciado"] else "Pitido activado")

    def registrar_evento(self, texto):
        self.panel_historial.agregar_evento(texto)

    def enviar_comando(self, descripcion, comando):
        self.registrar_evento(f"Orden: {descripcion}")
        self.fuente.aplicar_comando(comando)
        estado = self.fuente.estado_actual()
        if estado:
            self.mostrar(estado)

    def cambiar_fuente(self, evento):
        seleccion = self.combo_fuente.get()

        if seleccion == FUENTE_MQTT and self.fuente is not self.mqtt:
            try:
                self.mqtt.conectar()
            except Exception as error:
                messagebox.showerror("No se pudo conectar", str(error))
                self.combo_fuente.set(FUENTE_SIMULADA)
                return
            self.fuente = self.mqtt
        elif seleccion == FUENTE_SIMULADA and self.fuente is not self.simulador:
            self.mqtt.desconectar()
            self.fuente = self.simulador

        self.estado_anterior = None
        self.registrar_evento(f"Fuente de datos: {seleccion}")
        self.actualizar_info()

    def actualizar_info(self):
        minutos, segundos = divmod(int(time.time() - self.hora_inicio), 60)
        self.lbl_info.config(
            text=f"Fuente: {self.fuente.descripcion()}   |   "
                 f"Última lectura: {self.hora_ultima_lectura}   |   "
                 f"Lecturas: {self.lecturas}   |   "
                 f"Tiempo de uso: {minutos:02d}:{segundos:02d}"
        )

    def cerrar(self):
        self.mqtt.desconectar()
        self.destroy()


if __name__ == "__main__":
    app = AppInvernadero()
    app.mainloop()
