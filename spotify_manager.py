import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from dotenv import load_dotenv
import os
from time import sleep
import pyautogui
import psutil

# Importar variables
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
playlist_1_In = os.getenv("PLAYLIST_1")
playlist_2_Es = os.getenv("PLAYLIST_2")


def is_app_open(app_name: str) -> bool:
    for proc in psutil.process_iter(['name']):
        try:
            if (
                    proc.info['name'] and app_name.lower()
                    in proc.info['name'].lower()
                    ):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def wait_for_device(sp, timeout=10):
    """Espera hasta que Spotify tenga un dispositivo activo"""
    for _ in range(timeout):
        devices = sp.devices().get('devices', [])
        if devices:
            return True
        sleep(1)
    return False


def Spotify(talk):
    try:
        if not is_app_open("Spotify"):
            talk("Abriendo Spotify señor")
            pyautogui.hotkey("win", "7")
            sleep(2)
            pyautogui.press('space')

        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-modify-playback-state user-read-playback-state"
        ))

        if not wait_for_device(sp, timeout=10):
            talk("No se ha detectado todavía ha spotify señor, \
                vuelve a intentarlo por favor")
            return None

        return sp

    except Exception as e:
        print(f"\n\nError Spottitiitiititi: {e}\n\n")
        talk("abre primero spotify")
        return None
    except SpotifyException as e:
        print("Error spotify:", e)
        pyautogui.hotkey("win", "7")
        sleep(2)
        pyautogui.press('space')
        sleep(2)


def spotify_my_list(talk, playlist=1):
    sp = Spotify(talk)
    if sp is None:
        talk("No se ha podido abrir spotify")
        return False
    try:
        # Reproduce la playlist
        sp.shuffle(state=True)
        if playlist == 1:
            sp.start_playback(context_uri=f"spotify:playlist:{playlist_1_In}")
        elif playlist == 2:
            sp.start_playback(context_uri=f"spotify:playlist:{playlist_2_Es}")
        else:
            talk("No encuentro la lista")
    except SpotifyException as e:
        if "No active device" in str(e):
            talk("Spotify aún no estaba listo, \
                pero debería empezar en un momento.")
            sleep(2)
            # reintentar una vez
            try:
                pyautogui.hotkey("win", "7")
                sleep(2)
                pyautogui.press('space')
                sleep(2)
                if playlist == 1:
                    sp.start_playback(
                        context_uri=f"spotify:playlist:{playlist_1_In}"
                        )
                elif playlist == 2:
                    sp.start_playback(
                        context_uri=f"spotify:playlist:{playlist_2_Es}"
                        )
                else:
                    talk("No encuentro la lista")
            except SpotifyException:
                print("No se ha podido")
                pass
        else:
            talk("Ha ocurrido un error con Spotify señor.")
            print("Error spotify:", e)


def spotify_play(talk):
    sp = Spotify(talk)
    if sp is None:
        talk("No se ha podido abrir spotify")
        return False
    try:
        # Reproducir
        sp.start_playback()
    except SpotifyException as e:
        if "No active device" in str(e):
            talk("Spotify aún no estaba listo, \
                pero debería empezar en un momento.")
            sleep(2)
            pyautogui.hotkey("win", "7")
            sleep(2)
            pyautogui.press('space')
        else:
            talk("Ha ocurrido un error con Spotify señor.")
            print("Error spotify:", e)


def spotify_pause(talk):
    sp = Spotify(talk)
    if sp is None:
        talk("No se ha podido abrir spotify")
        return False
    try:
        # Pausa Spotify
        sp.pause_playback()
    except SpotifyException as e:
        talk("No he conseguido ejecutar Spotify señor")
        print("Error spotify:", e)


def spotify_next(talk):
    sp = Spotify(talk)
    if sp is None:
        talk("No se ha podido abrir spotify")
        return False
    try:
        # Siguiente
        sp.next_track()
    except SpotifyException as e:
        talk("No he conseguido ejecutar Spotify señor")
        print("Error spotify:", e)


def spotify_previous(talk):
    sp = Spotify(talk)
    if sp is None:
        talk("No se ha podido abrir spotify")
        return False
    try:
        # Anterior
        sp.previous_track()
    except SpotifyException as e:
        talk("No he conseguido ejecutar Spotify señor")
        print("Error spotify:", e)


def spotify_search_song(query, talk):
    sp = Spotify(talk)
    if sp is None:
        talk("No se ha podido abrir spotify")
        return False
    try:
        results = sp.search(q=query, type='track', limit=1)
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            sp.start_playback(uris=[track_uri])
            talk(f"Reproduciendo {results['tracks']['items'][0]['name']}")
        else:
            talk("No he podido encontrar esa canción señor")
    except SpotifyException as e:
        talk("No he conseguido ejecutar Spotify señor")
        print("Error spotify:", e)


def spotify_get_volume(talk):
    sp = Spotify(talk)
    if sp is None:
        talk("No se ha podido abrir spotify")
        return False
    playback = sp.current_playback()
    if playback and playback.get('device'):
        return playback['device']['volume_percent']
    return None


def spotify_set_volume(volume, talk):
    sp = Spotify(talk)
    if sp is None:
        talk("No se ha podido abrir spotify")
        return
    sp.volume(volume)


def transfer_music(talk, device_name):
    sp = Spotify(talk)
    if sp is None:
        talk("No se ha podido abrir spotify")
        return

    devices = sp.devices()
    device_id = ""

    for device in devices['devices']:
        if device['name'].lower() == device_name.lower():
            device_id = device['id']
            break

    if device_id:
        sp.transfer_playback(device_id, force_play=True)
    else:
        talk("Dispositivo no encontrado")


def spoti_info(talk, *args):
    sp = Spotify(talk)
    if sp is None:
        talk("No se ha podido abrir spotify")
        return

    playback = sp.current_playback()

    if not args:
        return None

    if playback and playback['is_playing']:
        device = playback['device']
        track = playback['item']
        choose_info = dict()
        information = {
            "device_name": device['name'],
            "device_type": device['type'],
            "device_id": device['id'],
            "device_volume": device['volume_percent'],
            "music_info": f"Está escuchando {track['name']}, de {track['artists'][0]['name']}"
        }

        for i in args:
            if i in information:
                choose_info[i] = information[i]
            else:
                choose_info[i] = "None"

        return choose_info

    else:
        talk("No hay ningún dispositivo activo ahora mismo señor.")
        return None
