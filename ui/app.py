import customtkinter as ctk
from ui.dashboard import DashboardView
from ui.inventario import InventarioView
from ui.registro import RegistroView
from ui.control_ciclo import ControlCicloView
from web.server import iniciar_servidor_web

class App(ctk.CTk):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.title(f"Sistema de Ataúdes — {usuario['nombre_completo']} ({usuario['rol']})")
        self.geometry("1280x780")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Layout: sidebar + contenido
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="🏛️ ATAÚDES", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 30))

        self.botones_menu = []
        menus = [
            ("📊 Dashboard", self.mostrar_dashboard),
            ("📦 Inventario", self.mostrar_inventario),
            ("➕ Registro / Edición", self.mostrar_registro),
            ("🔄 Control de Ciclo", self.mostrar_control_ciclo),
        ]
        for texto, cmd in menus:
            b = ctk.CTkButton(self.sidebar, text=texto, command=cmd, anchor="w", height=40)
            b.pack(fill="x", padx=10, pady=5)
            self.botones_menu.append(b)

        # Toggle tema
        ctk.CTkButton(self.sidebar, text="🌓 Cambiar Tema", command=self.toggle_tema).pack(side="bottom", padx=10, pady=10)
        ctk.CTkButton(self.sidebar, text="🚪 Cerrar Sesión", command=self.cerrar_sesion, fg_color="red", hover_color="darkred").pack(side="bottom", padx=10, pady=10)

        # Contenedor de vistas
        self.contenedor = ctk.CTkFrame(self, corner_radius=0)
        self.contenedor.grid(row=0, column=1, sticky="nsew")
        self.contenedor.grid_columnconfigure(0, weight=1)
        self.contenedor.grid_rowconfigure(0, weight=1)

        self.vistas = {}
        self.vista_actual = None

        # Iniciar servidor web para escaneo móvil
        try:
            iniciar_servidor_web()
        except Exception as e:
            print(f"⚠️ Servidor web no iniciado: {e}")

        self.mostrar_dashboard()

    def limpiar_contenedor(self):
        for w in self.contenedor.winfo_children():
            w.destroy()
        self.vista_actual = None

    def mostrar_dashboard(self):
        self.limpiar_contenedor()
        v = DashboardView(self.contenedor)
        v.pack(fill="both", expand=True)
        self.vista_actual = v

    def mostrar_inventario(self):
        self.limpiar_contenedor()
        v = InventarioView(self.contenedor, self)
        v.pack(fill="both", expand=True)
        self.vista_actual = v

    def mostrar_registro(self, ataud_editar=None):
        self.limpiar_contenedor()
        v = RegistroView(self.contenedor, self, ataud_editar)
        v.pack(fill="both", expand=True)
        self.vista_actual = v

    def mostrar_control_ciclo(self):
        self.limpiar_contenedor()
        v = ControlCicloView(self.contenedor)
        v.pack(fill="both", expand=True)
        self.vista_actual = v

    def toggle_tema(self):
        actual = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if actual == "Dark" else "dark")

    def cerrar_sesion(self):
        from tkinter import messagebox
        if messagebox.askyesno("Salir", "¿Cerrar sesión?"):
            self.destroy()
            from main import iniciar_app
            iniciar_app()