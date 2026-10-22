import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from acceso_datos import (
    AccesoDatosSQL,
    TIPOS_EQUIPO,
    ESPECIALIDADES_TECNICO,
    ESTADOS_TECNICO,
    ESTADOS_REPARACION,
)


class AplicacionTecnoService:
    def __init__(self, root):
        self.root = root
        self.root.title("TecnoService PC - Sistema de Gestión de Reparaciones (Bit&Fix)")
        self.root.geometry("1024x680")
        self.root.minsize(900, 600)

        # acceso a la base
        self.datos = AccesoDatosSQL()

        # estilos
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook.Tab', font=('Helvetica', 10, 'bold'), padding=[12, 6])
        self.style.configure('TLabelframe.Label', font=('Helvetica', 10, 'bold'), foreground='#1A365D')

        self.crear_encabezado()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_ingresos = ttk.Frame(self.notebook)
        self.tab_ordenes = ttk.Frame(self.notebook)
        self.tab_tecnicos = ttk.Frame(self.notebook)
        self.tab_repuestos = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_clientes, text=" Clientes ")
        self.notebook.add(self.tab_ingresos, text=" Ingresos ")
        self.notebook.add(self.tab_ordenes, text=" Órdenes ")
        self.notebook.add(self.tab_tecnicos, text=" Técnicos ")
        self.notebook.add(self.tab_repuestos, text=" Repuestos ")

        self.build_tab_clientes()
        self.build_tab_ingresos()
        self.build_tab_ordenes()
        self.build_tab_tecnicos()
        self.build_tab_repuestos()

        self.crear_barra_estado()

    def crear_encabezado(self):
        header_frame = tk.Frame(self.root, bg='#1A365D', height=50)
        header_frame.pack(fill='x', side='top')

        lbl_titulo = tk.Label(header_frame, text="TECNOSERVICE PC — Servicio Técnico Especializado",
                               font=('Helvetica', 14, 'bold'), fg='white', bg='#1A365D')
        lbl_titulo.pack(side='left', padx=15, pady=10)

        lbl_equipo = tk.Label(header_frame, text="Grupo Bit&Fix | COM B1",
                               font=('Helvetica', 10, 'italic'), fg='#E2E8F0', bg='#1A365D')
        lbl_equipo.pack(side='right', padx=15, pady=10)

    def crear_barra_estado(self):
        status_frame = tk.Frame(self.root, bg='#E2E8F0', height=25)
        status_frame.pack(fill='x', side='bottom')
        lbl_status = tk.Label(
            status_frame,
            text="Hito 3: conectado a PostgreSQL",
            font=('Helvetica', 9), bg='#E2E8F0', fg='#4A5568'
        )
        lbl_status.pack(side='left', padx=10, pady=2)

    def mostrar_error_bd(self, e):
        txt = str(e)
        if "chk_presupuesto" in txt:
            msg = "No se puede pasar a En Reparación, Terminado o Entregado sin presupuesto Aceptado."
        elif "duplicate key" in txt:
            msg = "Ya existe un registro con ese DNI, legajo, código o número de serie."
        elif "foreign key" in txt:
            msg = "No se puede eliminar: tiene registros asociados."
        else:
            msg = txt
        messagebox.showerror("Error en la base de datos", msg)

    def refrescar_todo(self):
        self.cargar_tabla_clientes()
        self.cargar_tabla_ingresos()
        self.refrescar_combo_ordenes()
        self.cargar_tabla_ordenes()
        self.cmb_eq_tec["values"] = [f"{t['apellido']}, {t['nombre']}" for t in self.datos.obtener_tecnicos()]

    # pestaña clientes
    def build_tab_clientes(self):
        self.cli_sel = None
        frame_form = ttk.LabelFrame(self.tab_clientes, text=" Alta / Edición de Cliente ", padding=10)
        frame_form.pack(side='left', fill='both', expand=False, padx=10, pady=10, ipadx=5)

        ttk.Label(frame_form, text="DNI:").grid(row=0, column=0, sticky='w', pady=5)
        self.ent_c_dni = ttk.Entry(frame_form, width=25)
        self.ent_c_dni.grid(row=0, column=1, pady=5)

        ttk.Label(frame_form, text="Nombre y Apellido:").grid(row=1, column=0, sticky='w', pady=5)
        self.ent_c_nombre = ttk.Entry(frame_form, width=25)
        self.ent_c_nombre.grid(row=1, column=1, pady=5)

        ttk.Label(frame_form, text="Teléfono:").grid(row=2, column=0, sticky='w', pady=5)
        self.ent_c_tel = ttk.Entry(frame_form, width=25)
        self.ent_c_tel.grid(row=2, column=1, pady=5)

        botones = ttk.Frame(frame_form)
        botones.grid(row=3, column=0, columnspan=2, pady=15)
        ttk.Button(botones, text="Guardar Nuevo", command=self.guardar_cliente).grid(row=0, column=0, padx=3, pady=3)
        ttk.Button(botones, text="Modificar", command=self.modificar_cliente).grid(row=0, column=1, padx=3, pady=3)
        ttk.Button(botones, text="Eliminar", command=self.eliminar_cliente).grid(row=1, column=0, padx=3, pady=3)
        ttk.Button(botones, text="Limpiar", command=self.limpiar_cliente).grid(row=1, column=1, padx=3, pady=3)

        frame_grid = ttk.LabelFrame(self.tab_clientes, text=" Clientes Registrados ", padding=10)
        frame_grid.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        cols = ("ID", "DNI", "Nombre", "Teléfono")
        self.tree_clientes = ttk.Treeview(frame_grid, columns=cols, show='headings', selectmode='browse')
        for c in cols:
            self.tree_clientes.heading(c, text=c)
            self.tree_clientes.column(c, width=120)
        self.tree_clientes.column("ID", width=50)
        self.tree_clientes.column("Nombre", width=220)
        self.tree_clientes.pack(fill='both', expand=True)
        self.tree_clientes.bind("<<TreeviewSelect>>", self.seleccionar_cliente)
        self.cargar_tabla_clientes()

    def cargar_tabla_clientes(self):
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        for c in self.datos.obtener_clientes():
            self.tree_clientes.insert('', 'end', iid=str(c['id']), values=(c['id'], c['dni'], c['nombre'], c['telefono']))

    def seleccionar_cliente(self, event=None):
        sel = self.tree_clientes.selection()
        if not sel:
            return
        v = self.tree_clientes.item(sel[0], 'values')
        self.cli_sel = int(v[0])
        for ent, val in ((self.ent_c_dni, v[1]), (self.ent_c_nombre, v[2]), (self.ent_c_tel, v[3])):
            ent.delete(0, tk.END)
            ent.insert(0, val)

    def limpiar_cliente(self):
        self.cli_sel = None
        for ent in (self.ent_c_dni, self.ent_c_nombre, self.ent_c_tel):
            ent.delete(0, tk.END)

    def guardar_cliente(self):
        dni, nombre, tel = self.ent_c_dni.get().strip(), self.ent_c_nombre.get().strip(), self.ent_c_tel.get().strip()
        if not dni or not nombre or not tel:
            messagebox.showwarning("Atención", "Complete DNI, nombre y teléfono.")
            return
        try:
            self.datos.agregar_cliente(dni, nombre, tel)
        except Exception as e:
            self.mostrar_error_bd(e)
            return
        self.refrescar_todo()
        self.limpiar_cliente()

    def modificar_cliente(self):
        if self.cli_sel is None:
            messagebox.showwarning("Atención", "Seleccione un cliente de la lista.")
            return
        dni, nombre, tel = self.ent_c_dni.get().strip(), self.ent_c_nombre.get().strip(), self.ent_c_tel.get().strip()
        if not dni or not nombre or not tel:
            messagebox.showwarning("Atención", "Complete DNI, nombre y teléfono.")
            return
        try:
            self.datos.modificar_cliente(self.cli_sel, dni, nombre, tel)
        except Exception as e:
            self.mostrar_error_bd(e)
            return
        self.refrescar_todo()
        self.limpiar_cliente()

    def eliminar_cliente(self):
        if self.cli_sel is None:
            messagebox.showwarning("Atención", "Seleccione un cliente de la lista.")
            return
        if not messagebox.askyesno("Confirmar", "Se eliminará el cliente junto con sus equipos y órdenes. ¿Continuar?"):
            return
        try:
            self.datos.eliminar_cliente(self.cli_sel)
        except Exception as e:
            self.mostrar_error_bd(e)
            return
        self.refrescar_todo()
        self.limpiar_cliente()

    # pestaña ingresos
    def build_tab_ingresos(self):
        frame_form = ttk.LabelFrame(self.tab_ingresos, text=" Registro de Cliente y Recepción de Hardware ", padding=10)
        frame_form.pack(side='left', fill='both', expand=False, padx=10, pady=10, ipadx=5)

        ttk.Label(frame_form, text="DNI Cliente:").grid(row=0, column=0, sticky='w', pady=4)
        self.ent_cli_dni = ttk.Entry(frame_form, width=25)
        self.ent_cli_dni.grid(row=0, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Nombre y Apellido:").grid(row=1, column=0, sticky='w', pady=4)
        self.ent_cli_nombre = ttk.Entry(frame_form, width=25)
        self.ent_cli_nombre.grid(row=1, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Teléfono Contacto:").grid(row=2, column=0, sticky='w', pady=4)
        self.ent_cli_tel = ttk.Entry(frame_form, width=25)
        self.ent_cli_tel.grid(row=2, column=1, pady=4, sticky='w')

        ttk.Separator(frame_form, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky='ew', pady=8)

        ttk.Label(frame_form, text="Tipo de Equipo:").grid(row=4, column=0, sticky='w', pady=4)
        self.cmb_eq_tipo = ttk.Combobox(frame_form, values=TIPOS_EQUIPO, width=23, state="readonly")
        self.cmb_eq_tipo.set(TIPOS_EQUIPO[0])
        self.cmb_eq_tipo.grid(row=4, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Marca:").grid(row=5, column=0, sticky='w', pady=4)
        self.ent_eq_marca = ttk.Entry(frame_form, width=25)
        self.ent_eq_marca.grid(row=5, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Modelo:").grid(row=6, column=0, sticky='w', pady=4)
        self.ent_eq_modelo = ttk.Entry(frame_form, width=25)
        self.ent_eq_modelo.grid(row=6, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Nº de Serie:").grid(row=7, column=0, sticky='w', pady=4)
        self.ent_eq_serie = ttk.Entry(frame_form, width=25)
        self.ent_eq_serie.grid(row=7, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Técnico Asignado:").grid(row=8, column=0, sticky='w', pady=4)
        nombres_tecnicos = [f"{t['apellido']}, {t['nombre']}" for t in self.datos.obtener_tecnicos()]
        self.cmb_eq_tec = ttk.Combobox(frame_form, values=nombres_tecnicos, width=23, state="readonly")
        if nombres_tecnicos:
            self.cmb_eq_tec.set(nombres_tecnicos[0])
        self.cmb_eq_tec.grid(row=8, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Presupuesto Est. ($):").grid(row=9, column=0, sticky='w', pady=4)
        self.ent_eq_presupuesto = ttk.Entry(frame_form, width=25)
        self.ent_eq_presupuesto.insert(0, "15000.00")
        self.ent_eq_presupuesto.grid(row=9, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Falla Reportada:").grid(row=10, column=0, sticky='nw', pady=4)
        self.txt_eq_falla = tk.Text(frame_form, width=25, height=3, font=('Helvetica', 9))
        self.txt_eq_falla.grid(row=10, column=1, pady=4, sticky='w')

        btn_box = ttk.Frame(frame_form)
        btn_box.grid(row=11, column=0, columnspan=2, pady=10)

        ttk.Button(btn_box, text="Registrar Ingreso", command=self.guardar_ingreso).pack(side='left', padx=5)
        ttk.Button(btn_box, text="Limpiar Formulario", command=self.limpiar_ingreso).pack(side='left', padx=5)

        # lista de ordenes
        frame_grid = ttk.LabelFrame(self.tab_ingresos, text=" Órdenes Registradas ", padding=10)
        frame_grid.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        cols = ("ID", "Cliente", "Equipo", "Estado", "Técnico")
        self.tree_ingresos = ttk.Treeview(frame_grid, columns=cols, show='headings', selectmode='browse')
        for c in cols:
            self.tree_ingresos.heading(c, text=c)
            self.tree_ingresos.column(c, width=110)
        self.tree_ingresos.column("ID", width=50)
        self.tree_ingresos.column("Cliente", width=160)
        self.tree_ingresos.column("Equipo", width=180)

        scrollbar = ttk.Scrollbar(frame_grid, orient='vertical', command=self.tree_ingresos.yview)
        self.tree_ingresos.configure(yscrollcommand=scrollbar.set)

        self.tree_ingresos.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.cargar_tabla_ingresos()

    def cargar_tabla_ingresos(self):
        for item in self.tree_ingresos.get_children():
            self.tree_ingresos.delete(item)
        for r in self.datos.obtener_reparaciones():
            self.tree_ingresos.insert('', 'end', values=(r['id'], r['cliente'], r['equipo'], r['estado'], r['tecnico']))

    def guardar_ingreso(self):
        dni = self.ent_cli_dni.get().strip()
        nombre = self.ent_cli_nombre.get().strip()
        tel = self.ent_cli_tel.get().strip()
        marca = self.ent_eq_marca.get().strip()
        modelo = self.ent_eq_modelo.get().strip()
        falla = self.txt_eq_falla.get("1.0", tk.END).strip()

        if not dni or not nombre or not marca or not modelo or not falla:
            messagebox.showwarning(
                "Campos Incompletos",
                "Por favor complete los campos obligatorios: DNI, Nombre, Marca, Modelo y Falla Reportada."
            )
            return

        try:
            presupuesto = float(self.ent_eq_presupuesto.get().strip() or 0)
        except ValueError:
            messagebox.showerror("Error de Formato", "El presupuesto estimado debe ser un número válido.")
            return

        tipo = self.cmb_eq_tipo.get()
        serie = self.ent_eq_serie.get().strip() or None
        equipo_desc = f"{tipo} {marca} {modelo}".strip()
        tecnico_sel = self.cmb_eq_tec.get()
        id_tecnico = next((t["id"] for t in self.datos.obtener_tecnicos()
                            if f"{t['apellido']}, {t['nombre']}" == tecnico_sel), None)
        try:
            cli = self.datos.agregar_cliente(dni, nombre, tel)
            nuevo_eq = self.datos.agregar_equipo(tipo, marca, modelo, serie, cli["id"], nombre)
            self.datos.agregar_reparacion(
                id_equipo=nuevo_eq["id"], equipo_desc=equipo_desc, cliente_nombre=nombre,
                id_tecnico=id_tecnico, tecnico_nombre=tecnico_sel, fecha=date.today().isoformat(),
                falla_reportada=falla, estimado=presupuesto
            )
        except Exception as e:
            self.mostrar_error_bd(e)
            return

        self.cargar_tabla_clientes()
        self.cargar_tabla_ingresos()
        self.refrescar_combo_ordenes()
        self.cargar_tabla_ordenes()
        messagebox.showinfo("Éxito", f"Ingreso registrado correctamente.\nCliente: {nombre}\nEquipo: {marca} {modelo}")
        self.limpiar_ingreso()

    def limpiar_ingreso(self):
        self.ent_cli_dni.delete(0, tk.END)
        self.ent_cli_nombre.delete(0, tk.END)
        self.ent_cli_tel.delete(0, tk.END)
        self.ent_eq_marca.delete(0, tk.END)
        self.ent_eq_modelo.delete(0, tk.END)
        self.ent_eq_serie.delete(0, tk.END)
        self.txt_eq_falla.delete("1.0", tk.END)

    # pestaña ordenes
    def build_tab_ordenes(self):
        frame_top = ttk.LabelFrame(self.tab_ordenes, text=" Actualización de Diagnóstico y Estado en Taller ", padding=10)
        frame_top.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_top, text="Orden Nº:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.cmb_ord_id = ttk.Combobox(frame_top, width=10, state="readonly")
        self.cmb_ord_id.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.cmb_ord_id.bind("<<ComboboxSelected>>", self.cargar_orden_seleccionada)

        ttk.Label(frame_top, text="Estado:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.cmb_ord_estado = ttk.Combobox(frame_top, values=ESTADOS_REPARACION, width=18, state="readonly")
        self.cmb_ord_estado.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(frame_top, text="Presupuesto:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.cmb_ord_presup = ttk.Combobox(frame_top, values=["Pendiente", "Aceptado", "Rechazado"],
                                           width=12, state="readonly")
        self.cmb_ord_presup.grid(row=0, column=5, padx=5, pady=5, sticky='w')

        ttk.Label(frame_top, text="Falla Reportada:").grid(row=1, column=0, padx=5, pady=5, sticky='nw')
        self.lbl_ord_falla = ttk.Label(frame_top, text="-", wraplength=260, foreground='#4A5568')
        self.lbl_ord_falla.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky='w')

        ttk.Label(frame_top, text="Diagnóstico Técnico:").grid(row=2, column=0, padx=5, pady=5, sticky='nw')
        self.txt_ord_diag = tk.Text(frame_top, width=60, height=3, font=('Helvetica', 9))
        self.txt_ord_diag.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky='w')

        btn_actualizar = ttk.Button(frame_top, text="Actualizar Orden", command=self.actualizar_orden)
        btn_actualizar.grid(row=2, column=4, padx=10, pady=5)

        frame_grid = ttk.LabelFrame(self.tab_ordenes, text=" Listado General de Órdenes de Servicio ", padding=10)
        frame_grid.pack(fill='both', expand=True, padx=10, pady=5)

        cols = ("Nº Orden", "Equipo", "Cliente", "Técnico Asignado", "Fecha Ingreso", "Estado", "Presupuesto", "Est. Presupuesto ($)", "Total Final ($)")
        self.tree_ordenes = ttk.Treeview(frame_grid, columns=cols, show='headings')
        for c in cols:
            self.tree_ordenes.heading(c, text=c)
            self.tree_ordenes.column(c, width=110)
        self.tree_ordenes.column("Nº Orden", width=70)

        scrollbar = ttk.Scrollbar(frame_grid, orient='vertical', command=self.tree_ordenes.yview)
        self.tree_ordenes.configure(yscrollcommand=scrollbar.set)
        self.tree_ordenes.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.refrescar_combo_ordenes()
        self.cargar_tabla_ordenes()

    def refrescar_combo_ordenes(self):
        ids = [str(r["id"]) for r in self.datos.obtener_reparaciones()]
        self.cmb_ord_id["values"] = ids
        if ids:
            self.cmb_ord_id.set(ids[0])
            self.cargar_orden_seleccionada()

    def cargar_orden_seleccionada(self, event=None):
        id_sel = self.cmb_ord_id.get()
        if not id_sel:
            return
        orden = next((r for r in self.datos.obtener_reparaciones() if str(r["id"]) == id_sel), None)
        if orden is None:
            return
        self.lbl_ord_falla.configure(text=orden["falla_reportada"])
        self.txt_ord_diag.delete("1.0", tk.END)
        self.txt_ord_diag.insert("1.0", orden.get("diagnostico") or "")
        self.cmb_ord_estado.set(orden["estado"])
        self.cmb_ord_presup.set(orden.get("presupuesto_aprobado") or "Pendiente")

    def cargar_tabla_ordenes(self):
        for item in self.tree_ordenes.get_children():
            self.tree_ordenes.delete(item)
        for r in self.datos.obtener_reparaciones():
            self.tree_ordenes.insert('', 'end', values=(
                r['id'], r['equipo'], r['cliente'], r['tecnico'], r['fecha'],
                r['estado'], r['presupuesto_aprobado'], f"${r['estimado']:.2f}", f"${r['total']:.2f}"
            ))

    def actualizar_orden(self):
        id_sel = self.cmb_ord_id.get()
        if not id_sel:
            messagebox.showwarning("Atención", "Seleccioná una orden de la lista.")
            return
        nuevo_estado = self.cmb_ord_estado.get()
        nuevo_diag = self.txt_ord_diag.get("1.0", tk.END).strip()
        try:
            actualizada = self.datos.actualizar_estado_reparacion(
                int(id_sel), nuevo_estado, nuevo_diag, self.cmb_ord_presup.get())
        except Exception as e:
            self.mostrar_error_bd(e)
            return
        if actualizada:
            self.cargar_tabla_ordenes()
            self.cargar_tabla_ingresos()
            messagebox.showinfo("Orden Actualizada", f"La orden Nº {id_sel} fue actualizada al estado '{nuevo_estado}'.")

    # pestaña tecnicos
    def build_tab_tecnicos(self):
        frame_form = ttk.LabelFrame(self.tab_tecnicos, text=" Alta / Edición de Técnico ", padding=10)
        frame_form.pack(side='left', fill='both', expand=False, padx=10, pady=10, ipadx=5)

        ttk.Label(frame_form, text="Legajo:").grid(row=0, column=0, sticky='w', pady=5)
        self.ent_tec_legajo = ttk.Entry(frame_form, width=20)
        self.ent_tec_legajo.grid(row=0, column=1, pady=5)

        ttk.Label(frame_form, text="DNI:").grid(row=1, column=0, sticky='w', pady=5)
        self.ent_tec_dni = ttk.Entry(frame_form, width=20)
        self.ent_tec_dni.grid(row=1, column=1, pady=5)

        ttk.Label(frame_form, text="Nombre:").grid(row=2, column=0, sticky='w', pady=5)
        self.ent_tec_nom = ttk.Entry(frame_form, width=20)
        self.ent_tec_nom.grid(row=2, column=1, pady=5)

        ttk.Label(frame_form, text="Apellido:").grid(row=3, column=0, sticky='w', pady=5)
        self.ent_tec_ape = ttk.Entry(frame_form, width=20)
        self.ent_tec_ape.grid(row=3, column=1, pady=5)

        ttk.Label(frame_form, text="Especialidad:").grid(row=4, column=0, sticky='w', pady=5)
        self.cmb_tec_esp = ttk.Combobox(frame_form, values=ESPECIALIDADES_TECNICO, width=18, state="readonly")
        self.cmb_tec_esp.set(ESPECIALIDADES_TECNICO[0])
        self.cmb_tec_esp.grid(row=4, column=1, pady=5)

        ttk.Label(frame_form, text="Estado:").grid(row=5, column=0, sticky='w', pady=5)
        self.cmb_tec_estado = ttk.Combobox(frame_form, values=ESTADOS_TECNICO, width=18, state="readonly")
        self.cmb_tec_estado.set(ESTADOS_TECNICO[0])
        self.cmb_tec_estado.grid(row=5, column=1, pady=5)

        botones = ttk.Frame(frame_form)
        botones.grid(row=6, column=0, columnspan=2, pady=15)
        ttk.Button(botones, text="Guardar Nuevo", command=self.guardar_tecnico).grid(row=0, column=0, padx=3, pady=3)
        ttk.Button(botones, text="Modificar", command=self.modificar_tecnico).grid(row=0, column=1, padx=3, pady=3)
        ttk.Button(botones, text="Eliminar", command=self.eliminar_tecnico).grid(row=1, column=0, padx=3, pady=3)
        ttk.Button(botones, text="Limpiar", command=self.limpiar_tecnico).grid(row=1, column=1, padx=3, pady=3)

        frame_grid = ttk.LabelFrame(self.tab_tecnicos, text=" Personal Técnico Registrado ", padding=10)
        frame_grid.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        cols = ("Legajo", "DNI", "Apellido", "Nombre", "Especialidad", "Estado")
        self.tree_tecnicos = ttk.Treeview(frame_grid, columns=cols, show='headings', selectmode='browse')
        for c in cols:
            self.tree_tecnicos.heading(c, text=c)
            self.tree_tecnicos.column(c, width=100)

        self.tree_tecnicos.pack(fill='both', expand=True)
        self.tree_tecnicos.bind("<<TreeviewSelect>>", self.seleccionar_tecnico)
        self.tec_sel = None
        self.cargar_tabla_tecnicos()

    def cargar_tabla_tecnicos(self):
        for item in self.tree_tecnicos.get_children():
            self.tree_tecnicos.delete(item)
        for t in self.datos.obtener_tecnicos():
            self.tree_tecnicos.insert('', 'end', iid=str(t['id']), values=(t['legajo'], t['dni'], t['apellido'], t['nombre'], t['especialidad'], t['estado']))

    def seleccionar_tecnico(self, event=None):
        sel = self.tree_tecnicos.selection()
        if not sel:
            return
        v = self.tree_tecnicos.item(sel[0], 'values')
        self.tec_sel = int(sel[0])
        for ent, val in ((self.ent_tec_legajo, v[0]), (self.ent_tec_dni, v[1]),
                         (self.ent_tec_ape, v[2]), (self.ent_tec_nom, v[3])):
            ent.delete(0, tk.END)
            ent.insert(0, val)
        self.cmb_tec_esp.set(v[4])
        self.cmb_tec_estado.set(v[5])

    def limpiar_tecnico(self):
        self.tec_sel = None
        for ent in (self.ent_tec_legajo, self.ent_tec_dni, self.ent_tec_nom, self.ent_tec_ape):
            ent.delete(0, tk.END)

    def datos_tecnico(self):
        legajo = self.ent_tec_legajo.get().strip()
        dni = self.ent_tec_dni.get().strip()
        nom = self.ent_tec_nom.get().strip()
        ape = self.ent_tec_ape.get().strip()
        if not legajo or not dni or not nom or not ape:
            messagebox.showwarning("Atención", "Por favor complete todos los datos del técnico.")
            return None
        return legajo, dni, nom, ape, self.cmb_tec_esp.get(), self.cmb_tec_estado.get()

    def guardar_tecnico(self):
        d = self.datos_tecnico()
        if not d:
            return
        try:
            self.datos.agregar_tecnico(*d)
        except Exception as e:
            self.mostrar_error_bd(e)
            return
        self.cargar_tabla_tecnicos()
        self.limpiar_tecnico()
        messagebox.showinfo("Éxito", f"Técnico {d[2]} {d[3]} registrado correctamente.")

    def modificar_tecnico(self):
        if self.tec_sel is None:
            messagebox.showwarning("Atención", "Seleccione un técnico de la lista.")
            return
        d = self.datos_tecnico()
        if not d:
            return
        try:
            self.datos.modificar_tecnico(self.tec_sel, *d)
        except Exception as e:
            self.mostrar_error_bd(e)
            return
        self.refrescar_todo()
        self.cargar_tabla_tecnicos()
        self.limpiar_tecnico()

    def eliminar_tecnico(self):
        if self.tec_sel is None:
            messagebox.showwarning("Atención", "Seleccione un técnico de la lista.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el técnico seleccionado?"):
            return
        try:
            self.datos.eliminar_tecnico(self.tec_sel)
        except Exception as e:
            self.mostrar_error_bd(e)
            return
        self.refrescar_todo()
        self.cargar_tabla_tecnicos()
        self.limpiar_tecnico()

    # pestaña repuestos
    def build_tab_repuestos(self):
        frame_form = ttk.LabelFrame(self.tab_repuestos, text=" Agregar / Modificar Repuesto ", padding=10)
        frame_form.pack(side='left', fill='both', expand=False, padx=10, pady=10, ipadx=5)

        ttk.Label(frame_form, text="Código:").grid(row=0, column=0, sticky='w', pady=5)
        self.ent_rep_cod = ttk.Entry(frame_form, width=20)
        self.ent_rep_cod.grid(row=0, column=1, pady=5)

        ttk.Label(frame_form, text="Descripción:").grid(row=1, column=0, sticky='w', pady=5)
        self.ent_rep_desc = ttk.Entry(frame_form, width=20)
        self.ent_rep_desc.grid(row=1, column=1, pady=5)

        ttk.Label(frame_form, text="Precio Unit. ($):").grid(row=2, column=0, sticky='w', pady=5)
        self.ent_rep_precio = ttk.Entry(frame_form, width=20)
        self.ent_rep_precio.grid(row=2, column=1, pady=5)

        ttk.Label(frame_form, text="Stock Actual:").grid(row=3, column=0, sticky='w', pady=5)
        self.ent_rep_stock = ttk.Entry(frame_form, width=20)
        self.ent_rep_stock.grid(row=3, column=1, pady=5)

        ttk.Label(frame_form, text="Stock Mínimo:").grid(row=4, column=0, sticky='w', pady=5)
        self.ent_rep_min = ttk.Entry(frame_form, width=20)
        self.ent_rep_min.insert(0, "2")
        self.ent_rep_min.grid(row=4, column=1, pady=5)

        botones = ttk.Frame(frame_form)
        botones.grid(row=5, column=0, columnspan=2, pady=15)
        ttk.Button(botones, text="Guardar Nuevo", command=self.guardar_repuesto).grid(row=0, column=0, padx=3, pady=3)
        ttk.Button(botones, text="Modificar", command=self.modificar_repuesto).grid(row=0, column=1, padx=3, pady=3)
        ttk.Button(botones, text="Eliminar", command=self.eliminar_repuesto).grid(row=1, column=0, padx=3, pady=3)
        ttk.Button(botones, text="Limpiar", command=self.limpiar_repuesto).grid(row=1, column=1, padx=3, pady=3)

        frame_grid = ttk.LabelFrame(self.tab_repuestos, text=" Inventario y Alertas de Stock ", padding=10)
        frame_grid.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        cols = ("Código", "Descripción", "Precio Unitario ($)", "Stock Actual", "Stock Mínimo", "Estado Stock")
        self.tree_repuestos = ttk.Treeview(frame_grid, columns=cols, show='headings', selectmode='browse')
        for c in cols:
            self.tree_repuestos.heading(c, text=c)
            self.tree_repuestos.column(c, width=110)
        self.tree_repuestos.column("Descripción", width=220)

        self.tree_repuestos.pack(fill='both', expand=True)
        self.tree_repuestos.bind("<<TreeviewSelect>>", self.seleccionar_repuesto)
        self.rep_sel = None
        self.cargar_tabla_repuestos()

    def cargar_tabla_repuestos(self):
        for item in self.tree_repuestos.get_children():
            self.tree_repuestos.delete(item)
        for r in self.datos.obtener_repuestos():
            estado = "NORMAL" if r['stock'] > r['minimo'] else "ALERTA STOCK BAJO"
            self.tree_repuestos.insert('', 'end', iid=str(r['id']), values=(r['codigo'], r['descripcion'], f"${r['precio']:.2f}", r['stock'], r['minimo'], estado))

    def seleccionar_repuesto(self, event=None):
        sel = self.tree_repuestos.selection()
        if not sel:
            return
        v = self.tree_repuestos.item(sel[0], 'values')
        self.rep_sel = int(sel[0])
        for ent, val in ((self.ent_rep_cod, v[0]), (self.ent_rep_desc, v[1]),
                         (self.ent_rep_precio, v[2].replace("$", "")),
                         (self.ent_rep_stock, v[3]), (self.ent_rep_min, v[4])):
            ent.delete(0, tk.END)
            ent.insert(0, val)

    def limpiar_repuesto(self):
        self.rep_sel = None
        for ent in (self.ent_rep_cod, self.ent_rep_desc, self.ent_rep_precio, self.ent_rep_stock):
            ent.delete(0, tk.END)
        self.ent_rep_min.delete(0, tk.END)
        self.ent_rep_min.insert(0, "2")

    def datos_repuesto(self):
        cod = self.ent_rep_cod.get().strip()
        desc = self.ent_rep_desc.get().strip()
        precio = self.ent_rep_precio.get().strip()
        stock = self.ent_rep_stock.get().strip()
        minimo = self.ent_rep_min.get().strip()
        if not cod or not desc or not precio or not stock or not minimo:
            messagebox.showwarning("Atención", "Por favor complete los campos obligatorios del repuesto.")
            return None
        try:
            return cod, desc, float(precio), int(stock), int(minimo)
        except ValueError:
            messagebox.showerror("Error de Formato", "Precio y Stock deben ser valores numéricos válidos.")
            return None

    def guardar_repuesto(self):
        d = self.datos_repuesto()
        if not d:
            return
        try:
            self.datos.agregar_repuesto(*d)
        except Exception as e:
            self.mostrar_error_bd(e)
            return
        self.cargar_tabla_repuestos()
        self.limpiar_repuesto()
        messagebox.showinfo("Éxito", f"Repuesto '{d[1]}' guardado en inventario.")

    def modificar_repuesto(self):
        if self.rep_sel is None:
            messagebox.showwarning("Atención", "Seleccione un repuesto de la lista.")
            return
        d = self.datos_repuesto()
        if not d:
            return
        try:
            self.datos.modificar_repuesto(self.rep_sel, *d)
        except Exception as e:
            self.mostrar_error_bd(e)
            return
        self.cargar_tabla_repuestos()
        self.limpiar_repuesto()

    def eliminar_repuesto(self):
        if self.rep_sel is None:
            messagebox.showwarning("Atención", "Seleccione un repuesto de la lista.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el repuesto seleccionado?"):
            return
        try:
            self.datos.eliminar_repuesto(self.rep_sel)
        except Exception as e:
            self.mostrar_error_bd(e)
            return
        self.cargar_tabla_repuestos()
        self.limpiar_repuesto()
