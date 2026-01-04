import flet as ft

def main(page: ft.Page):
        def window_event(e):
            if e.data == "close":
                pass

        def habilitar_micro(e):
            page.window.destroy()

        page.title = ""
        page.window.width = 200
        page.window.height = 200
        page.window.min_width = 200
        page.window.min_height = 200
        page.window.max_width = 200
        page.window.max_height = 200
        page.window.center()
        page.window.resizable = False
        page.window.maximizable = False
        page.window.prevent_close = True
        page.on_window_event = window_event
        page.theme_mode = ft.ThemeMode.DARK
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.vertical_alignment = ft.CrossAxisAlignment.CENTER
        page.horizontal_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        page.add(
                ft.Text("Micro silenciado", size=20),
                ft.FloatingActionButton(
                    on_click=habilitar_micro,
                    icon=ft.Icons.MIC_OFF
                    )
        )


ft.app(target=main)
