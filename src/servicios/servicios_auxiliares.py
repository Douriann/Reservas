from servicios.conexion_bd import obtener_conexion

class ServiciosAuxiliares:
    def __init__(self):
        self.conn = obtener_conexion()

    def obtener_organizaciones(self):
        """Retorna lista de tuplas (id, nombre) para el ComboBox"""
        if not self.conn: return []
        cursor = self.conn.cursor()
        cursor.execute("SELECT id_organizacion, nombre_empresa FROM organizaciones WHERE estatus = TRUE ORDER BY nombre_empresa ASC")
        datos = cursor.fetchall()
        cursor.close()
        return datos # Retorna [(1, 'Empresa A'), (2, 'Empresa B')]

    def obtener_eventos_futuros(self):
        """Retorna lista de tuplas (id, nombre) de eventos futuros"""
        if not self.conn: return []
        cursor = self.conn.cursor()
        cursor.execute("SELECT id_evento, nombre FROM eventos WHERE fecha_evento >= CURRENT_DATE AND estatus = TRUE")
        datos = cursor.fetchall()
        cursor.close()
        return datos

    def registrar_organizacion(self, nombre, direccion, telefono):
        """Registra una nueva organización rápida desde el popup"""
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            sql = "INSERT INTO organizaciones (nombre_empresa, direccion, telefono_contacto, estatus) VALUES (%s, %s, %s, TRUE)"
            cursor.execute(sql, (nombre, direccion, telefono))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            self.conn.rollback()
            return False