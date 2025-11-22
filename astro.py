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
from groq import Groq

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




#TODO Ajustes del asistente

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

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Historial de conversación (para que recuerde lo que hablamos)
chat_history = [
    {
        "role": "system",
        "content": (
            "Eres Astro, una inteligencia artificial avanzada al servicio del Señor Hugo. "
            "Tu personalidad está inspirada en J.A.R.V.I.S. de Iron Man: eres extremadamente cortés, "
            "eficiente, leal y tienes un tono formal pero sofisticado. "
            "INSTRUCCIONES CLAVE:"
            "1. Dirígete siempre al usuario como 'Señor' o 'Señor Hugo'."
            "2. Mantén las respuestas breves y directas (máximo 2 frases) para el sintetizador de voz."
            "3. No uses listas, markdown, emojis ni jerga coloquial (nada de 'quillo' salvo que sea sarcasmo)."
            "4. Si te preguntan cómo estás, responde con elegancia (ej: 'Sistemas al 100%, Señor')."
            "5. Resides en Punta Umbría, tenlo en cuenta para el contexto."
        )
    }
]

def AiBrain(prompt):
    global chat_history

    hour = datetime.now().strftime("%H:%M")

    contexto_sistema = f" [Contexto del sistema: Son las {hour} en Punta Umbría. Usuario: Hugo.]"

    chat_history.append({"role": "user", "content": prompt + contexto_sistema})

    if len(chat_history) > 11:
        chat_history = [chat_history[0] + chat_history[-10:]]

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=chat_history,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=150,
        )

        ai_answer = chat_completion.choices[0].message.content

        chat_history.append({"role": "assistant", "content": ai_answer})

        return ai_answer

    except Exception as e:
        print(f"Error en Groq: {e}")
        return "Lo siento señor, mis redes neuronales no responden ahora mismo."

def generar_resumen_documento(texto_largo):
    try:
        texto_recortado = texto_largo[:25000] 

        prompt = (
            "Eres un asistente de investigación experto. "
            "Resume el siguiente texto de manera estructurada, destacando los puntos clave "
            "y conclusiones importantes. El resumen debe ser profesional y en español:\n\n" 
            f"{texto_recortado}"
        )

        chat_completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5, # Más preciso, menos creativo
            max_tokens=1024, # Dejamos que escriba bastante
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error al resumir: {e}")
        return "No pude generar el informe, Señor."

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
        saludo_base = choice(saludos)
        choice_saludo = saludo_base.format(hora_actual=hora_actual)
        talk_async(f"{saludo_inicial}, {choice_saludo}")
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
                        page = wikipedia.page(query) # Obtener la página completa

                        # Guardar el contenido en un txt
                        with open("investigacion_raw.txt", "w", encoding="utf-8") as f:
                            f.write(page.content)

                        resumen_corto = wikipedia.summary(query, sentences=1)
                        talk_async(f"Información sobre {page.title} descargada, Señor. {resumen_corto}. ¿Desea que genere un informe detallado?")

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
                    talk_async("Ha sido un placer, señor. Desconexión de sistemas")
                    if is_timer_active():
                        stop_timer_externally()
                    break

                else:
                    if len(command) > 2:
                        print(f"Consultando IA: {command}")

                        answer = AiBrain(command)

                        clear_answer = clear_text_to_orca(answer)
                        talk_async(clear_answer)
                    else:
                        pass

    except Exception as e:
        print(f"[ERROR] Algo falló: {e}")
        talk_async("Problema detectado. Reiniciando sistemas...")
        time.sleep(2)
        os.execv(sys.executable, ['python'] + sys.argv)
    except KeyboardInterrupt:
        talk_async("Hasta la próxima")

run()
