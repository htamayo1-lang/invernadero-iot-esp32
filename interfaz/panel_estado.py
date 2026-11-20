from tkinter import ttk

VENTANA_ABIERTA = 0
VENTANA_CERRADA = 145


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

        self.lbl_modo = self.crear_indicador(0, "Modo")
        self.lbl_compuerta = self.crear_indicador(1, "Compuerta")
        self.lbl_bombillo = self.crear_indicador(2, "Bombillo")
        self.lbl_alerta = self.crear_indicador(3, "Alerta")

    def crear_indicador(self, fila, texto):
        ttk.Label(self, text=texto).grid(row=fila, column=0, sticky="w", pady=2)
        valor = ttk.Label(self, text="--", font=("Segoe UI", 10, "bold"))
        valor.grid(row=fila, column=1, sticky="e", pady=2)
        return valor

    def mostrar(self, estado):
        self.lbl_modo.config(text=estado["modo"])
        self.lbl_compuerta.config(text=texto_compuerta(estado["angulo_ventana"]))
        self.lbl_bombillo.config(text="Prendido" if estado["bombillo"] else "Apagado")
        self.lbl_alerta.config(text="Temperatura alta" if estado["alerta"] != "NORMAL" else "Normal")
