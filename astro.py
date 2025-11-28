from datetime import datetime
import requests
import pywhatkit as kit
import subprocess
import psutil
from dotenv import load_dotenv
import sys
import os
import ctypes
import json
import time
import difflib
import unicodedata
from random import choice
import wikipedia
import pyautogui
import keyboard
import traceback

#TODO: Importaciones de archivos
from spotify_manager import (
                                spotify_my_list, spotify_play, spotify_pause, 
                                spotify_next, spotify_previous, spotify_search_song, 
                                spotify_get_volume, spotify_set_volume
                            )
from timer_tool import parse_duration_string, stop_timer_externally, is_timer_active, start_thread
from system_config import (
                            AiBrain, generar_resumen_documento,
                            talk_async, listen, listen_keyword,
                            clear_text_to_orca, memory_manager,
                            delete_memory
                            )
from security import security, server


#################################################################################################################!


# Importar variables
load_dotenv()
VBOXMANAGE = os.getenv("VBOXMANAGE")
VM_NAME = os.getenv("VM_NAME")
api_key = os.getenv("WEATHER_KEY")

# Variables de configuración
stop = False

# Tiempour atmosférico
def weather(ciudad):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key}&units=metric&lang=es"

    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()
        datos_clima = respuesta.json()

        if respuesta.status_code == 200:
            temperatura = datos_clima['main']['temp']
            descripcion = datos_clima['weather'][0]['description']
            humedad = datos_clima['main']['humidity']
            return f"El clima en {ciudad} es {descripcion}, con una temperatura de {temperatura}°C, y una humedad del {humedad}%."

        else:
            return "No se ha podio obtener el clima. Inténtalo luego quillo."
    except requests.exceptions.RequestException as e:
        return f"Quillo que ha surgío un error. Este es el error {e}"



def searchYoutube(query):
    global stop
    stop = False
    talk_async(f"Repoduciendo {query} en Youtube")
    kit.playonyt(query)


def app_init(app_name):
    def is_app_running():
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and app_name.lower() in proc.info['name'].lower():
                talk_async("Ya está abierto")
                return True
        return False

    if is_app_running():
        return

    try:
        with open("rutas_apps.json", "r", encoding="utf-8") as f:
            rutas = json.load(f)
    except Exception as e:
        talk_async("No he podido cargar el archivo de las aplicaciones.")
        print("json:", e)
        return

    name_app = unicodedata.normalize('NFD', app_name)
    name_app_good = ''.join((c for c in name_app if unicodedata.category(c) != 'Mn'))
    condience = difflib.get_close_matches(name_app_good.lower(), rutas.keys(), n=1, cutoff=0.4)

    if condience:
        new_app = condience[0]
        ruta = rutas[new_app]

    if new_app in rutas:
        if new_app == "grabadora de pantalla":
            OBS_DIR = os.path.dirname(ruta)
            subprocess.Popen(ruta, cwd=OBS_DIR)
        elif new_app == "google":
            subprocess.Popen([ruta, "--profile-directory=Default"])
        elif new_app == "servidor":
            talk_async("Abriendo el servidor...")
            time.sleep(2)
            server(ruta, talk_async)
        else:
            subprocess.Popen(ruta)
        talk_async(f"Abriendo {new_app}")
    else:
        talk_async(f"Todavía no tengo acceso a {new_app} señor.")


def start_kali():
    try:
        subprocess.run(
            [VBOXMANAGE, "startvm", VM_NAME, "--type", "gui"],
            check=True
        )
    except subprocess.CalledProcessError:
        talk_async("No se ha podido iniciar Kali Linux señor. Le muestro el error en pantalla.")
        print(f"No se pudo iniciar la VM «{VM_NAME}».", file=sys.stderr)
        sys.exit(1)


