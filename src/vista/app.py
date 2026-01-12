import customtkinter as ctk
from vista.dashboard import VistaDashboard
from vista.informacion import VistaInformacion

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Registro en Línea")
        self.geometry("1100x650")

        # Configuración del Grid Principal (1x2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- SIDEBAR (IZQUIERDA) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="REGISTRO\nEVENTOS", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botones del Sidebar
        self.botones_sidebar = {}
        opciones = ["Inicio", "Tipo", "Información", "Aviso", "Estadísticas", "Facturación", "Pago", "Confirmación"]
        
        for i, opcion in enumerate(opciones):
            btn = ctk.CTkButton(self.sidebar_frame, text=opcion, command=lambda op=opcion: self.navegar(op))
            btn.grid(row=i+1, column=0, padx=20, pady=10)
            self.botones_sidebar[opcion] = btn

        # --- AREA DE CONTENIDO (DERECHA) ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Estado inicial
        self.navegar("Inicio")

    def navegar(self, nombre_vista):
        # 1. Resetear color de botones
        for btn in self.botones_sidebar.values():
            btn.configure(fg_color=["#3a7ebf", "#1f538d"]) # Color default (Light/Dark)

        # 2. Resaltar botón activo
        self.botones_sidebar[nombre_vista].configure(fg_color=["#3B8ED0", "#14375e"]) # Color activo

        # 3. Limpiar frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # 4. Cargar vista correspondiente
        if nombre_vista == "Inicio":
            VistaDashboard(self.main_frame).pack(fill="both", expand=True)
        
        elif nombre_vista == "Información":
            VistaInformacion(self.main_frame).pack(fill="both", expand=True)
            
        else:
            # Vistas no implementadas (Placeholders)
            ctk.CTkLabel(self.main_frame, text=f"Módulo: {nombre_vista}\n(En construcción)", font=("Roboto", 20)).pack(expand=True)