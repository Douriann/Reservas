import customtkinter as ctk
from servicios.servicios_auxiliares import ServiciosAuxiliares

class VentanaNuevaOrganizacion(ctk.CTkToplevel):
    def __init__(self, parent, callback_actualizar):
        super().__init__(parent)
        self.callback_actualizar = callback_actualizar # Función a ejecutar al cerrar para recargar el ComboBox
        self.service = ServiciosAuxiliares()
        
        self.title("Nueva Organización")
        self.geometry("400x350")
        self.resizable(False, False)

        # Título
        ctk.CTkLabel(self, text="Registrar Empresa", font=("Roboto", 20, "bold")).pack(pady=20)

        # Campos
        self.entry_nombre = ctk.CTkEntry(self, placeholder_text="Nombre de la Empresa", width=300)
        self.entry_nombre.pack(pady=10)

        self.entry_direccion = ctk.CTkEntry(self, placeholder_text="Dirección Fiscal", width=300)
        self.entry_direccion.pack(pady=10)

        self.entry_telefono = ctk.CTkEntry(self, placeholder_text="Teléfono de Contacto", width=300)
        self.entry_telefono.pack(pady=10)

        # Botón Guardar
        ctk.CTkButton(self, text="Guardar y Cerrar", command=self.guardar, fg_color="#28a745", hover_color="#218838").pack(pady=20)

    def guardar(self):
        nom = self.entry_nombre.get()
        dir = self.entry_direccion.get()
        tel = self.entry_telefono.get()

        if nom:
            exito = self.service.registrar_organizacion(nom, dir, tel)
            if exito:
                self.callback_actualizar() # ¡Importante! Avisamos a la ventana padre que actualice la lista
                self.destroy()
            else:
                print("Error al guardar")