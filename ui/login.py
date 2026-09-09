import customtkinter as ctk
from tkinter import messagebox
from database.daos import UsuarioDAO

class LoginModal(ctk.CTkToplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.title("Iniciar Sesión")
        self.geometry("420x360")
        self.resizable(False, False)
        
        # Hacer modal (bloquea la ventana principal hasta cerrarse)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancelar) # Si cierra con la X, se cierra la app

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="🏛️ SISTEMA DE ATAÚDES", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, pady=(30, 5))
        ctk.CTkLabel(self, text="Control de Inventario y Trazabilidad", text_color="gray").grid(row=1, column=0, pady=(0, 30))

        ctk.CTkLabel(self, text="Usuario:").grid(row=2, column=0, padx=60, sticky="w")
        self.entry_user = ctk.CTkEntry(self, width=300, placeholder_text="admin")
        self.entry_user.grid(row=3, column=0, padx=60, pady=5)
        self.entry_user.focus()

        ctk.CTkLabel(self, text="Contraseña:").grid(row=4, column=0, padx=60, sticky="w")
        self.entry_pass = ctk.CTkEntry(self, width=300, show="*", placeholder_text="••••••")
        self.entry_pass.grid(row=5, column=0, padx=60, pady=5)
        self.entry_pass.bind("<Return>", lambda e: self.login())

        self.btn = ctk.CTkButton(self, text="Iniciar Sesión", command=self.login, height=40)
        self.btn.grid(row=6, column=0, padx=60, pady=20)

        ctk.CTkLabel(self, text="Usuario por defecto: admin / admin123", text_color="gray", font=ctk.CTkFont(size=11)).grid(row=7, column=0)

    def login(self):
        u = self.entry_user.get().strip()
        p = self.entry_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Aviso", "Complete todos los campos", parent=self)
            return
        user = UsuarioDAO.autenticar(u, p)
        if user:
            self.on_success(user)
            self.destroy() # Se cierra limpiamente sin errores de "after"
        else:
            messagebox.showerror("Error", "Credenciales inválidas", parent=self)
            self.entry_pass.delete(0, "end")
            self.entry_pass.focus()

    def cancelar(self):
        self.destroy()
        # Si se cierra el login, cerramos toda la aplicación
        self.master.destroy()