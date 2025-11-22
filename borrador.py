import psutil

def system_status():
    print("analizando...")
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    print("analizando...")

    if cpu > 85 or ram > 85:
        estado_general = "Atención, Señor. Los niveles de consumo son elevados."
    else:
        estado_general = "Todos los sistemas funcionan dentro de los parámetros normales."

    mensaje = (f"Informe de estado: La carga de la CPU es del {cpu} por ciento. "
                f"El uso de memoria RAM es del {ram} por ciento."
                f"{estado_general}")

    print(mensaje)

system_status()