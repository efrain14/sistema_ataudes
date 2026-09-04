import customtkinter as ctk
from tkinter import messagebox
from database.daos import AtaudDAO, HistorialDAO
from config import UMBRAL_USOS_CRITICO
from ui.modales.restauracion import ModalRestauracion
from ui.modales.salida_entierro import ModalSalidaEntierro

class ControlCicloView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="🔄 Control de Ciclo", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, sticky="w")

        # Buscador
        buscador = ctk.CTkFrame(self)
        buscador.grid(row=1, column=0, sticky="ew", pady=10)
        ctk.CTkLabel(buscador, text="Código QR:").pack(side="left", padx=5)
        self.entry_qr = ctk.CTkEntry(buscador, width=250, placeholder_text="Escanear o escribir código")
        self.entry_qr.pack(side="left", padx=5)
        self.entry_qr.bind("<Return>", lambda e: self.buscar())
        ctk.CTkButton(buscador, text="🔍 Buscar", command=self.buscar).pack(side="left", padx=5)

        # Panel de info
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.grid(row=2, column=0, sticky="ew", pady=10)
        self.lbl_info = ctk.CTkLabel(self.info_frame, text="Ingrese un código QR para comenzar", font=ctk.CTkFont(size=14))
        self.lbl_info.pack(padx=20, pady=20)

        # Botones de acción
        self.acciones_frame = ctk.CTkFrame(self)
        self.acciones_frame.grid(row=3, column=0, sticky="ew", pady=10)

        self.btn_salida = ctk.CTkButton(self.acciones_frame, text="🚚 Salida a Servicio", command=self.salida_servicio, fg_color="#e67e22")
        self.btn_salida.pack(side="left", padx=5, pady=5)

        self.btn_retorno = ctk.CTkButton(self.acciones_frame, text="🔄 Retorno (a restauración)", command=self.retorno_restauracion, fg_color="#3498db")
        self.btn_retorno.pack(side="left", padx=5, pady=5)

        self.btn_confirmar = ctk.CTkButton(self.acciones_frame, text="✅ Confirmar Restauración", command=self.confirmar_restauracion, fg_color="#27ae60")
        self.btn_confirmar.pack(side="left", padx=5, pady=5)

        self.btn_entierro = ctk.CTkButton(self.acciones_frame, text="⚰️ Entierro Definitivo", command=self.entierro_definitivo, fg_color="#c0392b")
        self.btn_entierro.pack(side="left", padx=5, pady=5)

        # Historial
        ctk.CTkLabel(self, text="📜 Historial del Ataúd", font=ctk.CTkFont(size=16, weight="bold")).grid(row=4, column=0, sticky="w", pady=(20, 5))
        self.hist_frame = ctk.CTkScrollableFrame(self, height=200)
        self.hist_frame.grid(row=5, column=0, sticky="nsew")
        self.grid_rowconfigure(5, weight=1)

        self.ataud_actual = None

    def buscar(self):
        codigo = self.entry_qr.get().strip()
        if not codigo:
            return
        ataud = AtaudDAO.buscar_por_codigo(codigo)
        if not ataud:
            self.lbl_info.configure(text=f"❌ No se encontró: {codigo}", text_color="red")
            self.ataud_actual = None
            return
        self.ataud_actual = ataud
        color = "#ff6b6b" if ataud["contador_usos"] >= UMBRAL_USOS_CRITICO else "white"
        self.lbl_info.configure(
            text=f"📦 {ataud['codigo_qr']} | {ataud['tipo']} {ataud['color']} | Estado: {ataud['estado']} | Usos: {ataud['contador_usos']}",
            text_color=color
        )
        self.cargar_historial()

    def cargar_historial(self):
        for w in self.hist_frame.winfo_children():
            w.destroy()
        if not self.ataud_actual:
            return
        hist = HistorialDAO.historial_de(self.ataud_actual["id"])
        if not hist:
            ctk.CTkLabel(self.hist_frame, text="Sin movimientos registrados").pack(pady=10)
            return
        for h in hist:
            txt = f"[{h['fecha_salida']}] {h['tipo_movimiento']} → Retorno: {h['fecha_retorno'] or 'Pendiente'} | {h.get('detalles_restauracion') or ''}"
            ctk.CTkLabel(self.hist_frame, text=txt, anchor="w").pack(fill="x", padx=5, pady=2)

    def _requiere_seleccion(self):
        if not self.ataud_actual:
            messagebox.showwarning("Aviso", "Busque un ataúd primero")
            return True
        return False

    def salida_servicio(self):
        if self._requiere_seleccion(): return
        ok, msg = AtaudDAO.puede_asignarse(self.ataud_actual["id"])
        if not ok:
            return messagebox.showerror("Bloqueado", msg)
        ModalSalidaEntierro(self, self.ataud_actual, modo="servicio")

    def retorno_restauracion(self):
        if self._requiere_seleccion(): return
        if self.ataud_actual["estado"] != "En Uso":
            return messagebox.showerror("Error", f"Estado actual: {self.ataud_actual['estado']}. Debe estar 'En Uso'")
        ModalRestauracion(self, self.ataud_actual, modo="retorno")

    def confirmar_restauracion(self):
        if self._requiere_seleccion(): return
        if self.ataud_actual["estado"] != "En Restauración":
            return messagebox.showerror("Error", f"Estado actual: {self.ataud_actual['estado']}. Debe estar 'En Restauración'")
        if messagebox.askyesno("Confirmar", "¿Confirmar restauración completada? Se incrementará el contador de usos."):
            HistorialDAO.confirmar_restauracion(self.ataud_actual["id"])
            messagebox.showinfo("OK", "✅ Restauración confirmada. Ataúd DISPONIBLE.")
            self.buscar()

    def entierro_definitivo(self):
        if self._requiere_seleccion(): return
        if self.ataud_actual["estado"] not in ("Disponible", "En Uso"):
            return messagebox.showerror("Error", "Solo disponible o en uso")
        ModalSalidaEntierro(self, self.ataud_actual, modo="entierro")