def guardar_resumen():
    if os.path.exists("investigacion_raw.txt"):
        talk_async("Procesando datos, Señor. Esto tomará unos segundos...")

        # 1. Leer el archivo bruto
        with open("investigacion_raw.txt", "r", encoding="utf-8") as f:
            contenido = f.read()

        # 2. Pedir a la IA que lo resuma
        resumen_ia = generar_resumen_documento(contenido)

        # 3. Guardar el resumen limpio
        with open("resumen_final.txt", "w", encoding="utf-8") as f:
            f.write(f"INFORME GENERADO POR ASTRO\nFECHA: {datetime.now()}\n\n{resumen_ia}")

        talk_async("El informe ha sido generado y guardado en su carpeta de documentos, Señor.")

        # Abrir el archivo automáticamente para que lo veas
        os.startfile("resumen_final.txt") 
    else:
        talk_async("No hay ninguna investigación pendiente para resumir, Señor.")


saludos = [
    "Señor. Todos los sistemas están operativos.",
    "Señor. Listo para las instrucciones del día.",
    "Señor. Todos los sistemas se encuentran en óptimo estado",
    "Sistemas en línea, Señor. La hora actual en Punta Umbría es {hora_actual}. ¿Hay alguna instrucción pendiente?",
    "Operativo, Señor. La configuración es óptima y estoy listo para sus comandos. Son las {hora_actual}",
    "Señor Hugo. Bienvenido. La hora es {hora_actual}. ¿En qué puedo asistirle hoy?"
]

def saludo(hora_actual=None):
    franjas = {
        "buenos días": (6, 12),  # 6 AM a 12 PM
        "buenas tardes": (12, 20),  # 12 PM a 8 PM
        "buenas noches": (20, 6)  # 8 PM a 6 AM
    }

    if hora_actual is None:
        hora_actual = datetime.now().hour

    # Buscar la franja horaria adecuada
    for saludo, (inicio, fin) in franjas.items():
        # Verificar si la hora actual está dentro del rango de la franja
        if (inicio <= hora_actual < fin) or (fin < inicio and (hora_actual >= inicio or hora_actual < fin)):
            return saludo

    return "Hora no válida"


def periodoDia(hora=None):
    if hora is None:
        hora = datetime.now().hour

    if 6 <= hora < 12:
        return "de la mañana"
    elif 12 <= hora < 20:
        return "de la tarde"
    else:
        return "de la noche"


def system_status():
    print("analizando...")
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    print("analizando...")

    if cpu > 85 or ram > 85:
        estado_general = "Atención, Señor. Los niveles de consumo son elevados."
    else:
        estado_general = "Todos los sistemas funcionan dentro de los parámetros normales."

    mensaje = (f"Informe de estado: La carga de la CPU es del {cpu} por ciento. "
                f"El uso de memoria RAM es del {ram} por ciento."
                f"{estado_general}")

    time.sleep(5)
    talk_async(mensaje)

def open_work(name):
    ruta_base = r"C:\Users\elpaj\Documents"
    ruta_proyecto = os.path.join(ruta_base, name)

    os.makedirs(ruta_proyecto, exist_ok=True)

    subprocess.run(["code", ruta_proyecto], shell=True)


