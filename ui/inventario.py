import customtkinter as ctk
from tkinter import messagebox
from database.daos import AtaudDAO
from config import UMBRAL_USOS_CRITICO
from utils.export_excel import exportar_inventario_excel, exportar_historial_excel
from utils.export_pdf import exportar_inventario_pdf, exportar_historial_pdf
from tkinter import filedialog

class InventarioView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="📦 Inventario", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, sticky="w")

        # Filtros
        filtros_frame = ctk.CTkFrame(self)
        filtros_frame.grid(row=1, column=0, sticky="ew", pady=10)
        for i in range(6):
            filtros_frame.grid_columnconfigure(i, weight=1)

        labels = ["Código QR", "Cód. Viejo", "Tipo", "Color", "Estado"]
        self.filtros = {}
        for i, lbl in enumerate(labels):
            ctk.CTkLabel(filtros_frame, text=lbl).grid(row=0, column=i, padx=5)
            if lbl == "Estado":
                self.filtros[lbl] = ctk.CTkComboBox(filtros_frame, values=["", "Disponible", "En Uso", "En Restauración", "Dado de Baja"])
            else:
                self.filtros[lbl] = ctk.CTkEntry(filtros_frame, placeholder_text=lbl)
            self.filtros[lbl].grid(row=1, column=i, padx=5)
            self.filtros[lbl].bind("<KeyRelease>", lambda e: self.cargar_tabla())
            if hasattr(self.filtros[lbl], "configure"):
                try: self.filtros[lbl].configure(command=lambda e=None: self.cargar_tabla())
                except: pass

        ctk.CTkButton(filtros_frame, text="🔍 Buscar", command=self.cargar_tabla, width=100).grid(row=1, column=5, padx=5)

        # Tabla
        self.tabla_frame = ctk.CTkScrollableFrame(self)
        self.tabla_frame.grid(row=2, column=0, sticky="nsew")

        # Botones
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=3, column=0, sticky="ew", pady=10)
        ctk.CTkButton(btn_frame, text="➕ Nuevo Ataúd", command=lambda: self.app.mostrar_registro()).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="📊 Exportar Excel (Inv.)", command=self.exportar_inv_excel).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="📊 Exportar Excel (Hist.)", command=self.exportar_hist_excel).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="📄 Exportar PDF (Inv.)", command=self.exportar_inv_pdf).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="📄 Exportar PDF (Hist.)", command=self.exportar_hist_pdf).pack(side="left", padx=5)

        self.cargar_tabla()

    def cargar_tabla(self):
        for w in self.tabla_frame.winfo_children():
            w.destroy()
        filtros = {
            "codigo_qr": self.filtros["Código QR"].get(),
            "codigo_viejo": self.filtros["Cód. Viejo"].get(),
            "tipo": self.filtros["Tipo"].get(),
            "color": self.filtros["Color"].get(),
            "estado": self.filtros["Estado"].get(),
        }
        datos = AtaudDAO.listar(filtros)

        headers = ["ID", "Código QR", "Cód.Viejo", "Tipo", "Color", "Estado", "Usos", "Precio", "Acciones"]
        for j, h in enumerate(headers):
            ctk.CTkLabel(self.tabla_frame, text=h, font=ctk.CTkFont(weight="bold"), width=100).grid(row=0, column=j, padx=3, pady=3)
            
        from datetime import datetime    

        for i, a in enumerate(datos, start=1):
            es_critico = a["contador_usos"] >= UMBRAL_USOS_CRITICO and a["estado"] != "Dado de Baja"
            color = "#ff6b6b" if es_critico else ("#ffaa00" if a["estado"] == "En Uso" else "")
            
            # CONVERSIÓN DE FECHA PARA MOSTRAR
            fecha_mostrar = a["fecha_compra"]
            if fecha_mostrar:
                try:
                    fecha_mostrar = datetime.strptime(str(fecha_mostrar), "%Y-%m-%d").strftime("%d-%m-%Y")
                except:
                    pass # Si falla, deja la original

            valores = [a["id"], a["codigo_qr"], a["codigo_viejo"] or "-", a["tipo"], a["color"],
                        a["estado"], a["contador_usos"], f"${a['precio']}"]
            
            
            for j, v in enumerate(valores):
                lbl = ctk.CTkLabel(self.tabla_frame, text=str(v), text_color=color if color else None, width=100)
                lbl.grid(row=i, column=j, padx=3, pady=2)
            ctk.CTkButton(self.tabla_frame, text="Editar", width=70, command=lambda x=a: self.app.mostrar_registro(x)).grid(row=i, column=8, padx=3)

    def _guardar_como(self, ext):
        return filedialog.asksaveasfilename(defaultextension=f".{ext}", filetypes=[(f"*.{ext}", f"*.{ext}")])

    def exportar_inv_excel(self):
        ruta = self._guardar_como("xlsx")
        if ruta:
            ok, msg = exportar_inventario_excel(ruta)
            messagebox.showinfo("OK" if ok else "Error", msg if not ok else f"Guardado en:\n{msg}")

    def exportar_hist_excel(self):
        ruta = self._guardar_como("xlsx")
        if ruta:
            ok, msg = exportar_historial_excel(ruta)
            messagebox.showinfo("OK" if ok else "Error", msg if not ok else f"Guardado en:\n{msg}")

    def exportar_inv_pdf(self):
        ruta = self._guardar_como("pdf")
        if ruta:
            ok, msg = exportar_inventario_pdf(ruta)
            messagebox.showinfo("OK", f"PDF generado:\n{msg}")

    def exportar_hist_pdf(self):
        ruta = self._guardar_como("pdf")
        if ruta:
            ok, msg = exportar_historial_pdf(ruta)
            messagebox.showinfo("OK", f"PDF generado:\n{msg}")