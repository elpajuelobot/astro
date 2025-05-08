import tensorflow as tf
import numpy as np
from tensorflow import keras
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
import pickle
import random

# Cargar modelo y objetos
modelo = load_model("modelo_astro_V6.keras")
with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)
with open("encoder.pkl", "rb") as f:
    encoder = pickle.load(f)
with open("intenciones.pkl", "rb") as f:
    intenciones = pickle.load(f)

modelo.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])


# Umbral
umbral = 0.75

# Función para predecir
def responder(texto, nombre, hora_actual):
    if not texto.strip():
        return "No dijiste nada."
    secuencia = tokenizer.texts_to_sequences([texto])
    maxlen = modelo.input_shape[1]
    pad = pad_sequences(secuencia, maxlen=maxlen, padding='post')
    pred = modelo.predict(pad, verbose=0)
    prob = np.max(pred)
    clase = np.argmax(pred)
    if prob < umbral:  # Puedes ajustar este umbral
        return random.choice(intenciones["otros"]["respuesta"])
    tag = encoder.inverse_transform([clase])[0]
    if tag == "hora":
        return random.choice(intenciones["hora"]["respuesta"]).format(hora_actual=hora_actual)
    return random.choice(intenciones[tag]["respuesta"]).format(nombre=nombre)
