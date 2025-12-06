from spotify_manager import (
                                spotify_my_list, spotify_play, spotify_pause,
                                spotify_next, spotify_previous,
                                spotify_search_song,
                                spotify_get_volume, spotify_set_volume
                            )
from security import security
import time
import wikipedia
from timer_tool import (
                            parse_duration_string,
                            stop_timer_externally,
                            is_timer_active,
                            start_thread
                        )
from system_config import (
                            memory_manager, delete_memory,
                            AiBrain, clear_text_to_orca
                            )


class CommandHandler:
    def __init__(self, talk_async, listen):
        self.talk = talk_async
        self.listen = listen

    def can_handle(self, command: str) -> bool:
        return False

    def execute(self, command: str, **kwargs):
        pass


class MusicHandler(CommandHandler):
    def can_handle(self, command):
        keywords = ["spotify", "música", "canción", "voz", "volumen"]
        return any(k in command for k in keywords)

    def execute(self, command, **kwargs):
        if "pon spotify" in command or "pon música" in command:
            self.talk("Reproduciendo spotify...")
            spotify_play(self.talk)

        elif "the best" in command or "spanish version" in command:
            if "the best" in command:
                self.talk("Reproduciendo The best...")
                spotify_my_list(self.talk, playlist=1)
            elif "spanish version" in command:
                self.talk("Reproduciendo spanish version...")
                spotify_my_list(self.talk, playlist=2)

        elif "sigue la música" in command or "continúa la música" in command:
            self.talk("Reproduciendo...")
            spotify_play(self.talk)

        elif "para la música" in command or "música en pausa" in command:
            self.talk("Parando la música...")
            spotify_pause(self.talk)

        elif "pasa la canción" in command or "siguiente canción" in command:
            self.talk("Pasando a la siguiente canción...")
            spotify_next(self.talk)

        elif "canción anterior" in command:
            self.talk("Volviendo...")
            spotify_previous(self.talk)

        elif "pon la canción" in command or "busca la canción" in command:
            if "pon la canción" in command:
                query = command.replace("pon la canción", "").strip()
            elif "busca la canción" in command:
                query = command.replace("busca la canción", "").strip()

            spotify_search_song(query, self.talk)

        elif "sube el volumen" in command:
            if "máximo" in command:
                spotify_set_volume(100, self.talk)
            elif "%" in command or " al " in command:
                volumen = int((command
                            .replace("sube el volumen", "")
                            .replace("%", "")
                            .replace(" al ", "")
                            .strip()))
                spotify_set_volume(volumen, self.talk)
            else:
                original = spotify_get_volume(self.talk)
                spotify_set_volume(original + 10, self.talk)

        elif "baja el volumen" in command or "baja la voz" in command:
            if "mínimo" in command:
                spotify_set_volume(0, self.talk)
            elif "%" in command or " al " in command:
                volumen = int((command
                            .replace("baja el volumen", "")
                            .replace("baja la voz", "")
                            .replace("%", "")
                            .replace(" al ", "")
                            .strip()))
                spotify_set_volume(volumen, self.talk)
            else:
                original = spotify_get_volume(self.talk)
                spotify_set_volume(original - 10, self.talk)



