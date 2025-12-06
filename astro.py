from datetime import datetime
import requests
import pywhatkit as kit
import subprocess
import psutil
from dotenv import load_dotenv
import sys
import os
import json
import time
import difflib
import unicodedata
from random import choice
import traceback

# TODO: Importaciones de archivos
from timer_tool import stop_timer_externally, is_timer_active
from system_config import (
                            generar_resumen_documento,
                            talk_async, listen, listen_keyword,
                            )
from security import server
from handlers import AstroBrain


# Importar variables
load_dotenv()
VBOXMANAGE = os.getenv("VBOXMANAGE")
VM_NAME = os.getenv("VM_NAME")
api_key = os.getenv("WEATHER_KEY")

# Variables de configuración
stop = False


# Tiempo atmosférico
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
            return f"El clima en {ciudad} es {descripcion}, con una \
                temperatura de {temperatura}°C, y una humedad del {humedad}%."

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
            if (proc.info['name'] and app_name.lower()
                    in proc.info['name'].lower()):

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
    name_app_good = ''.join((c for c in name_app
                            if unicodedata.category(c) != 'Mn'))
    condience = difflib.get_close_matches(
                                        name_app_good.lower(),
                                        rutas.keys(), n=1, cutoff=0.4)

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
        elif new_app == "visual studio":
            subprocess.run("code", shell=True)
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
        talk_async("No se ha podido iniciar Kali Linux señor. \
                    Le muestro el error en pantalla.")
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
            f.write(f"INFORME GENERADO POR ASTRO\nFECHA: \
                    {datetime.now()}\n\n{resumen_ia}")

        talk_async("El informe ha sido generado y guardado \
                    en su carpeta de documentos, Señor.")

        # Abrir el archivo automáticamente para que lo veas
        os.startfile("resumen_final.txt")
    else:
        talk_async("No hay ninguna investigación \
                    pendiente para resumir, Señor.")


saludos = [
    "Señor. Todos los sistemas están operativos.",
    "Señor. Listo para las instrucciones del día.",
    "Señor. Todos los sistemas se encuentran en óptimo estado",
    "Sistemas en línea, Señor. La hora actual en Punta Umbría es \
        {hora_actual}. ¿Hay alguna instrucción pendiente?",
    "Operativo, Señor. La configuración es óptima y estoy listo \
        para sus comandos. Son las {hora_actual}",
    "Señor Hugo. Bienvenido. La hora es {hora_actual}. \
        ¿En qué puedo asistirle hoy?"
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
        if ((inicio <= hora_actual < fin) or
                (fin < inicio and (hora_actual >= inicio
                or hora_actual < fin))):

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
        estado_general = "Atención, Señor. \
            Los niveles de consumo son elevados."
    else:
        estado_general = "Todos los sistemas funcionan \
            dentro de los parámetros normales."

    mensaje = (
                "Informe de estado:"
                f"La carga de la CPU es del {cpu} por ciento. "
                f"El uso de memoria RAM es del {ram} por ciento."
                f"{estado_general}")

    time.sleep(5)
    talk_async(mensaje)


def open_work(name):
    ruta_base = r"C:\Users\elpaj\Documents"
    ruta_proyecto = os.path.join(ruta_base, name)

    os.makedirs(ruta_proyecto, exist_ok=True)

    subprocess.run(["code", ruta_proyecto], shell=True)


# !######      BUCLE PRINCIPAL      ######! #
def run():
    try:
        hora_actual = datetime.now().strftime("%H:%M")
        saludo_inicial = saludo()
        saludo_base = choice(saludos)
        choice_saludo = saludo_base.format(hora_actual=hora_actual)
        talk_async(f"{saludo_inicial}, {choice_saludo}")
        rec = ""

        # Configurar los handlers de Astro
        astro = AstroBrain(talk_async, listen)
        functions = {
            "start_kali": start_kali,
            "open_work": open_work,
            "app_init": app_init,
            "system_status": system_status,
            "guardar_resumen": guardar_resumen,
            "searchYoutube": searchYoutube,
            "weather": weather
        }

        while True:
            # ! Esperar palabra clave
            listen_keyword()

            time.sleep(2.5)

            rec = listen()
            if not rec:
                time.sleep(2)
                continue

            elif rec:
                command = rec.lower()

                if 'adiós' in command:
                    talk_async("Ha sido un placer, señor. \
                                Desconexión de sistemas")
                    if is_timer_active():
                        stop_timer_externally()
                    time.sleep(5)
                    break

                astro.process_command(command, **functions)

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
