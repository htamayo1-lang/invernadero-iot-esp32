from tkinter import ttk

from validacion import validar_numero

RANGO_ALARMA = (20.0, 45.0)
RANGO_BOMBILLO = (10.0, 40.0)
UMBRAL_ALARMA_INICIAL = 30.0
UMBRAL_BOMBILLO_INICIAL = 25.0


class PanelConfiguracion(ttk.LabelFrame):
    def __init__(self, padre, enviar_comando, registrar_evento):
        super().__init__(padre, text="Configuración de umbrales", padding=10)
        self.enviar_comando = enviar_comando
        self.registrar_evento = registrar_evento
        self.columnconfigure(1, weight=1)

        self.entry_alarma = self.crear_campo(0, "Umbral de alarma (°C)", UMBRAL_ALARMA_INICIAL, RANGO_ALARMA)
        self.entry_bombillo = self.crear_campo(1, "Umbral del bombillo (°C)", UMBRAL_BOMBILLO_INICIAL, RANGO_BOMBILLO)

        ttk.Button(self, text="Aplicar", command=self.aplicar).grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        self.lbl_mensaje = ttk.Label(self, text="Escribe un valor y presiona Enter o 'Aplicar'.", wraplength=380)
        self.lbl_mensaje.grid(row=3, column=0, columnspan=3, sticky="w", pady=(8, 0))

    def crear_campo(self, fila, texto, valor_inicial, rango):
        ttk.Label(self, text=texto).grid(row=fila, column=0, sticky="w", pady=3)

        campo = ttk.Entry(self, width=10, justify="center")
        campo.insert(0, str(valor_inicial))
        campo.grid(row=fila, column=1, sticky="ew", padx=5)
        campo.bind("<Return>", self.aplicar_con_enter)

        ttk.Label(self, text=f"({rango[0]:g} a {rango[1]:g})", foreground="gray").grid(row=fila, column=2, sticky="w")
        return campo

    def aplicar_con_enter(self, evento):
        self.aplicar()

    def aplicar(self):
        try:
            umbral_alarma = validar_numero(self.entry_alarma.get(), "Umbral de alarma", *RANGO_ALARMA)
            umbral_bombillo = validar_numero(self.entry_bombillo.get(), "Umbral del bombillo", *RANGO_BOMBILLO)
            if umbral_bombillo >= umbral_alarma:
                raise ValueError("El umbral del bombillo debe ser menor que el de alarma.")
        except ValueError as error:
            self.lbl_mensaje.config(text=str(error), foreground="red")
            self.registrar_evento(f"Error de validación: {error}")
            return

        self.enviar_comando(
            f"Umbrales: alarma {umbral_alarma:g} °C, bombillo {umbral_bombillo:g} °C",
            {"umbral_temp": umbral_alarma, "umbral_bombillo": umbral_bombillo},
        )
        self.lbl_mensaje.config(text="Umbrales guardados correctamente.", foreground="green")
