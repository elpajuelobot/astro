from astro import run
import sys
import psutil
import requests
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFontDatabase, QFont, QColor, QPalette
import webbrowser
import threading


# """ venv\Scripts\activate """
# cd C:\Users\elpaj\Documents\jarvis
# pip install -r requirements.txt

# -------------- CONFIGURACIÓN INICIAL --------------
CITY = "Punta Umbría"
WEATHER_API_KEY = "e8293aa48b895468205e158ee66eecd5"
FONT_PATH = "OCRAEXT.TTF"

# -------------- FUNCIONES AUXILIARES --------------
def get_weather():
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=es"
        response = requests.get(url)
        data = response.json()
        temp = int(data['main']['temp'])
        description = data['weather'][0]['description'].capitalize()
        return f"{temp}°C | {description}"
    except:
        return "Clima no disponible"

def get_spotify_track():
    for proc in psutil.process_iter(['name', 'cmdline']):
        if proc.info['name'] == 'Spotify.exe':
            try:
                title = proc.cmdline()[1] if len(proc.cmdline()) > 1 else ""
                if "Spotify" in title and " - " in title:
                    parts = title.split(" - ")
                    if len(parts) >= 2:
                        return f"{parts[0]} - {parts[1]}"
                return "Reproduciendo Spotify"
            except:
                pass
    return "Spotify no activo"

# -------------- CLASE DE LA INTERFAZ PRINCIPAL --------------
class AstroInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setWindowOpacity(0.9)

        self.mic_enabled = True
        self.mic_enabled_event = threading.Event()
        if self.mic_enabled:
            self.mic_enabled_event.set()
        else:
            self.mic_enabled_event.clear()
        self.old_pos = QPoint()

        self.init_ui()
        self.update_info()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)

    def init_ui(self):
        # Fuente
        font_id = QFontDatabase.addApplicationFont("FONT_PATH")  # Actualiza el path si es necesario
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Monospace"
        self.font = QFont(font_family, 12)

        # Paleta de color
        palette = QPalette()
        palette.setColor(QPalette.WindowText, QColor("#00ffff"))
        self.setPalette(palette)

        # Etiquetas
        self.clock_label = QLabel("--:--")
        self.weather_label = QLabel("Clima...")
        self.spotify_label = QLabel("Spotify...")
        for lbl in [self.clock_label, self.weather_label, self.spotify_label]:
            lbl.setFont(self.font)
            lbl.setStyleSheet("color: #00ffff;")

        # Botones
        self.btn_browser = QPushButton("🌐")
        self.btn_weather = QPushButton("☁️")
        self.btn_exit = QPushButton("❌")
        self.btn_mic = QPushButton("🔊")
        for btn in [self.btn_browser, self.btn_weather, self.btn_exit, self.btn_mic]:
            btn.setFont(QFont(self.font.family(), 14))
            btn.setStyleSheet("background-color: rgba(0,0,0,0.5); color: #00ffff; border: none; border-radius: 8px;")
            btn.setFixedSize(40, 40)

        self.btn_browser.clicked.connect(lambda: webbrowser.open("https://www.google.com"))
        self.btn_weather.clicked.connect(lambda: webbrowser.open(f"https://www.google.com/search?q=clima+{CITY}"))
        self.btn_exit.clicked.connect(self.close)
        self.btn_mic.clicked.connect(self.toggle_mic)

        # Layouts
        vbox = QVBoxLayout()
        vbox.addWidget(self.clock_label)
        vbox.addWidget(self.weather_label)
        vbox.addWidget(self.spotify_label)

        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_browser)
        hbox.addWidget(self.btn_weather)
        hbox.addWidget(self.btn_mic)
        hbox.addWidget(self.btn_exit)

        vbox.addLayout(hbox)
        self.setLayout(vbox)

        # Estilo
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 150);  /* Fondo translúcido */
                border: 2px solid #00ffff;  /* Borde visible */
                border-radius: 10px;  /* Bordes redondeados */
            }
        """)

        self.setFixedSize(300, 180)
        self.show()

    def mousePressEvent(self, event):
        """Captura el evento del ratón para mover la ventana."""
        self.old_pos = event.globalPos()
        event.accept()

    def mouseMoveEvent(self, event):
        """Mover la ventana con el ratón."""
        delta = QPoint(event.globalPos() - self.old_pos)
        self.move(self.pos() + delta)
        self.old_pos = event.globalPos()
        event.accept()

    def update_info(self):
        self.clock_label.setText(datetime.now().strftime("%H:%M:%S"))
        self.weather_label.setText(get_weather())
        self.spotify_label.setText(get_spotify_track())
        self.btn_mic.setText("🔊" if self.mic_enabled else "🔇")

    def toggle_mic(self):
        self.mic_enabled = not self.mic_enabled
        if self.mic_enabled:
            self.mic_enabled_event.set()
        else:
            self.mic_enabled_event.clear() 

    def asistente(self):
        run(self.mic_enabled_event)

    def paralelo(self):
        thread_asistente = threading.Thread(target=self.asistente)
        thread_asistente.daemon = True
        thread_asistente.start()
        print("El asistente se está ejecutando en segundo plano...")


# -------------- EJECUCIÓN PRINCIPAL --------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    jarvis = AstroInterface()
    jarvis.paralelo()
    sys.exit(app.exec_())
