import speech_recognition as sr
from datetime import datetime
from dotenv import load_dotenv
import os
from word2number import w2n
import time
import threading
import unicodedata
import pvporcupine
import pyaudio
import struct
import pvorca
from pydub import AudioSegment, effects
from pydub.playback import play
from random import choice
from groq import Groq
import json
from deep_translator import GoogleTranslator
import re
from ddgs import DDGS
from pynput import keyboard
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from base64 import b64encode
from mss import mss, tools
import pygetwindow as gw
from PIL import Image
from pynput import mouse
from pathlib import Path
import pystray
from PIL import Image

# ! Semaforo para controlar el audio
audio_lock = threading.Lock()
stop_audio_event = threading.Event()
# ! Detectar teclado para habilitar el micro
mic_unlock_event = threading.Event()
keyboard_listener = None

# Importar variables
load_dotenv()
access_key = os.getenv("ACCESS_KEY")
keyword_path = os.getenv("KEYWORD_PATH")
model_path = os.getenv("MODEL_PATH")
model_path_2 = os.getenv("MODEL_PATH_2")
gemini_key = os.getenv("GEMINI_API_KEY")
MEMORY_FILE = r"json files//astro_memory.json"
PROMT_FILE_GEMINI = r"json files//system_prompts//gemini_prompts.json"
PROMT_FILE_LLAMA = r"json files//system_prompts//llama_prompts.json"
SCREENSHOT_NAME = "screenshot.png"

# ! Cargar gemini-2.5-flash para reducir tiempo de espera al analizar código
gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", temperature=0.7, google_api_key=gemini_key
)


def memory_manager(new_memory=None):
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"memories": []}

    else:
        data = {"memories": []}

    if new_memory:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        data["memories"].append(f"[{timestamp}] {new_memory}")

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True

    else:
        if not data["memories"]:
            return "No tengo recuerdos previos."
        return "\n".join(data["memories"])


def delete_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            os.remove(MEMORY_FILE)
            global chat_history
            chat_history = [chat_history[0]]
            return True
        except Exception as e:
            print(f"Error al borrar memoria: {e}")
            return False
    else:
        return True


def get_information(query):
    try:
        print(f"--- BUSCANDO EN INTERNET: {query} ---")
        results = DDGS().text(query, max_results=3)
        if results:
            summary = ""
            for res in results:
                summary += f"- Título: {res['title']}\n \
                            Resumen: {res['body']}\n"
                print(summary)
            return summary
        return "No se han encontrado datos en internet"
    except Exception as e:
        print(f"Error de búsqueda: {e}")
        return "Error al intentar buscar en internet"


def screenshot_screen(type):
    file_path = Path(SCREENSHOT_NAME)

    if file_path.exists():
        os.remove(file_path)
    else:
        pass

    # TODO: Hacer captura de pantalla de VScode
    if type == "CODE":
        # ! Buscar VScode por el título
        windows = gw.getWindowsWithTitle("Visual Studio Code")
        if windows:
            vscode = windows[0]
            # ! Definir coordenadas de VScode
            x, y = vscode.left, vscode.top
            ancho, alto = vscode.width, vscode.height

            with mss() as sct:
                monitor = {"top": y, "left": x, "width": ancho, "height": alto}
                screenshot = sct.grab(monitor)
                Image.frombytes("RGB", screenshot.size, screenshot.rgb).save(
                    SCREENSHOT_NAME
                )

    elif type == "SCREEN":
        controller = mouse.Controller()
        x, y = controller.position
        print(f"Posición del mouse: ({x}, {y})")

        with mss() as sct:
            monitor_encontrado = None
            indice_monitor = None

            for i, monitor in enumerate(sct.monitors[1:], start=1):
                if (
                    monitor["left"] <= x < monitor["left"] + monitor["width"]
                    and monitor["top"] <= y < monitor["top"] + monitor["height"]
                ):
                    monitor_encontrado = monitor
                    indice_monitor = i
                    break

            if monitor_encontrado:
                print(f"✓ Mouse en Monitor {indice_monitor}: {monitor_encontrado}")

                screenshot = sct.grab(monitor_encontrado)
                tools.to_png(screenshot.rgb, screenshot.size, output=SCREENSHOT_NAME)

                print(f"✓ Captura guardada: {SCREENSHOT_NAME}")
                print(f"  Resolución: {screenshot.width}x{screenshot.height}")
            else:
                print("✗ No se pudo detectar el monitor")


groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def load_llama_prompt():
    if os.path.exists(PROMT_FILE_LLAMA):
        with open(PROMT_FILE_LLAMA, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return " ".join(data.get("llama_system_prompt", []))
            except (json.JSONDecodeError, KeyError):
                print("[Error] No se ha podido leer el system-prompt de llama.")
    return "Eres astro, un asistente cortés."


system_prompt = load_llama_prompt()

# Historial de conversación
chat_history = [
    {
        "role": "system",
        "content": system_prompt,
    }
]


def AiBrain(prompt):
    global chat_history

    hour = datetime.now().strftime("%H:%M")

    long_memory = memory_manager()

    contexto_sistema = (
        f" [Contexto del sistema: Son las {hour} en Punta Umbría. Usuario: Hugo. "
        f"DATOS QUE RECUERDAS SOBRE EL USUARIO: {long_memory}]"
    )

    chat_history.append({"role": "user", "content": prompt + contexto_sistema})

    if len(chat_history) > 11:
        chat_history = [chat_history[0]] + chat_history[-10:]

    try:
        # ! Cargar modelo llama-3.3-70b-versatile
        chat_completion = groq_client.chat.completions.create(
            messages=chat_history,
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            max_tokens=200,
            timeout=10,
        )

        # ! Generar respuesta
        ai_answer = chat_completion.choices[0].message.content

        # TODO: Búsqueda en internet
        # ! Buscar la etiqueta [SEARCH] en la respuesta generada
        search_web = re.search(r"\[SEARCH:(.*?)\]", ai_answer)

        # ? Si se encuentra la etiqueta [SEARCH]
        if search_web:
            # ! Buscar la información faltante
            query = search_web.group(1).strip()
            web_results = get_information(query=query)

            # ! Añadir los resultados de la búsqueda al historial
            chat_history.append(
                {
                    "role": "system",
                    "content": f"RESULTADOS DE BÚSQUEDA WEB PARA '{query}':\n{web_results}\n"
                    "Instrucción: Usa esta información para responder "
                    "a la pregunta original del usuario. "
                    "Sé breve y natural, como si ya lo supieras.",
                }
            )

            # ! Volver a cargar llama-3.3-70b-versatile pero esta vez con el nuevo historial
            chat_completion_2 = groq_client.chat.completions.create(
                messages=chat_history,
                model="llama-3.3-70b-versatile",
                temperature=0.6,
                max_tokens=200,
                timeout=10,
            )

            # ! Generar respuesta
            ai_answer = chat_completion_2.choices[0].message.content

        # TODO: Añadir nuevo recuerdo a la memoria
        memory_pattern = r"\[MEMORY:(.*?)\]"  # ! Etiqueta a buscar [MEMORY]
        match = re.search(
            memory_pattern, ai_answer
        )  # ! Buscar la etiqueta en la respuesta generada

        # ? Si se encuentra la etiqueta [MEMORY]
        if match:
            # ! Seleccionar el contenido del mensaje, excluyendo la etiqueta
            new_memory_content = match.group(1).strip()

            # ! Añadir el nuevo recuerdo a la memoria
            print(f">>>> DETECTADO NUEVO RECUERDO: {new_memory_content}")
            memory_manager(new_memory=new_memory_content)

            # ! Guardar Respuesta final
            ai_answer = re.sub(memory_pattern, "", ai_answer).strip()

        # TODO: Usar Gemini en lugar de Llama
        memory_pattern = r"\[GEMINI\]"  # ! Etiqueta a buscar [GEMINI]
        gem = re.search(
            memory_pattern, ai_answer
        )  # ! Buscar la etiqueta en la respuesta generada

        # ? Si se encuentra la etiqueta [GEMINI]
        if gem:
            try:
                llama_answer_content = ai_answer.replace("[GEMINI]", "").strip()

                # ! Informar del uso de Gemini
                print("Se ha empezado a utilizar Gemini...")

                # ! Definir Prompt
                with open(PROMT_FILE_GEMINI, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # ! Segunda parte del prompt
                gem_prompt = (
                    "IMPORTANTE: "
                    "1. Máximo 300 palabras. "
                    "2. NO uses markdown (nada de *, **, #, ```, -, etc.). "
                    "3. NO incluyas bloques de código. "
                    "4. Habla en lenguaje natural, como si estuvieras hablando directamente. "
                    "5. Si necesitas mencionar código, descríbelo con palabras. "
                    "Responde como JARVIS: elegante, breve y directo."
                )

                # ! Verificar petición del usuario
                if "CODE" in llama_answer_content:
                    # ! Crear prompt completo
                    gem_prompt_complete = data["type_prompt"]["code"] + gem_prompt
                    # ! Crear captura de VSCode
                    screenshot_screen("CODE")

                elif "SCREEN" in llama_answer_content:
                    # ! Crear prompt completo
                    gem_prompt_complete = data["type_prompt"]["screen"] + gem_prompt
                    # ! Crear captura de la pantalla en donde se encuentra el mouse
                    screenshot_screen("SCREEN")
                else:
                    talk_async(
                        "Lo siento señor, pero estoy teniendo problemas con mi sistema neuronal."
                    )
                    return

                # ! Abrir captura de la pantalla correspondiente
                with open(SCREENSHOT_NAME, "rb") as img:
                    img_bs64 = b64encode(img.read()).decode()

                # ! Crear el prompt para Gemini
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": gem_prompt_complete},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/png;base64,{img_bs64}",
                        },
                    ]
                )

                # ! Generar respuesta con Gemini
                response = gemini.invoke([message])
                ai_answer = response.content
                # ! Eliminar captura
                try:
                    os.remove(SCREENSHOT_NAME)
                except FileNotFoundError:
                    pass

                # ! Si la respuesta es demasiado larga, resumir con llama
                if len(ai_answer) > 1900:
                    print(
                        "[BRAIN] Respuesta de Gemini"
                        f"demasiado larga ({len(ai_answer)} chars). Resumiendo..."
                    )
                    # ! Prompt para generar el nuevo resumen
                    resumen_prompt = (
                        f"Resume lo siguiente en un MÁXIMO de 3 frases cortas y directas, "
                        f"manteniendo el tono J.A.R.V.I.S./Astro: {ai_answer}"
                    )

                    # ! Volver a cargar llama con su nuevo prompt para generar el resumen
                    generate_gem_resumen = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": resumen_prompt}],
                        temperature=0.5,
                        max_tokens=150,
                    )

                    ai_answer = generate_gem_resumen.choices[0].message.content
                    print(f"[RESUMEN] {ai_answer}")
            except Exception as e:
                print(f"Error en Gemini: {e}")
                return "Lo siento señor, pero gemini no está respondiendo debido a un error"

        chat_history.append(
            {"role": "assistant", "content": ai_answer}
        )  # ! Añadir respuesta final al historial
        return ai_answer  # ! Enviar respuesta final

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
            temperature=0.5,  # Más preciso, menos creativo
            max_tokens=1024,  # Dejamos que escriba bastante
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
]


