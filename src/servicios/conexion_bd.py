import os
import psycopg2
from dotenv import load_dotenv

# Cargamos las variables del archivo .env
load_dotenv()

def obtener_conexion():
    """
    Establece y retorna una conexión a la base de datos PostgreSQL.
    Retorna None si falla la conexión.
    """
    try:
        # Obtenemos las variables de entorno
        host = os.getenv('DB_HOST')
        database = os.getenv('DB_NAME')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        port = os.getenv('DB_PORT')

        # Intentamos conectar
        conexion = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        return conexion

    except psycopg2.Error as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return None

def cerrar_conexion(conexion):
    """Cierra la conexión si está abierta."""
    if conexion:
        conexion.close()
        print("🔒 Conexión cerrada correctamente.")

# --- BLOQUE DE PRUEBA ---
# Esto solo se ejecuta si corres este archivo directamente, no si lo importas.
if __name__ == "__main__":
    print("Probando conexión...")
    conn = obtener_conexion()
    if conn:
        print(f"✅ ¡Conexión exitosa a la base de datos '{os.getenv('DB_NAME')}'!")
        cerrar_conexion(conn)