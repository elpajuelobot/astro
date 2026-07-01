import os
import subprocess
import sys


def ejecutar_comandos_desde_fichero(ruta_archivo):
    # 1. Verificar si el archivo existe
    if not os.path.exists(ruta_archivo):
        print(f"[-] Error: El archivo '{ruta_archivo}' no existe.")
        sys.exit(1)

    print(f"[*] Leyendo comandos desde: {ruta_archivo}\n" + "-" * 40)

    # 2. Abrir y leer el archivo
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        for numero_linea, linea in enumerate(archivo, 1):
            # Limpiar espacios en blanco y saltos de línea
            comando = linea.strip()

            # Ignorar líneas vacías o comentarios (líneas que empiezan con #)
            if not comando or comando.startswith("#"):
                continue

            print(f"\n[+] [{numero_linea}] Ejecutando: {comando}")

            try:
                # 3. Ejecutar el comando en la shell
                # text=True hace que la salida sea string; check=True lanza excepción si falla
                resultado = subprocess.run(
                    comando,
                    shell=True,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # Mostrar la salida estándar si existe
                if resultado.stdout:
                    print(resultado.stdout.strip())

            except subprocess.CalledProcessError as e:
                # Capturar errores del comando sin detener el script entero
                print(
                    f"[-] Error al ejecutar la línea {numero_linea}: {comando}",
                    file=sys.stderr,
                )
                if e.stderr:
                    print(
                        f"Detalle del error:\n{e.stderr.strip()}",
                        file=sys.stderr,
                    )

    print("\n" + "-" * 40 + "\n[*] Proceso finalizado.")


if __name__ == "__main__":
    # Puedes cambiar el nombre del archivo aquí o pasarlo como argumento
    archivo_comandos = "comandos.txt"

    ejecutar_comandos_desde_fichero(archivo_comandos)
