import os
from pathlib import Path

import psycopg2
import psycopg2.extras

# Los datos de conexión se leen del archivo .env que está en la carpeta
# principal del proyecto. Ese archivo no se sube a GitHub (está en .gitignore).
# Para crearlo, copiar .env.example como .env y completar los valores.
RUTA_ENV = Path(__file__).resolve().parent.parent / ".env"


def cargar_env(ruta=RUTA_ENV):
    """Carga las variables del archivo .env sin pisar las que ya existen."""
    if not ruta.exists():
        return
    with open(ruta, encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


cargar_env()


class ConexionBD:
    def __init__(self):
        self.host = os.environ.get("DB_HOST")
        self.puerto = os.environ.get("DB_PORT", "5432")
        self.base_datos = os.environ.get("DB_NAME", "neondb")
        self.usuario = os.environ.get("DB_USER")
        self.contrasena = os.environ.get("DB_PASSWORD")

    def obtener_conexion(self):
        faltantes = [nombre for nombre, valor in (
            ("DB_HOST", self.host),
            ("DB_USER", self.usuario),
            ("DB_PASSWORD", self.contrasena),
        ) if not valor]
        if faltantes:
            print("Faltan datos de conexión en el archivo .env: " + ", ".join(faltantes))
            print("Copiá .env.example como .env en la carpeta principal y completalo.")
            return None
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.puerto,
                dbname=self.base_datos,
                user=self.usuario,
                password=self.contrasena,
                sslmode="require",
                cursor_factory=psycopg2.extras.RealDictCursor,
            )
            return conn
        except psycopg2.Error as e:
            print(f"Error al conectar con la base de datos: {e}")
            return None
