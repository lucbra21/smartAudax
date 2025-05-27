import streamlit as st
import pandas as pd
import openai
from dotenv import load_dotenv
import os

# Configura tu token de API de ChatGPT
load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")
def chatgpt_api(prompt, data, max_rows=40):
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
    response = openai.ChatCompletion.create(
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

    return response.choices[0].message['content']

def generate_prompt_matches():
    return """
    Como Director Técnico de Audax Italiano, proporciona un análisis técnico conciso del partido, enfocándote en:

    1. Contexto Táctico (máximo 3 líneas)
       - Estructura inicial y adaptaciones clave
       - Objetivos tácticos principales

    2. Desarrollo del Partido (máximo 3 líneas)
       - Momentos clave con datos específicos
       - Cambios tácticos más relevantes

    3. Evaluación del Rendimiento (máximo 3 líneas)
       - Métricas clave que respaldan el análisis
       - Comparación con el modelo de juego deseado

    4. Recomendaciones Técnicas (máximo 3 líneas)
       - Ajustes específicos basados en datos
       - Áreas de mejora con métricas concretas

    Utiliza datos específicos del partido para respaldar cada punto. 
    Limita cada sección a 3 líneas y enfócate en métricas concretas.
    """

def generate_prompt_ataque():
    return """
    Como Director Técnico de Audax Italiano, analiza el rendimiento ofensivo con datos concretos:

    1. Estructura Ofensiva (máximo 3 líneas)
       - Métricas de organización posicional
       - Efectividad en creación de espacios

    2. Transiciones Ofensivas (máximo 3 líneas)
       - Velocidad de transición (datos específicos)
       - Efectividad en aprovechamiento de espacios

    3. Finalización (máximo 3 líneas)
       - Estadísticas de oportunidades creadas
       - Efectividad en la definición

    4. Recomendaciones Técnicas (máximo 3 líneas)
       - Ajustes específicos con métricas de referencia
       - Áreas de mejora con datos concretos

    Utiliza datos específicos para cada punto. Limita cada sección a 3 líneas.
    """

def generate_prompt_defensa():
    return """
    Como Director Técnico de Audax Italiano, analiza el rendimiento defensivo con datos concretos:

    1. Organización Defensiva (máximo 3 líneas)
       - Métricas de estructura defensiva
       - Efectividad en coberturas

    2. Transiciones Defensivas (máximo 3 líneas)
       - Velocidad de transición (datos específicos)
       - Efectividad en recuperación

    3. Presión y Recuperación (máximo 3 líneas)
       - Estadísticas de presión efectiva
       - Eficiencia en recuperación de balón

    4. Recomendaciones Técnicas (máximo 3 líneas)
       - Ajustes específicos con métricas de referencia
       - Áreas de mejora con datos concretos

    Utiliza datos específicos para cada punto. Limita cada sección a 3 líneas.
    """

def generate_prompt_pelota_parada():
    return """
    Como Director Técnico de Audax Italiano, analiza el rendimiento en pelota parada con datos concretos:

    1. Saques de Esquina (máximo 3 líneas)
       - Estadísticas de efectividad
       - Métricas de organización

    2. Tiros Libres (máximo 3 líneas)
       - Datos de ejecución
       - Efectividad en aprovechamiento

    3. Saques de Banda (máximo 3 líneas)
       - Métricas de progresión
       - Efectividad en creación de peligro

    4. Recomendaciones Técnicas (máximo 3 líneas)
       - Ajustes específicos con métricas de referencia
       - Áreas de mejora con datos concretos

    Utiliza datos específicos para cada punto. Limita cada sección a 3 líneas.
    """

def generate_prompt_transiciones():
    return """
    Como Director Técnico de Audax Italiano, analiza las transiciones con datos concretos:

    1. Transiciones Ofensivas (máximo 3 líneas)
       - Velocidad de transición (datos específicos)
       - Efectividad en aprovechamiento

    2. Transiciones Defensivas (máximo 3 líneas)
       - Métricas de recuperación
       - Efectividad en contención

    3. Cambios de Fase (máximo 3 líneas)
       - Estadísticas de adaptación
       - Efectividad en implementación

    4. Recomendaciones Técnicas (máximo 3 líneas)
       - Ajustes específicos con métricas de referencia
       - Áreas de mejora con datos concretos

    Utiliza datos específicos para cada punto. Limita cada sección a 3 líneas.
    """

# Función auxiliar para cargar un CSV
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Error al cargar {file_path}: {e}")
        return None

# Función principal de la app Streamlit
def main():
    st.title("Análisis de Datos con ChatGPT API")
    st.write("Se mostrarán los prompts generados y las respuestas de ChatGPT para cada CSV.")
    
    # Cargar CSVs generados (ajusta las rutas según corresponda)
    matches_df = load_csv("outs_data/sb_matches.csv")
    events_df = load_csv("outs_data/sb_events.csv")
    team_match_stats_df = load_csv("outs_data/sb_team_match_stats.csv")
    player_match_stats_df = load_csv("outs_data/sb_player_match_stats.csv")
    
    # Generar los prompts
    prompt_ataque = generate_prompt_ataque()
    prompt_defensa = generate_prompt_defensa()
    prompt_pelota_parada = generate_prompt_pelota_parada()
    prompt_transiciones = generate_prompt_transiciones()
    
    # Llamar a la API de ChatGPT para cada CSV y mostrar la respuesta
    st.subheader("Respuesta para Ataque")
    if matches_df is not None:
        response_ataque = chatgpt_api(prompt_ataque, matches_df)
        st.write(response_ataque)
    
    st.subheader("Respuesta para Defensa")
    if events_df is not None:
        response_defensa = chatgpt_api(prompt_defensa, events_df)
        st.write(response_defensa)
    
    st.subheader("Respuesta para Pelota Parada")
    if team_match_stats_df is not None:
        response_pelota_parada = chatgpt_api(prompt_pelota_parada, team_match_stats_df)
        st.write(response_pelota_parada)

    st.subheader("Respuesta para Transiciones")
    if player_match_stats_df is not None:
        response_transiciones = chatgpt_api(prompt_transiciones, player_match_stats_df)
        st.write(response_transiciones)

# if __name__ == "__main__":
#     main()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8501))
    st.run(host="0.0.0.0", port=port)