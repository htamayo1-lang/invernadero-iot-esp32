import time
import tkinter as tk
from tkinter import ttk

MAX_FILAS = 200
COLUMNAS = (
    ("hora", "Hora", 90),
    ("temp_actual", "Temp. actual (°C)", 130),
    ("temp_promedio", "Temp. promedio (°C)", 140),
    ("humedad", "Humedad (%)", 110),
    ("modo", "Modo", 90),
    ("alerta", "Alerta", 110),
)
ROJO_CLARO = "#ffcdd2"


def hora_actual():
    return time.strftime("%H:%M:%S")


class PanelHistorial(ttk.LabelFrame):
    def __init__(self, padre):
        super().__init__(padre, text="Historial", padding=10)

        pestanas = ttk.Notebook(self)
        pestanas.pack(fill="both", expand=True)
        self.tabla = self.crear_tabla(pestanas)
        self.lista_eventos = self.crear_lista_eventos(pestanas)

        ttk.Button(self, text="Limpiar historial", command=self.limpiar).pack(anchor="e", pady=(6, 0))

    def crear_tabla(self, pestanas):
        marco = ttk.Frame(pestanas)
        pestanas.add(marco, text="Mediciones")

        tabla = ttk.Treeview(marco, columns=[clave for clave, _, _ in COLUMNAS], show="headings", height=7)
        for clave, titulo, ancho in COLUMNAS:
            tabla.heading(clave, text=titulo)
            tabla.column(clave, width=ancho, anchor="center")
        tabla.tag_configure("alerta", background=ROJO_CLARO)

        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return tabla

    def crear_lista_eventos(self, pestanas):
        marco = ttk.Frame(pestanas)
        pestanas.add(marco, text="Eventos")

        lista = tk.Listbox(marco, height=7, font=("Consolas", 10))
        barra = ttk.Scrollbar(marco, orient="vertical", command=lista.yview)
        lista.configure(yscrollcommand=barra.set)
        lista.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return lista

    def agregar_medicion(self, estado):
        valores = (
            hora_actual(),
            f"{estado['temp_actual']:.1f}",
            f"{estado['temp_promedio']:.1f}",
            f"{estado['humedad']:.0f}",
            estado["modo"],
            estado["alerta"],
        )
        etiquetas = ("alerta",) if estado["alerta"] != "NORMAL" else ()
        self.tabla.insert("", 0, values=valores, tags=etiquetas)

        filas = self.tabla.get_children()
        if len(filas) > MAX_FILAS:
            self.tabla.delete(filas[-1])

    def agregar_evento(self, texto):
        self.lista_eventos.insert(0, f"{hora_actual()}   {texto}")
        if "ALERTA" in texto or "Error" in texto:
            self.lista_eventos.itemconfig(0, foreground="red")

        if self.lista_eventos.size() > MAX_FILAS:
            self.lista_eventos.delete(tk.END)

    def limpiar(self):
        self.tabla.delete(*self.tabla.get_children())
        self.lista_eventos.delete(0, tk.END)
