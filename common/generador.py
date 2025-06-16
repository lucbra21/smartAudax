import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# Configura tu token de API de ChatGPT

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chatgpt_api(prompt, data, max_rows=60):
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
    if isinstance(data, dict):
        if "events" in data and not data["events"].empty:
            events_summary = data["events"].head(max_rows).to_csv(index=False)
            data_summary += f"Eventos relevantes:\n{events_summary}\n\n"
        
        if "team_stats" in data and not data["team_stats"].empty:
            team_stats_summary = data["team_stats"].to_csv(index=False)
            data_summary += f"Estadísticas de equipo:\n{team_stats_summary}\n\n"
            
        if "metrics" in data:
            metrics_summary = "\nMétricas calculadas:\n"
            for key, value in data["metrics"].items():
                metrics_summary += f"{key}: {value}\n"
            data_summary += metrics_summary
            
        if "previous_avg" in data and data["previous_avg"] is not None:
            prev_summary = "\nPromedios últimos 5 partidos:\n"
            for key, value in data["previous_avg"].items():
                prev_summary += f"{key}: {value:.2f}\n"
            data_summary += prev_summary
    
    # Si data es un DataFrame
    elif isinstance(data, pd.DataFrame) and not data.empty:
        data_summary = data.head(max_rows).to_csv(index=False)
    else:
        data_summary = "No hay datos disponibles para el análisis."

    # Construcción del mensaje a enviar
    message = f"{prompt}\n\nResumen de datos:\n{data_summary}"

    # Llamada a la API de OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """Eres un Director Técnico experto en fútbol, con amplia experiencia en análisis 
            táctico y datos. Tu objetivo es proporcionar análisis técnicos detallados y recomendaciones específicas basadas 
            en datos estadísticos y observaciones del juego. Debes mantener un enfoque técnico y profesional, utilizando 
            terminología específica del fútbol y respaldando tus conclusiones con datos concretos. 
            Debes siempre utilizar los datos como evidencia de factos, siempre expone los datos concretos que usas en cada analisis"""},
            {"role": "user", "content": message}
        ],
        temperature=0.2,
        max_tokens=800
    )

    return response.choices[0].message.content

def generate_prompt_matches():
    return """
    Como Director Técnico, proporciona un análisis técnico conciso del partido. 
    
    IMPORTANTE: Adapta tu análisis según el tipo de partido:
    - Si AUDAX ITALIANO participa: Enfócate en el rendimiento de Audax vs. el rival
    - Si Audax NO participa: Análisis general comparando ambos equipos
    
    Estructura tu análisis en:

    1. Contexto Táctico (máximo 3 líneas)
       - Estructura inicial y adaptaciones clave
       - Objetivos tácticos principales del/los equipo(s)

    2. Desarrollo del Partido (máximo 3 líneas)
       - Momentos clave con datos específicos
       - Cambios tácticos más relevantes

    3. Evaluación del Rendimiento (máximo 3 líneas)
       - Métricas clave que respaldan el análisis
       - Comparación con objetivos esperados

    4. Conclusiones Técnicas (máximo 3 líneas)
       - Puntos destacados del rendimiento
       - Aspectos más relevantes del partido

    Utiliza datos específicos del partido para respaldar cada punto. 
    Limita cada sección a 3 líneas y enfócate en métricas concretas.
    """

def generate_prompt_ataque():
    return """
    Como Director Técnico, analiza el rendimiento ofensivo. 
    
    IMPORTANTE: Adapta tu análisis según el contexto:
    - Si AUDAX ITALIANO participa: Análisis detallado del ataque de Audax vs. promedio histórico
    - Si Audax NO participa: Comparación ofensiva entre ambos equipos

    Estructura tu análisis en:

    1. Estructura Ofensiva (máximo 3 líneas)
       - Organización posicional y espacios generados
       - Efectividad en creación de oportunidades

    2. Progresión Ofensiva (máximo 3 líneas)
       - Calidad de transiciones hacia el ataque
       - Aprovechamiento de espacios en campo rival

    3. Finalización (máximo 3 líneas)
       - Estadísticas de oportunidades creadas y convertidas
       - Efectividad en la definición

    4. Recomendaciones Técnicas (máximo 3 líneas)
       - Ajustes específicos basados en datos
       - Áreas de mejora con métricas concretas

    Utiliza datos específicos para cada punto. Limita cada sección a 3 líneas.
    Si hay datos históricos disponibles, compara con el promedio de los últimos 5 partidos.
    """

def generate_prompt_defensa():
    return """
    Como Director Técnico, analiza el rendimiento defensivo.
    
    IMPORTANTE: Adapta tu análisis según el contexto:
    - Si AUDAX ITALIANO participa: Análisis detallado de la defensa de Audax vs. promedio histórico
    - Si Audax NO participa: Comparación defensiva entre ambos equipos

    Estructura tu análisis en:

    1. Organización Defensiva (máximo 3 líneas)
       - Estructura y compactidad del bloque defensivo
       - Efectividad en la presión y recuperación

    2. Duelos Defensivos (máximo 3 líneas)
       - Rendimiento en tackles e intercepciones
       - Eficacia en duelos individuales

    3. Transición Defensiva (máximo 3 líneas)
       - Velocidad y organización tras pérdida
       - Presión inmediata y repliegue

    4. Recomendaciones Técnicas (máximo 3 líneas)
       - Ajustes específicos basados en datos
       - Áreas de mejora con métricas concretas

    Utiliza datos específicos para cada punto. Limita cada sección a 3 líneas.
    Si hay datos históricos disponibles, compara con el promedio de los últimos 5 partidos.
    """

def generate_prompt_pelota_parada():
    return """
    Como Director Técnico, analiza el rendimiento en situaciones de pelota parada.
    
    IMPORTANTE: Adapta tu análisis según el contexto:
    - Si AUDAX ITALIANO participa: Análisis detallado de pelota parada de Audax vs. promedio histórico
    - Si Audax NO participa: Comparación de pelota parada entre ambos equipos

    Estructura tu análisis en:

    1. Efectividad Ofensiva (máximo 3 líneas)
       - Rendimiento en córners y tiros libres
       - Calidad de centros y remates

    2. Solidez Defensiva (máximo 3 líneas)
       - Organización en la defensa de pelotas paradas
       - Efectividad en el despeje y marcaje

    3. Variaciones Tácticas (máximo 3 líneas)
       - Diferentes esquemas utilizados
       - Creatividad y sorpresa en las jugadas

    4. Recomendaciones Técnicas (máximo 3 líneas)
       - Ajustes específicos basados en datos
       - Oportunidades de mejora

    Utiliza datos específicos para cada punto. Limita cada sección a 3 líneas.
    Si hay datos históricos disponibles, compara con el promedio de los últimos 5 partidos.
    """

def generate_prompt_transiciones():
    return """
    Como Director Técnico, analiza el rendimiento en las transiciones del juego.
    
    IMPORTANTE: Adapta tu análisis según el contexto:
    - Si AUDAX ITALIANO participa: Análisis detallado de transiciones de Audax vs. promedio histórico
    - Si Audax NO participa: Comparación de transiciones entre ambos equipos

    Estructura tu análisis en:

    1. Transiciones Ofensivas (máximo 3 líneas)
       - Velocidad y efectividad en contragolpes
       - Progresión hacia campo rival

    2. Transiciones Defensivas (máximo 3 líneas)
       - Organización tras pérdida del balón
       - Presión inmediata y recuperación

    3. Gestión de Espacios (máximo 3 líneas)
       - Aprovechamiento de espacios en transición
       - Coordinación entre líneas

    4. Recomendaciones Técnicas (máximo 3 líneas)
       - Ajustes específicos basados en datos
       - Oportunidades de mejora en transiciones

    Utiliza datos específicos para cada punto. Limita cada sección a 3 líneas.
    Si hay datos históricos disponibles, compara con el promedio de los últimos 5 partidos.
    """
