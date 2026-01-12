import customtkinter as ctk
from servicios.servicios_auxiliares import ServiciosAuxiliares
from tkinter import messagebox

class VentanaNuevoEvento(ctk.CTkToplevel):
    def __init__(self, parent, callback_actualizar):
        super().__init__(parent)
        self.callback_actualizar = callback_actualizar
        self.service = ServiciosAuxiliares()
        
        self.title("Nuevo Evento")
        self.geometry("400x450")
        self.resizable(False, False)

        ctk.CTkLabel(self, text="Registrar Evento", font=("Roboto", 20, "bold")).pack(pady=15)

        # Campos
        self.entry_nombre = ctk.CTkEntry(self, placeholder_text="Nombre del Evento", width=300)
        self.entry_nombre.pack(pady=8)

        self.entry_fecha = ctk.CTkEntry(self, placeholder_text="Fecha (YYYY-MM-DD)", width=300)
        self.entry_fecha.pack(pady=8)

        self.entry_lugar = ctk.CTkEntry(self, placeholder_text="Lugar / Ubicación", width=300)
        self.entry_lugar.pack(pady=8)

        self.entry_capacidad = ctk.CTkEntry(self, placeholder_text="Capacidad (Ej. 100)", width=300)
        self.entry_capacidad.pack(pady=8)
        
        self.entry_precio = ctk.CTkEntry(self, placeholder_text="Precio Base (Ej. 15.00)", width=300)
        self.entry_precio.pack(pady=8)

        ctk.CTkButton(self, text="Guardar Evento", command=self.guardar, fg_color="#28a745").pack(pady=20)

    def guardar(self):
        nom = self.entry_nombre.get()
        fec = self.entry_fecha.get()
        lug = self.entry_lugar.get()
        cap = self.entry_capacidad.get()
        pre = self.entry_precio.get()

        if not nom or not fec or not cap or not pre:
            messagebox.showwarning("Faltan datos", "Nombre, Fecha, Capacidad y Precio son obligatorios.")
            return

        # Validación simple de números
        try:
            int(cap)
            float(pre)
        except ValueError:
            messagebox.showerror("Error", "Capacidad debe ser entero y Precio un número decimal.")
            return

        if self.service.registrar_evento(nom, fec, lug, int(cap), float(pre)):
            messagebox.showinfo("Éxito", "Evento creado correctamente.")
            self.callback_actualizar()
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo guardar el evento. Verifique el formato de fecha (YYYY-MM-DD).")