-- =============================================================================
-- TRABAJO INTEGRADOR ABP - MÓDULO PROGRAMADOR (ISPC 2026)
-- EVIDENCIA 5 - HITO 2: ESTRUCTURA DE BASE DE DATOS Y DATOS DE PRUEBA
-- Sistema de Gestión de Reparaciones: "TecnoService PC"
-- Equipo: Bit&Fix (Comisión B1)
-- Integrantes: KIEFFER, Ricardo; JERONIMO, Juan; BILEISIS, Joaquin; ESPINOSA, Thiago
-- Engine: PostgreSQL 14+
-- =============================================================================

-- -----------------------------------------------------------------------------
-- BLOQUE 1: LIMPIEZA PREVIA (Para permitir re-ejecución sin errores)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS detalle_reparacion CASCADE;
DROP TABLE IF EXISTS reparacion CASCADE;
DROP TABLE IF EXISTS equipo CASCADE;
DROP TABLE IF EXISTS cliente CASCADE;
DROP TABLE IF EXISTS tecnico CASCADE;
DROP TABLE IF EXISTS repuesto CASCADE;

-- -----------------------------------------------------------------------------
-- BLOQUE 2: CREACIÓN DE TABLAS Y RESTRICCIONES (DDL)
-- -----------------------------------------------------------------------------

-- 1. Tabla CLIENTE
CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    dni VARCHAR(15) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(30) NOT NULL
);

-- 2. Tabla EQUIPO
-- Nota de diseño: EQUIPO guarda únicamente los datos del hardware en sí.
-- La falla reportada y el estado de cada visita al taller viven en REPARACION,
-- porque un mismo equipo puede ingresar varias veces con fallas distintas
-- (ver cardinalidad EQUIPO 1:N REPARACION más abajo).
CREATE TABLE equipo (
    id_equipo SERIAL PRIMARY KEY,
    tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('Notebook', 'PC de Escritorio', 'Impresora', 'All in One', 'Otro')),
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    numero_serie VARCHAR(50),
    id_cliente INT NOT NULL,
    CONSTRAINT fk_equipo_cliente FOREIGN KEY (id_cliente)
        REFERENCES cliente(id_cliente) ON DELETE CASCADE
);

-- 3. Tabla TECNICO
CREATE TABLE tecnico (
    id_tecnico SERIAL PRIMARY KEY,
    dni VARCHAR(15) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    especialidad VARCHAR(50) NOT NULL CHECK (especialidad IN ('Hardware', 'Software', 'Electrónica', 'General')),
    estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Inactivo'))
);

-- 4. Tabla REPARACION (Ordenes de Trabajo)
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
    id_equipo INT NOT NULL,
    id_tecnico INT NOT NULL,
    CONSTRAINT fk_reparacion_equipo FOREIGN KEY (id_equipo)
        REFERENCES equipo(id_equipo) ON DELETE CASCADE,
    CONSTRAINT fk_reparacion_tecnico FOREIGN KEY (id_tecnico)
        REFERENCES tecnico(id_tecnico) ON DELETE RESTRICT,
    CONSTRAINT chk_fechas CHECK (fecha_salida IS NULL OR fecha_salida >= fecha_ingreso)
);

-- 5. Tabla REPUESTO (Catálogo e Inventario)
CREATE TABLE repuesto (
    id_repuesto SERIAL PRIMARY KEY,
    descripcion VARCHAR(150) NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL CHECK (precio_unitario > 0),
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    stock_minimo INT NOT NULL DEFAULT 2 CHECK (stock_minimo >= 0)
);

-- 6. Tabla DETALLE_REPARACION (Resolución de relación N:M entre Reparación y Repuesto)
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

-- -----------------------------------------------------------------------------
-- BLOQUE 3: CREACIÓN DE ROLES DE SEGURIDAD (SGBD)
-- -----------------------------------------------------------------------------

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

-- Administrador: Control Total
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin_role;

-- Técnico: Lectura general, actualización de diagnósticos, estados y repuestos
GRANT SELECT ON cliente, equipo, tecnico, repuesto TO tecnico_role;
GRANT SELECT, INSERT, UPDATE ON reparacion, detalle_reparacion TO tecnico_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO tecnico_role;

-- Recepcionista: Carga de clientes, equipos y alta de ordenes de trabajo
GRANT SELECT, INSERT, UPDATE ON cliente, equipo, reparacion TO recepcion_role;
GRANT SELECT ON tecnico, repuesto TO recepcion_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO recepcion_role;

-- -----------------------------------------------------------------------------
-- BLOQUE 4: DATOS DE PRUEBA (10 Registros por tabla principal - Exigencia ISPC)
-- -----------------------------------------------------------------------------

-- Inserción de 10 Clientes
INSERT INTO cliente (dni, nombre, telefono) VALUES
('35123456', 'Carlos Gómez', '351-4567890'),
('38987654', 'María Fernández', '351-6543210'),
('29456123', 'Roberto Rodríguez', '351-7890123'),
('41234567', 'Laura Benítez', '351-1234567'),
('33876543', 'Daniel López', '351-8901234'),
('36543210', 'Ana Martínez', '351-2345678'),
('40123987', 'Gabriel Rossi', '351-3456789'),
('32654987', 'Patricia Morales', '351-9012345'),
('37890123', 'Fernando Castro', '351-5678901'),
('42567890', 'Florencia Romero', '351-6789012');

