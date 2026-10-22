# consultas a la base de datos

from conexion import ConexionBD

TIPOS_EQUIPO = ["Notebook", "PC de Escritorio", "Impresora", "All in One", "Otro"]
ESPECIALIDADES_TECNICO = ["Hardware", "Software", "Electrónica", "General"]
ESTADOS_TECNICO = ["Activo", "Inactivo"]
ESTADOS_REPARACION = ["Ingresada", "En Diagnóstico", "Esperando Repuesto", "En Reparación", "Terminado", "Entregado"]


class AccesoDatosSQL:
    def __init__(self):
        self.conexion = ConexionBD()

    # consultas
    def obtener_clientes(self):
        conn = self.conexion.obtener_conexion()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id_cliente AS id, dni, nombre, telefono
                FROM cliente ORDER BY id_cliente
            """)
            filas = cur.fetchall()
        conn.close()
        return [dict(f) for f in filas]

    def obtener_equipos(self):
        conn = self.conexion.obtener_conexion()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT e.id_equipo AS id, e.tipo, e.marca, e.modelo, e.numero_serie AS serie,
                       e.id_cliente, c.nombre AS cliente
                FROM equipo e JOIN cliente c ON e.id_cliente = c.id_cliente
                ORDER BY e.id_equipo
            """)
            filas = cur.fetchall()
        conn.close()
        return [dict(f) for f in filas]

    def obtener_tecnicos(self):
        conn = self.conexion.obtener_conexion()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id_tecnico AS id, legajo, dni, nombre, apellido, especialidad, estado
                FROM tecnico ORDER BY id_tecnico
            """)
            filas = cur.fetchall()
        conn.close()
        return [dict(f) for f in filas]

    def obtener_repuestos(self):
        conn = self.conexion.obtener_conexion()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id_repuesto AS id, codigo, descripcion,
                       precio_unitario AS precio, stock, stock_minimo AS minimo
                FROM repuesto ORDER BY id_repuesto
            """)
            filas = cur.fetchall()
        conn.close()
        return [dict(f) for f in filas]

    def obtener_reparaciones(self):
        conn = self.conexion.obtener_conexion()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.id_reparacion AS id, r.id_equipo,
                       (e.tipo || ' ' || e.marca || ' ' || e.modelo) AS equipo,
                       c.nombre AS cliente, r.id_tecnico,
                       (t.apellido || ', ' || t.nombre) AS tecnico,
                       r.fecha_ingreso AS fecha, r.falla_reportada,
                       r.diagnostico, r.estado, r.presupuesto_aprobado,
                       r.costo_estimado AS estimado, r.costo_total AS total
                FROM reparacion r
                JOIN equipo e ON r.id_equipo = e.id_equipo
                JOIN cliente c ON e.id_cliente = c.id_cliente
                JOIN tecnico t ON r.id_tecnico = t.id_tecnico
                ORDER BY r.id_reparacion
            """)
            filas = cur.fetchall()
        conn.close()
        return [dict(f) for f in filas]

    # altas
    def agregar_cliente(self, dni, nombre, telefono):
        conn = self.conexion.obtener_conexion()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO cliente (dni, nombre, telefono) VALUES (%s, %s, %s)
                ON CONFLICT (dni) DO UPDATE SET nombre = EXCLUDED.nombre, telefono = EXCLUDED.telefono
                RETURNING id_cliente AS id, dni, nombre, telefono
            """, (dni, nombre, telefono))
            nuevo = dict(cur.fetchone())
        conn.commit()
        conn.close()
        return nuevo

    def agregar_equipo(self, tipo, marca, modelo, serie, id_cliente, cliente_nombre):
        conn = self.conexion.obtener_conexion()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO equipo (tipo, marca, modelo, numero_serie, id_cliente)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_equipo AS id
            """, (tipo, marca, modelo, serie, id_cliente))
            nuevo_id = cur.fetchone()["id"]
        conn.commit()
        conn.close()
        return {"id": nuevo_id, "tipo": tipo, "marca": marca, "modelo": modelo,
                "serie": serie, "id_cliente": id_cliente, "cliente": cliente_nombre}

    def agregar_reparacion(self, id_equipo, equipo_desc, cliente_nombre, id_tecnico, tecnico_nombre,
                            fecha, falla_reportada, estimado):
        conn = self.conexion.obtener_conexion()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO reparacion (fecha_ingreso, falla_reportada, costo_estimado, id_equipo, id_tecnico)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_reparacion AS id
            """, (fecha, falla_reportada, estimado, id_equipo, id_tecnico))
            nuevo_id = cur.fetchone()["id"]
        conn.commit()
        conn.close()
        return {"id": nuevo_id, "id_equipo": id_equipo, "equipo": equipo_desc, "cliente": cliente_nombre,
                "id_tecnico": id_tecnico, "tecnico": tecnico_nombre, "fecha": fecha,
                "falla_reportada": falla_reportada, "diagnostico": "", "estado": "Ingresada",
                "estimado": estimado, "total": 0.00}

    def agregar_tecnico(self, legajo, dni, nombre, apellido, especialidad, estado):
        conn = self.conexion.obtener_conexion()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tecnico (legajo, dni, nombre, apellido, especialidad, estado)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_tecnico AS id
            """, (legajo, dni, nombre, apellido, especialidad, estado))
            nuevo_id = cur.fetchone()["id"]
        conn.commit()
        conn.close()
        return {"id": nuevo_id, "legajo": legajo, "dni": dni, "nombre": nombre,
                "apellido": apellido, "especialidad": especialidad, "estado": estado}

    def agregar_repuesto(self, codigo, descripcion, precio, stock, minimo):
        conn = self.conexion.obtener_conexion()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO repuesto (codigo, descripcion, precio_unitario, stock, stock_minimo)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_repuesto AS id
            """, (codigo, descripcion, float(precio), int(stock), int(minimo)))
            nuevo_id = cur.fetchone()["id"]
        conn.commit()
        conn.close()
        return {"id": nuevo_id, "codigo": codigo, "descripcion": descripcion,
                "precio": float(precio), "stock": int(stock), "minimo": int(minimo)}

    # actualizar orden
    def actualizar_estado_reparacion(self, id_reparacion, nuevo_estado, nuevo_diagnostico, presupuesto):
        conn = self.conexion.obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE reparacion
                    SET estado = %s, diagnostico = %s, presupuesto_aprobado = %s
                    WHERE id_reparacion = %s
                    RETURNING id_reparacion AS id, estado, diagnostico
                """, (nuevo_estado, nuevo_diagnostico, presupuesto, id_reparacion))
                fila = cur.fetchone()
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return dict(fila) if fila else None

    # modificar y eliminar
    def _ejecutar(self, sql, params):
        conn = self.conexion.obtener_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def modificar_cliente(self, id_cliente, dni, nombre, telefono):
        self._ejecutar("UPDATE cliente SET dni = %s, nombre = %s, telefono = %s WHERE id_cliente = %s",
                       (dni, nombre, telefono, id_cliente))

    def eliminar_cliente(self, id_cliente):
        self._ejecutar("DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,))

    def modificar_tecnico(self, id_tecnico, legajo, dni, nombre, apellido, especialidad, estado):
        self._ejecutar("""UPDATE tecnico SET legajo = %s, dni = %s, nombre = %s, apellido = %s,
                          especialidad = %s, estado = %s WHERE id_tecnico = %s""",
                       (legajo, dni, nombre, apellido, especialidad, estado, id_tecnico))

    def eliminar_tecnico(self, id_tecnico):
        self._ejecutar("DELETE FROM tecnico WHERE id_tecnico = %s", (id_tecnico,))

    def modificar_repuesto(self, id_repuesto, codigo, descripcion, precio, stock, minimo):
        self._ejecutar("""UPDATE repuesto SET codigo = %s, descripcion = %s, precio_unitario = %s,
                          stock = %s, stock_minimo = %s WHERE id_repuesto = %s""",
                       (codigo, descripcion, float(precio), int(stock), int(minimo), id_repuesto))

    def eliminar_repuesto(self, id_repuesto):
        self._ejecutar("DELETE FROM repuesto WHERE id_repuesto = %s", (id_repuesto,))
