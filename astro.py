import speech_recognition as sr
import pyttsx3 as pt3
from datetime import datetime
import requests
import pywhatkit as kit
import subprocess
import webbrowser
import psutil
from dotenv import load_dotenv
import sys
import os
from word2number import w2n
import ctypes
import pyautogui
import json
import time
import threading
import difflib
import unicodedata
import pvporcupine
import pyaudio
import struct
import pvorca
from pydub import AudioSegment, effects
from pydub.playback import play
from random import choice
import wikipedia
import string

#TODO: Importaciones de archivos
from spotify_manager import (
                                spotify_my_list, spotify_play, spotify_pause, 
                                spotify_next, spotify_previous, spotify_search_song, 
                                spotify_get_volume, spotify_set_volume
                            )
from timer_tool import parse_duration_string, stop_timer_externally, is_timer_active, start_thread


#################################################################################################################!


# Importar variables
load_dotenv()
VBOXMANAGE = os.getenv("VBOXMANAGE")
VM_NAME = os.getenv("VM_NAME")
api_key = os.getenv("WEATHER_KEY")
secret_key = os.getenv("CLAVE")
access_key = os.getenv("ACCESS_KEY")
keyword_path = os.getenv("KEYWORD_PATH")
model_path = os.getenv("MODEL_PATH")
model_path_2 = os.getenv("MODEL_PATH_2")

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


def lock_windows_pc():
    ctypes.windll.user32.LockWorkStation()


def security():
    for i in range(4):
        talk_async("Introduzca código de seguridad para acceder")

        code = listen()

        if code == secret_key:
            talk_async("Accediendo...")
            return True
        else:
            talk_async(f"Código introducido incorrecto.")
            time.sleep(1.3)

        if i == 4:
            talk_async("Bloqueando sistema.")
            time.sleep(1.5)
            lock_windows_pc()
            return False

def reboot_pc(command):
    command = command.lower()

    if "cierra" in command or "cerrar" in command:
        talk_async("Las ventanas solo se ocultarán.")
        pyautogui.hotkey('win', 'd')
        return

    time.sleep(2)

    if "reinicia" in command or "reiniciar" in command:
        os.startfile(r"C:\Users\elpaj\Documents\Astro\reboot.lnk")
    elif "apaga" in command or "apagar" in command:
        os.startfile(r"C:\Users\elpaj\Documents\Astro\shutdown.lnk")


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


#TODO Ajustes del asistente
name = "astro"
listener = sr.Recognizer()
saludos_activacion = [
    "Dime",  
    "¿Qué necesita, señor?",  
    "Le escucho",  
    "Aquí estoy",  
    "Preparado para ayudar",  
    "¿Sí, Hugo?",  
    "Adelante",  
    "¿Qué ordena?",  
    "Listo y operativo",  
    "A sus órdenes",  
    "¿Qué desea saber?",  
    "Estoy escuchando",  
    "Activo y esperando instrucciones",  
    "¿Qué hay que hacer?",  
    "Diga, jefe",
    "Ya estoy aquí",
    "¿Otra misión, señor?",
    "Procesando energía… listo.",
    "Configuración óptima, ¿qué sigue?"
]


orca = pvorca.create(
    access_key=access_key,
    model_path=model_path_2
    )

def hablar_orca(texto, tono=1.55, velocidad=1.0, volumen=1.0,
                eco=False, reverb=False, robot=False, suavizar=True):
    try:
        if not texto:
            return

        result = orca.synthesize(texto)
        if not result or len(result) < 2:
            print("[Orca] Error: síntesis vacía o inválida.")
            return

        audio_samples, sample_rate = result

        if isinstance(audio_samples, list):
            audio_bytes = struct.pack('<' + ('h' * len(audio_samples)), *audio_samples)
        else:
            audio_bytes = audio_samples

        try:
            sample_rate = int(sample_rate[0]) if isinstance(sample_rate, (list, tuple)) else int(sample_rate)
        except Exception:
            sample_rate = 16000

        # Intentar mono, si falla, estéreo
        try:
            audio = AudioSegment(data=audio_bytes, sample_width=2, frame_rate=sample_rate, channels=1)
        except Exception:
            audio = AudioSegment(data=audio_bytes, sample_width=2, frame_rate=sample_rate, channels=2)

        # ajustes de voz
        if tono != 1.0:
            audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * tono)}).set_frame_rate(sample_rate)
        if velocidad != 1.0:
            audio = audio.speedup(playback_speed=velocidad)
        if volumen != 0.0:
            audio += volumen
        if suavizar:
            audio = effects.normalize(audio)

        play(audio)

    except Exception as e:
        print(f"[ERROR] Orca al hablar: {e}")

def talk(text):
    hablar_orca(text, tono=1.55, velocidad=1, volumen=1)

def talk_async(text):
    if threading.active_count() < 2:
        threading.Thread(target=talk, args=(text,), daemon=True).start()

