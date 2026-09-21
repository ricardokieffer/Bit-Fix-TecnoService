"""
Módulo de Conexión a la Base de Datos - TecnoService PC
Motor: PostgreSQL (según Requisitos Técnicos Obligatorios de la cátedra).

Este módulo centraliza la apertura de conexiones para que acceso_datos.py
no tenga que conocer los parámetros de conexión ni la librería usada.
"""

import psycopg2
import psycopg2.extras


class ConexionBD:
    def __init__(self, host="localhost", puerto="5432", base_datos="tecnoservice",
                 usuario="postgres", contrasena=""):
        self.host = host
        self.puerto = puerto
        self.base_datos = base_datos
        self.usuario = usuario
        self.contrasena = contrasena

    def obtener_conexion(self):
        """Abre y devuelve una conexión a PostgreSQL, o None si falla."""
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.puerto,
                dbname=self.base_datos,
                user=self.usuario,
                password=self.contrasena,
                cursor_factory=psycopg2.extras.RealDictCursor,
            )
            return conn
        except psycopg2.Error as e:
            print(f"Error al conectar con la base de datos: {e}")
            return None
