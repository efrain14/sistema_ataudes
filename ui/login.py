import customtkinter as ctk
from tkinter import messagebox
from database.daos import UsuarioDAO

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.usuario = None  # Se guardará aquí si el login es exitoso
        self.title("Iniciar Sesión - Sistema de Ataúdes")
        self.geometry("420x360")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")

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
            messagebox.showwarning("Aviso", "Complete todos los campos")
            return
        user = UsuarioDAO.autenticar(u, p)
        if user:
            self.usuario = user  # Guardar usuario
            self.destroy()       # ✅ Cerrar ventana de login
        else:
            messagebox.showerror("Error", "Credenciales inválidas")
            self.entry_pass.delete(0, "end")
            self.entry_pass.focus()