def word_to_number(text):
    words = text.split()
    result = []

    for i in range(len(words)):
        try:
            num = w2n.word_to_num(words[i])
            result.append(str(num))
        except:
            result.append(words[i])

    return ' '.join(result)

def clear_text_to_orca(text):
    permitido = string.ascii_letters + string.digits + string.punctuation + " áéíóúñÁÉÍÓÚÑ"
    return ''.join(c for c in text if c in permitido or unicodedata.category(c).startswith('Z'))

def listen():
    rec = ""
    try:
        with sr.Microphone() as source:
            listener.adjust_for_ambient_noise(source, duration=1)
            print("\n\nEscuchando...\n\n")
            voice = listener.listen(source, timeout=10, phrase_time_limit=10)

        rec = listener.recognize_google(voice, language='es-ES').lower()
        try:
            rec = word_to_number(rec)
        except:
            pass
        print(rec)

    except sr.WaitTimeoutError as e:
        print(f"\nTiempo de espera agotado: {e}\n")
        return ""
    except sr.UnknownValueError:
        return ""  # No se pudo entender lo que dijiste
    except sr.RequestError:
        print("Error al conectar con el servicio de reconocimiento de voz.")
        pass
    return rec

def listen_keyword():
    porcupine = pvporcupine.create(
        access_key=access_key,
        keyword_paths=[keyword_path],
        model_path=model_path
        )  # puedes cambiar a otro hotword
    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    try:
        keyword_detected = False
        while not keyword_detected:
            try:
                pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)
                keyword_index = porcupine.process(pcm_unpacked)

                if keyword_index >= 0:
                    talk_async(choice(saludos_activacion))
                    keyword_detected = True
            except OSError as e:
                print("[Audio Error]:", e)
                time.sleep(0.5)
                continue

    except KeyboardInterrupt:
        print("Detenido por el usuario.")
    finally:
        stream.close()
        pa.terminate()
        porcupine.delete()


def run():
    try:
        hora_actual = datetime.now().strftime("%H:%M")
        saludo_inicial = saludo()
        saludo_final = periodoDia()
        talk_async(f"{saludo_inicial} Hugo, son las {hora_actual} minutos {saludo_final}")
        rec = ""

        while True:
            #! Esperar palabra clave
            listen_keyword()

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
                            .strip())

                    if not query:
                        talk_async("¿Qué desea saber?")
                        query = listen().strip()
                        if not query:
                            talk_async("No le he entendido señor")
                            continue

                    try:
                        page_title = wikipedia.search(query, results=1)
                        if not page_title:
                            talk_async(f"No he coseguido encontrar información en la wikipedia. Aquí te dejo la búsqueda")
                            webbrowser.open(f"https://www.google.com/search?q={query}")
                            continue

                        summary = wikipedia.summary(page_title[0], sentences=2)
                        clear_text = clear_text_to_orca(f"{page_title[0]}. {summary}")
                        talk_async(clear_text)

                    except wikipedia.exceptions.DisambiguationError as e:
                        talk_async(f"He encontrado varios resultados que podrían interesarle señor, por ejemplo: {', '.join(e.options[:3])}")
                    except wikipedia.exceptions.PageError:
                        talk_async(f"No he conseguido encontrar resultados válidos sobre {query}, señor")
                    except Exception as e:
                        print("[Wikipedia Error]:", e)
                        talk_async("No he conseguido conectarme con wikipedia señor")

                #TODO: Spotify
                elif "mi lista" in command:
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
                    acceso = security()
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
                #elif any(word in command for word in ["reiniciar", "reinicia", "apagar", "apaga", "cierra", "cerrar"]):
                #    acceso = security()
                #    if acceso:
                #        talk_async("Preparando el ordenador")
                #        time.sleep(1.5)
                #        reboot_pc(command)
                #    else:
                #        talk_async("Acceso denegado")

                elif "abre" in command or "inicia" in command:
                    if "abre" in command:
                        app = command.replace("abre", "").strip()
                    else:
                        app = command.replace("inicia", "").strip()

                    app_init(app_name=app)

                elif "vamos a trabajar" in command:
                    talk_async("Estoy preparando el entorno...")
                    app_init(app_name="visual studio")
                    time.sleep(0.5)
                    spotify_my_list(talk_async)
                    time.sleep(0.5)
                    app_init(app_name="google")


                #TODO: Despedida
                elif 'adiós' in command:
                    talk_async("¡Hasta luego quillo!")
                    if is_timer_active():
                        stop_timer_externally()
                    break

                else:
                    talk_async("No te he entendido")

    except Exception as e:
        print(f"[ERROR] Algo falló: {e}")
        talk_async("Problema detectado. Reiniciando sistemas...")
        time.sleep(2)
        os.execv(sys.executable, ['python'] + sys.argv)
    except KeyboardInterrupt:
        talk_async("Hasta la próxima")

run()
