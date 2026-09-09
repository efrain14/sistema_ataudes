import customtkinter as ctk
from database.schema import inicializar_bd
from ui.login import LoginModal
from ui.app import App

def iniciar_app():
    inicializar_bd()
    
    # Creamos la ventana principal primero (pero oculta o esperando)
    app = App(None) # Pasamos None inicialmente
    
    # Función que se ejecuta al loguearse exitosamente
    def on_login_success(usuario):
        app.usuario = usuario
        app.title(f"Sistema de Ataúdes — {usuario['nombre_completo']} ({usuario['rol']})")
        # Aquí podrías actualizar la UI si es necesario
    
    # Mostramos el modal de login
    login = LoginModal(app, on_login_success)
    
    # Iniciamos el bucle principal. Si el login se cancela, la app se cierra.
    app.mainloop()

if __name__ == "__main__":
    iniciar_app()