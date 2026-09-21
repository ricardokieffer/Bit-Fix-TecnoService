# 💻 TecnoService - Sistema de Gestión de Reparaciones de PC

**Módulo Programador** | Tecnicatura Superior en Desarrollo de Software — ISPC  
**Equipo:** Bit&Fix  
**Comisión:** COM B1  
**Entrega:** Evidencia 5 (Hito 2) — Septiembre 2026  

---

## 👥 Integrantes del Equipo y Roles

| Integrante | Rol Principal | Responsabilidades |
| :--- | :--- | :--- |
| **KIEFFER, Ricardo** | Coordinador & Validaciones | Coordinación general, control de versión en Git, validación de formularios Tkinter y manejo de excepciones. |
| **JERONIMO, Juan** | Modelo de Datos & Acceso SQL | Diseño del Modelo E-R (3FN), desarrollo del script SQL (DDL/DML), restricciones de integridad y roles SGBD. |
| **BILEISIS, Joaquin** | Interfaz Gráfica (UI) | Maquetado y desarrollo de la interfaz de escritorio en Python/Tkinter con navegación por pestañas (`ttk.Notebook`). |
| **ESPINOSA, Thiago** | Documentación y Pruebas | Redacción de informes técnicos, confección del Diccionario de Datos, bitácora de progreso y manual de usuario. |

---

## 📌 Descripción del Proyecto

**TecnoService** es una aplicación de escritorio diseñada para optimizar la gestión operativa de un taller de servicio técnico informático. El sistema abarca desde el ingreso y recepción de equipos informáticos (PCs, notebooks, impresoras) hasta el diagnóstico técnico, la asignación de repuestos del inventario y la liquidación final del servicio.

### 🚀 Funcionalidades Principales (4 Pestañas)
1. **Ingresos y Clientes:** Alta y gestión de datos de clientes, registro detallado del equipo, carga de la falla reportada, asignación de técnico responsable y presupuesto inicial estimado.
2. **Órdenes de Trabajo (Taller):** Actualización del diagnóstico por parte del técnico, cambio de estado del servicio, y asociación de repuestos consumidos especificando cantidades.
3. **Gestión de Técnicos (ABM):** Registro de profesionales habilitados, especialidad y estado de disponibilidad.
4. **Catálogo de Repuestos e Inventario (ABM):** Control de stock de componentes, precios unitarios y alertas visuales de stock mínimo para reabastecimiento.

---

## 📂 Estructura del Repositorio

```text
/
├── docs/                                  # Documentación técnica e informes
│   ├── Informe_Hito2_TecnoService.pdf    # Informe consolidado del Hito 2
│   ├── Diccionario_de_Datos_TecnoService.pdf # Diccionario de Datos del SGBD
├── sql/                                   # Scripts de Base de Datos
│   └── script_tecnoservice.sql            # Script DDL (Tablas, Claves, Checks, Roles e Inserts)
├── src/                                   # Código Fuente Python (Tkinter)
│   ├── main.py                            # Punto de entrada de la aplicación
│   ├── interfaz.py                        # Construcción de la interfaz gráfica (UI)
│   ├── acceso_datos.py                    # Capa de datos e interacción con listas
│   └── conexion.py                        # Módulo de conexión a la Base de Datos
└── README.md                              # Presentación del proyecto
```

---

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.12+
* **Interfaz Gráfica:** Tkinter / `ttk` (`ttk.Notebook`, `ttk.LabelFrame`, `ttk.Treeview`)
* **Base de Datos:** SQL Estándar (PostgreSQL / MySQL)
* **Control de Versiones:** Git & GitHub
