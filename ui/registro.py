import customtkinter as ctk
from tkinter import messagebox, simpledialog
from datetime import datetime
from database.daos import AtaudDAO
from utils.qr_generator import generar_qr


class CalendarioModal(ctk.CTkToplevel):
    """Modal simple para seleccionar fecha con tkcalendar."""
    def __init__(self, parent, fecha_inicial=None):
        super().__init__(parent)
        self.title("Seleccionar Fecha")
        self.geometry("320x280")
        self.resizable(False, False)
        self.grab_set()
        self.fecha_seleccionada = None
        
        try:
            from tkcalendar import DateEntry
            ctk.CTkLabel(self, text="Seleccione una fecha:", font=ctk.CTkFont(size=14)).pack(pady=(20, 10))
            
            # Frame para el calendario (usamos tkinter estándar dentro de CTk)
            import tkinter as tk
            frame = tk.Frame(self, bg="#2b2b2b")
            frame.pack(padx=20, pady=10)
            
            if fecha_inicial:
                try:
                    dt = datetime.strptime(fecha_inicial, "%d-%m-%Y")
                    fecha_ini = dt
                except:
                    fecha_ini = datetime.now()
            else:
                fecha_ini = datetime.now()
            
            self.cal = DateEntry(frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2,
                                date_pattern='dd-mm-yyyy',
                                locale='es_ES',
                                year=fecha_ini.year,
                                month=fecha_ini.month,
                                day=fecha_ini.day)
            self.cal.pack(padx=10, pady=10)
            
            ctk.CTkButton(self, text="✅ Confirmar", command=self.confirmar).pack(pady=15)
            ctk.CTkButton(self, text="❌ Cancelar", command=self.cancelar, fg_color="gray").pack(pady=5)
            
        except ImportError:
            ctk.CTkLabel(self, text="tkcalendar no instalado.\nEjecute: pip install tkcalendar", 
                        text_color="red").pack(pady=20)
            ctk.CTkButton(self, text="Cerrar", command=self.cancelar).pack(pady=10)
    
    def confirmar(self):
        try:
            self.fecha_seleccionada = self.cal.get_date().strftime("%d-%m-%Y")
        except:
            self.fecha_seleccionada = None
        self.destroy()
    
    def cancelar(self):
        self.fecha_seleccionada = None
        self.destroy()


