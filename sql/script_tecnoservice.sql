-- TecnoService PC - Hito 3 (Evidencia 6)
-- Equipo Bit&Fix - PostgreSQL

DROP TABLE IF EXISTS detalle_reparacion CASCADE;
DROP TABLE IF EXISTS reparacion CASCADE;
DROP TABLE IF EXISTS equipo CASCADE;
DROP TABLE IF EXISTS cliente CASCADE;
DROP TABLE IF EXISTS tecnico CASCADE;
DROP TABLE IF EXISTS repuesto CASCADE;

-- cliente
CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    dni VARCHAR(15) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(30) NOT NULL
);

-- equipo
CREATE TABLE equipo (
    id_equipo SERIAL PRIMARY KEY,
    tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('Notebook', 'PC de Escritorio', 'Impresora', 'All in One', 'Otro')),
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    numero_serie VARCHAR(50) UNIQUE,
    id_cliente INT NOT NULL,
    CONSTRAINT fk_equipo_cliente FOREIGN KEY (id_cliente)
        REFERENCES cliente(id_cliente) ON DELETE CASCADE
);

-- tecnico
CREATE TABLE tecnico (
    id_tecnico SERIAL PRIMARY KEY,
    legajo VARCHAR(20) UNIQUE NOT NULL,
    dni VARCHAR(15) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    especialidad VARCHAR(50) NOT NULL CHECK (especialidad IN ('Hardware', 'Software', 'Electrónica', 'General')),
    estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);

-- reparacion
CREATE TABLE reparacion (
    id_reparacion SERIAL PRIMARY KEY,
    fecha_ingreso DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_salida DATE,
    falla_reportada TEXT NOT NULL,
    diagnostico TEXT,
    costo_estimado NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (costo_estimado >= 0),
    costo_total NUMERIC(10, 2) DEFAULT 0.00 CHECK (costo_total >= 0),
    estado VARCHAR(30) DEFAULT 'Ingresada'
        CHECK (estado IN ('Ingresada', 'En Diagnóstico', 'Esperando Repuesto', 'En Reparación', 'Terminado', 'Entregado')),
    presupuesto_aprobado VARCHAR(20) DEFAULT 'Pendiente'
        CHECK (presupuesto_aprobado IN ('Pendiente', 'Aceptado', 'Rechazado')),
    id_equipo INT NOT NULL,
    id_tecnico INT NOT NULL,
    CONSTRAINT fk_reparacion_equipo FOREIGN KEY (id_equipo)
        REFERENCES equipo(id_equipo) ON DELETE CASCADE,
    CONSTRAINT fk_reparacion_tecnico FOREIGN KEY (id_tecnico)
        REFERENCES tecnico(id_tecnico) ON DELETE RESTRICT,
    CONSTRAINT chk_fechas CHECK (fecha_salida IS NULL OR fecha_salida >= fecha_ingreso),
    -- no avanzar sin presupuesto aceptado
    CONSTRAINT chk_presupuesto_aprobado_para_reparar CHECK (
        presupuesto_aprobado = 'Aceptado' OR estado NOT IN ('En Reparación', 'Terminado', 'Entregado')
    )
);

-- repuesto
CREATE TABLE repuesto (
    id_repuesto SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(150) NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL CHECK (precio_unitario > 0),
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    stock_minimo INT NOT NULL DEFAULT 2 CHECK (stock_minimo >= 0)
);

-- detalle_reparacion
CREATE TABLE detalle_reparacion (
    id_reparacion INT NOT NULL,
    id_repuesto INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1 CHECK (cantidad > 0),
    precio_unitario_aplicado NUMERIC(10, 2) NOT NULL CHECK (precio_unitario_aplicado > 0),
    PRIMARY KEY (id_reparacion, id_repuesto),
    CONSTRAINT fk_detalle_reparacion FOREIGN KEY (id_reparacion)
        REFERENCES reparacion(id_reparacion) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_repuesto FOREIGN KEY (id_repuesto)
        REFERENCES repuesto(id_repuesto) ON DELETE RESTRICT
);

