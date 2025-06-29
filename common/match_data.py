import pandas as pd
import os
from data.extraccion_datos import (
    get_credentials, 
    extract_match_specific_data, 
    extract_historical_team_stats,
    get_general_analysis,
    get_offensive_analysis,
    get_defensive_analysis,
    get_transitions_analysis,
    get_set_pieces_analysis,
    get_general_offensive_analysis,
    get_general_defensive_analysis,
    get_general_transitions_analysis,
    get_general_set_pieces_analysis
)
from statsbombpy import sb

def generar_datos(id_partido, local, visitante):
    """
    Genera los datos necesarios para el análisis de un partido.
    - Si Audax Italiano participa: Análisis enfocado en el rendimiento de Audax
    - Si Audax Italiano NO participa: Análisis general del partido
    
    Args:
        id_partido: ID del partido
        local: Nombre del equipo local
        visitante: Nombre del equipo visitante
        
    Returns:
        tuple: (match_data, attack_data, defense_data, set_piece_data, transition_data)
    """
    # Determinar si Audax Italiano participa en el partido
    es_audax_local = local == "Audax Italiano"
    es_audax_visitante = visitante == "Audax Italiano"
    audax_participa = es_audax_local or es_audax_visitante
    
    if audax_participa:
        equipo_analisis = local if es_audax_local else visitante
        equipo_rival = visitante if es_audax_local else local
    else:
        # Para partidos sin Audax, analizar ambos equipos
        equipo_analisis = None
        equipo_rival = None

    # Verificar que el archivo CSV de matches exista
    if not os.path.exists("outs_data/sb_matches.csv"):
        raise FileNotFoundError("No se encontró el archivo outs_data/sb_matches.csv")

    # Cargar datos adicionales del CSV de matches para obtener los goles
    df_matches = pd.read_csv("outs_data/sb_matches.csv")
    df_matches.columns = [col.strip() for col in df_matches.columns]
    
    # Verificar que el partido existe
    datos_partido = df_matches[
        (df_matches["match_id"] == id_partido) &
        (df_matches["home_team"] == local) &
        (df_matches["away_team"] == visitante)
    ]
    
    if datos_partido.empty:
        raise ValueError(f"No se encontró el partido con ID {id_partido} entre {local} y {visitante}")
    
    goles_local = datos_partido.iloc[0]["home_score"]
    goles_visitante = datos_partido.iloc[0]["away_score"]
    fecha_partido = datos_partido.iloc[0]["match_date"]

    # -----------------------
    # FETCH EVENTS ONCE
    # -----------------------
    creds = get_credentials()
    events = sb.events(match_id=id_partido, creds=creds)
    
    # Filter events by team for Audax analysis
    if audax_participa:
        events_audax = events[events['team'] == 'Audax Italiano']
        events_rival = events[events['team'] != 'Audax Italiano']
    else:
        events_local = events[events['team'] == local]
        events_visitante = events[events['team'] == visitante]

    # -----------------------
    # FETCH DYNAMIC DATA
    # -----------------------

    if audax_participa:
        # ANÁLISIS ENFOCADO EN AUDAX ITALIANO
        print(f"Generando análisis enfocado en Audax Italiano...")

        # Análisis específico de Audax
        general_data, attack_data, defense_data, set_piece_data, transition_data = generar_analisis_audax(events)
        
    else:
        # ANÁLISIS GENERAL DEL PARTIDO
        print(f"Generando análisis general del partido {local} vs {visitante}...")

        # Análisis general del partido
        general_data, attack_data, defense_data, set_piece_data, transition_data = generar_analisis_general(events)
        

    # Preparar datos completos del partido para el análisis general
    match_data_complete = {
        "match_info": {
            "id": id_partido,
            "local": local,
            "visitante": visitante,
            "goles_local": goles_local,
            "goles_visitante": goles_visitante,
            "fecha": fecha_partido,
            "audax_participa": audax_participa,
            "es_audax_local": es_audax_local if audax_participa else None,
            "equipo_rival": equipo_rival if audax_participa else None
        },
        "match_events": general_data,
    }

    return match_data_complete, attack_data, defense_data, set_piece_data, transition_data, events_audax

def generar_analisis_audax(events):
    """
    Genera análisis específico enfocado en el rendimiento de Audax Italiano.
    
    Args:
        match_id: ID del partido
        
    Returns:
        tuple: (general_data, attack_data, defense_data, set_piece_data, transition_data)
    """
    
    # Usar las nuevas funciones de análisis para obtener datos más precisos
    if not events.empty:
        # Obtener credenciales para las funciones de análisis
        print(events.columns)
        general_analysis = get_general_analysis(events)
        
        # Análisis ofensivo mejorado
        offensive_analysis = get_offensive_analysis(events)
        
        # Análisis defensivo mejorado
        defensive_analysis = get_defensive_analysis(events)
        
        # Análisis de transiciones mejorado
        transitions_analysis = get_transitions_analysis(events)
        
        # Análisis de pelota parada mejorado
        set_pieces_analysis = get_set_pieces_analysis(events)
    else:
        # Fallback a análisis original si no hay match_id
        general_analysis = {}
        offensive_analysis = {}
        defensive_analysis = {}
        transitions_analysis = {}
        set_pieces_analysis = {}
    

    return general_analysis, offensive_analysis, defensive_analysis, set_pieces_analysis, transitions_analysis


def generar_analisis_general(events):
    """
    Genera análisis general del partido comparando ambos equipos.
    
    Args:
        match_id: ID del partido
        
    Returns:
        tuple: (general_data, attack_data, defense_data, set_piece_data, transition_data)
    """
    
    # Usar las nuevas funciones de análisis para obtener datos más precisos
    if not events.empty:
        # Obtener credenciales para las funciones de análisis
        # Análisis general del partido
        general_analysis = get_general_analysis(events)
        # Análisis ofensivo mejorado (general)
        offensive_analysis = get_general_offensive_analysis(events)
        # Análisis defensivo mejorado (general)
        defensive_analysis = get_general_defensive_analysis(events)
        # Análisis de transiciones mejorado (general)
        transitions_analysis = get_general_transitions_analysis(events)
        # Análisis de pelota parada mejorado (general)
        set_pieces_analysis = get_general_set_pieces_analysis(events)
    else:
        # Fallback a análisis original si no hay match_id
        general_analysis = {}
        offensive_analysis = {}
        defensive_analysis = {}
        transitions_analysis = {}
        set_pieces_analysis = {}


    return general_analysis, offensive_analysis, defensive_analysis, transitions_analysis, set_pieces_analysis