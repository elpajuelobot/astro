import speech_recognition as sr
import pyttsx3 as pt3
from datetime import datetime
import requests
import pywhatkit as kit
import subprocess
import time
import webbrowser
from usar_memoria import *

# Tiempo atmosférico
def weather(ciudad):
    api_key = "e8293aa48b895468205e158ee66eecd5"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key}&units=metric&lang=es"

    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()
        datos_clima = respuesta.json()

        if respuesta.status_code == 200:
            temperatura = datos_clima['main']['temp']
            descripcion = datos_clima['weather'][0]['description']
            humedad = datos_clima['main']['humidity']
            return f"El clima en {ciudad} es {descripcion}, con una temperatura de {temperatura}°C,y una humedad del {humedad}%."

        else:
            return "No se ha podio obtener el clima. Inténtalo luego quillo."
    except requests.exceptions.RequestException as e:
        return f"Quillo que ha surgío un error. Este es el error {e}"


def searchYoutube(query):
    talk(f"Repoduciendo {query} en Youtube")
    kit.playonyt(query)


def screen·On·Of():
    comando = ['C:\\ABD\\platform-tools\\adb', 'shell', 'dumpsys', 'window', 'policy']
    result = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    salida = result.stdout.lower()  # minúsculas para evitar errores por mayúsculas

    if "screen_state_on" in salida or "interactive_state_awake" in salida:
        return True
    elif "screen_state_off" in salida or "interactive_state_asleep" in salida:
        return False
    else:
        return None


def mobileOn():
    # Verificar estado de la pantalla
    if screen·On·Of():
        talk("La pantalla ya está encendida")
        return
    elif not screen·On·Of():
        talk("Encendiendo móvil")

    # Esperar
    time.sleep(2)
    subprocess.run(['adb', 'shell', 'input', 'keyevent', '26'])
    # Esperar
    time.sleep(1)
    # 1. Enciende la pantalla
    subprocess.run(['adb', 'shell', 'wm', 'dismiss-keyguard'])
    time.sleep(0.5)
    # 3. Inyecta PIN
    subprocess.run(['adb','shell','input','text', '1939m'])
    time.sleep(0.3)
    # 4. Pulsa ENTER
    subprocess.run(['adb','shell','input','keyevent','66'])
    time.sleep(0.5)


def openApp(nombre_app):
    # Verificar estado de la pantalla
    if screen·On·Of():
        pass
    elif not screen·On·Of():
        talk("Encendiendo móvil")
        time.sleep(2)
        mobileOn()
        time.sleep(2)

    # Obtener la lista de todos los paquetes instalados
    result = subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'pm', 'list', 'packages'], capture_output=True, text=True)

    # Buscar el paquete que contiene el nombre de la app en la lista
    for line in result.stdout.splitlines():
        if nombre_app.lower() in line.lower():  # Ignorar mayúsculas/minúsculas
            # Obtener el nombre del paquete (después de 'package:')
            package_name = line.split(':')[1]
            print(f"Abriendo la app: {package_name}")
            # Intentar abrir la aplicación
            subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'monkey', '-p', f'{package_name}', '-c', 'android.intent.category.LAUNCHER', '1'])
            return

    # Si no se encuentra la app
    print(f"No se encontró la aplicación '{nombre_app}'.")


def autoClose():
    # Verificar estado de la pantalla
    if screen·On·Of():
        return
    elif not screen·On·Of():
        talk("Encendiendo móvil")
        time.sleep(2)
        mobileOn()
        time.sleep(2)

    # Abre la vista de apps recientes
    subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'keyevent', 'KEYCODE_APP_SWITCH'])
    time.sleep(2)

    # Contar cuántas apps hay
    resultado = subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'dumpsys', 'activity', 'recents'],
                                stdout=subprocess.PIPE,
                                text=True)
    lineas = resultado.stdout.splitlines()
    abiertas = [linea for linea in lineas if 'Recent #0' not in linea and 'Recent #' in linea]
    cantidad = len(abiertas)

    for _ in range(cantidad - 2):
        subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'swipe', '500', '1300', '500', '500'])
        time.sleep(2)

    # Volver a inicio
    subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'keyevent', 'KEYCODE_HOME'])


