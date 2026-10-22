# 💻 TecnoService - Sistema de Gestión de Reparaciones de PC

Módulo Programador | Tecnicatura Superior en Desarrollo de Software - ISPC
Equipo: Bit&Fix
Comisión: COM B1
Entrega: Evidencia 6 (Hito 3) - Octubre 2026

## Integrantes del Equipo y Roles

| Integrante | Rol Principal | Responsabilidades |
|---|---|---|
| KIEFFER, Ricardo | Coordinador & Validaciones | Coordinación general, control de versión en Git, validación de formularios Tkinter y manejo de excepciones. |
| JERONIMO, Juan | Modelo de Datos & Acceso SQL | Diseño del Modelo E-R (3FN), desarrollo del script SQL (DDL/DML), restricciones de integridad y roles SGBD. |
| BILEISIS, Joaquin | Interfaz Gráfica (UI) | Maquetado y desarrollo de la interfaz de escritorio en Python/Tkinter con navegación por pestañas (ttk.Notebook). |
| ESPINOSA, Thiago | Documentación y Pruebas | Redacción de informes técnicos, confección del Diccionario de Datos, bitácora de progreso y manual de usuario. |

## Descripción del Proyecto

TecnoService es una aplicación de escritorio para la gestión de un taller de servicio técnico informático. Abarca desde el ingreso de equipos (PCs, notebooks, impresoras) hasta el diagnóstico técnico, el uso de repuestos del inventario y el costo final del servicio.

## Funcionalidades (5 pestañas)

- **Clientes (ABM):** alta, modificación y baja de clientes del taller.
- **Ingresos:** registro de cliente y equipo, falla reportada, técnico responsable y presupuesto inicial estimado.
- **Órdenes:** actualización del diagnóstico y del estado del servicio, y presupuesto del cliente (Pendiente / Aceptado / Rechazado). Una orden no puede pasar a En Reparación, Terminado o Entregado sin presupuesto Aceptado.
- **Técnicos (ABM):** alta, modificación y baja de técnicos, con su especialidad y estado.
- **Repuestos (ABM):** alta, modificación y baja de repuestos, con precios y alerta visual de stock mínimo.

El control de stock al usar un repuesto en una orden lo hace la base de datos con un trigger. La pantalla para cargar repuestos en cada orden queda para la entrega final.

## Estado del Hito 3

- Base de datos implementada en PostgreSQL (servicio Neon) con 6 tablas, datos de prueba, roles (admin_role, tecnico_role, recepcion_role), restricciones CHECK, claves foráneas y trigger de stock.
- La aplicación se conecta a la base con psycopg2 y hace altas y consultas con sentencias SQL propias.

## Estructura del Repositorio

```
/
├── Docs/                                  # Documentación técnica e informes
│   ├── Informe_Hito2_TecnoService.pdf
│   ├── Diccionario_de_Datos_TecnoService.pdf
│   ├── Minuta_de_Requerimientos_TecnoService.pdf
│   ├── Modelo_Relacional_y_Normalizacion_TecnoService.pdf
│   └── EV6_BitFix.pdf
├── sql/
│   └── script_tecnoservice.sql            # Tablas, claves, checks, trigger, roles e inserts
├── src/
│   ├── main.py                            # Punto de entrada
│   ├── interfaz.py                        # Interfaz gráfica (Tkinter)
│   ├── acceso_datos.py                    # Consultas SQL a la base
│   └── conexion.py                        # Conexión a PostgreSQL
└── README.md
```

## Tecnologías

- Lenguaje: Python 3.12+
- Interfaz gráfica: Tkinter / ttk (Notebook, LabelFrame, Treeview)
- Base de datos: PostgreSQL (Neon) con psycopg2
- Control de versiones: Git y GitHub

## Cómo probarlo

1. Instalar la librería: `pip install psycopg2-binary`
2. Abrir una terminal en la carpeta `src`.
3. Ejecutar: `python main.py`

La base de datos está en Neon y ya tiene los datos cargados. Los datos de conexión están en `conexion.py`. Para crear la base desde cero se puede ejecutar `sql/script_tecnoservice.sql`.
