import customtkinter as ctk
from database.schema import inicializar_bd
from ui.login import LoginWindow
from ui.app import App


def iniciar_app():
    inicializar_bd()
    
    # Crear ventana de login y esperar a que se cierre
    login = LoginWindow()
    login.mainloop()  # Bloquea aquí hasta que el usuario cierre el login
    
    # Si el login fue exitoso, self.usuario tendrá datos
    if login.usuario:
        app = App(login.usuario)
        app.mainloop()
    else:
        print("❌ Login cancelado o fallido. Saliendo...")


if __name__ == "__main__":
    iniciar_app()