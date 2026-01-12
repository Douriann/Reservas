import customtkinter as ctk
from tkinter import messagebox
from servicios.servicios_auxiliares import ServiciosAuxiliares
from vista.nueva_organizacion import VentanaNuevaOrganizacion
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
        
        self.lista_orgs = []  # Para guardar tuplas (id, nombre)
        self.lista_eventos = []

        # Título
        ctk.CTkLabel(self, text="Registro y Solicitud de Reserva", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0, 20))

        # --- FORMULARIO ---
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", pady=10)

        # Cédula
        self.entry_cedula = ctk.CTkEntry(form_frame, placeholder_text="Cédula (V-12345678)", width=200)
        self.entry_cedula.grid(row=0, column=0, padx=10, pady=10)

        # Nombre y Apellidos
        self.entry_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombre", width=200)
        self.entry_nombre.grid(row=0, column=1, padx=10, pady=10)
        self.entry_apellido = ctk.CTkEntry(form_frame, placeholder_text="Apellido Paterno", width=200)
        self.entry_apellido.grid(row=0, column=2, padx=10, pady=10)

        # Contacto
        self.entry_email = ctk.CTkEntry(form_frame, placeholder_text="Correo Electrónico", width=200)
        self.entry_email.grid(row=1, column=0, padx=10, pady=10)
        self.entry_telefono = ctk.CTkEntry(form_frame, placeholder_text="Teléfono", width=200)
        self.entry_telefono.grid(row=1, column=1, padx=10, pady=10)
        self.entry_cargo = ctk.CTkEntry(form_frame, placeholder_text="Cargo / Puesto", width=200)
        self.entry_cargo.grid(row=1, column=2, padx=10, pady=10)

        # --- SELECCIONES ---
        select_frame = ctk.CTkFrame(self, fg_color="transparent")
        select_frame.pack(fill="x", pady=10)

        # Evento
        ctk.CTkLabel(select_frame, text="Evento:").pack(side="left", padx=5)
        self.combo_evento = ctk.CTkComboBox(select_frame, width=250)
        self.combo_evento.pack(side="left", padx=5)

        # Organización (Con botón de crear)
        ctk.CTkLabel(select_frame, text="Organización:").pack(side="left", padx=(20, 5))
        self.combo_org = ctk.CTkComboBox(select_frame, width=250)
        self.combo_org.pack(side="left", padx=5)
        
        btn_nueva_org = ctk.CTkButton(select_frame, text="+", width=30, command=self.abrir_popup_org)
        btn_nueva_org.pack(side="left", padx=5)

        # Botón de Acción (Asignado a variable self.btn_guardar para poder bloquearlo)
        self.btn_guardar = ctk.CTkButton(
            self, 
            text="Registrar y Generar Comprobante", 
            height=40, 
            font=("Roboto", 14, "bold"),
            command=self.procesar_registro
        )
        self.btn_guardar.pack(pady=30)

        # Cargar datos iniciales
        self.cargar_combos()

    def cargar_combos(self):
        # Organizaciones
        datos_org = self.aux_service.obtener_organizaciones()
        self.lista_orgs = datos_org 
        nombres_org = [x[1] for x in datos_org]
        self.combo_org.configure(values=nombres_org)
        if nombres_org: self.combo_org.set(nombres_org[0])

        # Eventos
        datos_evt = self.aux_service.obtener_eventos_futuros()
        self.lista_eventos = datos_evt
        nombres_evt = [x[1] for x in datos_evt]
        self.combo_evento.configure(values=nombres_evt)
        if nombres_evt: self.combo_evento.set(nombres_evt[0])

    def abrir_popup_org(self):
        VentanaNuevaOrganizacion(self, self.cargar_combos)

    def procesar_registro(self):
        # --- PASO DE SEGURIDAD: BLOQUEAR BOTÓN ---
        self.btn_guardar.configure(state="disabled", text="Procesando...")
        self.update_idletasks()

        try:
            # 1. Obtener textos
            nombre_org_seleccionado = self.combo_org.get()
            nombre_evt_seleccionado = self.combo_evento.get()

            if not nombre_org_seleccionado or not nombre_evt_seleccionado:
                messagebox.showwarning("Faltan datos", "Por favor seleccione una Organización y un Evento.")
                return

            # 2. Buscar IDs correspondientes
            idx_org = None
            for org in self.lista_orgs:
                if org[1] == nombre_org_seleccionado:
                    idx_org = org[0]
                    break
            
            idx_evt = None
            for evt in self.lista_eventos:
                if evt[1] == nombre_evt_seleccionado:
                    idx_evt = evt[0]
                    break

            if idx_org is None or idx_evt is None:
                messagebox.showerror("Error", "No se pudo identificar la organización o el evento.")
                return

            # 3. Crear Modelos
            org_modelo = Organizacion(nombre_empresa=nombre_org_seleccionado, id_organizacion=idx_org)
            
            try:
                asistente_modelo = Asistente(
                    cedula=self.entry_cedula.get(),
                    nombre=self.entry_nombre.get(),
                    apellido_paterno=self.entry_apellido.get(),
                    apellido_materno=None, 
                    email=self.entry_email.get(),
                    telefono=self.entry_telefono.get(),
                    puesto_cargo=self.entry_cargo.get(),
                    id_organizacion=idx_org
                )
            except Exception as e:
                messagebox.showerror("Error de Datos", f"Verifique los campos del asistente.\nDetalle: {e}")
                return

            # 4. Llamar al Gestor (Ahora devuelve un DICCIONARIO)
            # NOTA: Asegúrate de haber actualizado gestor_reserva.py como acordamos antes
            respuesta = self.gestor_reserva.registrar_reserva_completa(asistente_modelo, org_modelo, idx_evt)

            if respuesta["exito"]:
                # 5. Generar PDF con los datos REALES devueltos por la BD
                datos_reales = respuesta["datos_pdf"]
                
                try:
                    ruta = self.generador_pdf.generar_comprobante(datos_reales)
                    messagebox.showinfo("Éxito", f"Registro Exitoso.\nComprobante guardado en:\n{ruta}")
                    
                    # Limpiar campos
                    self.entry_cedula.delete(0, 'end')
                    self.entry_nombre.delete(0, 'end')
                    self.entry_apellido.delete(0, 'end')
                    self.entry_email.delete(0, 'end')
                    self.entry_telefono.delete(0, 'end')
                    self.entry_cargo.delete(0, 'end')
                    
                except Exception as e:
                    messagebox.showwarning("Registro con Alerta", f"Se guardó en BD pero falló el PDF: {e}")
            else:
                # Mostrar el mensaje de error que viene del gestor (ej. "Ya registrado")
                messagebox.showerror("Atención", respuesta["mensaje"])

        except Exception as e:
            messagebox.showerror("Error Crítico", f"Ocurrió un error inesperado: {e}")
        
        finally:
            # --- PASO FINAL: REACTIVAR BOTÓN ---
            self.btn_guardar.configure(state="normal", text="Registrar y Generar Comprobante")