class SystemHandler(CommandHandler):
    def can_handle(self, command):
        keywords = [
            "abre", "inicia",
            "kali", "trabajar",
            "sistema", "proyecto",
            "accede", "acceso"
            ]
        return any(k in command for k in keywords)

    def execute(self, command, **kwargs):
        # Funciones
        start_kali = kwargs['start_kali']
        open_work = kwargs['open_work']
        app_init = kwargs['app_init']
        system_status = kwargs['system_status']

        if "kali" in command or "cali" in command:
            acceso = security(self.talk, self.listen)
            if acceso:
                self.talk("Abriendo Kali linux...")
                start_kali()
            else:
                self.talk("Acceso denegado.")
        elif "vamos a trabajar" in command:
            self.talk("Estoy preparando el entorno...")
            app_init(app_name="visual studio")
            time.sleep(0.5)
            spotify_my_list(self.talk)
            time.sleep(0.5)
            app_init(app_name="google")

        elif ("estado del sistema" in command or
                "informe del sistema" in command):
            self.talk("Analizando telemetría del sistema señor...")
            system_status()

        elif any(word in command for word in [
                                            "nuevo proyecto",
                                            "inicia el proyecto",
                                            "abre el proyecto"]):
            if "abre el proyecto" in command:
                name = command.replace("abre el proyecto ", "")

                open_work(name=name)

            else:
                self.talk("¿Cómo desea llamar la carpeta, señor?")

                time.sleep(4)

                name = self.listen()

                if name:
                    name = name.replace(" ", "_")
                    open_work(name=name)

        elif any(word in command for word in [
                                            "abre", "accede",
                                            "acceso", "inicia"]):
            app = (
                    command
                    .replace(" el ", "")
                    .replace("accede al", "")
                    .replace("acceso al", "")
                    .replace("inicia", "")
                    .replace("abre", "").strip())
            app_init(app_name=app)


