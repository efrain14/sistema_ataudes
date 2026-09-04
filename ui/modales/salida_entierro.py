import customtkinter as ctk
from tkinter import messagebox
from database.daos import HistorialDAO

class ModalSalidaEntierro(ctk.CTkToplevel):
    def __init__(self, parent, ataud, modo="servicio"):
        super().__init__(parent)
        self.parent_view = parent
        self.ataud = ataud
        self.modo = modo
        titulo = "⚰️ Entierro Definitivo" if modo == "entierro" else "🚚 Salida a Servicio"
        self.title(titulo)
        self.geometry("500x350")
        self.grab_set()

        ctk.CTkLabel(self, text=f"{titulo}: {ataud['codigo_qr']}", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        ctk.CTkLabel(self, text="Destino / Servicio / Cementerio:").pack(padx=20, anchor="w")
        self.entry_destino = ctk.CTkEntry(self, width=450)
        self.entry_destino.pack(padx=20, pady=5)

        ctk.CTkLabel(self, text="Observaciones:").pack(padx=20, anchor="w")
        self.txt_obs = ctk.CTkTextbox(self, width=450, height=100)
        self.txt_obs.pack(padx=20, pady=5)

        if modo == "entierro":
            ctk.CTkLabel(self, text="⚠️ El ataúd NO retornará al inventario", text_color="red").pack(pady=5)

        ctk.CTkButton(self, text="💾 Registrar", command=self.guardar, height=40,
                      fg_color="#c0392b" if modo == "entierro" else "#e67e22").pack(pady=20)

    def guardar(self):
        destino = self.entry_destino.get().strip()
        obs = self.txt_obs.get("1.0", "end").strip()
        if not destino:
            return messagebox.showwarning("Aviso", "Indique el destino")
        if self.modo == "entierro":
            if messagebox.askyesno("Confirmar", "¿Confirmar entierro definitivo? El ataúd se dará de baja."):
                HistorialDAO.registrar_salida_entierro_definitivo(self.ataud["id"], destino, obs)
                messagebox.showinfo("OK", "✅ Entierro registrado. Ataúd DADO DE BAJA.")
                self.destroy()
                self.parent_view.buscar()
        else:
            HistorialDAO.registrar_salida_servicio(self.ataud["id"], destino, "Operador")
            messagebox.showinfo("OK", "✅ Salida registrada. Estado: En Uso.")
            self.destroy()
            self.parent_view.buscar()