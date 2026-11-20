import tkinter as tk
from tkinter import ttk

VENTANA_ABIERTA = 0
VENTANA_CERRADA = 145

VERDE = "#2e7d32"
ROJO = "#c62828"
ROJO_OSCURO = "#7f0000"
AMARILLO = "#f9a825"
AZUL = "#1565c0"
GRIS = "#757575"


def texto_compuerta(angulo):
    if angulo == VENTANA_ABIERTA:
        return "Abierta"
    if angulo == VENTANA_CERRADA:
        return "Cerrada"
    return f"{angulo}°"


class PanelEstado(ttk.LabelFrame):
    def __init__(self, padre):
        super().__init__(padre, text="Estado del sistema", padding=10)
        self.columnconfigure(1, weight=1)
        self.id_parpadeo = None
        self.parpadeo_encendido = False

        self.lbl_modo = self.crear_indicador(0, "Modo")
        self.lbl_compuerta = self.crear_indicador(1, "Compuerta")
        self.lbl_bombillo = self.crear_indicador(2, "Bombillo")
        self.lbl_pitido = self.crear_indicador(3, "Pitido")

        self.lbl_umbrales = ttk.Label(self, text="Umbrales: --", foreground=GRIS)
        self.lbl_umbrales.grid(row=4, column=0, columnspan=2, sticky="w", pady=(6, 0))

        self.lbl_alarma = tk.Label(self, text="ESPERANDO DATOS", font=("Segoe UI", 13, "bold"), fg="white", bg=GRIS, pady=5)
        self.lbl_alarma.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    def crear_indicador(self, fila, texto):
        ttk.Label(self, text=texto).grid(row=fila, column=0, sticky="w", pady=2)
        valor = tk.Label(self, text="--", width=14, fg="white", bg=GRIS, font=("Segoe UI", 10, "bold"))
        valor.grid(row=fila, column=1, sticky="e", pady=2)
        return valor

    def pintar(self, indicador, texto, color):
        indicador.config(text=texto, bg=color)

    def mostrar(self, estado):
        en_alerta = estado["alerta"] != "NORMAL"
        compuerta = texto_compuerta(estado["angulo_ventana"])

        self.pintar(self.lbl_modo, estado["modo"], VERDE if estado["modo"] == "AUTO" else AMARILLO)
        self.pintar(self.lbl_compuerta, compuerta, AZUL if compuerta == "Abierta" else GRIS)
        self.pintar(self.lbl_bombillo, "Prendido" if estado["bombillo"] else "Apagado", AMARILLO if estado["bombillo"] else GRIS)

        if estado["silenciado"]:
            self.pintar(self.lbl_pitido, "Silenciado", AMARILLO)
        elif en_alerta:
            self.pintar(self.lbl_pitido, "Sonando", ROJO)
        else:
            self.pintar(self.lbl_pitido, "Apagado", GRIS)

        self.lbl_umbrales.config(
            text=f"Umbral de alarma: {estado['umbral_temp']:.1f} °C   ·   "
                 f"Umbral del bombillo: {estado['umbral_bombillo']:.1f} °C"
        )
        self.mostrar_alarma(en_alerta, estado["silenciado"])

    def mostrar_alarma(self, en_alerta, silenciado):
        if en_alerta and self.id_parpadeo is None:
            if not silenciado:
                self.bell()
            self.parpadear()
        elif not en_alerta:
            self.detener_parpadeo()
            self.lbl_alarma.config(text="✔ TEMPERATURA NORMAL", bg=VERDE)

    def parpadear(self):
        self.parpadeo_encendido = not self.parpadeo_encendido
        color = ROJO if self.parpadeo_encendido else ROJO_OSCURO
        self.lbl_alarma.config(text="⚠ ALERTA: TEMPERATURA ALTA", bg=color)
        self.id_parpadeo = self.after(500, self.parpadear)

    def detener_parpadeo(self):
        if self.id_parpadeo is not None:
            self.after_cancel(self.id_parpadeo)
            self.id_parpadeo = None

    def mostrar_sin_datos(self):
        self.detener_parpadeo()
        self.lbl_alarma.config(text="ESPERANDO DATOS", bg=GRIS)