-- Inserción de 10 Equipos (solo datos del hardware; la falla va en REPARACION)
INSERT INTO equipo (tipo, marca, modelo, numero_serie, id_cliente) VALUES
('Notebook', 'Lenovo', 'IdeaPad 3', 'SN-LEN-001', 1),
('PC de Escritorio', 'Exo', 'Ready D1', 'SN-EXO-002', 2),
('Notebook', 'HP', 'Pavilion 15', 'SN-HP-003', 3),
('Impresora', 'Epson', 'EcoTank L3110', 'SN-EPS-004', 4),
('All in One', 'Dell', 'Inspirion 24', 'SN-DEL-005', 5),
('Notebook', 'Asus', 'VivoBook 14', 'SN-ASU-006', 6),
('PC de Escritorio', 'Custom', 'Gamer Ryzen 5', 'SN-CUS-007', 7),
('Notebook', 'Acer', 'Aspire 5', 'SN-ACE-008', 8),
('Impresora', 'HP', 'LaserJet P1102w', 'SN-HPP-009', 9),
('Notebook', 'Bangho', 'Max Y2', 'SN-BAN-010', 10);

-- Inserción de 10 Técnicos
INSERT INTO tecnico (dni, nombre, apellido, especialidad, estado) VALUES
('30111222', 'Ricardo', 'Kieffer', 'Hardware', 'Activo'),
('31222333', 'Juan', 'Jeronimo', 'Software', 'Activo'),
('32333444', 'Joaquín', 'Bileisis', 'Hardware', 'Activo'),
('33444555', 'Thiago', 'Espinosa', 'General', 'Activo'),
('28555666', 'Gonzalo', 'Pérez', 'Electrónica', 'Activo'),
('29666777', 'Romina', 'Sosa', 'Software', 'Activo'),
('34777888', 'Esteban', 'Quinteros', 'Hardware', 'Activo'),
('35888999', 'Lucía', 'Alvarez', 'General', 'Activo'),
('36999000', 'Martín', 'Acosta', 'Electrónica', 'Inactivo'),
('37000111', 'Sofía', 'Navarro', 'Software', 'Activo');

-- Inserción de 10 Repuestos (Catálogo)
INSERT INTO repuesto (descripcion, precio_unitario, stock, stock_minimo) VALUES
('Disco Solido SSD 480GB Kingston SATA3', 45000.00, 15, 3),
('Memoria RAM 8GB DDR4 3200MHz Crucial', 32000.00, 20, 5),
('Fuente de Alimentación 600W LNC', 38000.00, 8, 2),
('Pantalla LED 15.6 Slim 30 Pines Notebook', 95000.00, 4, 1),
('Batería Notebook HP Pavilion TPN-Q221', 52000.00, 6, 2),
('Modulo Teclado Español Asus VivoBook', 28000.00, 5, 2),
('Pasta Térmica Artic MX-4 4g', 12000.00, 25, 5),
('Cargador Universal Notebook 90W', 22000.00, 12, 3),
('Toner HP CE285A 85A Compatible', 18000.00, 10, 3),
('Cabezal de Impresión Epson L3110', 65000.00, 3, 1);

-- Inserción de 10 Ordenes de Reparación (la falla reportada ahora vive acá)
INSERT INTO reparacion (fecha_ingreso, fecha_salida, falla_reportada, diagnostico, costo_estimado, costo_total, estado, id_equipo, id_tecnico) VALUES
('2026-09-01', '2026-09-03', 'Lentitud extrema y apagados repentinos', 'Fuente quemada por sobretensión. Se reemplaza fuente.', 15000.00, 53000.00, 'Entregado', 2, 1),
('2026-09-02', '2026-09-05', 'Sistema operativo no arranca (pantalla azul)', 'Disco HDD dañado. Cambio por SSD 480GB y reinstalación de S.O.', 20000.00, 65000.00, 'Terminado', 10, 2),
('2026-09-05', NULL, 'Pantalla rota por caída', 'Pantalla destruida. Se requiere repuesto de módulo LED.', 25000.00, 120000.00, 'Esperando Repuesto', 3, 3),
('2026-09-08', '2026-09-10', 'Atasco de papel y luz roja parpadeando', 'Limpieza de rodillos y despeje de sensor de papel.', 12000.00, 12000.00, 'Terminado', 4, 4),
('2026-09-10', NULL, 'Ruido fuerte en el ventilador y sobrecalentamiento', 'Cooler obstruido con tierra. Cambio de pasta térmica y limpieza.', 18000.00, 30000.00, 'En Reparación', 5, 5),
('2026-09-12', NULL, 'Teclado no responde en varias teclas', 'Falla de matriz del teclado. Pedido de repuesto.', 15000.00, 43000.00, 'Esperando Repuesto', 6, 1),
('2026-09-14', NULL, 'No da video al encender', 'Falso contacto en memoria RAM. Se realiza mantenimiento de contactos.', 15000.00, 15000.00, 'En Diagnóstico', 7, 3),
('2026-09-15', NULL, 'Batería no retiene carga', 'Batería agotada en ciclo de vida. Reemplazo pendiente de aprobación.', 10000.00, 62000.00, 'Ingresada', 8, 4),
('2026-09-18', NULL, 'Imprime con rayas negras verticales', 'Toner desgastado con pérdida de polvo.', 10000.00, 28000.00, 'En Reparación', 9, 2),
('2026-09-20', NULL, 'No enciende, sin luces de carga', 'Pendiente de revisión inicial en banco de pruebas.', 15000.00, 15000.00, 'Ingresada', 1, 1);

-- Inserción de detalles de repuestos usados en las reparaciones
INSERT INTO detalle_reparacion (id_reparacion, id_repuesto, cantidad, precio_unitario_aplicado) VALUES
(1, 3, 1, 38000.00), -- Reparación 1 usó 1 Fuente de 600W
(2, 1, 1, 45000.00), -- Reparación 2 usó 1 SSD 480GB
(5, 7, 1, 12000.00), -- Reparación 5 usó 1 Pasta Térmica
(9, 9, 1, 18000.00); -- Reparación 9 usó 1 Toner HP
