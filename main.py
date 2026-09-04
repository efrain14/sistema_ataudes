import customtkinter as ctk
from database.schema import inicializar_bd
from ui.login import LoginWindow
from ui.app import App


def iniciar_app():
    inicializar_bd()
    def on_login_ok(usuario):
        app = App(usuario)
        app.mainloop()
    login = LoginWindow(on_login_ok)
    login.mainloop()


if __name__ == "__main__":
    iniciar_app()