import customtkinter as ctk
import sys
from database.schema import inicializar_bd
from ui.login import LoginModal
from ui.app import App

def iniciar_app():
    # 1. Inicializar base de datos
    inicializar_bd()
    
    # 2. Crear la ventana principal
    app = App(usuario=None)
    
    # Ocultar la ventana principal hasta que el usuario se loguee
    app.withdraw() 
    
    # 3. Función que se ejecuta cuando el login es exitoso
    def on_login_success(usuario):
        app.usuario = usuario
        app.actualizar_titulo_usuario()
        app.deiconify() # Mostrar la ventana principal
        app.mostrar_dashboard() # Cargar el dashboard
        
    # 4. Mostrar el modal de login
    login = LoginModal(app, on_login_success)
    
    # 5. Iniciar el bucle principal
    app.mainloop()

if __name__ == "__main__":
    iniciar_app()