import customtkinter as ctk
from tkinter import messagebox
from servicios.servicios_auxiliares import ServiciosAuxiliares
from vista.nueva_organizacion import VentanaNuevaOrganizacion
from vista.nuevo_evento import VentanaNuevoEvento  # <--- NUEVO IMPORT
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

        # Título
        ctk.CTkLabel(self, text="Registro y Solicitud de Reserva", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0, 20))

        # --- FORMULARIO ---
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", pady=10)
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(2, weight=1)

        # Fila 0
        self.entry_cedula = ctk.CTkEntry(form_frame, placeholder_text="Cédula * (V-12345678)", width=200)
        self.entry_cedula.grid(row=0, column=0, padx=10, pady=10)
        self.entry_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombre *", width=200)
        self.entry_nombre.grid(row=0, column=1, padx=10, pady=10)
        self.entry_apellido = ctk.CTkEntry(form_frame, placeholder_text="Apellido Paterno *", width=200)
        self.entry_apellido.grid(row=0, column=2, padx=10, pady=10)

        # Fila 1
        self.entry_apellido_mat = ctk.CTkEntry(form_frame, placeholder_text="Apellido Materno", width=200)
        self.entry_apellido_mat.grid(row=1, column=0, padx=10, pady=10)
        self.entry_email = ctk.CTkEntry(form_frame, placeholder_text="Correo Electrónico *", width=200)
        self.entry_email.grid(row=1, column=1, padx=10, pady=10)
        self.entry_telefono = ctk.CTkEntry(form_frame, placeholder_text="Teléfono", width=200)
        self.entry_telefono.grid(row=1, column=2, padx=10, pady=10)

        # Fila 2
        self.entry_cargo = ctk.CTkEntry(form_frame, placeholder_text="Cargo / Puesto", width=200)
        self.entry_cargo.grid(row=2, column=0, padx=10, pady=10)

        # --- SELECCIONES ---
        select_frame = ctk.CTkFrame(self, fg_color="transparent")
        select_frame.pack(fill="x", pady=10)

        # Organización
        ctk.CTkLabel(select_frame, text="Organización *:").pack(side="left", padx=5)
        self.combo_org = ctk.CTkComboBox(select_frame, width=230)
        self.combo_org.pack(side="left", padx=5)
        ctk.CTkButton(select_frame, text="+", width=30, command=self.abrir_popup_org).pack(side="left", padx=5)

        # Evento (Ahora con botón +)
        ctk.CTkLabel(select_frame, text="Evento *:").pack(side="left", padx=(20, 5))
        self.combo_evento = ctk.CTkComboBox(select_frame, width=230)
        self.combo_evento.pack(side="left", padx=5)
        ctk.CTkButton(select_frame, text="+", width=30, command=self.abrir_popup_evento).pack(side="left", padx=5)

        # --- OPCIONES DE PAGO (RadioButtons) ---
        pago_frame = ctk.CTkFrame(self, fg_color="transparent")
        pago_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(pago_frame, text="Estado del Pago:", font=("Roboto", 14, "bold")).pack(side="left", padx=10)
        
        # Variable de control (1=Pendiente, 3=Confirmado según tu BD)
        self.var_estado_pago = ctk.IntVar(value=1)
        
        self.radio_pendiente = ctk.CTkRadioButton(pago_frame, text="Pendiente por Pagar", variable=self.var_estado_pago, value=1)
        self.radio_pendiente.pack(side="left", padx=20)
        
        self.radio_pagado = ctk.CTkRadioButton(pago_frame, text="Pago Inmediato (Confirmar)", variable=self.var_estado_pago, value=3)
        self.radio_pagado.pack(side="left", padx=20)

        # Botón de Acción
        self.btn_guardar = ctk.CTkButton(self, text="Registrar y Generar Comprobante", height=40, font=("Roboto", 14, "bold"), command=self.procesar_registro)
        self.btn_guardar.pack(pady=20)

        self.cargar_combos()

    def cargar_combos(self):
        # Organizaciones
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

    def abrir_popup_org(self):
        VentanaNuevaOrganizacion(self, self.cargar_combos)
    
    def abrir_popup_evento(self):
        VentanaNuevoEvento(self, self.cargar_combos)

    def procesar_registro(self):
        # 0. Validación
        cedula = self.entry_cedula.get().strip()
        nombre = self.entry_nombre.get().strip()
        apellido_p = self.entry_apellido.get().strip()
        email = self.entry_email.get().strip()
        org_sel = self.combo_org.get()
        evt_sel = self.combo_evento.get()

        if not cedula or not nombre or not apellido_p or not email or not org_sel or not evt_sel:
            messagebox.showwarning("Incompleto", "Llene los campos obligatorios (*).")
            return

        self.btn_guardar.configure(state="disabled", text="Procesando...")
        self.update_idletasks()

        try:
            # 1. Obtener IDs
            idx_org = next((x[0] for x in self.lista_orgs if x[1] == org_sel), None)
            idx_evt = next((x[0] for x in self.lista_eventos if x[1] == evt_sel), None)

            if idx_org is None or idx_evt is None:
                messagebox.showerror("Error", "Selección inválida.")
                return

            # 2. Modelos
            org_modelo = Organizacion(nombre_empresa=org_sel, id_organizacion=idx_org)
            asistente_modelo = Asistente(
                cedula=cedula, nombre=nombre, apellido_paterno=apellido_p,
                apellido_materno=self.entry_apellido_mat.get().strip() or None, 
                email=email, telefono=self.entry_telefono.get().strip(),
                puesto_cargo=self.entry_cargo.get().strip(), id_organizacion=idx_org
            )

            # 3. Llamar al Gestor con el estado seleccionado
            estado_seleccionado = self.var_estado_pago.get()
            
            respuesta = self.gestor_reserva.registrar_reserva_completa(
                asistente_modelo, org_modelo, idx_evt, id_estado=estado_seleccionado
            )

            if respuesta["exito"]:
                datos_reales = respuesta["datos_pdf"]
                try:
                    ruta = self.generador_pdf.generar_comprobante(datos_reales)
                    messagebox.showinfo("Éxito", f"Registro Guardado ({datos_reales['estado_pago']}).\nPDF: {ruta}")
                    # Limpiar...
                    self.entry_cedula.delete(0, 'end')
                    self.entry_nombre.delete(0, 'end')
                    self.entry_apellido.delete(0, 'end')
                    self.entry_apellido_mat.delete(0, 'end')
                    self.entry_email.delete(0, 'end')
                    self.entry_telefono.delete(0, 'end')
                    self.entry_cargo.delete(0, 'end')
                    self.var_estado_pago.set(1) # Resetear a Pendiente
                except Exception as e:
                    messagebox.showwarning("Alerta", f"Guardado pero error en PDF: {e}")
            else:
                messagebox.showerror("Error", respuesta["mensaje"])

        except Exception as e:
            messagebox.showerror("Error Crítico", f"{e}")
        finally:
            self.btn_guardar.configure(state="normal", text="Registrar y Generar Comprobante")