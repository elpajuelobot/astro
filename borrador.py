#import flet
#from flet import Page, TextField, ElevatedButton, Column, Text, Colors
#
#def main(page: Page):
#    page.title = "Astro"
#    page.bgcolor = Colors.BLUE_GREY_900
#    page.theme_mode = "dark"
#    input_box = TextField(label="Escribe tu mensaje",
#                            border_color=Colors.BLUE_200,
#                            focused_border_color=Colors.BLUE_400,
#                            text_style=flet.TextStyle(color=Colors.WHITE)
#                            )
#    chat_area = Column()
#
#    def send_message(e):
#        user_message = input_box.value
#        chat_area.controls.append(Text(f"Usuario: {user_message}", color=Colors.WHITE))
#        user_message = user_message.lower()
#
#        if "hola" in user_message:
#            response = "Adios tonto"
#        elif "clima" in user_message:
#            response = "Que te importa"
#        else:
#            response = "Eres un inutil"
#
#        chat_area.controls.append(Text(f"Chatbot: {response}", color=Colors.WHITE))
#        input_box.value = ""
#        page.update()
#
#    send_button = ElevatedButton(text="Enviar",
#                                    on_click=send_message,
#                                    bgcolor=Colors.BLUE_700,
#                                    color=Colors.WHITE
#                                )
#
#    page.add(input_box, send_button, chat_area)
#
#flet.app(target=main)
