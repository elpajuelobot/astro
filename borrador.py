"""
import os
from getpass import getpass
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Obtener API key (solo necesitas hacerlo una vez)

# Modelos gratuitos disponibles:
# - "gemini-1.5-flash" (más rápido, recomendado para el plan gratuito)
# - "gemini-1.5-pro" (más potente pero con límites más estrictos)
# - "gemini-pro" (versión anterior)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Modelo gratuito más eficiente
    temperature=0.7,
    google_api_key="AIzaSyC6geFvfhQv6K-a-Psqob_ZA7q7CXAIjSA"
)

# Prompt con historial
prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente útil y amigable."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Crear la cadena
chain = prompt | llm

# Almacén de historiales por sesión
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Cadena con memoria
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# Función para chatear
def chat(mensaje):
    response = chain_with_history.invoke(
        {"input": mensaje},
        config={"configurable": {"session_id": "mi_sesion"}}
    )
    return response.content

# Ejemplo de uso
if __name__ == "__main__":
    print("Chat iniciado. Escribe 'salir' para terminar.\n")
    
    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() in ['salir', 'exit', 'quit']:
            print("¡Hasta luego!")
            break
        
        respuesta = chat(pregunta)
        print(f"Asistente: {respuesta}\n")



# AIzaSyC6geFvfhQv6K-a-Psqob_ZA7q7CXAIjSA

import json

with open("gemini_prompts.json", "r", encoding="utf-8") as prompt_gem:
    data = json.load(prompt_gem)

gem_prompt = (
    "NO te alargues mucho. No utilices símbolos como los * u otros"
    "para poner las palabras en negrita o cosas así por el estilo."
)

gem_prompt_complete = data['type_prompt']['code'] + gem_prompt

print(gem_prompt_complete)
"""


from mss import mss, tools
import pygetwindow as gw
from PIL import Image

ventanas = gw.getWindowsWithTitle('Visual Studio Code')

if ventanas:
    ventana = ventanas[0]

    x, y = ventana.left, ventana.top
    ancho, alto = ventana.width, ventana.height

    with mss() as sct:
        monitor = {"top": y, "left": x, "width": ancho, "height": alto}
        screenshot = sct.grab(monitor)
        Image.frombytes("RGB", screenshot.size, screenshot.rgb).save("vscode.png")




#with mss() as sct:
#    for i, monitor in enumerate(sct.monitors):
#        print(f"Monitor {i}: {monitor}")
#
#    hello = int(input("\n\nElije tonto\n"))
#
#    screenshot = sct.grab(sct.monitors[hello])
#    tools.to_png(screenshot.rgb, screenshot.size, output="screenshot.png")







