import customtkinter as ctk
from ui.dashboard import DashboardView
from ui.inventario import InventarioView
from ui.registro import RegistroView
from ui.control_ciclo import ControlCicloView
from web.server import iniciar_servidor_web
from ui.login import LoginModal

class App(ctk.CTk):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario
        
        if self.usuario is not None:
            nombre = self.usuario.get('nombre_completo', 'Usuario')
            rol = self.usuario.get('rol', 'Rol')
            self.title(f"Sistema de Ataúdes — {nombre} ({rol})")
        else:
            self.title("Sistema de Ataúdes — Iniciando sesión...")
            
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

        ctk.CTkLabel(self.sidebar, text="️ ATAÚDES", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 30))

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

        # Toggle tema y Cerrar Sesión
        ctk.CTkButton(self.sidebar, text="🌓 Cambiar Tema", command=self.toggle_tema).pack(side="bottom", padx=10, pady=10)
        ctk.CTkButton(self.sidebar, text="🚪 Cerrar Sesión", command=self.cerrar_sesion, fg_color="#c0392b", hover_color="#a93226").pack(side="bottom", padx=10, pady=10)

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
            print(f"️ Servidor web no iniciado: {e}")

        # Cargar dashboard por defecto
        self.mostrar_dashboard()

    def actualizar_titulo_usuario(self):
        """Actualiza el título de la ventana una vez que el usuario se loguea."""
        if self.usuario:
            nombre = self.usuario.get('nombre_completo', 'Usuario')
            rol = self.usuario.get('rol', 'Rol')
            self.title(f"Sistema de Ataúdes — {nombre} ({rol})")

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
        if messagebox.askyesno("Salir", "¿Está seguro de que desea cerrar sesión?"):
            # En lugar de destruir la ventana, la ocultamos
            self.withdraw() 
            self.usuario = None
            
            # Función para cuando vuelva a loguearse
            def on_login_success(usuario):
                self.usuario = usuario
                self.actualizar_titulo_usuario()
                self.deiconify() # Volver a mostrar la ventana
                self.mostrar_dashboard()
                
            # Mostrar el login de nuevo
            login = LoginModal(self, on_login_success)