import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from database.daos import AtaudDAO
from utils.qr_generator import generar_qr

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

        campos = [
            ("Código QR *", "codigo_qr", False),
            ("Código Viejo", "codigo_viejo", True),
            ("Tipo *", "tipo", False),
            ("Color *", "color", False),
            ("Precio *", "precio", False),
            ("Fecha Compra * (YYYY-MM-DD)", "fecha_compra", False),
            ("Factura *", "factura_compra", False),
            ("Proveedor *", "proveedor_nombre", False),
            ("Contacto Proveedor", "proveedor_contacto", True),
        ]
        self.entries = {}
        for i, (label, key, opcional) in enumerate(campos):
            fila, col = divmod(i, 2)
            ctk.CTkLabel(form, text=label).grid(row=fila, column=col*2, padx=10, pady=8, sticky="w")
            e = ctk.CTkEntry(form, width=250)
            e.grid(row=fila, column=col*2+1, padx=10, pady=8)
            self.entries[key] = e

        if ataud_editar:
            for k, v in ataud_editar.items():
                if k in self.entries and v is not None:
                    self.entries[k].insert(0, str(v))
            self.entries["codigo_qr"].configure(state="disabled")

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", pady=20)
        ctk.CTkButton(btn_frame, text="💾 Guardar", command=self.guardar).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="❌ Cancelar", command=lambda: self.app.mostrar_inventario(), fg_color="gray").pack(side="left", padx=10)

    def guardar(self):
        data = {k: e.get().strip() for k, e in self.entries.items()}
        # Validaciones
        if not self.ataud:
            if not data["codigo_qr"]:
                return messagebox.showwarning("Aviso", "Código QR obligatorio")
        for campo in ["tipo", "color", "precio", "fecha_compra", "factura_compra", "proveedor_nombre"]:
            if not data[campo]:
                return messagebox.showwarning("Aviso", f"Campo obligatorio: {campo}")
        try:
            data["precio"] = float(data["precio"])
            if data["precio"] <= 0:
                raise ValueError()
        except:
            return messagebox.showerror("Error", "Precio debe ser un número positivo")
        try:
            datetime.strptime(data["fecha_compra"], "%Y-%m-%d")
        except:
            return messagebox.showerror("Error", "Fecha inválida. Use formato YYYY-MM-DD")

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