import sys
import subprocess
import importlib
from system_config import talk_async
import time


def reload_modules():
    modules_reload = [
        'handlers',
        'system_config',
        'timer_tool',
        'security',
        'spotify_manager'
    ]

    try:
        talk_async("Iniciando actualización de sistemas, señor...")

        for modules_name in modules_reload:
            if modules_name in sys.modules:
                importlib.reload(sys.modules[modules_name])
                print(f"Módulo '{modules_name}' actualizado con éxito")

        talk_async("Sistemas actualizados correctamente. Todos los módulos operativos")
        return True

    except Exception as e:
        talk_async("Error durante la actualización.")
        print(f"Error al recargar módulos: {e}")
        return False


def restart_system():
    talk_async("Reiniciando sistemas, señor. Volveré en un momento.")

    try:
        python = sys.executable
        script = sys.argv[0]
        time.sleep(2)

        subprocess.Popen([python, script] + sys.argv[1:])
        sys.exit(0)

    except Exception as e:
        talk_async("Error al reiniciar el sistema, señor")
        print(f"Error al reiniciar sistema: {e}")
        return False
