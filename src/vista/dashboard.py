import customtkinter as ctk
from servicios.gestor_dashboard import GestorDashboard

class VistaDashboard(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.gestor = GestorDashboard()
        
        # Título
        ctk.CTkLabel(self, text="Panel de Control - Eventos", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0, 20))

        # --- SECCIÓN 1: PRÓXIMOS EVENTOS ---
        ctk.CTkLabel(self, text="📅 Próximos Eventos", font=("Roboto", 18)).pack(anchor="w", pady=5)
        
        self.frame_eventos = ctk.CTkScrollableFrame(self, height=150, fg_color=("#dbdbdb", "#2b2b2b"))
        self.frame_eventos.pack(fill="x", pady=(0, 20))
        self.cargar_eventos()

        # --- SECCIÓN 2: ESTADO DE PAGOS ---
        container_pagos = ctk.CTkFrame(self, fg_color="transparent")
        container_pagos.pack(fill="both", expand=True)

        # Columna Pendientes
        col_pend = ctk.CTkFrame(container_pagos)
        col_pend.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ctk.CTkLabel(col_pend, text="⚠️ Pendientes por Pagar", text_color="#d9534f", font=("Roboto", 16, "bold")).pack(pady=10)
        self.lista_pendientes = ctk.CTkScrollableFrame(col_pend)
        self.lista_pendientes.pack(fill="both", expand=True)
        self.cargar_asistentes(self.lista_pendientes, 'PENDIENTE')

        # Columna Pagados
        col_pag = ctk.CTkFrame(container_pagos)
        col_pag.pack(side="right", fill="both", expand=True, padx=(10, 0))
        ctk.CTkLabel(col_pag, text="✅ Pagos Confirmados", text_color="#5cb85c", font=("Roboto", 16, "bold")).pack(pady=10)
        self.lista_pagados = ctk.CTkScrollableFrame(col_pag)
        self.lista_pagados.pack(fill="both", expand=True)
        self.cargar_asistentes(self.lista_pagados, 'PAGADO')

    def cargar_eventos(self):
        eventos = self.gestor.obtener_eventos_proximos()
        if not eventos:
            ctk.CTkLabel(self.frame_eventos, text="No hay eventos próximos.").pack()
            return
        
        for evt in eventos:
            card = ctk.CTkFrame(self.frame_eventos, fg_color=("#ffffff", "#3a3a3a"))
            card.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(card, text=f"{evt['nombre']} | {evt['fecha']}", font=("Roboto", 14, "bold")).pack(anchor="w", padx=10, pady=5)
            ctk.CTkLabel(card, text=f"Lugar: {evt['lugar']} (Cap: {evt['capacidad']})").pack(anchor="w", padx=10, pady=(0, 5))

    def cargar_asistentes(self, frame, estado):
        asistentes = self.gestor.obtener_asistentes_por_estado_pago(estado)
        if not asistentes:
            ctk.CTkLabel(frame, text="Sin registros.").pack()
            return
        
        for asis in asistentes:
            txt = f"{asis['nombre_completo']}\n{asis['evento']} - ${asis['monto']}"
            lbl = ctk.CTkLabel(frame, text=txt, justify="left", anchor="w", padx=10)
            lbl.pack(fill="x", pady=2)
            ctk.CTkFrame(frame, height=1, fg_color="gray").pack(fill="x") # Separador