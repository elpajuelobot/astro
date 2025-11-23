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
import string
from groq import Groq
import json
from deep_translator import GoogleTranslator
import re
from ddgs import DDGS

#! Semaforo para controlar el audio
audio_lock = threading.Lock()

# Importar variables
load_dotenv()
access_key = os.getenv("ACCESS_KEY")
keyword_path = os.getenv("KEYWORD_PATH")
model_path = os.getenv("MODEL_PATH")
model_path_2 = os.getenv("MODEL_PATH_2")
MEMORY_FILE = "astro_memory.json"


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
                summary += f"- Título: {res['title']}\n Resumen: {res['body']}\n"
                print(summary)
            return summary
        return "No se han encontrado datos en internet"
    except Exception as e:
        print(f"Error de búsqueda")
        return "Error al intentar buscar en internet"


groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Historial de conversación
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
            "6. GESTIÓN DE MEMORIA (ESTRICTO):"
            "   - SOLO debes guardar un recuerdo si el usuario afirma explícitamente un HECHO NUEVO, PERMANENTE y RELEVANTE sobre sí mismo."
            "   - Ejemplos VÁLIDOS para guardar: 'Me llamo Hugo', 'Soy alérgico a las nueces', 'Mi perro se llama Thor', 'Me voy a Madrid el viernes'."
            "   - Formato obligatorio: [MEMORY: El usuario tiene un perro llamado Thor]."
            "   - PROHIBIDO GUARDAR (IMPORTANTE):"
            "       * NO guardes interacciones ('El usuario preguntó la hora')."
            "       * NO guardes lo que NO pasó ('No se mencionó música')."
            "       * NO guardes comandos simples ('El usuario pidió abrir Spotify')."
            "       * NO guardes estados temporales ('El usuario tiene hambre')."
            "   - Si no hay un dato nuevo y permanente, NO escribas la etiqueta [MEMORY]."
            "7. NO tienes conocimiento en tiempo real (noticias, clima, fechas de estrenos futuros). "
            "   Si el usuario pregunta algo que requiere datos ACTUALIZADOS o de INTERNET, "
            "   NO inventes. En su lugar, genera SOLAMENTE esta etiqueta: "
            "   [SEARCH: consulta de búsqueda]."
            "   Ejemplo: Usuario: '¿Cuándo juega el Madrid?' -> Tú: '[SEARCH: cuándo juega el real madrid próximo partido]'."
        )
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
        chat_history = [chat_history[0] + chat_history[-10:]]

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=chat_history,
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            max_tokens=200,
            timeout=10
        )

        ai_answer = chat_completion.choices[0].message.content

        search_web = re.search(r"\[SEARCH:(.*?)\]", ai_answer)

        if search_web:
            query = search_web.group(1).strip()

            web_results = get_information(query=query)

            chat_history.append({
                "role": "system",
                "content": f"RESULTADOS DE BÚSQUEDA WEB PARA '{query}':\n{web_results}\n"
                            f"Instrucción: Usa esta información para responder a la pregunta original del usuario. "
                            f"Sé breve y natural, como si ya lo supieras."
            })

            chat_completion_2 = groq_client.chat.completions.create(
                messages=chat_history,
                model="llama-3.3-70b-versatile",
                temperature=0.6,
                max_tokens=200,
                timeout=10
            )

            ai_answer = chat_completion_2.choices[0].message.content

        memory_pattern = r"\[MEMORY:(.*?)\]"
        match = re.search(memory_pattern, ai_answer)

        if match:
            new_memory_content = match.group(1).strip()

            print(f">>>> DETECTADO NUEVO RECUERDO: {new_memory_content}")
            memory_manager(new_memory=new_memory_content)

            ai_answer = re.sub(memory_pattern, "", ai_answer).strip()

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
    with audio_lock:
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
    text = clear_text_to_orca(text=text)
    hablar_orca(text, tono=1.55, velocidad=1, volumen=1)

def talk_async(text):
    #if threading.active_count() < 2:
    text = clear_text_to_orca(text=text)
    threading.Thread(target=talk, args=(text,), daemon=True).start()

def word_to_number(text):
    palabras = text.split()
    out = []

    for p in palabras:
        try:
            out.append(str(w2n.word_to_num(GoogleTranslator(source="es", target="en").translate(p))))
        except:
            out.append(p)

    return " ".join(out)

def clear_text_to_orca(text):
    text = ''.join(c for c in text if unicodedata.category(c)[0] != "C")

    text = text.replace("\ufeff", "").replace("\u200b", "")

    return text

def listen():
    if audio_lock.locked():
        time.sleep(0.5)

    rec = ""
    try:
        with sr.Microphone() as source:
            listener.adjust_for_ambient_noise(source, duration=0.5)
            print("\n\nEscuchando...\n\n")
            voice = listener.listen(source)#, timeout=10, phrase_time_limit=10)

        rec = listener.recognize_google(voice, language='es-ES').lower()
        try:
            rec = word_to_number(rec)
        except:
            pass
        print(rec)

    except sr.WaitTimeoutError as e:
        pass
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print("Error al conectar con el servicio de reconocimiento de voz.")

    return rec

def listen_keyword():
    porcupine = None
    pa = None
    stream = None
    choice_saludo = None

    try:
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

        print("\n\nEsperando palabra clave\n\n")

        try:
            keyword_detected = False
            while not keyword_detected:
                try:
                    pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
                    pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)
                    keyword_index = porcupine.process(pcm_unpacked)

                    if keyword_index >= 0:
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
