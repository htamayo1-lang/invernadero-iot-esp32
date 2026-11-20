from tkinter import ttk

TEMP_MAXIMA = 50
HUMEDAD_MAXIMA = 100


class PanelVariables(ttk.LabelFrame):
    def __init__(self, padre):
        super().__init__(padre, text="Variables del invernadero", padding=10)
        self.columnconfigure(1, weight=1)

        self.lbl_temp_actual = self.crear_fila(0, "Temperatura actual")
        self.lbl_temp_promedio = self.crear_fila(1, "Temperatura promedio")
        self.barra_temp = self.crear_barra(2, TEMP_MAXIMA)
        self.lbl_humedad = self.crear_fila(3, "Humedad")
        self.barra_humedad = self.crear_barra(4, HUMEDAD_MAXIMA)

    def crear_fila(self, fila, texto):
        ttk.Label(self, text=texto).grid(row=fila, column=0, sticky="w")
        valor = ttk.Label(self, text="--", font=("Segoe UI", 18, "bold"))
        valor.grid(row=fila, column=1, sticky="e")
        return valor

    def crear_barra(self, fila, maximo):
        barra = ttk.Progressbar(self, maximum=maximo)
        barra.grid(row=fila, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        return barra
