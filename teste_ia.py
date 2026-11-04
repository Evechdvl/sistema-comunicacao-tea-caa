import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY", "").strip()

client = genai.Client(api_key=api_key)

texto_palavras = "Eu querer água"

# Desativa o raciocínio interno (thinking) para evitar que ele consuma os tokens da resposta
config = types.GenerateContentConfig(
    system_instruction=(
        "Você é um motor de CAA para pessoas autistas. "
        "Sua função é transformar palavras soltas em uma frase clara, educada, correta e em primeira pessoa do singular, "
        "em Português do Brasil. "
        "Devolva APENAS a frase pronta final, sem aspas e sem explicações."
    ),
    temperature=0.2,
    max_output_tokens=300,
    thinking_config=types.ThinkingConfig(thinking_budget=0),  # Garante 100% dos tokens para a resposta
)

print("A enviar requisição...")

try:
    response = client.models.generate_content(
        model="models/gemini-3.5-flash",
        contents=f"Transforme em frase: {texto_palavras}",
        config=config,
    )

    print("✅ Resposta da IA:", response.text.strip().replace('"', '').replace("'", ""))

except Exception as e:
    print(f"❌ Erro: {e}")