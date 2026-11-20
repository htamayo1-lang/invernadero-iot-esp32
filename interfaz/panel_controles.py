from tkinter import ttk

VENTANA_ABIERTA = 0
VENTANA_CERRADA = 145


class PanelControles(ttk.LabelFrame):
    def __init__(self, padre, enviar_comando):
        super().__init__(padre, text="Controles", padding=10)
        self.enviar_comando = enviar_comando
        self.silenciado = False

        modos = ttk.Frame(self)
        modos.pack(fill="x")
        self.btn_auto = ttk.Button(modos, text="Modo AUTO", command=self.modo_auto)
        self.btn_auto.pack(side="left", expand=True, fill="x", padx=2)
        self.btn_manual = ttk.Button(modos, text="Modo MANUAL", command=self.modo_manual)
        self.btn_manual.pack(side="left", expand=True, fill="x", padx=2)

        ttk.Label(self, text="Solo disponibles en modo MANUAL:").pack(anchor="w", pady=(8, 2))

        manuales = ttk.Frame(self)
        manuales.pack(fill="x")
        manuales.columnconfigure((0, 1), weight=1)
        self.btn_abrir = self.crear_boton(manuales, "Abrir compuerta", self.abrir_compuerta, 0, 0)
        self.btn_cerrar = self.crear_boton(manuales, "Cerrar compuerta", self.cerrar_compuerta, 0, 1)
        self.btn_prender = self.crear_boton(manuales, "Prender bombillo", self.prender_bombillo, 1, 0)
        self.btn_apagar = self.crear_boton(manuales, "Apagar bombillo", self.apagar_bombillo, 1, 1)
        self.btn_pitido = ttk.Button(manuales, text="Silenciar pitido", command=self.alternar_pitido)
        self.btn_pitido.grid(row=2, column=0, columnspan=2, sticky="ew", padx=2, pady=2)

        self.botones_manuales = [self.btn_abrir, self.btn_cerrar, self.btn_prender, self.btn_apagar, self.btn_pitido]

    def crear_boton(self, padre, texto, accion, fila, columna):
        boton = ttk.Button(padre, text=texto, command=accion)
        boton.grid(row=fila, column=columna, sticky="ew", padx=2, pady=2)
        return boton

    def modo_auto(self):
        self.enviar_comando("Cambiar a modo AUTO", {"modo": "AUTO"})

    def modo_manual(self):
        self.enviar_comando("Cambiar a modo MANUAL", {"modo": "MANUAL"})

    def abrir_compuerta(self):
        self.enviar_comando("Abrir compuerta", {"angulo_forzado": VENTANA_ABIERTA})

    def cerrar_compuerta(self):
        self.enviar_comando("Cerrar compuerta", {"angulo_forzado": VENTANA_CERRADA})

    def prender_bombillo(self):
        self.enviar_comando("Prender bombillo", {"bombillo": True})

    def apagar_bombillo(self):
        self.enviar_comando("Apagar bombillo", {"bombillo": False})

    def alternar_pitido(self):
        if self.silenciado:
            self.enviar_comando("Activar pitido", {"silenciar": False})
        else:
            self.enviar_comando("Silenciar pitido", {"silenciar": True})

    def mostrar(self, estado):
        if estado is None:
            self.cambiar_estado([self.btn_auto, self.btn_manual] + self.botones_manuales, "disabled")
            return

        manual = estado["modo"] == "MANUAL"
        self.cambiar_estado([self.btn_auto], "normal" if manual else "disabled")
        self.cambiar_estado([self.btn_manual], "disabled" if manual else "normal")
        self.cambiar_estado(self.botones_manuales, "normal" if manual else "disabled")

        self.silenciado = estado["silenciado"]
        self.btn_pitido.config(text="Activar pitido" if self.silenciado else "Silenciar pitido")

    def cambiar_estado(self, botones, estado):
        for boton in botones:
            boton.config(state=estado)
