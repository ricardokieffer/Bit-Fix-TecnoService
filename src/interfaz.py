import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from acceso_datos import (
    AccesoDatosMock,
    StockInsuficienteError,
    TIPOS_EQUIPO,
    ESPECIALIDADES_TECNICO,
    ESTADOS_TECNICO,
    ESTADOS_REPARACION,
    ESTADOS_PRESUPUESTO,
)


class AplicacionTecnoService:
    def __init__(self, root):
        self.root = root
        self.root.title("TecnoService PC - Sistema de Gestión de Reparaciones (Bit&Fix)")
        self.root.geometry("1080x700")
        self.root.minsize(960, 620)

        # Capa de datos (prototipo en memoria - Hito 2, aún sin conexión a la base)
        self.datos = AccesoDatosMock()

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook.Tab', font=('Helvetica', 10, 'bold'), padding=[10, 6])
        self.style.configure('TLabelframe.Label', font=('Helvetica', 10, 'bold'), foreground='#1A365D')

        self.crear_encabezado()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_ingresos = ttk.Frame(self.notebook)
        self.tab_ordenes = ttk.Frame(self.notebook)
        self.tab_tecnicos = ttk.Frame(self.notebook)
        self.tab_repuestos = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_clientes, text=" 1. Clientes ")
        self.notebook.add(self.tab_ingresos, text=" 2. Ingresos ")
        self.notebook.add(self.tab_ordenes, text=" 3. Órdenes de Trabajo ")
        self.notebook.add(self.tab_tecnicos, text=" 4. Técnicos ")
        self.notebook.add(self.tab_repuestos, text=" 5. Repuestos ")

        self.build_tab_clientes()
        self.build_tab_ingresos()
        self.build_tab_ordenes()
        self.build_tab_tecnicos()
        self.build_tab_repuestos()

        self.crear_barra_estado()

    def crear_encabezado(self):
        header_frame = tk.Frame(self.root, bg='#1A365D', height=50)
        header_frame.pack(fill='x', side='top')
        tk.Label(header_frame, text="TECNOSERVICE PC — Servicio Técnico Especializado",
                  font=('Helvetica', 14, 'bold'), fg='white', bg='#1A365D').pack(side='left', padx=15, pady=10)
        tk.Label(header_frame, text="Grupo Bit&Fix | COM B1",
                  font=('Helvetica', 10, 'italic'), fg='#E2E8F0', bg='#1A365D').pack(side='right', padx=15, pady=10)

    def crear_barra_estado(self):
        status_frame = tk.Frame(self.root, bg='#E2E8F0', height=25)
        status_frame.pack(fill='x', side='bottom')
        tk.Label(status_frame,
                  text="Modo prototipo (Hito 2): datos de prueba en memoria | Motor destino: PostgreSQL",
                  font=('Helvetica', 9), bg='#E2E8F0', fg='#4A5568').pack(side='left', padx=10, pady=2)

    # ================================================================
    # PESTAÑA 1: CLIENTES (ABM completo)
    # ================================================================
    def build_tab_clientes(self):
        self.id_cliente_seleccionado = None

        frame_form = ttk.LabelFrame(self.tab_clientes, text=" Alta / Edición de Cliente ", padding=10)
        frame_form.pack(side='left', fill='both', expand=False, padx=10, pady=10, ipadx=5)

        ttk.Label(frame_form, text="DNI:").grid(row=0, column=0, sticky='w', pady=5)
        self.ent_cli2_dni = ttk.Entry(frame_form, width=22)
        self.ent_cli2_dni.grid(row=0, column=1, pady=5)

        ttk.Label(frame_form, text="Nombre y Apellido:").grid(row=1, column=0, sticky='w', pady=5)
        self.ent_cli2_nombre = ttk.Entry(frame_form, width=22)
        self.ent_cli2_nombre.grid(row=1, column=1, pady=5)

        ttk.Label(frame_form, text="Teléfono:").grid(row=2, column=0, sticky='w', pady=5)
        self.ent_cli2_tel = ttk.Entry(frame_form, width=22)
        self.ent_cli2_tel.grid(row=2, column=1, pady=5)

        botones = ttk.Frame(frame_form)
        botones.grid(row=3, column=0, columnspan=2, pady=15)
        ttk.Button(botones, text="Guardar Nuevo", command=self.guardar_cliente_nuevo).pack(side='left', padx=3)
        ttk.Button(botones, text="Modificar", command=self.modificar_cliente_seleccionado).pack(side='left', padx=3)
        ttk.Button(botones, text="Eliminar", command=self.eliminar_cliente_seleccionado).pack(side='left', padx=3)
        ttk.Button(botones, text="Limpiar", command=self.limpiar_form_cliente).pack(side='left', padx=3)

        frame_grid = ttk.LabelFrame(self.tab_clientes, text=" Clientes Registrados ", padding=10)
        frame_grid.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        cols = ("ID", "DNI", "Nombre", "Teléfono")
        self.tree_clientes = ttk.Treeview(frame_grid, columns=cols, show='headings')
        for c in cols:
            self.tree_clientes.heading(c, text=c)
            self.tree_clientes.column(c, width=140)
        self.tree_clientes.column("ID", width=50)
        self.tree_clientes.bind("<<TreeviewSelect>>", self.on_select_cliente)

        scrollbar = ttk.Scrollbar(frame_grid, orient='vertical', command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscrollcommand=scrollbar.set)
        self.tree_clientes.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.cargar_tabla_clientes()

    def cargar_tabla_clientes(self):
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        for c in self.datos.obtener_clientes():
            self.tree_clientes.insert('', 'end', values=(c['id'], c['dni'], c['nombre'], c['telefono']))

    def on_select_cliente(self, event=None):
        seleccion = self.tree_clientes.selection()
        if not seleccion:
            return
        valores = self.tree_clientes.item(seleccion[0])['values']
        self.id_cliente_seleccionado = valores[0]
        self.ent_cli2_dni.delete(0, tk.END); self.ent_cli2_dni.insert(0, valores[1])
        self.ent_cli2_nombre.delete(0, tk.END); self.ent_cli2_nombre.insert(0, valores[2])
        self.ent_cli2_tel.delete(0, tk.END); self.ent_cli2_tel.insert(0, valores[3])

    def limpiar_form_cliente(self):
        self.id_cliente_seleccionado = None
        self.ent_cli2_dni.delete(0, tk.END)
        self.ent_cli2_nombre.delete(0, tk.END)
        self.ent_cli2_tel.delete(0, tk.END)
        if self.tree_clientes.selection():
            self.tree_clientes.selection_remove(self.tree_clientes.selection())

    def _leer_form_cliente(self):
        dni = self.ent_cli2_dni.get().strip()
        nombre = self.ent_cli2_nombre.get().strip()
        tel = self.ent_cli2_tel.get().strip()
        if not dni or not nombre:
            messagebox.showwarning("Atención", "DNI y Nombre son obligatorios.")
            return None
        return dni, nombre, tel

    def guardar_cliente_nuevo(self):
        datos_form = self._leer_form_cliente()
        if not datos_form:
            return
        self.datos.agregar_cliente(*datos_form)
        self.cargar_tabla_clientes()
        self.actualizar_combos_dependientes()
        messagebox.showinfo("Éxito", "Cliente registrado correctamente.")
        self.limpiar_form_cliente()

    def modificar_cliente_seleccionado(self):
        if self.id_cliente_seleccionado is None:
            messagebox.showinfo("Atención", "Seleccioná un cliente de la lista para modificar.")
            return
        datos_form = self._leer_form_cliente()
        if not datos_form:
            return
        self.datos.modificar_cliente(self.id_cliente_seleccionado, *datos_form)
        self.cargar_tabla_clientes()
        messagebox.showinfo("Éxito", "Cliente modificado correctamente.")

    def eliminar_cliente_seleccionado(self):
        if self.id_cliente_seleccionado is None:
            messagebox.showinfo("Atención", "Seleccioná un cliente de la lista para eliminar.")
            return
        if not messagebox.askyesno("Confirmar eliminación", "¿Seguro que querés eliminar este cliente?"):
            return
        try:
            self.datos.eliminar_cliente(self.id_cliente_seleccionado)
            self.cargar_tabla_clientes()
            self.limpiar_form_cliente()
            messagebox.showinfo("Éxito", "Cliente eliminado.")
        except ValueError as e:
            messagebox.showerror("No se puede eliminar", str(e))

    # ================================================================
    # PESTAÑA 2: INGRESOS (Cliente + Equipo + Orden inicial)
    # ================================================================
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
        ttk.Label(frame_form, text="(si el DNI ya existe, se reutiliza el cliente)",
                  foreground='#718096', font=('Helvetica', 8)).grid(row=3, column=0, columnspan=2, sticky='w')

        ttk.Separator(frame_form, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky='ew', pady=8)

        ttk.Label(frame_form, text="Tipo de Equipo:").grid(row=5, column=0, sticky='w', pady=4)
        self.cmb_eq_tipo = ttk.Combobox(frame_form, values=TIPOS_EQUIPO, width=23, state="readonly")
        self.cmb_eq_tipo.set(TIPOS_EQUIPO[0])
        self.cmb_eq_tipo.grid(row=5, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Marca:").grid(row=6, column=0, sticky='w', pady=4)
        self.ent_eq_marca = ttk.Entry(frame_form, width=25)
        self.ent_eq_marca.grid(row=6, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Modelo:").grid(row=7, column=0, sticky='w', pady=4)
        self.ent_eq_modelo = ttk.Entry(frame_form, width=25)
        self.ent_eq_modelo.grid(row=7, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Nº de Serie:").grid(row=8, column=0, sticky='w', pady=4)
        self.ent_eq_serie = ttk.Entry(frame_form, width=25)
        self.ent_eq_serie.grid(row=8, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Técnico Asignado:").grid(row=9, column=0, sticky='w', pady=4)
        self.cmb_eq_tec = ttk.Combobox(frame_form, width=23, state="readonly")
        self.cmb_eq_tec.grid(row=9, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Presupuesto Est. ($):").grid(row=10, column=0, sticky='w', pady=4)
        self.ent_eq_presupuesto = ttk.Entry(frame_form, width=25)
        self.ent_eq_presupuesto.insert(0, "15000.00")
        self.ent_eq_presupuesto.grid(row=10, column=1, pady=4, sticky='w')

        ttk.Label(frame_form, text="Falla Reportada:").grid(row=11, column=0, sticky='nw', pady=4)
        self.txt_eq_falla = tk.Text(frame_form, width=25, height=3, font=('Helvetica', 9))
        self.txt_eq_falla.grid(row=11, column=1, pady=4, sticky='w')

        btn_box = ttk.Frame(frame_form)
        btn_box.grid(row=12, column=0, columnspan=2, pady=10)
        ttk.Button(btn_box, text="Registrar Ingreso", command=self.guardar_ingreso).pack(side='left', padx=5)
        ttk.Button(btn_box, text="Limpiar Formulario", command=self.limpiar_ingreso).pack(side='left', padx=5)

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

        self.actualizar_combos_dependientes()
        self.cargar_tabla_ingresos()

    def actualizar_combos_dependientes(self):
        """Refresca los combobox que dependen de listas de técnicos/repuestos/órdenes."""
        nombres_tecnicos = [f"{t['apellido']}, {t['nombre']}" for t in self.datos.obtener_tecnicos()]
        if hasattr(self, 'cmb_eq_tec'):
            self.cmb_eq_tec['values'] = nombres_tecnicos
            if nombres_tecnicos and not self.cmb_eq_tec.get():
                self.cmb_eq_tec.set(nombres_tecnicos[0])
        if hasattr(self, 'repuesto_combo'):
            self.repuesto_combo['values'] = [f"{r['id']} - {r['descripcion']} (stock: {r['stock']})"
                                              for r in self.datos.obtener_repuestos()]

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

        # 1) Cliente: si el DNI ya existe, se reutiliza (evita duplicados)
        cli = next((c for c in self.datos.obtener_clientes() if c["dni"] == dni), None)
        if cli is None:
            cli = self.datos.agregar_cliente(dni, nombre, tel)
        else:
            self.datos.modificar_cliente(cli["id"], dni, nombre, tel or cli["telefono"])

        # 2) Equipo (solo datos de hardware)
        tipo = self.cmb_eq_tipo.get()
        serie = self.ent_eq_serie.get().strip()
        equipo_desc = f"{tipo} {marca} {modelo}".strip()
        nuevo_eq = self.datos.agregar_equipo(tipo, marca, modelo, serie, cli["id"], nombre)

        # 3) Reparación / Orden de trabajo (acá vive la falla reportada y el estado)
        tecnico_sel = self.cmb_eq_tec.get()
        id_tecnico = next((t["id"] for t in self.datos.obtener_tecnicos()
                            if f"{t['apellido']}, {t['nombre']}" == tecnico_sel), None)
        self.datos.agregar_reparacion(
            id_equipo=nuevo_eq["id"], equipo_desc=equipo_desc, cliente_nombre=nombre,
            id_tecnico=id_tecnico, tecnico_nombre=tecnico_sel, fecha=date.today().isoformat(),
            falla_reportada=falla, estimado=presupuesto
        )

        self.cargar_tabla_ingresos()
        self.cargar_tabla_clientes()
        self.refrescar_combo_ordenes()
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

    # ================================================================
    # PESTAÑA 3: ÓRDENES DE TRABAJO
    # ================================================================
    def build_tab_ordenes(self):
        frame_top = ttk.LabelFrame(self.tab_ordenes, text=" Actualización de Diagnóstico y Estado en Taller ", padding=10)
        frame_top.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_top, text="Orden Nº:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.cmb_ord_id = ttk.Combobox(frame_top, width=10, state="readonly")
        self.cmb_ord_id.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.cmb_ord_id.bind("<<ComboboxSelected>>", self.cargar_orden_seleccionada)

        ttk.Label(frame_top, text="Estado:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.cmb_ord_estado = ttk.Combobox(frame_top, values=ESTADOS_REPARACION, width=16, state="readonly")
        self.cmb_ord_estado.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(frame_top, text="Presupuesto:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.cmb_ord_presupuesto = ttk.Combobox(frame_top, values=ESTADOS_PRESUPUESTO, width=12, state="readonly")
        self.cmb_ord_presupuesto.grid(row=0, column=5, padx=5, pady=5, sticky='w')
        ttk.Button(frame_top, text="Guardar Presupuesto", command=self.guardar_presupuesto).grid(row=0, column=6, padx=5)

        ttk.Label(frame_top, text="Falla Reportada:").grid(row=1, column=0, padx=5, pady=5, sticky='nw')
        self.lbl_ord_falla = ttk.Label(frame_top, text="-", wraplength=260, foreground='#4A5568')
        self.lbl_ord_falla.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky='w')

        ttk.Label(frame_top, text="Diagnóstico Técnico:").grid(row=2, column=0, padx=5, pady=5, sticky='nw')
        self.txt_ord_diag = tk.Text(frame_top, width=50, height=3, font=('Helvetica', 9))
        self.txt_ord_diag.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky='w')
        ttk.Button(frame_top, text="Actualizar Orden", command=self.actualizar_orden).grid(row=2, column=4, padx=10, pady=5)

        # --- Repuestos utilizados en la orden seleccionada ---
        frame_rep = ttk.LabelFrame(self.tab_ordenes, text=" Repuestos Utilizados en esta Orden ", padding=8)
        frame_rep.pack(fill='x', padx=10, pady=(0, 5))

        self.lista_repuestos_orden = tk.Listbox(frame_rep, height=3)
        self.lista_repuestos_orden.pack(side='left', fill='both', expand=True, padx=(0, 10))

        add_frame = ttk.Frame(frame_rep)
        add_frame.pack(side='left')
        ttk.Label(add_frame, text="Repuesto:").grid(row=0, column=0, sticky='w')
        self.repuesto_combo = ttk.Combobox(add_frame, width=32, state="readonly")
        self.repuesto_combo.grid(row=0, column=1, padx=4)
        ttk.Label(add_frame, text="Cant.:").grid(row=0, column=2, sticky='w')
        self.ent_rep_cantidad = ttk.Entry(add_frame, width=5)
        self.ent_rep_cantidad.insert(0, "1")
        self.ent_rep_cantidad.grid(row=0, column=3, padx=4)
        ttk.Button(add_frame, text="Agregar a la orden", command=self.agregar_repuesto_a_orden).grid(row=0, column=4, padx=4)

        frame_grid = ttk.LabelFrame(self.tab_ordenes, text=" Listado General de Órdenes de Servicio ", padding=10)
        frame_grid.pack(fill='both', expand=True, padx=10, pady=5)

        cols = ("Nº Orden", "Equipo", "Cliente", "Técnico", "Fecha", "Estado", "Presupuesto", "Est. ($)", "Total ($)")
        self.tree_ordenes = ttk.Treeview(frame_grid, columns=cols, show='headings')
        for c in cols:
            self.tree_ordenes.heading(c, text=c)
            self.tree_ordenes.column(c, width=95)
        self.tree_ordenes.column("Nº Orden", width=60)

        scrollbar = ttk.Scrollbar(frame_grid, orient='vertical', command=self.tree_ordenes.yview)
        self.tree_ordenes.configure(yscrollcommand=scrollbar.set)
        self.tree_ordenes.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.actualizar_combos_dependientes()
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
        self.txt_ord_diag.insert("1.0", orden.get("diagnostico", ""))
        self.cmb_ord_estado.set(orden["estado"])
        self.cmb_ord_presupuesto.set(orden["presupuesto_aprobado"])
        self.refrescar_lista_repuestos_orden(orden)

    def refrescar_lista_repuestos_orden(self, orden):
        self.lista_repuestos_orden.delete(0, tk.END)
        if not orden["repuestos_usados"]:
            self.lista_repuestos_orden.insert(tk.END, "(sin repuestos asociados)")
        for u in orden["repuestos_usados"]:
            self.lista_repuestos_orden.insert(
                tk.END, f"{u['descripcion']} x{u['cantidad']} (${u['precio_unitario_aplicado']:.2f} c/u)"
            )

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
            self.datos.actualizar_estado_reparacion(int(id_sel), nuevo_estado, nuevo_diag)
        except ValueError as e:
            # Regla de negocio: presupuesto no aceptado (ver acceso_datos.puede_avanzar_estado)
            messagebox.showerror("Regla de negocio", str(e))
            return
        self.cargar_tabla_ordenes()
        self.cargar_tabla_ingresos()
        messagebox.showinfo("Orden Actualizada", f"La orden Nº {id_sel} fue actualizada al estado '{nuevo_estado}'.")

    def guardar_presupuesto(self):
        id_sel = self.cmb_ord_id.get()
        if not id_sel:
            messagebox.showwarning("Atención", "Seleccioná una orden de la lista.")
            return
        nuevo_valor = self.cmb_ord_presupuesto.get()
        if not nuevo_valor:
            return
        self.datos.actualizar_presupuesto(int(id_sel), nuevo_valor)
        self.cargar_tabla_ordenes()
        messagebox.showinfo("Presupuesto Actualizado", f"Presupuesto de la orden Nº {id_sel}: {nuevo_valor}.")

    def agregar_repuesto_a_orden(self):
        id_sel = self.cmb_ord_id.get()
        if not id_sel:
            messagebox.showwarning("Atención", "Seleccioná una orden de la lista.")
            return
        seleccion = self.repuesto_combo.get()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccioná un repuesto del catálogo.")
            return
        id_repuesto = int(seleccion.split(" - ")[0])
        try:
            cantidad = int(self.ent_rep_cantidad.get().strip())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Cantidad inválida", "Ingresá un número entero mayor a cero.")
            return

        try:
            orden = self.datos.usar_repuesto_en_reparacion(int(id_sel), id_repuesto, cantidad)
        except StockInsuficienteError as e:
            # Regla de negocio: no hay stock suficiente (equivalente al trigger SQL)
            messagebox.showerror("Sin stock suficiente", str(e))
            return

        self.refrescar_lista_repuestos_orden(orden)
        self.actualizar_combos_dependientes()  # el combo de repuestos muestra el stock actualizado
        self.cargar_tabla_repuestos()
        self.cargar_tabla_ordenes()
        messagebox.showinfo("Repuesto agregado", "El repuesto se descontó del stock y se asoció a la orden.")

    # ================================================================
    # PESTAÑA 4: TÉCNICOS (ABM completo)
    # ================================================================
    def build_tab_tecnicos(self):
        self.id_tecnico_seleccionado = None

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
        ttk.Button(botones, text="Guardar Nuevo", command=self.guardar_tecnico_nuevo).pack(side='left', padx=3)
        ttk.Button(botones, text="Modificar", command=self.modificar_tecnico_seleccionado).pack(side='left', padx=3)
        ttk.Button(botones, text="Eliminar", command=self.eliminar_tecnico_seleccionado).pack(side='left', padx=3)
        ttk.Button(botones, text="Limpiar", command=self.limpiar_form_tecnico).pack(side='left', padx=3)

        frame_grid = ttk.LabelFrame(self.tab_tecnicos, text=" Personal Técnico Registrado ", padding=10)
        frame_grid.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        cols = ("Legajo", "DNI", "Apellido", "Nombre", "Especialidad", "Estado")
        self.tree_tecnicos = ttk.Treeview(frame_grid, columns=cols, show='headings')
        for c in cols:
            self.tree_tecnicos.heading(c, text=c)
            self.tree_tecnicos.column(c, width=100)
        self.tree_tecnicos.bind("<<TreeviewSelect>>", self.on_select_tecnico)
        self.tree_tecnicos.pack(fill='both', expand=True)

        self.cargar_tabla_tecnicos()

    def cargar_tabla_tecnicos(self):
        for item in self.tree_tecnicos.get_children():
            self.tree_tecnicos.delete(item)
        for t in self.datos.obtener_tecnicos():
            self.tree_tecnicos.insert('', 'end', iid=t['id'],
                                        values=(t['legajo'], t['dni'], t['apellido'], t['nombre'], t['especialidad'], t['estado']))

    def on_select_tecnico(self, event=None):
        seleccion = self.tree_tecnicos.selection()
        if not seleccion:
            return
        self.id_tecnico_seleccionado = int(seleccion[0])
        valores = self.tree_tecnicos.item(seleccion[0])['values']
        self.ent_tec_legajo.delete(0, tk.END); self.ent_tec_legajo.insert(0, valores[0])
        self.ent_tec_dni.delete(0, tk.END); self.ent_tec_dni.insert(0, valores[1])
        self.ent_tec_ape.delete(0, tk.END); self.ent_tec_ape.insert(0, valores[2])
        self.ent_tec_nom.delete(0, tk.END); self.ent_tec_nom.insert(0, valores[3])
        self.cmb_tec_esp.set(valores[4])
        self.cmb_tec_estado.set(valores[5])

    def limpiar_form_tecnico(self):
        self.id_tecnico_seleccionado = None
        for entry in [self.ent_tec_legajo, self.ent_tec_dni, self.ent_tec_nom, self.ent_tec_ape]:
            entry.delete(0, tk.END)
        if self.tree_tecnicos.selection():
            self.tree_tecnicos.selection_remove(self.tree_tecnicos.selection())

    def _leer_form_tecnico(self):
        legajo = self.ent_tec_legajo.get().strip()
        dni = self.ent_tec_dni.get().strip()
        nom = self.ent_tec_nom.get().strip()
        ape = self.ent_tec_ape.get().strip()
        if not legajo or not dni or not nom or not ape:
            messagebox.showwarning("Atención", "Por favor complete todos los datos del técnico.")
            return None
        return legajo, dni, nom, ape, self.cmb_tec_esp.get(), self.cmb_tec_estado.get()

    def guardar_tecnico_nuevo(self):
        datos_form = self._leer_form_tecnico()
        if not datos_form:
            return
        legajo, dni, nom, ape, esp, est = datos_form
        self.datos.agregar_tecnico(legajo, dni, nom, ape, esp, est)
        self.cargar_tabla_tecnicos()
        self.actualizar_combos_dependientes()
        messagebox.showinfo("Éxito", f"Técnico {nom} {ape} registrado correctamente.")
        self.limpiar_form_tecnico()

    def modificar_tecnico_seleccionado(self):
        if self.id_tecnico_seleccionado is None:
            messagebox.showinfo("Atención", "Seleccioná un técnico de la lista para modificar.")
            return
        datos_form = self._leer_form_tecnico()
        if not datos_form:
            return
        self.datos.modificar_tecnico(self.id_tecnico_seleccionado, *datos_form)
        self.cargar_tabla_tecnicos()
        self.actualizar_combos_dependientes()
        messagebox.showinfo("Éxito", "Técnico modificado correctamente.")

    def eliminar_tecnico_seleccionado(self):
        if self.id_tecnico_seleccionado is None:
            messagebox.showinfo("Atención", "Seleccioná un técnico de la lista para eliminar.")
            return
        if not messagebox.askyesno("Confirmar eliminación", "¿Seguro que querés eliminar este técnico?"):
            return
        try:
            self.datos.eliminar_tecnico(self.id_tecnico_seleccionado)
            self.cargar_tabla_tecnicos()
            self.actualizar_combos_dependientes()
            self.limpiar_form_tecnico()
            messagebox.showinfo("Éxito", "Técnico eliminado.")
        except ValueError as e:
            messagebox.showerror("No se puede eliminar", str(e))

    # ================================================================
    # PESTAÑA 5: REPUESTOS (ABM completo)
    # ================================================================
    def build_tab_repuestos(self):
        self.id_repuesto_seleccionado = None

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
        ttk.Button(botones, text="Guardar Nuevo", command=self.guardar_repuesto_nuevo).pack(side='left', padx=3)
        ttk.Button(botones, text="Modificar", command=self.modificar_repuesto_seleccionado).pack(side='left', padx=3)
        ttk.Button(botones, text="Eliminar", command=self.eliminar_repuesto_seleccionado).pack(side='left', padx=3)
        ttk.Button(botones, text="Limpiar", command=self.limpiar_form_repuesto).pack(side='left', padx=3)

        frame_grid = ttk.LabelFrame(self.tab_repuestos, text=" Inventario y Alertas de Stock ", padding=10)
        frame_grid.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        cols = ("Código", "Descripción", "Precio Unitario ($)", "Stock Actual", "Stock Mínimo", "Estado Stock")
        self.tree_repuestos = ttk.Treeview(frame_grid, columns=cols, show='headings')
        for c in cols:
            self.tree_repuestos.heading(c, text=c)
            self.tree_repuestos.column(c, width=105)
        self.tree_repuestos.column("Descripción", width=220)
        self.tree_repuestos.bind("<<TreeviewSelect>>", self.on_select_repuesto)
        self.tree_repuestos.pack(fill='both', expand=True)

        self.cargar_tabla_repuestos()

    def cargar_tabla_repuestos(self):
        for item in self.tree_repuestos.get_children():
            self.tree_repuestos.delete(item)
        for r in self.datos.obtener_repuestos():
            estado = "NORMAL" if r['stock'] > r['minimo'] else "ALERTA STOCK BAJO"
            self.tree_repuestos.insert('', 'end', iid=r['id'],
                                        values=(r['codigo'], r['descripcion'], f"${r['precio']:.2f}", r['stock'], r['minimo'], estado))

    def on_select_repuesto(self, event=None):
        seleccion = self.tree_repuestos.selection()
        if not seleccion:
            return
        self.id_repuesto_seleccionado = int(seleccion[0])
        valores = self.tree_repuestos.item(seleccion[0])['values']
        self.ent_rep_cod.delete(0, tk.END); self.ent_rep_cod.insert(0, valores[0])
        self.ent_rep_desc.delete(0, tk.END); self.ent_rep_desc.insert(0, valores[1])
        self.ent_rep_precio.delete(0, tk.END); self.ent_rep_precio.insert(0, str(valores[2]).replace("$", ""))
        self.ent_rep_stock.delete(0, tk.END); self.ent_rep_stock.insert(0, valores[3])
        self.ent_rep_min.delete(0, tk.END); self.ent_rep_min.insert(0, valores[4])

    def limpiar_form_repuesto(self):
        self.id_repuesto_seleccionado = None
        for entry in [self.ent_rep_cod, self.ent_rep_desc, self.ent_rep_precio, self.ent_rep_stock]:
            entry.delete(0, tk.END)
        self.ent_rep_min.delete(0, tk.END)
        self.ent_rep_min.insert(0, "2")
        if self.tree_repuestos.selection():
            self.tree_repuestos.selection_remove(self.tree_repuestos.selection())

    def _leer_form_repuesto(self):
        cod = self.ent_rep_cod.get().strip()
        desc = self.ent_rep_desc.get().strip()
        precio = self.ent_rep_precio.get().strip()
        stock = self.ent_rep_stock.get().strip()
        minimo = self.ent_rep_min.get().strip()
        if not cod or not desc or not precio or not stock:
            messagebox.showwarning("Atención", "Por favor complete los campos obligatorios del repuesto.")
            return None
        try:
            return cod, desc, float(precio), int(stock), int(minimo or 0)
        except ValueError:
            messagebox.showerror("Error de Formato", "Precio y Stock deben ser valores numéricos válidos.")
            return None

    def guardar_repuesto_nuevo(self):
        datos_form = self._leer_form_repuesto()
        if not datos_form:
            return
        self.datos.agregar_repuesto(*datos_form)
        self.cargar_tabla_repuestos()
        self.actualizar_combos_dependientes()
        messagebox.showinfo("Éxito", f"Repuesto '{datos_form[1]}' guardado en inventario.")
        self.limpiar_form_repuesto()

    def modificar_repuesto_seleccionado(self):
        if self.id_repuesto_seleccionado is None:
            messagebox.showinfo("Atención", "Seleccioná un repuesto de la lista para modificar.")
            return
        datos_form = self._leer_form_repuesto()
        if not datos_form:
            return
        self.datos.modificar_repuesto(self.id_repuesto_seleccionado, *datos_form)
        self.cargar_tabla_repuestos()
        self.actualizar_combos_dependientes()
        messagebox.showinfo("Éxito", "Repuesto modificado correctamente.")

    def eliminar_repuesto_seleccionado(self):
        if self.id_repuesto_seleccionado is None:
            messagebox.showinfo("Atención", "Seleccioná un repuesto de la lista para eliminar.")
            return
        if not messagebox.askyesno("Confirmar eliminación", "¿Seguro que querés eliminar este repuesto?"):
            return
        try:
            self.datos.eliminar_repuesto(self.id_repuesto_seleccionado)
            self.cargar_tabla_repuestos()
            self.actualizar_combos_dependientes()
            self.limpiar_form_repuesto()
            messagebox.showinfo("Éxito", "Repuesto eliminado.")
        except ValueError as e:
            messagebox.showerror("No se puede eliminar", str(e))
