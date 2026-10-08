import customtkinter as ctk
import sys
from database.schema import inicializar_bd
from ui.login import LoginWindow
from ui.app import App

def iniciar_app():
    inicializar_bd()
    
    # 1. Una sola ventana principal para toda la vida de la aplicación
    root = ctk.CTk()
    root.title("Sistema de Ataúdes")
    root.geometry("1280x780")
    root.withdraw() # Oculta la ventana principal al inicio
    
    app_frame = None # Referencia al marco del dashboard

    # 2. Qué hacer cuando el login es exitoso
    def on_login_success(usuario):
        nonlocal app_frame
        root.deiconify() # Muestra la ventana principal
        # Crea el dashboard y lo inserta en la ventana principal
        app_frame = App(root, usuario, on_logout)
        app_frame.pack(fill="both", expand=True)

    # 3. Qué hacer al cerrar sesión - CIERRA TODA LA APLICACIÓN
    def on_logout():
        nonlocal app_frame
        if app_frame:
            app_frame.pack_forget()
            app_frame.destroy()
            app_frame = None
        
        # ✅ Cerrar toda la aplicación en lugar de mostrar login
        root.destroy()
        sys.exit(0)

    # 4. Mostrar el login inicial
    LoginWindow(root, on_login_success)
    
    # 5. Iniciar el bucle principal
    root.mainloop()

if __name__ == "__main__":
    iniciar_app()