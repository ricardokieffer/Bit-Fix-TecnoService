import psycopg2
import psycopg2.extras


class ConexionBD:
    # datos de la base en Neon
    def __init__(self, host="ep-muddy-bread-b4m17p0l-pooler.c-6.us-east-2.aws.neon.tech", puerto="5432", base_datos="neondb",
                 usuario="neondb_owner", contrasena="npg_qzOWlsw7P5Ki"):
        self.host = host
        self.puerto = puerto
        self.base_datos = base_datos
        self.usuario = usuario
        self.contrasena = contrasena

    def obtener_conexion(self):
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
