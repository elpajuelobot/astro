from deep_translator import GoogleTranslator
from word2number import w2n

def es_to_number(text):
    palabras = text.split()
    out = []

    for p in palabras:
        try:
            out.append(str(w2n.word_to_num(GoogleTranslator(source="es", target="en").translate(p))))
        except:
            out.append(p)

    return " ".join(out)

print(es_to_number("Tengo dos perros"))
