import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from dotenv import load_dotenv
import os
import json
import subprocess
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
        with open("rutas_apps.json", "r", encoding="utf-8") as f:
            rutas = json.load(f)
            if not is_app_open("Spotify"):
                subprocess.Popen([rutas["spotify"]])
                talk("Abriendo spotify señor")
                sleep(5)
                pyautogui.press('space')
            else:
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
