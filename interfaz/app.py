import tkinter as tk
from tkinter import ttk

from panel_variables import PanelVariables
from panel_estado import PanelEstado


class AppInvernadero(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Invernadero IoT - Panel de control")
        self.geometry("980x760")
        self.minsize(900, 700)
        ttk.Style(self).theme_use("clam")

        self.crear_encabezado()
        self.crear_paneles()
        self.crear_barra_estado()

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

    def crear_encabezado(self):
        encabezado = ttk.Frame(self, padding=(15, 10))
        encabezado.grid(row=0, column=0, columnspan=2, sticky="ew")

        ttk.Label(encabezado, text="Invernadero IoT", font=("Segoe UI", 20, "bold")).pack(side="left")

    def crear_paneles(self):
        self.panel_variables = PanelVariables(self)
        self.panel_variables.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.panel_estado = PanelEstado(self)
        self.panel_estado.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)

    def crear_barra_estado(self):
        self.lbl_info = ttk.Label(self, text="Iniciando...", relief="sunken", padding=(10, 3))
        self.lbl_info.grid(row=4, column=0, columnspan=2, sticky="ew")


if __name__ == "__main__":
    app = AppInvernadero()
    app.mainloop()
