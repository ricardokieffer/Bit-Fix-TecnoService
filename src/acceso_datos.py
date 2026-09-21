# Capa de Acceso a Datos (Data Access Layer) - Mock
# En este Hito 2 la aplicación es un prototipo navegable "aún sin conexión
# a la base" (según lineamientos de cátedra): los datos viven en memoria.
# La conexión real a PostgreSQL (conexion.py) se integrará en el Hito 3.
#
# Los valores de tipo/especialidad/estado usados acá son EXACTAMENTE los
# mismos que los CHECK del script_tecnoservice.sql, para que al migrar a la
# base real ningún dato mock viole una restricción.

TIPOS_EQUIPO = ["Notebook", "PC de Escritorio", "Impresora", "All in One", "Otro"]
ESPECIALIDADES_TECNICO = ["Hardware", "Software", "Electrónica", "General"]
ESTADOS_TECNICO = ["Activo", "Inactivo"]
ESTADOS_REPARACION = ["Ingresada", "En Diagnóstico", "Esperando Repuesto", "En Reparación", "Terminado", "Entregado"]


class AccesoDatosMock:
    def __init__(self):
        self.clientes = [
            {"id": 1, "dni": "35123456", "nombre": "García, Ana Maria", "telefono": "351-4567890"},
            {"id": 2, "dni": "38987654", "nombre": "Martínez, Carlos", "telefono": "351-6543210"},
            {"id": 3, "dni": "32111222", "nombre": "López, Sofía", "telefono": "351-7890123"}
        ]

        # EQUIPO: solo datos del hardware (la falla y el estado viven en REPARACION)
        self.equipos = [
            {"id": 1, "tipo": "Notebook", "marca": "Lenovo", "modelo": "IdeaPad 3", "serie": "NV123456", "id_cliente": 1, "cliente": "García, Ana Maria"},
            {"id": 2, "tipo": "PC de Escritorio", "marca": "Exo", "modelo": "Ready", "serie": "EX987654", "id_cliente": 2, "cliente": "Martínez, Carlos"},
            {"id": 3, "tipo": "Impresora", "marca": "Epson", "modelo": "L3210", "serie": "EP456789", "id_cliente": 3, "cliente": "López, Sofía"}
        ]

        self.tecnicos = [
            {"id": 1, "legajo": "TEC-001", "dni": "33444555", "nombre": "Gonzalo", "apellido": "Pérez", "especialidad": "Hardware", "estado": "Activo"},
            {"id": 2, "legajo": "TEC-002", "dni": "36777888", "nombre": "Mariana", "apellido": "Ríos", "especialidad": "Software", "estado": "Activo"},
            {"id": 3, "legajo": "TEC-003", "dni": "40111222", "nombre": "Esteban", "apellido": "Fernández", "especialidad": "General", "estado": "Inactivo"}
        ]

        self.repuestos = [
            {"id": 1, "codigo": "REP-001", "descripcion": "Disco SSD Kingston 480GB SATA3", "precio": 45000.00, "stock": 8, "minimo": 3},
            {"id": 2, "codigo": "REP-002", "descripcion": "Memoria RAM DDR4 8GB 3200MHz", "precio": 32000.00, "stock": 12, "minimo": 5},
            {"id": 3, "codigo": "REP-003", "descripcion": "Fuente de Alimentación LNC 600W", "precio": 58000.00, "stock": 1, "minimo": 2},
            {"id": 4, "codigo": "REP-004", "descripcion": "Pasta Térmica Arctic MX-4 4g", "precio": 12000.00, "stock": 15, "minimo": 4}
        ]

        # REPARACION (orden de trabajo): acá vive la falla reportada y el estado
        self.reparaciones = [
            {"id": 1001, "id_equipo": 1, "equipo": "Notebook Lenovo IdeaPad 3", "cliente": "García, Ana Maria",
             "id_tecnico": 1, "tecnico": "Pérez, Gonzalo", "fecha": "2026-09-18",
             "falla_reportada": "No enciende, pantalla negra", "diagnostico": "",
             "estado": "En Diagnóstico", "estimado": 65000.00, "total": 0.00},
            {"id": 1002, "id_equipo": 2, "equipo": "PC Exo Ready", "cliente": "Martínez, Carlos",
             "id_tecnico": 2, "tecnico": "Ríos, Mariana", "fecha": "2026-09-19",
             "falla_reportada": "Lentitud extrema, posible disco dañado", "diagnostico": "",
             "estado": "Esperando Repuesto", "estimado": 45000.00, "total": 77000.00},
            {"id": 1003, "id_equipo": 3, "equipo": "Impresora Epson L3210", "cliente": "López, Sofía",
             "id_tecnico": 3, "tecnico": "Fernández, Esteban", "fecha": "2026-09-20",
             "falla_reportada": "Atasco de papel y parpadea luz roja", "diagnostico": "Limpieza de rodillos realizada.",
             "estado": "Terminado", "estimado": 25000.00, "total": 25000.00}
        ]

    # ---- Consultas ----
    def obtener_clientes(self):
        return self.clientes

    def obtener_equipos(self):
        return self.equipos

    def obtener_tecnicos(self):
        return self.tecnicos

    def obtener_repuestos(self):
        return self.repuestos

    def obtener_reparaciones(self):
        return self.reparaciones

    # ---- Altas ----
    def agregar_cliente(self, dni, nombre, telefono):
        nuevo_id = len(self.clientes) + 1
        nuevo = {"id": nuevo_id, "dni": dni, "nombre": nombre, "telefono": telefono}
        self.clientes.append(nuevo)
        return nuevo

    def agregar_equipo(self, tipo, marca, modelo, serie, id_cliente, cliente_nombre):
        nuevo_id = len(self.equipos) + 1
        nuevo = {"id": nuevo_id, "tipo": tipo, "marca": marca, "modelo": modelo,
                  "serie": serie, "id_cliente": id_cliente, "cliente": cliente_nombre}
        self.equipos.append(nuevo)
        return nuevo

    def agregar_reparacion(self, id_equipo, equipo_desc, cliente_nombre, id_tecnico, tecnico_nombre,
                            fecha, falla_reportada, estimado):
        nuevo_id = 1001 + len(self.reparaciones)
        nueva = {"id": nuevo_id, "id_equipo": id_equipo, "equipo": equipo_desc, "cliente": cliente_nombre,
                  "id_tecnico": id_tecnico, "tecnico": tecnico_nombre, "fecha": fecha,
                  "falla_reportada": falla_reportada, "diagnostico": "", "estado": "Ingresada",
                  "estimado": estimado, "total": 0.00}
        self.reparaciones.append(nueva)
        return nueva

    def agregar_tecnico(self, legajo, dni, nombre, apellido, especialidad, estado):
        nuevo_id = len(self.tecnicos) + 1
        nuevo = {"id": nuevo_id, "legajo": legajo, "dni": dni, "nombre": nombre,
                  "apellido": apellido, "especialidad": especialidad, "estado": estado}
        self.tecnicos.append(nuevo)
        return nuevo

    def agregar_repuesto(self, codigo, descripcion, precio, stock, minimo):
        nuevo_id = len(self.repuestos) + 1
        nuevo = {"id": nuevo_id, "codigo": codigo, "descripcion": descripcion,
                  "precio": float(precio), "stock": int(stock), "minimo": int(minimo)}
        self.repuestos.append(nuevo)
        return nuevo

    # ---- Modificación de estado de una orden ----
    def actualizar_estado_reparacion(self, id_reparacion, nuevo_estado, nuevo_diagnostico):
        for r in self.reparaciones:
            if r["id"] == id_reparacion:
                r["estado"] = nuevo_estado
                r["diagnostico"] = nuevo_diagnostico
                return r
        return None
