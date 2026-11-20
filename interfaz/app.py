import time
import tkinter as tk
from tkinter import ttk

from simulador import SimuladorInvernadero
from panel_variables import PanelVariables
from panel_estado import PanelEstado
from panel_controles import PanelControles

INTERVALO_MS = 2000


class AppInvernadero(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Invernadero IoT - Panel de control")
        self.geometry("980x760")
        self.minsize(900, 700)
        ttk.Style(self).theme_use("clam")

        self.simulador = SimuladorInvernadero()
        self.fuente = self.simulador
        self.lecturas = 0
        self.hora_ultima_lectura = "--"

        self.crear_encabezado()
        self.crear_paneles()
        self.crear_barra_estado()

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

        self.actualizar()

    def crear_encabezado(self):
        encabezado = ttk.Frame(self, padding=(15, 10))
        encabezado.grid(row=0, column=0, columnspan=2, sticky="ew")

        ttk.Label(encabezado, text="Invernadero IoT", font=("Segoe UI", 20, "bold")).pack(side="left")

    def crear_paneles(self):
        self.panel_variables = PanelVariables(self)
        self.panel_variables.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.panel_estado = PanelEstado(self)
        self.panel_estado.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)

        self.panel_controles = PanelControles(self, self.enviar_comando)
        self.panel_controles.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

    def crear_barra_estado(self):
        self.lbl_info = ttk.Label(self, text="Iniciando...", relief="sunken", padding=(10, 3))
        self.lbl_info.grid(row=4, column=0, columnspan=2, sticky="ew")

    def actualizar(self):
        estado = self.fuente.actualizar()
        if estado:
            self.lecturas += 1
            self.hora_ultima_lectura = time.strftime("%H:%M:%S")
            self.mostrar(estado)
        else:
            self.panel_controles.mostrar(None)
            self.panel_estado.mostrar_sin_datos()

        self.actualizar_info()
        self.after(INTERVALO_MS, self.actualizar)

    def mostrar(self, estado):
        self.panel_variables.mostrar(estado)
        self.panel_estado.mostrar(estado)
        self.panel_controles.mostrar(estado)

    def enviar_comando(self, descripcion, comando):
        self.fuente.aplicar_comando(comando)
        estado = self.fuente.estado_actual()
        if estado:
            self.mostrar(estado)

    def actualizar_info(self):
        self.lbl_info.config(
            text=f"Fuente: {self.fuente.descripcion()}   |   "
                 f"Última lectura: {self.hora_ultima_lectura}   |   "
                 f"Lecturas: {self.lecturas}"
        )


if __name__ == "__main__":
    app = AppInvernadero()
    app.mainloop()