-- trigger: controla el stock y lo descuenta
CREATE OR REPLACE FUNCTION fn_validar_y_descontar_stock()
RETURNS TRIGGER AS $$
DECLARE
    stock_actual INT;
BEGIN
    SELECT stock INTO stock_actual FROM repuesto WHERE id_repuesto = NEW.id_repuesto;

    IF stock_actual IS NULL THEN
        RAISE EXCEPTION 'El repuesto % no existe', NEW.id_repuesto;
    END IF;

    IF stock_actual < NEW.cantidad THEN
        RAISE EXCEPTION 'Stock insuficiente para el repuesto % (disponible: %, solicitado: %)',
            NEW.id_repuesto, stock_actual, NEW.cantidad;
    END IF;

    UPDATE repuesto SET stock = stock - NEW.cantidad WHERE id_repuesto = NEW.id_repuesto;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_stock
    BEFORE INSERT ON detalle_reparacion
    FOR EACH ROW
    EXECUTE FUNCTION fn_validar_y_descontar_stock();

-- roles
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'admin_role') THEN
        CREATE ROLE admin_role;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'tecnico_role') THEN
        CREATE ROLE tecnico_role;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'recepcion_role') THEN
        CREATE ROLE recepcion_role;
    END IF;
END $$;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin_role;

GRANT SELECT ON cliente, equipo, repuesto TO tecnico_role;
GRANT SELECT, INSERT, UPDATE ON reparacion, detalle_reparacion TO tecnico_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO tecnico_role;

GRANT SELECT, INSERT, UPDATE ON cliente, equipo, reparacion TO recepcion_role;
GRANT SELECT ON tecnico, repuesto TO recepcion_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO recepcion_role;

-- datos de prueba
INSERT INTO cliente (dni, nombre, telefono) VALUES
('35123456', 'Garcia, Ana Maria', '351-4567890'),
('38987654', 'Martinez, Carlos', '351-6543210'),
('32111222', 'Lopez, Sofia', '351-7890123'),
('30456789', 'Fernandez, Luis', '351-2223344'),
('37888999', 'Rodriguez, Carla', '351-5556677'),
('33222111', 'Gomez, Pablo', '351-8889900'),
('36555444', 'Alvarez, Marina', '351-1112233'),
('31999888', 'Diaz, Ramiro', '351-4445566'),
('39777666', 'Torres, Lucia', '351-7778899'),
('34000111', 'Suarez, Diego', '351-9990011');

INSERT INTO tecnico (legajo, dni, nombre, apellido, especialidad, estado) VALUES
('TEC-001', '33444555', 'Gonzalo', 'Perez', 'Hardware', 'Activo'),
('TEC-002', '36777888', 'Mariana', 'Rios', 'Software', 'Activo'),
('TEC-003', '40111222', 'Esteban', 'Fernandez', 'General', 'Inactivo'),
('TEC-004', '38222333', 'Lucas', 'Molina', 'Electrónica', 'Activo'),
('TEC-005', '35666777', 'Paula', 'Gimenez', 'Hardware', 'Activo'),
('TEC-006', '37888099', 'Nadia', 'Sosa', 'Software', 'Activo'),
('TEC-007', '39000111', 'Franco', 'Acosta', 'General', 'Activo'),
('TEC-008', '34555666', 'Valeria', 'Nunez', 'Electrónica', 'Inactivo'),
('TEC-009', '36111222', 'Sergio', 'Ramos', 'Hardware', 'Activo'),
('TEC-010', '38999000', 'Camila', 'Ortiz', 'Software', 'Activo');

