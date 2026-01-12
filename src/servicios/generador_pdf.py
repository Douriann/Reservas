import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import qrcode

class GeneradorPDF:
    def __init__(self, carpeta_reportes="reportes"):
        self.ruta_base = os.path.join(os.getcwd(), carpeta_reportes)
        os.makedirs(self.ruta_base, exist_ok=True)

    def generar_comprobante(self, datos: dict):
        """
        Recibe un diccionario con: codigo, evento, fecha_evento, asiento, 
        asistente_nombre, organizacion, fecha_solicitud, estado_pago, precio
        """
        nombre_archivo = f"comprobante_{datos['codigo']}.pdf"
        ruta_completa = os.path.join(self.ruta_base, nombre_archivo)

        c = canvas.Canvas(ruta_completa, pagesize=letter)
        width, height = letter

        # --- ENCABEZADO ---
        c.setFont("Helvetica-Bold", 22)
        c.drawString(1 * inch, height - 1 * inch, "Comprobante de Pre-Registro")
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, height - 1.4 * inch, f"Evento: {datos['evento']}")
        c.setFont("Helvetica", 12)
        c.drawString(1 * inch, height - 1.6 * inch, f"Fecha del Evento: {datos['fecha_evento']}")

        # --- CAJA DE DATOS DEL REGISTRO ---
        y_start = height - 2.5 * inch
        line_height = 20
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1 * inch, y_start, "Detalles del Registro:")
        
        c.setFont("Helvetica", 11)
        # 1. Asistente y Organización
        c.drawString(1.2 * inch, y_start - 30, f"Asistente: {datos['asistente_nombre']} (C.I: {datos['asistente_cedula']})")
        c.drawString(1.2 * inch, y_start - 50, f"Organización: {datos['organizacion']}")
        
        # 2. Datos de Reserva (Lo que pediste explícitamente)
        c.drawString(1.2 * inch, y_start - 80, f"Nro. Reserva: {datos['codigo']}")
        c.drawString(1.2 * inch, y_start - 100, f"Fecha Solicitud: {datos['fecha_solicitud']}")
        c.drawString(1.2 * inch, y_start - 120, f"Asiento Asignado: {datos['asiento']}")
        
        # 3. Estado y Precio
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1.2 * inch, y_start - 150, f"Estado: {datos['estado_pago']}")
        c.drawString(1.2 * inch, y_start - 170, f"Total a Pagar: ${datos['precio']}")

        # --- QR CODE ---
        qr = qrcode.make(datos['codigo'])
        ruta_qr = "temp_qr.png"
        qr.save(ruta_qr)
        # Dibujamos QR a la derecha
        c.drawImage(ruta_qr, 4.5 * inch, height - 4.5 * inch, width=2*inch, height=2*inch)
        
        if os.path.exists(ruta_qr):
            os.remove(ruta_qr)

        # --- PIE DE PÁGINA ---
        c.setFont("Helvetica", 9)
        c.drawString(1 * inch, 1 * inch, "Nota: Presente este comprobante en taquilla para completar su pago.")
        c.save()

        return ruta_completa