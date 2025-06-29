import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# Configura tu token de API de ChatGPT

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chatgpt_api(prompt, data, max_rows=100):
   """
   Envía a la API de ChatGPT un prompt junto con un resumen de los datos.
   
   Parámetros:
      - prompt (str): el mensaje inicial que contextualiza la tarea.
      - data (dict/DataFrame): datos del partido y métricas calculadas.
      - max_rows (int): límite de filas a incluir en el resumen.
   """
   # Preparar el resumen de los datos
   data_summary = ""
    
   # Si data es un diccionario con eventos, team_stats y metrics
   if isinstance(data, dict) and data != {}:
      data_summary = data
         
    
   # Si data es un DataFrame
   elif isinstance(data, pd.DataFrame) and not data.empty:
      data_summary = data.head(max_rows).to_csv(index=False)
   else:
      data_summary = "No hay datos disponibles para el análisis."

    # Construcción del mensaje a enviar


   message = f"{prompt}\n\nResumen de datos:\n{data_summary}"

   # Llamada a la API de OpenAI
   response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": """Eres un Director Técnico experto en fútbol. Tu objetivo es proporcionar análisis técnicos basados ÚNICAMENTE en los datos proporcionados.

REGLAS CRÍTICAS:
1. Usa SOLO los datos que se te proporcionan
2. NO inventes información ni hagas suposiciones
3. Si no hay datos suficientes para un aspecto, indícalo claramente
4. Mantén los análisis concisos y directos
5. Prioriza los datos de "enhanced_analysis" sobre otros datos
6. Escribe en lenguaje claro y accesible para un presidente de club

IMPORTANTE: Si no tienes datos para respaldar una afirmación, NO la hagas."""},
            {"role": "user", "content": message}
        ],
        temperature=0.1,
        max_tokens=800
    )

   return response.choices[0].message.content

def generate_prompt_matches():
    return """
    Como Director Técnico, proporciona una sinopsis narrativa del partido, basándote ÚNICAMENTE en los datos proporcionados.
    
    IMPORTANTE: 
    - Usa SOLO los datos que se te proporcionan, no inventes información
    - Si no hay datos suficientes para un aspecto, indícalo claramente
    - Mantén el análisis conciso (máximo 200 palabras)
    - Prioriza los datos de match_info y match_events si están disponibles
    - Enfócate en la narrativa del partido, no en estadísticas técnicas
    
    Escribe un análisis fluido que incluya:

    - Equipos participantes, resultado final y fecha del partido
    - Formaciones utilizadas por cada equipo (si están en match_events.formations)
    - Cómo se desarrolló el partido cronológicamente
    - Momentos clave basados en el timing de los goles y qué jugadores marcaron
    - El ritmo y la intensidad del partido
    - Cómo se vio el equipo en el campo
    - Aspectos positivos y áreas de mejora
    - Un resumen ejecutivo del partido y sus implicaciones para el club

    Si no hay datos suficientes para algún aspecto, omítelo en lugar de inventar información.
    Escribe en lenguaje claro y accesible para un presidente de club, evitando jerga técnica excesiva.
    """

def generate_prompt_ataque():
    return """
    Como Director Técnico, analiza el rendimiento ofensivo del equipo, basándote ÚNICAMENTE en los datos proporcionados.
    
    IMPORTANTE: 
    - Usa SOLO los datos de enhanced_analysis si están disponibles
    - Si no hay datos suficientes, indícalo claramente
    - Mantén el análisis conciso
    - Enfócate en la narrativa ofensiva, no en estadísticas técnicas
    - Describe cómo se vio el ataque del equipo
    
    Escribe un análisis que incluya:

    - Cómo se comportó el equipo en ataque
    - Jugadores que destacaron ofensivamente (solo si hay datos específicos)
    - La efectividad general del juego ofensivo
    - Momentos o situaciones ofensivas importantes

    Si no hay datos para algún aspecto, omítelo. No inventes información.
    Escribe en lenguaje claro y accesible para un presidente de club, evitando jerga técnica excesiva.
    """

def generate_prompt_defensa():
    return """
    Como Director Técnico, analiza el rendimiento defensivo del equipo, basándote ÚNICAMENTE en los datos proporcionados.
    
    IMPORTANTE: 
    - Usa SOLO los datos de enhanced_analysis si están disponibles
    - Si no hay datos suficientes, indícalo claramente
    - Mantén el análisis conciso 
    - Enfócate en la narrativa defensiva, no en estadísticas técnicas
    - Describe cómo se vio la defensa del equipo
    
    Escribe un análisis que incluya:

    - Cómo se comportó el equipo en defensa
    - Jugadores que destacaron defensivamente (solo si hay datos específicos)
    - La solidez general del juego defensivo
    - Momentos o situaciones defensivas importantes

    Si no hay datos para algún aspecto, omítelo. No inventes información.
    Escribe en lenguaje claro y accesible para un presidente de club, evitando jerga técnica excesiva.
    """

def generate_prompt_pelota_parada():
    return """
    Como Director Técnico, analiza el rendimiento en pelota parada del equipo, basándote ÚNICAMENTE en los datos proporcionados.
    
    IMPORTANTE: 
    - Usa SOLO los datos de enhanced_analysis si están disponibles
    - Si no hay datos suficientes, indícalo claramente
    - Mantén el análisis conciso 
    - Enfócate en la narrativa de pelota parada, no en estadísticas técnicas
    - Describe cómo se vio el equipo en estas situaciones
    
    Escribe un análisis que incluya:

    - Cómo se comportó el equipo en pelota parada
    - La efectividad en situaciones específicas (solo si hay datos)
    - Momentos importantes de pelota parada
    - La impresión general del rendimiento en estas situaciones

    Si no hay datos para algún aspecto, omítelo. No inventes información.
    Escribe en lenguaje claro y accesible para un presidente de club, evitando jerga técnica excesiva.
    """

def generate_prompt_transiciones():
    return """
    Como Director Técnico, analiza el rendimiento en transiciones del equipo, basándote ÚNICAMENTE en los datos proporcionados.
    
    IMPORTANTE: 
    - Usa SOLO los datos de enhanced_analysis si están disponibles
    - Si no hay datos suficientes, indícalo claramente
    - Mantén el análisis conciso 
    - Enfócate en la narrativa de transiciones, no en estadísticas técnicas
    - Describe cómo se vio el equipo en estas situaciones
    
    Escribe un análisis que incluya:

    - Cómo se comportó el equipo en las transiciones
    - La efectividad en contragolpes (solo si hay datos)
    - Momentos importantes de transición
    - La impresión general del rendimiento en estas situaciones

    Si no hay datos para algún aspecto, omítelo. No inventes información.
    Escribe en lenguaje claro y accesible para un presidente de club, evitando jerga técnica excesiva.
    """