class RegistroView(ctk.CTkFrame):
    def __init__(self, parent, app, ataud_editar=None):
        super().__init__(parent)
        self.app = app
        self.ataud = ataud_editar
        self.pack(fill="both", expand=True, padx=20, pady=20)

        titulo = "✏️ Editar Ataúd" if ataud_editar else "➕ Registrar Nuevo Ataúd"
        ctk.CTkLabel(self, text=titulo, font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", pady=(0, 20))

        form = ctk.CTkFrame(self)
        form.pack(fill="x")
        for i in range(2):
            form.grid_columnconfigure(i, weight=1)

        # Obtener tipos y colores únicos de la BD
        tipos_bd = AtaudDAO.obtener_tipos_unicos()
        colores_bd = AtaudDAO.obtener_colores_unicos()
        
        # Valores por defecto si la BD está vacía
        tipos_default = ["Madera", "Metal", "Ecológico", "Madera Roble", "Madera Pino"]
        colores_default = ["Caoba", "Negro", "Blanco", "Marrón", "Gris"]
        
        tipos_values = list(set(tipos_bd + tipos_default)) if tipos_bd else tipos_default
        colores_values = list(set(colores_bd + colores_default)) if colores_bd else colores_default

        # Campos del formulario (orden de navegación)
        campos = [
            ("Código QR *", "codigo_qr", False, "entry"),
            ("Código Viejo", "codigo_viejo", True, "entry"),
            ("Tipo *", "tipo", False, "combobox", tipos_values),
            ("Color *", "color", False, "combobox", colores_values),
            ("Precio *", "precio", False, "entry"),
            ("Fecha Compra * (DD-MM-AAAA)", "fecha_compra", False, "fecha"),
            ("Factura *", "factura_compra", False, "entry"),
            ("Proveedor *", "proveedor_nombre", False, "entry"),
            ("Contacto Proveedor", "proveedor_contacto", True, "entry"),
        ]
        
        self.entries = {}
        self.widgets_orden = []  # Para navegación con teclado
        
        for i, campo in enumerate(campos):
            label = campo[0]
            key = campo[1]
            opcional = campo[2]
            tipo = campo[3]
            
            fila, col = divmod(i, 2)
            ctk.CTkLabel(form, text=label).grid(row=fila, column=col*2, padx=10, pady=8, sticky="w")
            
            if tipo == "combobox":
                values = campo[4]
                e = ctk.CTkComboBox(form, values=values, width=250)
                # Permitir escribir valores nuevos (por defecto CTkComboBox lo permite)
            elif tipo == "fecha":
                # Frame con entry + botón de calendario
                fecha_frame = ctk.CTkFrame(form, fg_color="transparent")
                fecha_frame.grid(row=fila, column=col*2+1, padx=10, pady=8, sticky="ew")
                
                e = ctk.CTkEntry(fecha_frame, width=180, placeholder_text="DD-MM-AAAA")
                e.pack(side="left")
                
                btn_cal = ctk.CTkButton(fecha_frame, text="📅", width=40, 
                                        command=lambda entry=e: self.abrir_calendario(entry))
                btn_cal.pack(side="left", padx=5)
                
                self.entries[key] = e
                self.widgets_orden.append(e)
                continue  # Saltar el grid normal
            else:
                e = ctk.CTkEntry(form, width=250)
            
            e.grid(row=fila, column=col*2+1, padx=10, pady=8)
            self.entries[key] = e
            self.widgets_orden.append(e)

        # Configurar navegación con teclado (Enter y Tab)
        self.configurar_navegacion_teclado()

                # Si es edición, cargar datos y deshabilitar código QR
        if ataud_editar:
            for k, v in ataud_editar.items():
                if k == "fecha_compra" and v:
                    # Convertir de YYYY-MM-DD a DD-MM-AAAA para el formulario
                    try:
                        dt = datetime.strptime(str(v), "%Y-%m-%d")
                        v = dt.strftime("%d-%m-%Y")
                    except:
                        pass
                
                if k in self.entries and v is not None:
                    if isinstance(self.entries[k], ctk.CTkComboBox):
                        self.entries[k].set(str(v))
                    else:
                        self.entries[k].delete(0, "end")
                        self.entries[k].insert(0, str(v))
            self.entries["codigo_qr"].configure(state="readonly")

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", pady=20)
        ctk.CTkButton(btn_frame, text="💾 Guardar", command=self.guardar).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="❌ Cancelar", command=lambda: self.app.mostrar_inventario(), fg_color="gray").pack(side="left", padx=10)

    def configurar_navegacion_teclado(self):
        """Configura Enter y Tab para moverse entre campos."""
        for i, widget in enumerate(self.widgets_orden):
            if i < len(self.widgets_orden) - 1:
                siguiente = self.widgets_orden[i + 1]
            else:
                siguiente = None  # Último campo
            
            def mover_focus(event, sig=siguiente):
                if sig:
                    sig.focus_set()
                    # Si es ComboBox, seleccionar todo el texto
                    if isinstance(sig, ctk.CTkComboBox):
                        sig.focus_set()
                return "break"  # Evitar comportamiento por defecto
            
            widget.bind("<Return>", mover_focus)
            widget.bind("<Tab>", mover_focus)

    def abrir_calendario(self, entry):
        """Abre el modal de calendario y pone la fecha en el entry."""
        fecha_actual = entry.get().strip()
        modal = CalendarioModal(self, fecha_actual if fecha_actual else None)
        self.wait_window(modal)  # Esperar a que se cierre el modal
        
        if modal.fecha_seleccionada:
            entry.delete(0, "end")
            entry.insert(0, modal.fecha_seleccionada)

    def guardar(self):
        data = {k: e.get().strip() if isinstance(e, ctk.CTkEntry) else e.get() 
                for k, e in self.entries.items()}
        
        # Validaciones
        if not self.ataud:
            if not data["codigo_qr"]:
                return messagebox.showwarning("Aviso", "Código QR obligatorio")
        
        for campo in ["tipo", "color", "precio", "fecha_compra", "factura_compra", "proveedor_nombre"]:
            if not data[campo]:
                return messagebox.showwarning("Aviso", f"Campo obligatorio: {campo}")
        
        try:
            data["precio"] = float(data["precio"].replace(",", "."))
            if data["precio"] <= 0:
                raise ValueError()
        except:
            return messagebox.showerror("Error", "Precio debe ser un número positivo")
        
        # Validar formato de fecha DD-MM-AAAA
        try:
            datetime.strptime(data["fecha_compra"], "%d-%m-%Y")
        except:
            return messagebox.showerror("Error", "Fecha inválida. Use formato DD-MM-AAAA o seleccione del calendario 📅")

        # Convertir fecha a formato de BD (AAAA-MM-DD) antes de guardar
        fecha_obj = datetime.strptime(data["fecha_compra"], "%d-%m-%Y")
        data["fecha_compra"] = fecha_obj.strftime("%Y-%m-%d")

        if self.ataud:
            ok, msg = AtaudDAO.actualizar(self.ataud["id"], data)
        else:
            ok, msg = AtaudDAO.crear(data)

        if ok:
            # Generar QR
            ataud = AtaudDAO.buscar_por_codigo(data["codigo_qr"])
            ruta_qr = generar_qr(ataud)
            messagebox.showinfo("Éxito", f"{msg}\n\nQR generado en:\n{ruta_qr}")
            self.app.mostrar_inventario()
        else:
            messagebox.showerror("Error", msg)