def WhatsappMessage(contacto, text):
    # Verificar estado de la pantalla
    if screen·On·Of():
        pass
    elif not screen·On·Of():
        talk("Encendiendo móvil")
        time.sleep(2)
        mobileOn()
        time.sleep(2)

    # Cambiando text
    def escape_for_adb(text):
        if not text:
            return ""
        # Escapar caracteres no compatibles
        text = text.strip().replace(' ', '%s')\
            .replace('!', '').replace('¿', '').replace('?', '')\
            .replace('á', 'a').replace('é', 'e').replace('í', 'i')\
            .replace('ó', 'o').replace('ú', 'u')
        return text

    contacto_escaped = escape_for_adb(contacto)
    text_escaped = escape_for_adb(text)

    if not contacto_escaped or not text_escaped:
        print("❌ Error: El contacto o el mensaje están vacíos después del escape.")
        return

    try:
        # Abrir WhatsApp
        subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'monkey', '-p', 'com.whatsapp', '-c', 'android.intent.category.LAUNCHER', '1'])
        time.sleep(2)

        # Buscar contacto
        subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'tap', '900', '200'])  # lupa
        time.sleep(2)
        subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'text', contacto_escaped])
        time.sleep(2)
        subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'tap', '500', '400'])  # primer resultado
        time.sleep(2)

        # Escribir mensaje
        subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'text', text_escaped])
        time.sleep(2)
        subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'tap', '1000', '2200'])  # botón enviar
        time.sleep(2)

        # Cerrar WhatsApp
        subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'keyevent', 'KEYCODE_APP_SWITCH'])
        time.sleep(1)
        subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'swipe', '500', '1300', '500', '500'])
        time.sleep(1)
        subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'keyevent', 'KEYCODE_HOME'])

    except Exception as e:
        print(f"⚠️ Error al enviar mensaje por WhatsApp: {e}")


def Spotify(cancion):
    # Verificar estado de la pantalla
    if screen·On·Of():
        pass
    elif not screen·On·Of():
        talk("Encendiendo móvil")
        time.sleep(2)
        mobileOn()
        time.sleep(2)

    def escape_for_adb(cancion):
        cancion = cancion.replace(' ', '%s')  # Espacios
        cancion = cancion.replace('!', '')    # Opcional: eliminar signos no válidos
        cancion = cancion.replace('¿', '')    # adb no puede escribirlos
        cancion = cancion.replace('?', '')    # lo mismo
        cancion = cancion.replace('á', 'a')   # Reemplaza tildes
        cancion = cancion.replace('é', 'e')
        cancion = cancion.replace('í', 'i')
        cancion = cancion.replace('ó', 'o')
        cancion = cancion.replace('ú', 'u')
        # Puedes seguir agregando reemplazos si quieres más compatibilidad
        return cancion

    cancion_formt = escape_for_adb(cancion)
    # Abrir Spotify
    subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'monkey', '-p', 'com.spotify.music', '-c', 'android.intent.category.LAUNCHER', '1'])
    time.sleep(2)
    subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'tap', '440', '2150'])
    time.sleep(2)
    subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'tap', '440', '450'])
    time.sleep(2)
    subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'text', cancion_formt])
    time.sleep(2)
    subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'keyevent', '66'])
    time.sleep(2)
    subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'tap', '440', '450'])
    time.sleep(2)
    subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'tap', '940', '950'])
    time.sleep(2)
    subprocess.run(['C:\\ABD\\platform-tools\\adb', 'shell', 'input', 'keyevent', 'KEYCODE_HOME'])


