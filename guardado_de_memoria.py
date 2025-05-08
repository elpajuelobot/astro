import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
import pickle
from json import load

# Intenciones
with open("data.json", "r", encoding="utf-8") as fileIntenciones:
    intenciones = load(fileIntenciones)

# Preparar datos
X = []
y = []
for intent, datos in intenciones.items():
    for pregunta in datos["preguntas"]:
        X.append(pregunta)
        y.append(intent)

tokenizer = Tokenizer(oov_token="<OOV>")
tokenizer.fit_on_texts(X)
X_seq = tokenizer.texts_to_sequences(X)
X_pad = pad_sequences(X_seq, padding='post')

encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# Crear modelo
modelo = Sequential()
modelo.add(Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=16))
modelo.add(GlobalAveragePooling1D())
modelo.add(Dense(16, activation='relu'))
modelo.add(Dense(len(set(y_encoded)), activation='softmax'))

modelo.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
modelo.summary()
modelo.fit(X_pad, y_encoded, epochs=500, verbose=1)

# Guardar modelo y objetos
modelo.save("modelo_astro_V6.keras")
with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)
with open("encoder.pkl", "wb") as f:
    pickle.dump(encoder, f)
with open("intenciones.pkl", "wb") as f:
    pickle.dump(intenciones, f)

print("✅ Modelo, tokenizer, encoder e intenciones guardados.")