INSERT INTO repuesto (codigo, descripcion, precio_unitario, stock, stock_minimo) VALUES
('REP-001', 'Disco SSD Kingston 480GB SATA3', 45000.00, 8, 3),
('REP-002', 'Memoria RAM DDR4 8GB 3200MHz', 32000.00, 12, 5),
('REP-003', 'Fuente de Alimentacion LNC 600W', 58000.00, 1, 2),
('REP-004', 'Pasta Termica Arctic MX-4 4g', 12000.00, 15, 4),
('REP-005', 'Teclado USB Generico', 9000.00, 20, 5),
('REP-006', 'Cargador Notebook 65W', 22000.00, 6, 2),
('REP-007', 'Placa de Video GT 1030', 95000.00, 3, 1),
('REP-008', 'Cooler CPU 120mm', 15000.00, 10, 3),
('REP-009', 'Cable SATA 50cm', 3000.00, 25, 5),
('REP-010', 'Bateria Notebook Generica', 48000.00, 4, 2);

INSERT INTO equipo (tipo, marca, modelo, numero_serie, id_cliente) VALUES
('Notebook', 'Lenovo', 'IdeaPad 3', 'NV123456', 1),
('PC de Escritorio', 'Exo', 'Ready', 'EX987654', 2),
('Impresora', 'Epson', 'L3210', 'EP456789', 3),
('Notebook', 'HP', 'Pavilion 15', 'HP111222', 4),
('PC de Escritorio', 'Genérica', 'Gamer', 'PC333444', 5),
('All in One', 'Dell', 'Inspiron 24', 'DL555666', 6),
('Notebook', 'Asus', 'Vivobook', 'AS777888', 7),
('Impresora', 'HP', 'DeskJet 2775', 'HP999000', 8),
('Notebook', 'Acer', 'Aspire 5', 'AC222333', 9),
('PC de Escritorio', 'Genérica', 'Oficina', 'PC444555', 10);

INSERT INTO reparacion (fecha_ingreso, falla_reportada, diagnostico, costo_estimado, costo_total, estado, presupuesto_aprobado, id_equipo, id_tecnico) VALUES
('2026-09-18', 'No enciende, pantalla negra', NULL, 65000.00, 0.00, 'En Diagnóstico', 'Pendiente', 1, 1),
('2026-09-19', 'Lentitud extrema, posible disco danado', NULL, 45000.00, 77000.00, 'Esperando Repuesto', 'Aceptado', 2, 2),
('2026-09-20', 'Atasco de papel y parpadea luz roja', 'Limpieza de rodillos realizada.', 25000.00, 25000.00, 'Terminado', 'Aceptado', 3, 3),
('2026-09-21', 'No carga la bateria', NULL, 48000.00, 0.00, 'Ingresada', 'Pendiente', 4, 1),
('2026-09-22', 'Se apaga sola al rato de uso', NULL, 32000.00, 0.00, 'Ingresada', 'Pendiente', 5, 4),
('2026-09-23', 'No da imagen en el monitor', 'Falla de fuente detectada.', 58000.00, 58000.00, 'En Reparación', 'Aceptado', 6, 5),
('2026-09-24', 'Teclado no responde', NULL, 9000.00, 0.00, 'Ingresada', 'Pendiente', 7, 6),
('2026-09-25', 'Imprime con rayas', NULL, 15000.00, 0.00, 'En Diagnóstico', 'Pendiente', 8, 3),
('2026-09-26', 'Ruido en el cooler', NULL, 15000.00, 0.00, 'Ingresada', 'Pendiente', 9, 1),
('2026-09-27', 'Cliente rechazo presupuesto', 'Costo de reparacion no conveniente.', 95000.00, 0.00, 'En Diagnóstico', 'Rechazado', 10, 2);

INSERT INTO detalle_reparacion (id_reparacion, id_repuesto, cantidad, precio_unitario_aplicado) VALUES
(2, 1, 1, 45000.00),
(2, 4, 1, 12000.00),
(3, 9, 2, 3000.00),
(6, 3, 1, 58000.00);
