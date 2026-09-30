# Capa de Acceso a Datos (Data Access Layer) - Mock
# En este Hito 2 la aplicación es un prototipo navegable "aún sin conexión
# a la base" (según lineamientos de cátedra): los datos viven en memoria.
# La conexión real a PostgreSQL (conexion.py) se integrará en el Hito 3.
#
# Los valores de tipo/especialidad/estado usados acá son EXACTAMENTE los
# mismos que los CHECK del script_tecnoservice.sql, para que al migrar a la
# base real ningún dato mock viole una restricción.
#
# Reglas de negocio de la Minuta de Requerimientos reflejadas acá (y en el
# script SQL, como trigger / CHECK) para que el prototipo se comporte igual
# a como la base real se va a comportar en el Hito 3:
#   - No se puede usar un repuesto si no hay stock suficiente (ver
#     usar_repuesto_en_reparacion). En la base real esto lo resuelve el
#     trigger trg_validar_stock.
#   - No se puede pasar una orden a "En Reparación"/"Terminado"/"Entregado"
#     si el presupuesto no fue Aceptado (ver puede_avanzar_estado). En la
#     base real esto lo resuelve el CHECK chk_presupuesto_aprobado_para_reparar.

TIPOS_EQUIPO = ["Notebook", "PC de Escritorio", "Impresora", "All in One", "Otro"]
ESPECIALIDADES_TECNICO = ["Hardware", "Software", "Electrónica", "General"]
ESTADOS_TECNICO = ["Activo", "Inactivo"]
ESTADOS_REPARACION = ["Ingresada", "En Diagnóstico", "Esperando Repuesto", "En Reparación", "Terminado", "Entregado"]
ESTADOS_PRESUPUESTO = ["Pendiente", "Aceptado", "Rechazado"]
ESTADOS_QUE_REQUIEREN_PRESUPUESTO_ACEPTADO = {"En Reparación", "Terminado", "Entregado"}


