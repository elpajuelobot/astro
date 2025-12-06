import time
import ctypes
from dotenv import load_dotenv
import os
import subprocess
import flet as ft
import pyautogui
import winsound

load_dotenv()

secret_key = os.getenv("CLAVE")
password = os.getenv("PASSWORD_SERVER")


def lock_windows_pc():
    ctypes.windll.user32.LockWorkStation()


def security(talk_async, listen):
    for i in range(4):
        talk_async("Introduzca código de seguridad para acceder")

        time.sleep(2.5)

        code = listen()

        if code == secret_key:
            talk_async("Accediendo...")
            return True
        else:
            talk_async("Código introducido incorrecto.")
            time.sleep(1.3)

        if i == 4:
            talk_async("Bloqueando sistema.")
            time.sleep(1.5)
            lock_windows_pc()
            return False


def server(ruta, talk_async):
    talk_async("Señor, debe introducir la contraseña \
                para poder acceder al servidor")
    time.sleep(4)
    winsound.MessageBeep()

    def main(page: ft.Page):
        page.title = "Acceso seguridad - Astro Security"
        page.window.width = 400
        page.window.height = 250
        page.window.center()
        page.window.resizable = False
        page.theme_mode = ft.ThemeMode.DARK
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.vertical_alignment = ft.CrossAxisAlignment.CENTER

        def verificar_password(e):
            if password_input.value == password:
                # Si la clave es correcta
                page.snack_bar = ft.SnackBar(
                    ft.Text("Acceso concedido. Abriendo servidor...")
                    )
                page.snack_bar.open = True
                page.update()

                # Abrir el acceso directo
                try:
                    subprocess.Popen(ruta, shell=True)
                    time.sleep(4)
                    pyautogui.write(password)
                    time.sleep(1)
                    pyautogui.press("enter")

                except Exception as ex:
                    print(f"Error al abrir la ruta: {ex}")

                # Cerrar la ventana de Flet
                page.window.close()
            else:
                password_input.error_text = "Clave incorrecta"
                password_input.update()

        # Campo de texto
        password_input = ft.TextField(
            label="Clave de seguridad",
            password=True,
            can_reveal_password=True,
            width=300,
            on_submit=verificar_password,
            autofocus=True
        )

        # Botón de confirmación
        submit_btn = ft.ElevatedButton(
            text="Acceder",
            on_click=verificar_password,
            icon="lock_open"
        )

        page.add(
            ft.Text(
                "Autenticación requerida", size=20, weight=ft.FontWeight.BOLD
                ),
            password_input,
            submit_btn
        )

    ft.app(target=main)