def battery():
    # Ejecutamos el comando ADB y obtenemos la salida en formato de texto
    result = subprocess.run(
        ['C:\\ABD\\platform-tools\\adb', 'shell', 'dumpsys', 'battery'], 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    
    # Ahora tenemos la salida como un string en result.stdout
    salida = result.stdout
    
    # Buscamos el nivel de batería, la fuente de poder y el estado
    if 'level' in salida:
        # Buscamos la línea que contiene el nivel de la batería
        for line in salida.splitlines():
            if 'level' in line:
                # Extraemos el nivel de batería
                level = line.split(":")[1].strip()
                talk(f"El dispositivo móvil tiene un {level}% de batería.")
                return
    else:
        talk("No se pudo obtener el nivel de batería.")


def saludo(hora_actual=None):
    # Definir franjas horarias
    franjas = {
        "buenos días": (6, 12),  # 6 AM a 12 PM
        "buenas tardes": (12, 20),  # 12 PM a 8 PM
        "buenas noches": (20, 6)  # 8 PM a 6 AM
    }

    # Si no se pasa hora_actual, usar la hora del sistema
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


# Ajustes del asistente
name = "astro"
listener = sr.Recognizer()
engine = pt3.init()
voices = engine.getProperty('voices')
rate = engine.getProperty('rate')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', rate - 50)

def talk(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    rec = ""
    try:
        with sr.Microphone() as source:
            listener.adjust_for_ambient_noise(source, duration=1)
            print("Escuchando...")
            voice = listener.listen(source, timeout=10, phrase_time_limit=10)

        rec = listener.recognize_google(voice, language='es-ES')
        rec = rec.lower()

    except sr.WaitTimeoutError:
        pass
    except sr.UnknownValueError:
        pass  # No se pudo entender lo que dijiste
    except sr.RequestError:
        print("Error al conectar con el servicio de reconocimiento de voz.")
        pass
    return rec

def run(mic_enabled_event):
    try:
        hora_actual = datetime.now().strftime("%H:%M")
        saludo_inicial = saludo()
        saludo_final = periodoDia()
        talk(f"{saludo_inicial} Hugo, son las {hora_actual} minutos {saludo_final}")
        rec = ""

        while True:
            if mic_enabled_event.is_set():
                rec = listen()
                if not rec:
                    continue

                if name in rec:
                    if 'reproduce' in rec:
                        query = rec.replace("astro reproduce", "").strip()
                        while True:
                            if query == "":
                                talk("No has dicho nada. ¿Qué quieres que reproduzca en youtube?")
                                query = listen()
                                if query != "":
                                    break
                            else:
                                break
                        searchYoutube(query)

                    elif 'qué tiempo' in rec:
                        ciudad = "Punta Umbría"
                        resultado_clima = weather(ciudad)
                        talk(resultado_clima)

                    elif 'mensaje' in rec:
                        contacto = ""
                        while True:
                            talk("¿A quién quieres enviarle el mensaje?")
                            contacto = listen()
                            if not contacto:
                                talk("No te he entendido. Repítelo.")
                                continue

                            talk(f"¿Quieres enviarle un mensaje a {contacto}? Di sí o no.")
                            confirmacion = listen()

                            if "sí" in confirmacion or "si" in confirmacion:
                                break
                            elif "no" in confirmacion:
                                continue
                            else:
                                talk("Sigo sin entenderte. Habla más claro.")

                        while True:
                            talk(f"¿Qué quieres enviarle a {contacto}?")
                            mensaje = listen()
                            if mensaje:
                                talk("Enviando mensaje.")
                                time.sleep(2)
                                WhatsappMessage(contacto, mensaje)
                                time.sleep(2)
                                talk("Mensaje enviado.")
                                break
                            else:
                                talk("No he podido escuchar el mensaje. Inténalo de nuevo.")

                    elif 'abre una aplicación' in rec:
                        while True:
                            talk("¿Qué aplicación quieres abrir?")
                            app = listen()

                            if not app:
                                talk("No te he entendido. Repítelo.")
                                continue

                            talk(f"¿Quieres abrir {app}? Di sí o no.")
                            confirmacion = listen()
                            print("confirmación", confirmacion)

                            if "sí" in confirmacion or "si" in confirmacion:
                                talk(f"Abriendo {app}...")
                                openApp(app)
                                break
                            elif "no" in confirmacion:
                                continue
                            else:
                                talk("No te he entendido. Inténtalo de nuevo.")
                    elif 'cierra' in rec:
                        talk("Cerrando aplicaciones")
                        time.sleep(2)
                        autoClose()
                        talk("Aplicaciones cerradas")

                    elif "teléfono" in rec:
                        mobileOn()

                    elif "pon una canción" in rec or "música" in rec:
                        while True:
                            talk("¿Qué canción quieres?")
                            cancion = listen()

                            if not cancion:
                                talk("No te he entendido, ¿puedes repetir?")
                                continue

                            talk(f"¿Quieres reproducir este canción: {cancion}?")
                            confirmacion = listen()

                            if "sí" in confirmacion or "si" in confirmacion:
                                talk(f"Reproduciendo la siguiente canción: {cancion}")
                                Spotify(cancion)
                                break
                            elif "no" in confirmacion:
                                talk("Vale, entonces ¿cuál quieres?")
                                continue
                            else:
                                talk("No me enterao un carajo, repite.")

                    elif "buscar" in rec or "búscame" in rec:
                        talk("¿Sobre qué quieres que busque?")
                        query = listen()

                        if not query:
                            talk("No te he entendido. Repite")
                            continue

                        if "sí" in rec or "si" in rec:
                            talk(f"Buscando información sobre '{query}' en internet...")
                            webbrowser.open(f"https://www.google.com/search?q={query}")
                            break
                        elif "no" in rec:
                            talk("Vale, entonces sobre que tienes interés en saber")
                            continue
                        else:
                            talk("no te he entendido")

                    elif 'batería' in rec:
                        battery()

                    elif 'adiós' in rec:
                        talk("¡Hasta luego quillo!")
                        break

                    else:
                        rec = rec.replace("astro", "").lstrip()
                        hora_actual = datetime.now().strftime("%H:%M")
                        respuesta = responder(rec, "Hugo", hora_actual)
                        talk(respuesta)
            else:
                talk("Micro desactivado")
                mic_enabled_event.wait()
                talk("Micro activado")
                continue

    except Exception as e:
        print(f"[ERROR] Algo falló: {e}")

