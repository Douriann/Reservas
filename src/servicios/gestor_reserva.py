import psycopg2
from servicios.conexion_bd import obtener_conexion
from modelo.Asistente import Asistente
from modelo.Organizacion import Organizacion
from datetime import datetime

class GestorReserva:
    def __init__(self):
        self.conn = obtener_conexion()

    # Cambia la línea de definición por esta (id_estado ahora es un argumento dinámico):
    def registrar_reserva_completa(self, asistente: Asistente, org: Organizacion, id_evento: int, id_estado: int) -> dict:
            """
            Retorna un diccionario con resultado y datos.
            Keys: 'exito' (bool), 'mensaje' (str), 'datos_pdf' (dict o None)
            """
            if not self.conn:
                return {"exito": False, "mensaje": "Sin conexión BD", "datos_pdf": None}

            try:
                cursor = self.conn.cursor()
                
                # --- PASO 0: OBTENER DATOS DEL EVENTO (PRECIO Y FECHA) ---
                # Soluciona el problema del $0.00 y la fecha genérica
                sql_evento = "SELECT precio_base, fecha_evento, nombre FROM eventos WHERE id_evento = %s"
                cursor.execute(sql_evento, (id_evento,))
                datos_evento = cursor.fetchone()
                
                if not datos_evento:
                    return {"exito": False, "mensaje": "Evento no encontrado", "datos_pdf": None}
                
                precio_evento = datos_evento[0] # Precio real
                fecha_evento = datos_evento[1]  # Fecha real
                nombre_evento = datos_evento[2]

                # --- PASO 1: GESTIÓN DE ORGANIZACIÓN ---
                sql_org_buscar = "SELECT id_organizacion FROM organizaciones WHERE nombre_empresa = %s"
                cursor.execute(sql_org_buscar, (org.nombre_empresa,))
                resultado_org = cursor.fetchone()

                if resultado_org:
                    id_org = resultado_org[0]
                else:
                    sql_org_crear = """
                        INSERT INTO organizaciones (nombre_empresa, direccion, telefono_contacto, estatus)
                        VALUES (%s, %s, %s, %s) RETURNING id_organizacion
                    """
                    cursor.execute(sql_org_crear, (org.nombre_empresa, org.direccion, org.telefono_contacto, True))
                    id_org = cursor.fetchone()[0]

                # --- PASO 2: GESTIÓN DE ASISTENTE ---
                sql_asist_buscar = "SELECT id_asistente FROM asistentes WHERE cedula = %s"
                cursor.execute(sql_asist_buscar, (asistente.cedula,))
                resultado_asist = cursor.fetchone()

                if resultado_asist:
                    id_asistente = resultado_asist[0]
                else:
                    sql_asist_crear = """
                        INSERT INTO asistentes (cedula, id_organizacion, nombre, apellido_paterno, 
                                            apellido_materno, email, telefono, puesto_cargo, fecha_registro, estatus)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_asistente
                    """
                    cursor.execute(sql_asist_crear, (
                        asistente.cedula, id_org, asistente.nombre, asistente.apellido_paterno,
                        asistente.apellido_materno, asistente.email, asistente.telefono, 
                        asistente.puesto_cargo, datetime.now(), True
                    ))
                    id_asistente = cursor.fetchone()[0]

                # --- PASO 2.5: VERIFICAR DUPLICADOS ---
                sql_check = "SELECT codigo_reserva FROM reservas WHERE id_evento = %s AND id_asistente = %s"
                cursor.execute(sql_check, (id_evento, id_asistente))
                existe = cursor.fetchone()
                if existe:
                    self.conn.rollback()
                    return {"exito": False, "mensaje": f"El asistente ya está registrado.\nCódigo: {existe[0]}", "datos_pdf": None}

                # --- PASO 3: CREAR RESERVA ---
                timestamp_actual = datetime.now()
                codigo_reserva = f"RES-{int(timestamp_actual.timestamp())}"
                
                # Calcular Asiento
                sql_count = "SELECT COUNT(*) FROM reservas WHERE id_evento = %s"
                cursor.execute(sql_count, (id_evento,))
                count = cursor.fetchone()[0]
                numero_asiento = f"A-{count + 1}"

                sql_reserva = """
                    INSERT INTO reservas (codigo_reserva, id_evento, id_asistente, id_estado_reserva, 
                                        fecha_solicitud, numero_asiento, total_a_pagar, estatus)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                # AQUÍ INSERTAMOS EL PRECIO REAL (precio_evento)
                cursor.execute(sql_reserva, (
                    codigo_reserva, id_evento, id_asistente, id_estado,
                    timestamp_actual, numero_asiento, precio_evento, True
                ))

                self.conn.commit()
                cursor.close()

                nombre_estado = "Confirmado / Pagado" if id_estado == 3 else "Pendiente por Pagar"
                # --- RETORNO DE DATOS COMPLETOS PARA EL PDF ---
                datos_para_reporte = {
                    "codigo": codigo_reserva,
                    "fecha_solicitud": timestamp_actual.strftime("%Y-%m-%d %H:%M"),
                    "evento": nombre_evento,
                    "fecha_evento": str(fecha_evento),
                    "asiento": numero_asiento,
                    "precio": precio_evento,
                    "asistente_nombre": asistente.nombre_completo(),
                    "asistente_cedula": asistente.cedula,
                    "organizacion": org.nombre_empresa,
                    "estado_pago": nombre_estado 
                }

                return {"exito": True, "mensaje": "Reserva Exitosa", "datos_pdf": datos_para_reporte}

            except Exception as e:
                self.conn.rollback()
                return {"exito": False, "mensaje": f"Error: {e}", "datos_pdf": None}

    def __del__(self):
        if self.conn:
            self.conn.close()