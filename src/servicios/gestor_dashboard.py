from servicios.conexion_bd import obtener_conexion
from datetime import date

class GestorDashboard:
    def __init__(self):
        self.conn = obtener_conexion()

    def obtener_eventos_proximos(self):
        """
        Retorna una lista de eventos cuya fecha es mayor a hoy.
        """
        if not self.conn: return []
        
        try:
            cursor = self.conn.cursor()
            # Filtramos por fecha > fecha actual
            query = """
                SELECT id_evento, nombre, fecha_evento, lugar, capacidad_total 
                FROM eventos 
                WHERE fecha_evento >= CURRENT_DATE AND estatus = TRUE
                ORDER BY fecha_evento ASC
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            # Convertimos a una lista de diccionarios para facilitar su uso en la Vista
            eventos = []
            for row in resultados:
                eventos.append({
                    "id": row[0],
                    "nombre": row[1],
                    "fecha": row[2],
                    "lugar": row[3],
                    "capacidad": row[4]
                })
            cursor.close()
            return eventos
        except Exception as e:
            print(f"Error al obtener eventos próximos: {e}")
            return []

    def obtener_asistentes_por_estado_pago(self, estado: str):
        """
        Filtra asistentes según si deben o ya pagaron.
        estado: 'PENDIENTE' o 'PAGADO'
        """
        if not self.conn: return []

        try:
            cursor = self.conn.cursor()
            
            # Construimos la query base con JOINS para tener nombres legibles
            base_query = """
                SELECT a.nombre, a.apellido_paterno, e.nombre, r.codigo_reserva, r.total_a_pagar
                FROM reservas r
                JOIN asistentes a ON r.id_asistente = a.id_asistente
                JOIN eventos e ON r.id_evento = e.id_evento
                JOIN estados_reserva er ON r.id_estado_reserva = er.id_estado_reserva
                WHERE r.estatus = TRUE
            """

            if estado == 'PENDIENTE':
                # Buscamos estado 'PENDIENTE'
                query = base_query + " AND er.nombre = 'PENDIENTE'"
            elif estado == 'PAGADO':
                # Buscamos 'FACTURADO' o 'CONFIRMADO' (Ambos cuentan como proceso de pago avanzado)
                query = base_query + " AND er.nombre IN ('FACTURADO', 'CONFIRMADO')"
            else:
                return []

            cursor.execute(query)
            resultados = cursor.fetchall()
            
            lista_asistentes = []
            for row in resultados:
                lista_asistentes.append({
                    "nombre_completo": f"{row[0]} {row[1]}",
                    "evento": row[2],
                    "codigo": row[3],
                    "monto": row[4]
                })
            cursor.close()
            return lista_asistentes

        except Exception as e:
            print(f"Error al obtener asistentes ({estado}): {e}")
            return []
            
    def __del__(self):
        if self.conn:
            self.conn.close()