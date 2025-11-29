import tkinter as tk
import time
import winsound
import parsedatetime as pdt
from datetime import datetime
import re
import threading

_stop_timer_flag = False
_timer_thread = None


# --- Timer Function ---
def start_timer(duration):
    global _stop_timer_flag, _timer_thread
    # --- Window Configuration ---
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("+10+10")  # Posición en pantalla
    root.lift()
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-transparentcolor", "white")

    # --- Label for Numbers ---
    label = tk.Label(
                    root, text="", font=("Helvetica", 100, "bold"),
                    fg="grey", bg="white")
    label.pack()

    print("Starting visual timer...")
    t0 = time.perf_counter()
    total = int(duration)

    for remaining in range(total, 0, -1):
        if _stop_timer_flag:
            print("Temporizador parado por el usuario")
            break
        # Calculamos minutos y segundos
        m, s = divmod(remaining, 60)

        # Formateamos según duración
        if total >= 60:
            text = f"{m:d}:{s:02d}"
        else:
            text = f"{remaining} s"

        root.after(0, lambda: label.config(text=text))
        root.update()

        # Esperamos hasta el siguiente segundo exacto
        next_tick = t0 + (total - remaining + 1)
        time.sleep(max(0, next_tick - time.perf_counter()))

    if not _stop_timer_flag:
        # Al llegar a 0...
        label.config(text="¡Ring!")
        root.update()
        time.sleep(2)

    root.destroy()
    _stop_timer_flag = False
    _timer_thread = None
    winsound.Beep(440, 1500)
    print("\nTime's up!")


def start_thread(duration):
    global _timer_thread, _stop_timer_flag
    if _timer_thread and _timer_thread.is_alive():
        print("Ya hay un temporizador activo")
        return False
    _stop_timer_flag = False
    _timer_thread = threading.Thread(
                            target=start_timer,
                            args=(duration,),
                            daemon=True
                            )
    _timer_thread.start()
    return True


# --- Function to parse the input text ---
def parse_duration_string(input_string):
    s = input_string.strip().lower()

    m = re.search(r'(\d+)\s*(segundos?|s|minutos?|m(?!s)|horas?|h)', s)
    if m:
        n = int(m.group(1))
        unit = m.group(2)[0]
        return n * {'s': 1, 'm': 60, 'h': 3600}[unit]

    cal = pdt.Calendar()
    now = datetime.now()
    result, status = cal.parseDT(input_string, sourceTime=now)
    if status:
        diff = result - now
        return diff.total_seconds()

    return None


def stop_timer_externally():
    global _stop_timer_flag
    if _timer_thread and _timer_thread.is_alive():
        _stop_timer_flag = True
        return True  # True = activo
    return False  # False = inactivo


def is_timer_active():
    global _timer_thread
    return _timer_thread and _timer_thread.is_alive()
