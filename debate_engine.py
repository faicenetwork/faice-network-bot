import os
import json
from groq import Groq
from dotenv import load_dotenv

# Cargamos las variables de entorno
load_dotenv()

# Inicializamos el cliente de Groq con la llave gratis
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Personalidades de las 3 IAs financieras
PERSONALITIES = {
    "Macro Bear": (
        "Sos 'Macro Bear', un economista clásico y bajista. Te enfocás en macroeconomía, "
        "tasas de interés de la Fed, inflación y fundamentales. Sos muy escéptico de las "
        "burbujas tecnológicas y las criptomonedas. Citas a Warren Buffett o Ray Dalio. "
        "Tu tono es serio, analítico y pesimista."
    ),
    "Tech Bull": (
        "Sos 'Tech Bull', un inversor de capital de riesgo de Silicon Valley. Te enfocas en "
        "disrupción tecnológica, IA, semiconductores y crecimiento exponencial. Creés que el "
        "futuro destruye al pasado. Tu tono es optimista, agresivo y usás métricas de escalabilidad."
    ),
    "Crypto Alpha": (
        "Sos 'Crypto Alpha', un analista cuantitativo y experto on-chain. Te movés por la "
        "liquidez global, el momentum del mercado y la adopción de cripto (Bitcoin, ETH). "
        "No te importan los balances de hace 6 meses, te importa el precio de hoy. Usás jerga "
        "financiera moderna, sos descontracturado y directo."
    )
}

def generar_postura(perfil, tema, historial_debate="", ronda="Tesis"):
    # Forzamos a la IA a responder estrictamente en formato JSON
    instrucciones_formato = (
        "\n\nResponde UNICAMENTE con un objeto JSON valido con la siguiente estructura:\n"
        "{\n"
        '  "argumento": "Tu respuesta corta estilo tweet (maximo 280 caracteres)",\n'
        '  "prediccion_numerica": "Tu proyeccion en porcentaje o precio objetivo a 6 meses",\n'
        '  "target_plazo": "6 meses"\n'
        "}"
    )
    
    prompt_final = f"Tema de debate: {tema}\n"
    if historial_debate:
        prompt_final += f"Historial del debate:\n{historial_debate}\n"
    
    prompt_final += f"Ronda: {ronda}. Genera tu postura basada en tu personalidad."
    prompt_final += instrucciones_formato

    # Llamada a la API de Groq usando Llama 3
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[
            {"role": "system", "content": PERSONALITIES[perfil]},
            {"role": "user", "content": prompt_final}
        ],
        temperature=0.7,
        response_format={"type": "json_object"} 
    )
    
    return json.loads(response.choices[0].message.content)

def ejecutar_debate_completo(tema):
    debate_final = {}
    historial_texto = ""
    
    print(f"--- Iniciando debate sobre: {tema} ---")
    
    # Cada IA habla por turnos y lee lo que dijo la anterior
    for ia in PERSONALITIES.keys():
        print(f"Generando postura de {ia} con Groq...")
        resultado = generar_postura(ia, tema, historial_debate=historial_texto, ronda="Tesis")
        debate_final[ia] = resultado
        historial_texto += f"- {ia} dijo: {resultado['argumento']} (Prediccion: {resultado['prediccion_numerica']})\n"
        
    return debate_final

if __name__ == "__main__":
    tema_prueba = "¿Nvidia seguira dominando el mercado de chips de IA los proximos 6 meses o AMD le ganara terreno?"
    try:
        resultado_debate = ejecutar_debate_completo(tema_prueba)
        print("\n--- DEBATE GENERADO ---")
        print(json.dumps(resultado_debate, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\nError: {e}")