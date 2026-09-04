import customtkinter as ctk
from tkinter import messagebox
from database.daos import HistorialDAO

class ModalRestauracion(ctk.CTkToplevel):
    def __init__(self, parent, ataud, modo="retorno"):
        super().__init__(parent)
        self.parent_view = parent
        self.ataud = ataud
        self.title("Bitácora de Restauración")
        self.geometry("500x400")
        self.grab_set()

        ctk.CTkLabel(self, text=f"🔄 Retorno: {ataud['codigo_qr']}", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        ctk.CTkLabel(self, text="Detalle los trabajos de limpieza, desinfección y/o reparación:").pack(padx=20, anchor="w")

        self.txt_detalles = ctk.CTkTextbox(self, width=450, height=150)
        self.txt_detalles.pack(padx=20, pady=10)

        ctk.CTkLabel(self, text="Responsable:").pack(padx=20, anchor="w")
        self.entry_resp = ctk.CTkEntry(self, width=450)
        self.entry_resp.pack(padx=20, pady=5)

        ctk.CTkButton(self, text="💾 Guardar Retorno", command=self.guardar, height=40).pack(pady=20)

    def guardar(self):
        detalles = self.txt_detalles.get("1.0", "end").strip()
        resp = self.entry_resp.get().strip()
        if not detalles or not resp:
            return messagebox.showwarning("Aviso", "Complete todos los campos")
        HistorialDAO.registrar_retorno_restauracion(self.ataud["id"], detalles, resp)
        messagebox.showinfo("OK", "✅ Retorno registrado. Estado: En Restauración")
        self.destroy()
        self.parent_view.buscar()