class StockInsuficienteError(Exception):
    pass


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

        # REPARACION (orden de trabajo): acá vive la falla reportada y el estado.
        # "presupuesto_aprobado": Pendiente / Aceptado / Rechazado.
        # "repuestos_usados": detalle de repuestos consumidos en esta orden.
        self.reparaciones = [
            {"id": 1001, "id_equipo": 1, "equipo": "Notebook Lenovo IdeaPad 3", "cliente": "García, Ana Maria",
             "id_tecnico": 1, "tecnico": "Pérez, Gonzalo", "fecha": "2026-09-18",
             "falla_reportada": "No enciende, pantalla negra", "diagnostico": "",
             "estado": "En Diagnóstico", "presupuesto_aprobado": "Pendiente",
             "estimado": 65000.00, "total": 0.00, "repuestos_usados": []},
            {"id": 1002, "id_equipo": 2, "equipo": "PC Exo Ready", "cliente": "Martínez, Carlos",
             "id_tecnico": 2, "tecnico": "Ríos, Mariana", "fecha": "2026-09-19",
             "falla_reportada": "Lentitud extrema, posible disco dañado", "diagnostico": "",
             "estado": "Esperando Repuesto", "presupuesto_aprobado": "Aceptado",
             "estimado": 45000.00, "total": 77000.00, "repuestos_usados": []},
            {"id": 1003, "id_equipo": 3, "equipo": "Impresora Epson L3210", "cliente": "López, Sofía",
             "id_tecnico": 3, "tecnico": "Fernández, Esteban", "fecha": "2026-09-20",
             "falla_reportada": "Atasco de papel y parpadea luz roja", "diagnostico": "Limpieza de rodillos realizada.",
             "estado": "Terminado", "presupuesto_aprobado": "Aceptado",
             "estimado": 25000.00, "total": 25000.00, "repuestos_usados": []}
        ]

    # =========================================================
    # CLIENTE - ABM completo
    # =========================================================
    def obtener_clientes(self):
        return self.clientes

    def agregar_cliente(self, dni, nombre, telefono):
        nuevo_id = (max((c["id"] for c in self.clientes), default=0)) + 1
        nuevo = {"id": nuevo_id, "dni": dni, "nombre": nombre, "telefono": telefono}
        self.clientes.append(nuevo)
        return nuevo

    def modificar_cliente(self, id_cliente, dni, nombre, telefono):
        for c in self.clientes:
            if c["id"] == id_cliente:
                c["dni"], c["nombre"], c["telefono"] = dni, nombre, telefono
                return c
        return None

    def eliminar_cliente(self, id_cliente):
        tiene_equipos = any(e["id_cliente"] == id_cliente for e in self.equipos)
        if tiene_equipos:
            raise ValueError("No se puede eliminar: el cliente tiene equipos registrados.")
        self.clientes = [c for c in self.clientes if c["id"] != id_cliente]

    # =========================================================
    # EQUIPO
    # =========================================================
    def obtener_equipos(self):
        return self.equipos

    def agregar_equipo(self, tipo, marca, modelo, serie, id_cliente, cliente_nombre):
        nuevo_id = (max((e["id"] for e in self.equipos), default=0)) + 1
        nuevo = {"id": nuevo_id, "tipo": tipo, "marca": marca, "modelo": modelo,
                  "serie": serie, "id_cliente": id_cliente, "cliente": cliente_nombre}
        self.equipos.append(nuevo)
        return nuevo

    # =========================================================
    # REPARACION (orden de trabajo)
    # =========================================================
    def obtener_reparaciones(self):
        return self.reparaciones

    def agregar_reparacion(self, id_equipo, equipo_desc, cliente_nombre, id_tecnico, tecnico_nombre,
                            fecha, falla_reportada, estimado):
        nuevo_id = 1001 + len(self.reparaciones)
        nueva = {"id": nuevo_id, "id_equipo": id_equipo, "equipo": equipo_desc, "cliente": cliente_nombre,
                  "id_tecnico": id_tecnico, "tecnico": tecnico_nombre, "fecha": fecha,
                  "falla_reportada": falla_reportada, "diagnostico": "", "estado": "Ingresada",
                  "presupuesto_aprobado": "Pendiente", "estimado": estimado, "total": 0.00,
                  "repuestos_usados": []}
        self.reparaciones.append(nueva)
        return nueva

    def puede_avanzar_estado(self, id_reparacion, nuevo_estado):
        """Regla de negocio (minuta): valida que si el nuevo estado exige
        presupuesto aceptado, la orden ya lo tenga. Devuelve (ok, mensaje)."""
        rep = next((r for r in self.reparaciones if r["id"] == id_reparacion), None)
        if rep is None:
            return False, "La orden no existe."
        if nuevo_estado in ESTADOS_QUE_REQUIEREN_PRESUPUESTO_ACEPTADO and rep["presupuesto_aprobado"] != "Aceptado":
            return False, (
                f"No se puede pasar la orden a '{nuevo_estado}' porque el presupuesto todavía "
                f"está en estado '{rep['presupuesto_aprobado']}'. Primero debe marcarse como Aceptado."
            )
        return True, ""

    def actualizar_estado_reparacion(self, id_reparacion, nuevo_estado, nuevo_diagnostico):
        ok, mensaje = self.puede_avanzar_estado(id_reparacion, nuevo_estado)
        if not ok:
            raise ValueError(mensaje)
        for r in self.reparaciones:
            if r["id"] == id_reparacion:
                r["estado"] = nuevo_estado
                r["diagnostico"] = nuevo_diagnostico
                return r
        return None

    def actualizar_presupuesto(self, id_reparacion, nuevo_valor):
        for r in self.reparaciones:
            if r["id"] == id_reparacion:
                r["presupuesto_aprobado"] = nuevo_valor
                return r
        return None

    def usar_repuesto_en_reparacion(self, id_reparacion, id_repuesto, cantidad):
        """Regla de negocio (minuta): no se puede usar un repuesto sin stock
        suficiente. Equivalente mock del trigger trg_validar_stock del SQL."""
        rep = next((r for r in self.reparaciones if r["id"] == id_reparacion), None)
        repuesto = next((x for x in self.repuestos if x["id"] == id_repuesto), None)
        if rep is None or repuesto is None:
            raise ValueError("Orden o repuesto inexistente.")
        if repuesto["stock"] < cantidad:
            raise StockInsuficienteError(
                f"Stock insuficiente para '{repuesto['descripcion']}': "
                f"disponible {repuesto['stock']}, solicitado {cantidad}."
            )
        repuesto["stock"] -= cantidad
        rep["repuestos_usados"].append({
            "id_repuesto": repuesto["id"], "descripcion": repuesto["descripcion"],
            "cantidad": cantidad, "precio_unitario_aplicado": repuesto["precio"],
        })
        rep["total"] = rep.get("total", 0.0) + repuesto["precio"] * cantidad
        return rep

    # =========================================================
    # TECNICO - ABM completo
    # =========================================================
    def obtener_tecnicos(self):
        return self.tecnicos

    def agregar_tecnico(self, legajo, dni, nombre, apellido, especialidad, estado):
        nuevo_id = (max((t["id"] for t in self.tecnicos), default=0)) + 1
        nuevo = {"id": nuevo_id, "legajo": legajo, "dni": dni, "nombre": nombre,
                  "apellido": apellido, "especialidad": especialidad, "estado": estado}
        self.tecnicos.append(nuevo)
        return nuevo

    def modificar_tecnico(self, id_tecnico, legajo, dni, nombre, apellido, especialidad, estado):
        for t in self.tecnicos:
            if t["id"] == id_tecnico:
                t.update(legajo=legajo, dni=dni, nombre=nombre, apellido=apellido,
                         especialidad=especialidad, estado=estado)
                return t
        return None

    def eliminar_tecnico(self, id_tecnico):
        tiene_ordenes = any(r["id_tecnico"] == id_tecnico for r in self.reparaciones)
        if tiene_ordenes:
            raise ValueError("No se puede eliminar: el técnico tiene órdenes de trabajo asignadas.")
        self.tecnicos = [t for t in self.tecnicos if t["id"] != id_tecnico]

    # =========================================================
    # REPUESTO - ABM completo
    # =========================================================
    def obtener_repuestos(self):
        return self.repuestos

    def agregar_repuesto(self, codigo, descripcion, precio, stock, minimo):
        nuevo_id = (max((r["id"] for r in self.repuestos), default=0)) + 1
        nuevo = {"id": nuevo_id, "codigo": codigo, "descripcion": descripcion,
                  "precio": float(precio), "stock": int(stock), "minimo": int(minimo)}
        self.repuestos.append(nuevo)
        return nuevo

    def modificar_repuesto(self, id_repuesto, codigo, descripcion, precio, stock, minimo):
        for r in self.repuestos:
            if r["id"] == id_repuesto:
                r.update(codigo=codigo, descripcion=descripcion, precio=float(precio),
                         stock=int(stock), minimo=int(minimo))
                return r
        return None

    def eliminar_repuesto(self, id_repuesto):
        usado = any(any(u["id_repuesto"] == id_repuesto for u in r["repuestos_usados"])
                    for r in self.reparaciones)
        if usado:
            raise ValueError("No se puede eliminar: el repuesto ya fue utilizado en alguna orden.")
        self.repuestos = [r for r in self.repuestos if r["id"] != id_repuesto]