class SearchHandler(CommandHandler):
    def can_handle(self, command):
        keywords = [
            "buscar", "búscame",
            "investiga", "averigua",
            "encuentra", "qué es",
            "quién es", "qué significa",
            "informe", "resumen"
            ]
        return any(k in command for k in keywords)

    def execute(self, command, **kwargs):
        # Funciones
        guardar_resumen = kwargs['guardar_resumen']
        searchYoutube = kwargs['searchYoutube']

        if any(word in command for word in [
                                "buscar", "búscame",
                                "investiga", "averigua",
                                "encuentra", "qué es",
                                "quién es", "qué significa"]):

            wikipedia.set_lang("es")

            query = (
                    command
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
                self.talk("¿Qué desea saber?")
                time.sleep(1.5)
                query = self.listen().strip()
                if not query:
                    self.talk("No le he entendido señor")
                    return

            try:
                page = wikipedia.page(query)  # Obtener la página completa

                # Guardar el contenido en un txt
                with open("investigacion_raw.txt", "w", encoding="utf-8") as f:
                    f.write(page.content)

                resumen_corto = wikipedia.summary(query, sentences=1)
                self.talk(f"Información sobre {page.title} descargada, Señor. \
                    {resumen_corto}. ¿Desea que genere un informe detallado?")

                time.sleep(3)

                summary = self.listen().strip()
                if "si" in summary or "sí" in summary:
                    guardar_resumen()
                else:
                    self.talk("Entendido")

            except wikipedia.exceptions.DisambiguationError as e:
                self.talk("Hay varios temas con ese nombre, \
                        Señor. Sea más específico.")
                print("Wiki error", e)
            except Exception as e:
                print(e)
                self.talk("No pude acceder a la base de datos, Señor.")

        elif "genera un informe" in command or "resumen del texto" in command:
            guardar_resumen()

        elif 'reproduce' in command:
            query = command.replace("astro reproduce", "").strip()
            while True:
                if query == "":
                    self.talk("No has dicho nada. \
                            ¿Qué quieres que reproduzca en youtube?")
                    time.sleep(3)
                    query = self.listen()
                    if query != "":
                        break
                else:
                    break
            searchYoutube(query)


class TimerHandler(CommandHandler):
    def can_handle(self, command):
        keywords = ["temporizador", "cuenta atrás"]
        return any(k in command for k in keywords)

    def execute(self, command, **kwargs):
        if any(word in command for word in [
                                "para el temporizador",
                                "quita el temporizador"
                                ]):
            if stop_timer_externally():
                self.talk("Parando temporizador.")
            else:
                self.talk("No hay ningún temporizador activo.")

        elif "temporizador" in command or "cuenta atrás" in command:
            if is_timer_active():
                self.talk("Ya hay un temporizador en marcha.")
                return

            duration = parse_duration_string(command)

            if duration is not None and duration > 0:
                self.talk(f"Ejecutando temporizador \
                        de {int(duration)} segundos")
                timer = start_thread(duration)
                if not timer:
                    self.talk("Ya hay un temporizador en marcha.")
            else:
                self.talk("La entrada no ha podido ejecutarse \
                        correctamente. Inténtalo de nuevo.")


class MemoryHandler(CommandHandler):
    def can_handle(self, command):
        keywords = [
            "recuerda", "memoria",
            "sabes de mi"
            ]
        return any(k in command for k in keywords)

    def execute(self, command, **kwargs):
        if "recuerda que" in command or "guarda en tu memoria que" in command:
            memory_text = (
                            command
                            .replace("recuerda que", "")
                            .replace("guarda en tu memoria que", "")
                            .strip())

            if memory_text:
                self.talk(f"Guardando en mi base de datos: {memory_text}")
                memory_manager(new_memory=memory_text)
            else:
                self.talk("¿Qué es lo que quieres que recuerde, señor?")

        elif any(word in command for word in [
                                            "qué tienes en tu memoria",
                                            "léeme tu memoria",
                                            "qué sabes de mi"]):
            datos = memory_manager()
            if "No tengo recuerdos" in datos:
                self.talk("Mi base de datos de recuerdos está vacía, Señor.")
            else:
                self.talk("Accediendo a los registros encriptados...")
                clear_dates = datos.replace("[", "").replace("]", " del ")
                self.talk(f"Esto es lo que tengo guardado: {clear_dates}")

        elif any(word in command for word in [
                                            "borra tu memoria",
                                            "formatea tu memoria",
                                            "elimina tu memoria"]):
            self.talk("Advertencia. Señor, está a punto de eliminar \
                    permanentemente todos los datos de mi memoria \
                    ¿Desea continuar?")

            time.sleep(6.5)

            confirmacion = self.listen()

            if any(word in confirmacion for word in [
                                                    "sí",
                                                    "si",
                                                    "hazlo",
                                                    "procede"]):
                if delete_memory():
                    self.talk("Memoria formateada. Todos \
                            los datos han sido eliminados exitosamente.")
                else:
                    self.talk("Ha ocurrido un error al eliminar \
                            los datos de mi memoria señor.")
            else:
                self.talk("Cancelando protocolo de borrado")


class OtherQuestionsHandler(CommandHandler):
    def can_handle(self, command):
        keywords = [
            "qué tiempo", "que tiempo",
            "estás ahí", "estás despierto"
            ]
        return any(k in command for k in keywords)

    def execute(self, command, **kwargs):
        # Funciones
        weather = kwargs['weather']

        if 'qué tiempo' in command:
            ciudad = "Punta Umbría"
            resultado_clima = weather(ciudad)
            self.talk(resultado_clima)

        elif "Estás ahí" in command or "estás despierto" in command:
            self.talk("Para usted siempre Señor")


class AIBrainHandler(CommandHandler):
    def can_handle(self, command):
        return True

    def execute(self, command, **kwargs):
        if len(command) > 2:
            print(f"Consultando IA: {command}")

            answer = AiBrain(command)

            clear_answer = clear_text_to_orca(answer)
            self.talk(clear_answer)
        else:
            pass


class AstroBrain:
    def __init__(self, talk_async, listen):
        self.handlers = [
            MusicHandler(talk_async, listen),
            SystemHandler(talk_async, listen),
            SearchHandler(talk_async, listen),
            TimerHandler(talk_async, listen),
            MemoryHandler(talk_async, listen),
            OtherQuestionsHandler(talk_async, listen),
            AIBrainHandler(talk_async, listen)
        ]

    def process_command(self, command, **kwargs):
        for handler in self.handlers:
            if handler.can_handle(command):
                try:
                    handler.execute(command, **kwargs)
                    return
                except Exception as e:
                    print(f"Error en módulo {type(handler).__name__}: {e}")
