import customtkinter as ctk
from ui.dashboard import DashboardView
from ui.inventario import InventarioView
from ui.registro import RegistroView
from ui.control_ciclo import ControlCicloView
from web.server import iniciar_servidor_web

class App(ctk.CTkFrame):
    def __init__(self, parent, usuario, on_logout_callback):
        super().__init__(parent)
        self.usuario = usuario
        self.on_logout_callback = on_logout_callback
        self.pack(fill="both", expand=True)
        
        parent.title(f"Sistema de Ataúdes — {usuario['nombre_completo']} ({usuario['rol']})")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Layout: Sidebar (col 0) + Contenido (col 1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="🏛️ ATAÚDES", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 30))

        menus = [
            ("📊 Dashboard", self.mostrar_dashboard),
            ("📦 Inventario", self.mostrar_inventario),
            (" Registro / Edición", self.mostrar_registro),
            ("🔄 Control de Ciclo", self.mostrar_control_ciclo),
        ]
        for texto, cmd in menus:
            ctk.CTkButton(self.sidebar, text=texto, command=cmd, anchor="w", height=40).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(self.sidebar, text="🌓 Cambiar Tema", command=self.toggle_tema).pack(side="bottom", padx=10, pady=10)
        ctk.CTkButton(self.sidebar, text=" Cerrar Sesión", command=self.cerrar_sesion, fg_color="#c0392b", hover_color="#a93226").pack(side="bottom", padx=10, pady=10)

        # Contenedor de vistas
        self.contenedor = ctk.CTkFrame(self, corner_radius=0)
        self.contenedor.grid(row=0, column=1, sticky="nsew")
        self.contenedor.grid_columnconfigure(0, weight=1)
        self.contenedor.grid_rowconfigure(0, weight=1)

        # Iniciar servidor web
        try:
            iniciar_servidor_web()
        except Exception as e:
            print(f"️ Servidor web no iniciado: {e}")

        self.mostrar_dashboard()

    def limpiar_contenedor(self):
        for w in self.contenedor.winfo_children():
            w.destroy()

    def mostrar_dashboard(self):
        self.limpiar_contenedor()
        DashboardView(self.contenedor).pack(fill="both", expand=True)

    def mostrar_inventario(self):
        self.limpiar_contenedor()
        InventarioView(self.contenedor, self).pack(fill="both", expand=True)

    def mostrar_registro(self, ataud_editar=None):
        self.limpiar_contenedor()
        RegistroView(self.contenedor, self, ataud_editar).pack(fill="both", expand=True)

    def mostrar_control_ciclo(self):
        self.limpiar_contenedor()
        ControlCicloView(self.contenedor).pack(fill="both", expand=True)

    def toggle_tema(self):
        actual = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if actual == "Dark" else "dark")

    def _limpiar_todo(self):
        """Destruye TODOS los widgets hijos antes de destruir el frame."""
        # Destruir todos los widgets del contenedor
        for w in self.contenedor.winfo_children():
            w.destroy()
        
        # Destruir todos los widgets del sidebar
        for w in self.sidebar.winfo_children():
            w.destroy()
        
        # Quitar el sidebar y contenedor del grid
        self.sidebar.grid_forget()
        self.contenedor.grid_forget()

    def cerrar_sesion(self):
        from tkinter import messagebox
        if messagebox.askyesno("Salir", "¿Está seguro de que desea cerrar sesión?"):
            # ✅ LIMPIEZA TOTAL antes de destruir
            self._limpiar_todo()
            # Forzar actualización visual
            self.update_idletasks()
            # Llamar al callback de logout
            self.on_logout_callback()