orca = pvorca.create(access_key=access_key, model_path=model_path_2)


def hablar_orca(
    texto,
    tono=1.55,
    velocidad=1.0,
    volumen=1.0,
    eco=False,
    reverb=False,
    robot=False,
    suavizar=True,
):
    with audio_lock:
        stop_audio_event.clear()
        try:
            if not texto:
                return

            result = orca.synthesize(texto)
            if not result or len(result) < 2:
                print("[Orca] Error: síntesis vacía o inválida.")
                return

            audio_samples, sample_rate = result

            if isinstance(audio_samples, list):
                audio_bytes = struct.pack(
                    "<" + ("h" * len(audio_samples)), *audio_samples
                )
            else:
                audio_bytes = audio_samples

            try:
                sample_rate = (
                    int(sample_rate[0])
                    if isinstance(sample_rate, (list, tuple))
                    else int(sample_rate)
                )
            except Exception:
                sample_rate = 16000

            # Intentar mono, si falla, estéreo
            try:
                audio = AudioSegment(
                    data=audio_bytes, sample_width=2, frame_rate=sample_rate, channels=1
                )
            except Exception:
                audio = AudioSegment(
                    data=audio_bytes, sample_width=2, frame_rate=sample_rate, channels=2
                )

            # ajustes de voz
            if tono != 1.0:
                audio = audio._spawn(
                    audio.raw_data,
                    overrides={"frame_rate": int(audio.frame_rate * tono)},
                ).set_frame_rate(sample_rate)
            if velocidad != 1.0:
                audio = audio.speedup(playback_speed=velocidad)
            if volumen != 0.0:
                audio += volumen
            if suavizar:
                audio = effects.normalize(audio)

            if stop_audio_event.is_set():
                return

            play(audio)

        except Exception as e:
            print(f"[ERROR] Orca al hablar: {e}")