#!######      BUCLE PRINCIPAL      ######!#
def run():
    try:
        hora_actual = datetime.now().strftime("%H:%M")
        saludo_inicial = saludo()
        saludo_final = periodoDia()
        saludo_base = choice(saludos)
        choice_saludo = saludo_base.format(hora_actual=hora_actual)
        talk_async(f"{saludo_inicial}, {choice_saludo}")
        rec = ""

        while True:
            #! Esperar palabra clave
            listen_keyword()

            time.sleep(2.5)

            rec = listen()
            if not rec:
                time.sleep(2)
                continue

            elif rec:
                command = rec.lower()

                #TODO Búsqueda en Youtube
                if 'reproduce' in command:
                    query = command.replace("astro reproduce", "").strip()
                    while True:
                        if query == "":
                            talk_async("No has dicho nada. ¿Qué quieres que reproduzca en youtube?")
                            time.sleep(3)
                            query = listen()
                            if query != "":
                                break
                        else:
                            break
                    searchYoutube(query)

                #TODO Tiempo atmosférico
                elif 'qué tiempo' in command:
                    ciudad = "Punta Umbría"
                    resultado_clima = weather(ciudad)
                    talk_async(resultado_clima)

                #TODO Búsqueda en la web
                elif any(word in command for word in ["buscar", "búscame", "investiga", "averigua",
                                                    "encuentra", "qué es", "quién es", "qué significa"]):

                    wikipedia.set_lang("es")

                    query = (command
                            .replace("buscar", "")
                            .replace("búscame", "")
                            .replace("investiga", "")
                            .replace("averigua", "")
                            .replace("encuentra", "")
                            .replace("qué es", "")
                            .replace("quién es", "")
                            .replace("qué significa", "")
                            .replace("en la wikipedia", "")
                            .replace("en wikipedia", "")
                            .replace("en google", "")
                            .replace(" un ", " ")
                            .replace(" sobre ", " ")
                            .replace("sobre la", "")
                            .replace(" que ", "")
                            .replace(" qué ", "")
                            .replace(" sabes ", "")
                            .strip())

                    if not query:
                        talk_async("¿Qué desea saber?")
                        time.sleep(1.5)
                        query = listen().strip()
                        if not query:
                            talk_async("No le he entendido señor")
                            continue

                    try:
                        page = wikipedia.page(query) # Obtener la página completa

                        # Guardar el contenido en un txt
                        with open("investigacion_raw.txt", "w", encoding="utf-8") as f:
                            f.write(page.content)

                        resumen_corto = wikipedia.summary(query, sentences=1)
                        talk_async(f"Información sobre {page.title} descargada, Señor. {resumen_corto}. ¿Desea que genere un informe detallado?")

                        time.sleep(3)

                        summary = listen().strip()
                        if "si" in summary or "sí" in summary:
                            guardar_resumen()
                        else:
                            talk_async("Entendido")

                    except wikipedia.exceptions.DisambiguationError as e:
                        talk_async(f"Hay varios temas con ese nombre, Señor. Sea más específico.")
                    except Exception as e:
                        print(e)
                        talk_async("No pude acceder a la base de datos, Señor.")

                elif "genera un informe" in command or "haz un resumen del texto" in command:
                    guardar_resumen()

                #TODO: Spotify
                elif "pon spotify" in command or "pon música" in command:
                    talk_async("Reproduciendo The Best...")
                    spotify = spotify_my_list(talk_async)

                elif "sigue la música" in command or "continúa la música" in command:
                    talk_async("Reproduciendo...")
                    spotify = spotify_play(talk_async)

                elif "para la música" in command or "pon la música en pausa" in command:
                    talk_async("Parando la música...")
                    spotify = spotify_pause(talk_async)

                elif "pasa la canción" in command or "siguiente canción" in command:
                    talk_async("Pasando a la siguiente canción...")
                    spotify = spotify_next(talk_async)

                elif "canción anterior" in command:
                    talk_async("Volviendo...")
                    spotify = spotify_previous(talk_async)

                elif "pon la canción" in command or "busca la canción" in command:
                    if "pon la canción" in command:
                        query = command.replace("pon la canción", "").strip()
                    elif "busca la canción" in command:
                        query = command.replace("busca la canción", "").strip()

                    spotify = spotify_search_song(query, talk_async)

                elif "sube el volumen" in command:
                    original = spotify_get_volume(talk_async)
                    spotify = spotify_set_volume(original + 10, talk_async)

                elif "baja el volumen" in command or "baja la voz" in command:
                    original = spotify_get_volume(talk_async)
                    spotify = spotify_set_volume(original - 10, talk_async)


                #TODO: Kali linux
                elif "kali" in command or "cali" in command:
                    acceso = security(talk_async, listen)
                    if acceso:
                        talk_async("Abriendo Kali linux...")
                        start_kali()
                    else:
                        talk_async("Acceso denegado.")


                #TODO: Temporizador
                elif "para el temporizador" in command or "quita el temporizador" in command:
                    if stop_timer_externally():
                        talk_async("Parando temporizador.")
                    else:
                        talk_async("No hay ningún temporizador activo.")

                elif "temporizador" in command or "cuenta atrás" in command:
                    if is_timer_active():
                        talk_async("Ya hay un temporizador en marcha.")
                        continue

                    duration = parse_duration_string(command)

                    if duration is not None and duration > 0:
                        talk_async(f"Ejecutando temporizador de {int(duration)} segundos")
                        timer = start_thread(duration)
                        if not timer:
                            talk_async("Ya hay un temporizador en marcha.")
                    else:
                        talk_async("La entrada no ha podido ejecutarse correctamente. Inténtalo de nuevo.")


                #TODO: Preguntas
                elif "Estás ahí" in command or "estás despierto" in command:
                    talk_async("Para usted siempre Señor")


                #TODO: Sistema
                elif "vamos a trabajar" in command:
                    talk_async("Estoy preparando el entorno...")
                    app_init(app_name="visual studio")
                    time.sleep(0.5)
                    spotify_my_list(talk_async)
                    time.sleep(0.5)
                    app_init(app_name="google")

                elif "estado del sistema" in command or "informe del sistema" in command:
                    talk_async("Analizando telemetría del sistema señor...")
                    system_status()

                elif any(word in command for word in ["nuevo proyecto", "inicia el proyecto",
                                                    "abre el proyecto"]):
                    if "abre el proyecto" in command:
                        name = command.replace("abre el proyecto ", "")

                        open_work(name=name)

                    else:
                        talk_async("¿Cómo desea llamar la carpeta, señor?")

                        time.sleep(4)

                        name = listen()

                        if name:
                            name = name.replace(" ", "_")
                            open_work(name=name)

                elif any(word in command for word in ["abre", "accede",
                                                    "acceso", "inicia"]):
                    app = (command
                            .replace(" el ", "")
                            .replace("accede al", "")
                            .replace("acceso al", "")
                            .replace("inicia", "")
                            .replace("abre", "").strip())
                    app_init(app_name=app)


                #TODO Interacción con memoria
                elif "recuerda que" in command or "guarda en tu memoria que" in command:
                    memory_text = (command
                                    .replace("recuerda que", "")
                                    .replace("guarda en tu memoria que", "")
                                    .strip())

                    if memory_text:
                        talk_async(f"Guardando en mi base de datos: {memory_text}")
                        memory_manager(new_memory=memory_text)
                    else:
                        talk_async("¿Qué es lo que quieres que recuerde, señor?")

                elif any(word in command for word in ["qué tienes en tu memoria", "léeme tu memoria",
                                                    "qué sabes de mi"]):
                    datos = memory_manager()
                    if "No tengo recuerdos" in datos:
                        talk_async("Mi base de datos de recuerdos está vacía, Señor.")
                    else:
                        talk_async("Accediendo a los registros encriptados...")
                        clear_dates = datos.replace("[", "").replace("]", " del ")
                        talk_async(f"Esto es lo que tengo guardado: {clear_dates}")

                elif any(word in command for word in ["borra tu memoria", "formatea tu memoria",
                                                    "elimina tu memoria"]):
                    talk_async("Advertencia. Señor, está a punto de eliminar" \
                                "permanentemente todos los datos de mi memoria" \
                                "¿Desea continuar?")

                    time.sleep(6.5)

                    confirmacion = listen()

                    if any(word in confirmacion for word in ["sí", "si", "hazlo", "procede"]):
                        if delete_memory():
                            talk_async("Memoria formateada. Todos los datos han sido eliminados exitosamente.")
                        else:
                            talk_async("Ha ocurrido un error al eliminar los datos de mi memoria señor.")
                    else:
                        talk_async("Cancelando protocolo de borrado")


                #TODO: Despedida
                elif 'adiós' in command:
                    talk_async("Ha sido un placer, señor. Desconexión de sistemas")
                    if is_timer_active():
                        stop_timer_externally()
                    break

                #TODO Uso de AI
                else:
                    if len(command) > 2:
                        print(f"Consultando IA: {command}")

                        answer = AiBrain(command)

                        clear_answer = clear_text_to_orca(answer)
                        talk_async(clear_answer)
                    else:
                        pass

    except Exception as e:
        traceback.print_exc()
        print(f"[ERROR] Algo falló: {e}")
        talk_async("Problema detectado. Reiniciando sistemas...")
        input("Presiona ENTER para salir y ver el error...")
    except KeyboardInterrupt:
        talk_async("Hasta la próxima")


if __name__ == "__main__":
    run()
    print("\nScript cerrado\n")
