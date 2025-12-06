import os

usuario = os.environ["USERNAME"]

inicio_usuario = fr"C:\Users\{usuario}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"
inicio_global = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"

print(inicio_usuario)
print(inicio_global)