def talk(text):
    text = clear_text_to_orca(text=text)
    hablar_orca(text, tono=1.55, velocidad=1, volumen=1)


def talk_async(text):
    # if threading.active_count() < 2:
    text = clear_text_to_orca(text=text)
    threading.Thread(target=talk, args=(text,), daemon=True).start()


def word_to_number(text):
    palabras = text.split()
    out = []

    for p in palabras:
        try:
            out.append(
                str(
                    w2n.word_to_num(
                        GoogleTranslator(source="es", target="en").translate(p)
                    )
                )
            )
        except Exception:
            out.append(p)

    return " ".join(out)


def clear_text_to_orca(text):
    text = "".join(c for c in text if unicodedata.category(c)[0] != "C")

    text = text.replace("\ufeff", "").replace("\u200b", "")

    return text


def listen():
    # if audio_lock.locked():
    #    time.sleep(0.2)

    rec = ""
    try:
        with sr.Microphone() as source:
            # winsound.Beep(550, 125)
            listener.pause_threshold = 0.5
            listener.non_speaking_duration = 0.4
            listener.phrase_threshold = 0.3
            listener.energy_threshold = 400
            print("\n\nEscuchando...\n\n")
            voice = listener.listen(source, timeout=5, phrase_time_limit=12)

        rec = listener.recognize_google(voice, language="es-ES").lower()
        try:
            rec = word_to_number(rec)
        except Exception:
            pass
        print(rec)

    except sr.WaitTimeoutError:
        pass
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print("Error al conectar con el servicio de reconocimiento de voz.")

    return rec


def init_micro():
    with sr.Microphone() as source:
        print("[!] Calibrando ruido de fondo")
        listener.adjust_for_ambient_noise(source, duration=1)
        listener.dynamic_energy_threshold = True


def listen_keyword():
    porcupine = None
    pa = None
    stream = None
    choice_saludo = None

    try:
        porcupine = pvporcupine.create(
            access_key=access_key, keyword_paths=[keyword_path], model_path=model_path
        )  # puedes cambiar a otro hotword
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )

        print("\n\nEsperando palabra clave\n\n")

        try:
            keyword_detected = False
            while not keyword_detected:
                try:
                    pcm = stream.read(
                        porcupine.frame_length, exception_on_overflow=False
                    )
                    pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)
                    keyword_index = porcupine.process(pcm_unpacked)

                    if keyword_index >= 0:
                        stop_audio_event.set()
                        choice_saludo = choice(saludos_activacion)
                        keyword_detected = True
                except OSError as e:
                    print("[Audio Error]:", e)
                    time.sleep(0.5)
                    continue

        except KeyboardInterrupt:
            print("Detenido por el usuario.")

    except Exception as e:
        print(f"[Porcupine Error]: {e}")

    finally:
        if stream is not None:
            stream.close()
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()
        if choice_saludo:
            talk_async(choice_saludo)


def wait_for_mic_unlock():
    mic_unlock_event.clear()
    print("[SISTEMA] Micrófono silenciado")

    def on_activate():
        print("Reactivando micrófono...")
        mic_unlock_event.set()

    hotkeys = {"<ctrl>+<shift>+m": on_activate, "<ctrl>+<shift>+M": on_activate}

    with keyboard.GlobalHotKeys(hotkeys=hotkeys):
        mic_unlock_event.wait()

    return True


def setup_stray():
    image = Image.open("astro_icon.png")

    def on_quit(icon, item):
        icon.stop()
        os._exit(0)

    menu = pystray.Menu(
        pystray.MenuItem("Estado: Operativo", lambda: None, enabled=False),
        pystray.MenuItem("Cerrar Astro", on_quit)
    )

    icon = pystray.Icon("Astro", image, "Astro AI", menu)
    icon.run()
