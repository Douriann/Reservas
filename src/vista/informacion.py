import customtkinter as ctk
from tkinter import messagebox
from servicios.servicios_auxiliares import ServiciosAuxiliares
from vista.nueva_organizacion import VentanaNuevaOrganizacion
from vista.nuevo_evento import VentanaNuevoEvento
from modelo.Asistente import Asistente
from modelo.Organizacion import Organizacion
from servicios.gestor_reserva import GestorReserva
from servicios.generador_pdf import GeneradorPDF

class VistaInformacion(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.aux_service = ServiciosAuxiliares()
        self.gestor_reserva = GestorReserva()
        self.generador_pdf = GeneradorPDF()
        
        self.lista_orgs = [] 
        self.lista_eventos = []
        self.lista_metodos_pago = [] # Lista nueva para pagos

        # Título
        ctk.CTkLabel(self, text="Registro y Solicitud de Reserva", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0, 20))

        # --- FORMULARIO ---
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", pady=10)
        form_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # --- FILA 0: CÉDULA Y BÚSQUEDA ---
        frame_cedula = ctk.CTkFrame(form_frame, fg_color="transparent")
        frame_cedula.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.btn_buscar = ctk.CTkButton(frame_cedula, text="🔍", width=40, fg_color="#FF9800", hover_color="#F57C00", command=self.buscar_cedula)
        self.btn_buscar.pack(side="right", padx=(5, 0))

        self.entry_cedula = ctk.CTkEntry(frame_cedula, placeholder_text="Cédula * (V-12345678)")
        self.entry_cedula.pack(side="left", fill="x", expand=True) 

        # Resto de campos
        self.entry_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombre *")
        self.entry_nombre.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.entry_apellido = ctk.CTkEntry(form_frame, placeholder_text="Apellido Paterno *")
        self.entry_apellido.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        # Fila 1
        self.entry_apellido_mat = ctk.CTkEntry(form_frame, placeholder_text="Apellido Materno")
        self.entry_apellido_mat.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.entry_email = ctk.CTkEntry(form_frame, placeholder_text="Correo Electrónico *")
        self.entry_email.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.entry_telefono = ctk.CTkEntry(form_frame, placeholder_text="Teléfono")
        self.entry_telefono.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        # Fila 2
        self.entry_cargo = ctk.CTkEntry(form_frame, placeholder_text="Cargo / Puesto")
        self.entry_cargo.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # --- SELECCIONES ---
        select_frame = ctk.CTkFrame(self, fg_color="transparent")
        select_frame.pack(fill="x", pady=10)

        # Organización
        ctk.CTkLabel(select_frame, text="Organización *:").pack(side="left", padx=5)
        self.combo_org = ctk.CTkComboBox(select_frame, width=230)
        self.combo_org.pack(side="left", padx=5)
        self.btn_add_org = ctk.CTkButton(select_frame, text="+", width=30, command=self.abrir_popup_org)
        self.btn_add_org.pack(side="left", padx=5)

        # Evento
        ctk.CTkLabel(select_frame, text="Evento *:").pack(side="left", padx=(20, 5))
        self.combo_evento = ctk.CTkComboBox(select_frame, width=230)
        self.combo_evento.pack(side="left", padx=5)
        ctk.CTkButton(select_frame, text="+", width=30, command=self.abrir_popup_evento).pack(side="left", padx=5)

        # --- OPCIONES DE PAGO ---
        self.pago_frame = ctk.CTkFrame(self, fg_color="transparent") # Lo hacemos self para acceder
        self.pago_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(self.pago_frame, text="Estado del Pago:", font=("Roboto", 14, "bold")).pack(side="left", padx=10)
        
        self.var_estado_pago = ctk.IntVar(value=1)
        
        # Agregamos command=self.toggle_pago_ui a los radios para detectar cambios
        self.radio_pendiente = ctk.CTkRadioButton(self.pago_frame, text="Pendiente por Pagar", variable=self.var_estado_pago, value=1, command=self.toggle_pago_ui)
        self.radio_pendiente.pack(side="left", padx=20)
        
        self.radio_pagado = ctk.CTkRadioButton(self.pago_frame, text="Pago Inmediato (Confirmar)", variable=self.var_estado_pago, value=3, command=self.toggle_pago_ui)
        self.radio_pagado.pack(side="left", padx=20)

        # --- COMBOBOX DE MÉTODOS DE PAGO (OCULTO AL INICIO) ---
        # Creamos un frame interno para que el combo y su etiqueta aparezcan juntos
        self.frame_metodo_pago = ctk.CTkFrame(self.pago_frame, fg_color="transparent")
        
        ctk.CTkLabel(self.frame_metodo_pago, text="Método:").pack(side="left", padx=5)
        self.combo_metodo_pago = ctk.CTkComboBox(self.frame_metodo_pago, width=180)
        self.combo_metodo_pago.pack(side="left", padx=5)

        # Botón de Acción
        self.btn_guardar = ctk.CTkButton(self, text="Registrar y Generar Comprobante", height=40, font=("Roboto", 14, "bold"), command=self.procesar_registro)
        self.btn_guardar.pack(pady=20)
        
        # --- LÓGICA DE ESTADO INICIAL ---
        self.campos_personales = [
            self.entry_nombre, self.entry_apellido, self.entry_apellido_mat,
            self.entry_email, self.entry_telefono, self.entry_cargo
        ]
        
        self.busqueda_realizada = False
        self.cargar_combos()
        self.cambiar_estado_campos("disabled")

    def cambiar_estado_campos(self, estado):
        for campo in self.campos_personales:
            campo.configure(state=estado)
        self.combo_org.configure(state=estado)
        self.btn_add_org.configure(state=estado)

    def limpiar_campos_personales(self):
        for campo in self.campos_personales:
            campo.delete(0, 'end')

    def cargar_combos(self):
        # Org
        datos_org = self.aux_service.obtener_organizaciones()
        self.lista_orgs = datos_org 
        nombres_org = [x[1] for x in datos_org]
        self.combo_org.configure(values=nombres_org)
        if nombres_org: self.combo_org.set(nombres_org[0])
        else: self.combo_org.set("")

        # Eventos
        datos_evt = self.aux_service.obtener_eventos_futuros()
        self.lista_eventos = datos_evt
        nombres_evt = [x[1] for x in datos_evt]
        self.combo_evento.configure(values=nombres_evt)
        if nombres_evt: self.combo_evento.set(nombres_evt[0])
        else: self.combo_evento.set("")

        # Métodos de Pago
        datos_pago = self.aux_service.obtener_metodos_pago()
        self.lista_metodos_pago = datos_pago
        nombres_pago = [x[1] for x in datos_pago]
        self.combo_metodo_pago.configure(values=nombres_pago)
        if nombres_pago: self.combo_metodo_pago.set(nombres_pago[0])

    def abrir_popup_org(self):
        VentanaNuevaOrganizacion(self, self.cargar_combos)
    
    def abrir_popup_evento(self):
        VentanaNuevoEvento(self, self.cargar_combos)

    def buscar_cedula(self):
        # ... (Igual que antes) ...
        cedula = self.entry_cedula.get().strip()
        if not cedula:
            messagebox.showwarning("Atención", "Ingrese una cédula para buscar.")
            return
        datos = self.gestor_reserva.obtener_datos_asistente(cedula)
        self.cambiar_estado_campos("normal")
        self.limpiar_campos_personales()
        if datos:
            messagebox.showinfo("Encontrado", f"El asistente ya existe.\nSe cargaron sus datos.")
            self.entry_nombre.insert(0, datos["nombre"])
            self.entry_apellido.insert(0, datos["apellido_p"])
            self.entry_apellido_mat.insert(0, datos["apellido_m"])
            self.entry_email.insert(0, datos["email"])
            self.entry_telefono.insert(0, datos["telefono"])
            self.entry_cargo.insert(0, datos["cargo"])
            id_org_prev = datos["id_org"]
            nombre_org = next((x[1] for x in self.lista_orgs if x[0] == id_org_prev), None)
            if nombre_org: self.combo_org.set(nombre_org)
        else:
            messagebox.showinfo("Nuevo", "Cédula no registrada.\nPor favor complete los datos.")
        self.busqueda_realizada = True

    # --- NUEVA LÓGICA DE UI DE PAGO ---
    def toggle_pago_ui(self):
        """Muestra u oculta el combo de pagos según el radio button"""
        estado = self.var_estado_pago.get()
        if estado == 3: # Pago Inmediato
            self.frame_metodo_pago.pack(side="left", padx=10)
        else:
            self.frame_metodo_pago.pack_forget()

    def procesar_registro(self):
        if not self.busqueda_realizada:
            messagebox.showwarning("Alto", "Debe buscar la cédula primero.")
            return

        cedula = self.entry_cedula.get().strip()
        nombre = self.entry_nombre.get().strip()
        apellido_p = self.entry_apellido.get().strip()
        email = self.entry_email.get().strip()
        org_sel = self.combo_org.get()
        evt_sel = self.combo_evento.get()

        if not cedula or not nombre or not apellido_p or not email or not org_sel or not evt_sel:
            messagebox.showwarning("Incompleto", "Llene los campos obligatorios (*).")
            return

        # 0.5 Validar Pago si es Inmediato
        idx_metodo_pago = None
        estado_seleccionado = self.var_estado_pago.get()
        
        if estado_seleccionado == 3: # Inmediato
            metodo_sel = self.combo_metodo_pago.get()
            if not metodo_sel:
                messagebox.showwarning("Pago", "Seleccione un método de pago.")
                return
            # Buscar ID del método
            idx_metodo_pago = next((x[0] for x in self.lista_metodos_pago if x[1] == metodo_sel), None)

        self.btn_guardar.configure(state="disabled", text="Procesando...")
        self.update_idletasks()

        try:
            idx_org = next((x[0] for x in self.lista_orgs if x[1] == org_sel), None)
            idx_evt = next((x[0] for x in self.lista_eventos if x[1] == evt_sel), None)

            if idx_org is None or idx_evt is None:
                messagebox.showerror("Error", "Selección inválida.")
                return

            org_modelo = Organizacion(nombre_empresa=org_sel, id_organizacion=idx_org)
            asistente_modelo = Asistente(
                cedula=cedula, nombre=nombre, apellido_paterno=apellido_p,
                apellido_materno=self.entry_apellido_mat.get().strip() or None, 
                email=email, telefono=self.entry_telefono.get().strip(),
                puesto_cargo=self.entry_cargo.get().strip(), id_organizacion=idx_org
            )

            # --- LLAMADA ACTUALIZADA ---
            respuesta = self.gestor_reserva.registrar_reserva_completa(
                asistente_modelo, 
                org_modelo, 
                idx_evt, 
                id_estado=estado_seleccionado, 
                id_metodo_pago=idx_metodo_pago # Enviamos el pago
            )

            if respuesta["exito"]:
                datos_reales = respuesta["datos_pdf"]
                try:
                    ruta = self.generador_pdf.generar_comprobante(datos_reales)
                    messagebox.showinfo("Éxito", f"Registro Guardado ({datos_reales['estado_pago']}).\nPDF: {ruta}")
                    
                    self.entry_cedula.delete(0, 'end')
                    self.limpiar_campos_personales()
                    self.var_estado_pago.set(1)
                    self.toggle_pago_ui() # Resetear UI de pago
                    
                    self.cambiar_estado_campos("disabled")
                    self.busqueda_realizada = False
                    
                except Exception as e:
                    messagebox.showwarning("Alerta", f"Guardado pero error en PDF: {e}")
            else:
                messagebox.showerror("Error", respuesta["mensaje"])

        except Exception as e:
            messagebox.showerror("Error Crítico", f"{e}")
        finally:
            self.btn_guardar.configure(state="normal", text="Registrar y Generar Comprobante")