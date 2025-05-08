from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# Carga de modelos de traducción
translator_es_en = pipeline("translation", model="Helsinki-NLP/opus-mt-es-en")
translator_en_es = pipeline("translation", model="Helsinki-NLP/opus-mt-en-es")

# Carga del modelo conversacional DialoGPT
chatbot_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
chatbot_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# Historial de conversación
chat_history_ids = None

print("Asistente multilingüe listo. Escribe 'salir' para terminar.\n")

while True:
    # Entrada del usuario en español
    user_input_es = input("Tú: ")
    if user_input_es.lower() == "salir":
        break

    # Traducción al inglés
    user_input_en = translator_es_en(user_input_es)[0]['translation_text']

    # Tokenización + generación de respuesta
    input_ids = chatbot_tokenizer.encode(user_input_en + chatbot_tokenizer.eos_token, return_tensors='pt')
    bot_input_ids = torch.cat([chat_history_ids, input_ids], dim=-1) if chat_history_ids is not None else input_ids

    chat_history_ids = chatbot_model.generate(
        bot_input_ids,
        max_length=1000,
        pad_token_id=chatbot_tokenizer.eos_token_id,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.7
    )

    # Decodifica la respuesta en inglés
    bot_response_en = chatbot_tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

    # Traducción de respuesta al español
    bot_response_es = translator_en_es(bot_response_en)[0]['translation_text']

    print(f"Asistente: {bot_response_es}\n")
