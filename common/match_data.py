import pandas as pd
import os
from data.extraccion_datos import get_credentials, extract_match_specific_data, extract_historical_team_stats

def get_last_5_matches_for_audax(matches_df, current_match_date):
    """
    Obtiene los IDs de los últimos 5 partidos de Audax Italiano anteriores al partido actual.
    
    Args:
        matches_df: DataFrame con todos los partidos
        current_match_date: Fecha del partido actual
        
    Returns:
        list: Lista de match_ids de los últimos 5 partidos
    """
    # Filtrar partidos de Audax Italiano
    audax_matches = matches_df[
        (matches_df["home_team"] == "Audax Italiano") | 
        (matches_df["away_team"] == "Audax Italiano")
    ].copy()
    
    # Convertir fecha a datetime si no lo está
    audax_matches['match_date'] = pd.to_datetime(audax_matches['match_date'])
    current_date = pd.to_datetime(current_match_date)
    
    # Filtrar partidos anteriores al actual
    previous_matches = audax_matches[audax_matches['match_date'] < current_date]
    
    # Ordenar por fecha descendente y tomar los primeros 5
    previous_matches = previous_matches.sort_values('match_date', ascending=False)
    last_5_matches = previous_matches.head(5)
    
    return last_5_matches['match_id'].tolist()

def calcular_promedio_5_partidos_dinamico(creds, matches_df, current_match_date, metric_columns):
    """
    Calcula el promedio de las métricas de los 5 partidos anteriores para Audax Italiano
    obteniendo los datos dinámicamente desde la API.
    
    Args:
        creds: Credenciales de la API
        matches_df: DataFrame con todos los partidos
        current_match_date: Fecha del partido actual
        metric_columns: Lista de columnas de métricas a promediar
        
    Returns:
        pd.Series: Series con los promedios de las métricas, o None si no hay datos suficientes
    """
    try:
        # Obtener los IDs de los últimos 5 partidos
        last_5_match_ids = get_last_5_matches_for_audax(matches_df, current_match_date)
        
        if len(last_5_match_ids) == 0:
            print("No se encontraron partidos anteriores para calcular promedios")
            return None
        
        print(f"Obteniendo datos históricos de {len(last_5_match_ids)} partidos anteriores...")
        
        # Obtener estadísticas de equipo para esos partidos
        historical_team_stats = extract_historical_team_stats(creds, last_5_match_ids)
        
        if historical_team_stats.empty:
            print("No se pudieron obtener estadísticas históricas")
            return None
        
        # Filtrar solo datos de Audax Italiano
        audax_historical_stats = historical_team_stats[
            historical_team_stats['team_name'] == 'Audax Italiano'
        ]
        
        if audax_historical_stats.empty:
            print("No se encontraron estadísticas históricas de Audax Italiano")
            return None
        
        # Calcular promedios solo para las columnas que existen en los datos
        existing_columns = [col for col in metric_columns if col in audax_historical_stats.columns]
        
        if not existing_columns:
            print("No se encontraron columnas de métricas en los datos históricos")
            return None
        
        averages = audax_historical_stats[existing_columns].mean()
        print(f"Promedios calculados para {len(existing_columns)} métricas de {len(audax_historical_stats)} partidos")
        
        return averages
        
    except Exception as e:
        print(f"Error al calcular promedios dinámicos: {e}")
        return None

def calcular_promedio_5_partidos(team_stats_df, matches_df, team_name, current_match_date, metric_columns):
    """
    Calcula el promedio de las métricas de los 5 partidos anteriores para un equipo.
    """
    # Obtener todos los partidos del equipo
    team_matches = team_stats_df[team_stats_df['team_name'] == team_name].copy()
    
    # Añadir fecha del partido
    team_matches = team_matches.merge(
        matches_df[['match_id', 'match_date']], 
        on='match_id', 
        how='left'
    )
    
    # Ordenar por fecha
    team_matches = team_matches.sort_values('match_date', ascending=False)
    
    # Encontrar el índice del partido actual
    current_match_idx = team_matches[team_matches['match_date'] == current_match_date].index[0]
    
    # Obtener los 5 partidos anteriores
    previous_matches = team_matches.iloc[current_match_idx + 1:current_match_idx + 6]
    
    if len(previous_matches) == 0:
        return None
    
    # Calcular promedios
    averages = previous_matches[metric_columns].mean()
    return averages


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
    # FETCH DYNAMIC DATA
    # -----------------------

    # Obtener credenciales y extraer datos específicos del partido
    creds = get_credentials()
    match_specific_data = extract_match_specific_data(creds, id_partido)
    
    # Extraer los DataFrames del diccionario
    events_df = match_specific_data["events"]
    current_team_stats_df = match_specific_data["team_match_stats"]
    
    # Para los promedios de 5 partidos, usar extracción dinámica solo si Audax participa
    matches_df = df_matches

    # Filtrar datos para el partido específico
    match_data = datos_partido
    events_data = events_df[events_df["match_id"] == id_partido]
    team_stats_data = current_team_stats_df[current_team_stats_df["match_id"] == id_partido]

    # Verificar que hay datos para el partido
    if match_data.empty or events_data.empty or team_stats_data.empty:
        raise ValueError(f"No hay datos suficientes para el partido con ID {id_partido}")

    if audax_participa:
        # ANÁLISIS ENFOCADO EN AUDAX ITALIANO
        print(f"Generando análisis enfocado en Audax Italiano...")
        
        # Filtrar eventos para Audax Italiano
        audax_events = events_data[events_data["team"] == "Audax Italiano"]
        rival_events = events_data[events_data["team"] != "Audax Italiano"]

        # Obtener estadísticas del equipo
        audax_team_stats = team_stats_data[team_stats_data["team_name"] == "Audax Italiano"]
        rival_team_stats = team_stats_data[team_stats_data["team_name"] != "Audax Italiano"]

        # Análisis específico de Audax
        attack_data, defense_data, set_piece_data, transition_data = generar_analisis_audax(
            audax_events, rival_events, audax_team_stats, rival_team_stats, 
            creds, matches_df, fecha_partido
        )
        
    else:
        # ANÁLISIS GENERAL DEL PARTIDO
        print(f"Generando análisis general del partido {local} vs {visitante}...")
        
        # Separar eventos por equipo
        local_events = events_data[events_data["team"] == local]
        visitante_events = events_data[events_data["team"] == visitante]

        # Obtener estadísticas de ambos equipos
        local_team_stats = team_stats_data[team_stats_data["team_name"] == local]
        visitante_team_stats = team_stats_data[team_stats_data["team_name"] == visitante]

        # Análisis general del partido
        attack_data, defense_data, set_piece_data, transition_data = generar_analisis_general(
            local_events, visitante_events, local, visitante,
            local_team_stats, visitante_team_stats
        )

    # Añadir información adicional al match_data
    match_data = {
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
        "raw_data": match_data
    }

    return match_data, attack_data, defense_data, set_piece_data, transition_data

def generar_analisis_audax(audax_events, rival_events, audax_team_stats, rival_team_stats, creds, matches_df, fecha_partido):
    """
    Genera análisis específico enfocado en el rendimiento de Audax Italiano.
    
    Args:
        audax_events: Eventos de Audax Italiano
        rival_events: Eventos del equipo rival
        audax_team_stats: Estadísticas de Audax
        rival_team_stats: Estadísticas del rival
        creds: Credenciales API
        matches_df: DataFrame de partidos
        fecha_partido: Fecha del partido
        
    Returns:
        tuple: (attack_data, defense_data, set_piece_data, transition_data)
    """
    
    # 1. ANÁLISIS DE ATAQUE DE AUDAX
    attack_events = audax_events[
        (audax_events["type"] == "Shot") | 
        (audax_events["type"] == "Pass") | 
        (audax_events["type"] == "Carry") |
        (audax_events["type"] == "Dribble") |
        (audax_events["type"] == "Cross") |
        (audax_events["type"] == "Through Ball")
    ]
    
    attack_metrics = {
        "total_shots": len(attack_events[attack_events["type"] == "Shot"]),
        "shots_on_target": len(attack_events[(attack_events["type"] == "Shot") & 
            (attack_events.get("shot_outcome", "") == "On Target")]),
        "total_xg": attack_events[attack_events["type"] == "Shot"]["shot_statsbomb_xg"].sum() if "shot_statsbomb_xg" in attack_events.columns else 0,
        
        # Comparación con rival
        "rival_shots": len(rival_events[rival_events["type"] == "Shot"]),
        "rival_xg": rival_events[rival_events["type"] == "Shot"]["shot_statsbomb_xg"].sum() if "shot_statsbomb_xg" in rival_events.columns else 0,
        
        # Análisis específico de Audax
        "shots_box": len(attack_events[(attack_events["type"] == "Shot") & 
            (attack_events["location_x"] >= 102)]) if "location_x" in attack_events.columns else 0,
        "total_passes": len(attack_events[attack_events["type"] == "Pass"]),
        "successful_passes": len(attack_events[(attack_events["type"] == "Pass") & 
            (attack_events.get("pass_outcome", "") == "Successful")]),
        "total_crosses": len(attack_events[attack_events["type"] == "Cross"]),
        "successful_crosses": len(attack_events[(attack_events["type"] == "Cross") & 
            (attack_events.get("pass_outcome", "") == "Successful")]),
        "total_dribbles": len(attack_events[attack_events["type"] == "Dribble"]),
        "successful_dribbles": len(attack_events[(attack_events["type"] == "Dribble") & 
            (attack_events.get("dribble_outcome", "") == "Successful")]),
        "progressive_carries": len(attack_events[(attack_events["type"] == "Carry") & 
            (attack_events.get("carry_progressive", "") == True)]) if "carry_progressive" in attack_events.columns else 0,
        "key_passes": len(attack_events[(attack_events["type"] == "Pass") & 
            (attack_events.get("pass_shot_assist", "") == True)]) if "pass_shot_assist" in attack_events.columns else 0,
        "assists": len(attack_events[(attack_events["type"] == "Pass") & 
            (attack_events.get("pass_goal_assist", "") == True)]) if "pass_goal_assist" in attack_events.columns else 0
    }

    # 2. ANÁLISIS DE DEFENSA DE AUDAX
    defense_events = audax_events[
        (audax_events["type"] == "Pressure") | 
        (audax_events["type"] == "Tackle") | 
        (audax_events["type"] == "Interception") |
        (audax_events["type"] == "Block") |
        (audax_events["type"] == "Clearance") |
        (audax_events["type"] == "Ball Recovery")
    ]
    
    defense_metrics = {
        "total_pressures": len(defense_events[defense_events["type"] == "Pressure"]),
        "successful_pressures": len(defense_events[(defense_events["type"] == "Pressure") & 
            (defense_events.get("pressure_outcome", "") == "Success")]),
        "total_tackles": len(defense_events[defense_events["type"] == "Tackle"]),
        "successful_tackles": len(defense_events[(defense_events["type"] == "Tackle") & 
            (defense_events.get("tackle_outcome", "") == "Success")]),
        "interceptions": len(defense_events[defense_events["type"] == "Interception"]),
        "ball_recoveries": len(defense_events[defense_events["type"] == "Ball Recovery"]),
        "blocks": len(defense_events[defense_events["type"] == "Block"]),
        "clearances": len(defense_events[defense_events["type"] == "Clearance"]),
        
        # Análisis por zonas (enfoque Audax)
        "pressures_att_third": len(defense_events[(defense_events["type"] == "Pressure") & 
            (defense_events["location_x"] >= 80)]) if "location_x" in defense_events.columns else 0,
        "recoveries_att_third": len(defense_events[(defense_events["type"] == "Ball Recovery") & 
            (defense_events["location_x"] >= 80)]) if "location_x" in defense_events.columns else 0,
    }

    # 3. ANÁLISIS DE PELOTA PARADA DE AUDAX
    set_piece_events = audax_events[
        (audax_events["type"] == "Foul Won") | 
        (audax_events["type"] == "Pass") |  # Para córners y tiros libres
        (audax_events["type"] == "Throw In")
    ].copy()
    
    # Identificar córners (pases desde las esquinas)
    corners = set_piece_events[
        (set_piece_events["type"] == "Pass") &
        (
            # Esquina superior derecha
            ((set_piece_events["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) >= 120) &
             (set_piece_events["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 80)) |
            # Esquina superior izquierda
            ((set_piece_events["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) >= 120) &
             (set_piece_events["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 0)) |
            # Esquina inferior derecha
            ((set_piece_events["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) <= 0) &
             (set_piece_events["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 80)) |
            # Esquina inferior izquierda
            ((set_piece_events["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) <= 0) &
             (set_piece_events["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 0))
        )
    ].copy()

    # Separar córners completados e incompletos
    completed_corners = corners[corners.get("pass_outcome", "") == "Success"]
    incomplete_corners = corners[corners.get("pass_outcome", "") != "Success"]
    
    set_piece_metrics = {
        "total_corners": len(corners),
        "completed_corners": len(completed_corners),
        "incomplete_corners": len(incomplete_corners),
        "corner_completion_rate": len(completed_corners) / len(corners) if len(corners) > 0 else 0,
        "total_free_kicks": len(set_piece_events[set_piece_events.get("pass_outcome", "") == "Foul Won"]),
        "total_throw_ins": len(set_piece_events[set_piece_events.get("pass_outcome", "") == "Throw In"]),
        "successful_throw_ins": len(set_piece_events[set_piece_events.get("pass_outcome", "") == "Success"]),
        "set_piece_shots": len(set_piece_events[set_piece_events.get("pass_shot_assist", "") == True]) if "pass_shot_assist" in set_piece_events.columns else 0,
        "set_piece_goals": len(set_piece_events[set_piece_events.get("pass_goal_assist", "") == True]) if "pass_goal_assist" in set_piece_events.columns else 0,
    }

    # 4. ANÁLISIS DE TRANSICIONES DE AUDAX
    transition_events = audax_events[
        (audax_events["type"] == "Carry") | 
        (audax_events["type"] == "Dribble") |
        (audax_events["type"] == "Pressure") |
        (audax_events["type"] == "Ball Recovery") |
        (audax_events["type"] == "Pass") |
        (audax_events["type"] == "Counter Attack")
    ]
    
    transition_metrics = {
        "counter_attacks": len(transition_events[transition_events["type"] == "Counter Attack"]),
        "progressive_carries": len(transition_events[(transition_events["type"] == "Carry") & 
            (transition_events.get("carry_progressive", "") == True)]) if "carry_progressive" in transition_events.columns else 0,
        "high_recoveries": len(transition_events[(transition_events["type"] == "Ball Recovery") & 
            (transition_events["location_x"] >= 80)]) if "location_x" in transition_events.columns else 0,
        "transition_pressures": len(transition_events[(transition_events["type"] == "Pressure") & 
            (transition_events.get("pressure_duration", 0) <= 5)]) if "pressure_duration" in transition_events.columns else 0,
        "forward_passes_transition": len(transition_events[(transition_events["type"] == "Pass") & 
            (transition_events.get("pass_progressive", "") == True)]) if "pass_progressive" in transition_events.columns else 0,
    }

    # Preparar datos con promedios históricos dinámicos
    attack_data = {
        "events": attack_events,
        "team_stats": audax_team_stats,
        "metrics": attack_metrics,
        "previous_avg": calcular_promedio_5_partidos_dinamico(creds, matches_df, fecha_partido, [
            "team_match_np_xg", "team_match_np_shots", "team_match_goals",
            "team_match_xa", "team_match_key_passes", "team_match_assists",
            "team_match_passing_ratio", "team_match_crossing_ratio"
        ]),
        "focus": "audax"
    }
    
    defense_data = {
        "events": defense_events,
        "team_stats": audax_team_stats,
        "metrics": defense_metrics,
        "previous_avg": calcular_promedio_5_partidos_dinamico(creds, matches_df, fecha_partido, [
            "team_match_tackles", "team_match_interceptions", "team_match_pressures",
            "team_match_counterpressures", "team_match_ball_recoveries"
        ]),
        "focus": "audax"
    }
    
    set_piece_data = {
        "events": set_piece_events,
        "team_stats": audax_team_stats,
        "metrics": set_piece_metrics,
        "previous_avg": calcular_promedio_5_partidos_dinamico(creds, matches_df, fecha_partido, [
            "team_match_crossing_ratio", "team_match_box_cross_ratio"
        ]),
        "focus": "audax"
    }
    
    transition_data = {
        "events": transition_events,
        "team_stats": audax_team_stats,
        "metrics": transition_metrics,
        "previous_avg": calcular_promedio_5_partidos_dinamico(creds, matches_df, fecha_partido, [
            "team_match_possession", "team_match_counterpressures",
            "team_match_ball_recoveries", "team_match_pressure_regains"
        ]),
        "focus": "audax"
    }

    return attack_data, defense_data, set_piece_data, transition_data


def generar_analisis_general(local_events, visitante_events, local_name, visitante_name, local_team_stats, visitante_team_stats):
    """
    Genera análisis general del partido comparando ambos equipos.
    
    Args:
        local_events: Eventos del equipo local
        visitante_events: Eventos del equipo visitante
        local_name: Nombre del equipo local
        visitante_name: Nombre del equipo visitante
        local_team_stats: Estadísticas del equipo local
        visitante_team_stats: Estadísticas del equipo visitante
        
    Returns:
        tuple: (attack_data, defense_data, set_piece_data, transition_data)
    """
    
    # Combinar eventos de ambos equipos para análisis general
    all_events = pd.concat([local_events, visitante_events], ignore_index=True)
    
    # 1. ANÁLISIS GENERAL DE ATAQUE
    local_attack = local_events[local_events["type"].isin(["Shot", "Pass", "Cross", "Dribble"])]
    visitante_attack = visitante_events[visitante_events["type"].isin(["Shot", "Pass", "Cross", "Dribble"])]
    
    attack_metrics = {
        # Comparación entre equipos
        f"{local_name}_shots": len(local_attack[local_attack["type"] == "Shot"]),
        f"{visitante_name}_shots": len(visitante_attack[visitante_attack["type"] == "Shot"]),
        f"{local_name}_xg": local_attack[local_attack["type"] == "Shot"]["shot_statsbomb_xg"].sum() if "shot_statsbomb_xg" in local_attack.columns else 0,
        f"{visitante_name}_xg": visitante_attack[visitante_attack["type"] == "Shot"]["shot_statsbomb_xg"].sum() if "shot_statsbomb_xg" in visitante_attack.columns else 0,
        f"{local_name}_passes": len(local_attack[local_attack["type"] == "Pass"]),
        f"{visitante_name}_passes": len(visitante_attack[visitante_attack["type"] == "Pass"]),
        f"{local_name}_crosses": len(local_attack[local_attack["type"] == "Cross"]),
        f"{visitante_name}_crosses": len(visitante_attack[visitante_attack["type"] == "Cross"]),
        
        # Análisis de dominio
        "total_shots": len(local_attack[local_attack["type"] == "Shot"]) + len(visitante_attack[visitante_attack["type"] == "Shot"]),
        "total_xg": (local_attack[local_attack["type"] == "Shot"]["shot_statsbomb_xg"].sum() if "shot_statsbomb_xg" in local_attack.columns else 0) + 
                   (visitante_attack[visitante_attack["type"] == "Shot"]["shot_statsbomb_xg"].sum() if "shot_statsbomb_xg" in visitante_attack.columns else 0)
    }

    # 2. ANÁLISIS GENERAL DE DEFENSA
    local_defense = local_events[local_events["type"].isin(["Pressure", "Tackle", "Interception", "Block"])]
    visitante_defense = visitante_events[visitante_events["type"].isin(["Pressure", "Tackle", "Interception", "Block"])]
    
    defense_metrics = {
        f"{local_name}_pressures": len(local_defense[local_defense["type"] == "Pressure"]),
        f"{visitante_name}_pressures": len(visitante_defense[visitante_defense["type"] == "Pressure"]),
        f"{local_name}_tackles": len(local_defense[local_defense["type"] == "Tackle"]),
        f"{visitante_name}_tackles": len(visitante_defense[visitante_defense["type"] == "Tackle"]),
        f"{local_name}_interceptions": len(local_defense[local_defense["type"] == "Interception"]),
        f"{visitante_name}_interceptions": len(visitante_defense[visitante_defense["type"] == "Interception"]),
        
        "total_defensive_actions": len(local_defense) + len(visitante_defense),
        "defensive_intensity": (len(local_defense[local_defense["type"] == "Pressure"]) + 
                               len(visitante_defense[visitante_defense["type"] == "Pressure"]))
    }

    # 3. ANÁLISIS GENERAL DE PELOTA PARADA
    local_set_pieces = local_events[
        (local_events["type"] == "Foul Won") | 
        (local_events["type"] == "Pass") |
        (local_events["type"] == "Throw In")
    ]
    visitante_set_pieces = visitante_events[
        (visitante_events["type"] == "Foul Won") | 
        (visitante_events["type"] == "Pass") |
        (visitante_events["type"] == "Throw In")
    ]
    
    # Identificar córners para ambos equipos
    local_corners = local_set_pieces[
        (local_set_pieces["type"] == "Pass") &
        (
            ((local_set_pieces["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) >= 120) &
             (local_set_pieces["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 80)) |
            ((local_set_pieces["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) >= 120) &
             (local_set_pieces["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 0)) |
            ((local_set_pieces["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) <= 0) &
             (local_set_pieces["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 80)) |
            ((local_set_pieces["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) <= 0) &
             (local_set_pieces["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 0))
        )
    ]
    
    visitante_corners = visitante_set_pieces[
        (visitante_set_pieces["type"] == "Pass") &
        (
            ((visitante_set_pieces["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) >= 120) &
             (visitante_set_pieces["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 80)) |
            ((visitante_set_pieces["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) >= 120) &
             (visitante_set_pieces["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 0)) |
            ((visitante_set_pieces["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) <= 0) &
             (visitante_set_pieces["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 80)) |
            ((visitante_set_pieces["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) <= 0) &
             (visitante_set_pieces["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 0))
        )
    ]

    # Separar córners completados e incompletos para cada equipo
    local_completed_corners = local_corners[local_corners.get("pass_outcome", "") == "Success"]
    local_incomplete_corners = local_corners[local_corners.get("pass_outcome", "") != "Success"]
    visitante_completed_corners = visitante_corners[visitante_corners.get("pass_outcome", "") == "Success"]
    visitante_incomplete_corners = visitante_corners[visitante_corners.get("pass_outcome", "") != "Success"]
    
    set_piece_metrics = {
        f"{local_name}_total_corners": len(local_corners),
        f"{local_name}_completed_corners": len(local_completed_corners),
        f"{local_name}_incomplete_corners": len(local_incomplete_corners),
        f"{local_name}_corner_completion_rate": len(local_completed_corners) / len(local_corners) if len(local_corners) > 0 else 0,
        f"{visitante_name}_total_corners": len(visitante_corners),
        f"{visitante_name}_completed_corners": len(visitante_completed_corners),
        f"{visitante_name}_incomplete_corners": len(visitante_incomplete_corners),
        f"{visitante_name}_corner_completion_rate": len(visitante_completed_corners) / len(visitante_corners) if len(visitante_corners) > 0 else 0,
        f"{local_name}_free_kicks": len(local_set_pieces[local_set_pieces.get("pass_outcome", "") == "Foul Won"]),
        f"{visitante_name}_free_kicks": len(visitante_set_pieces[visitante_set_pieces.get("pass_outcome", "") == "Foul Won"]),
        f"{local_name}_throw_ins": len(local_set_pieces[local_set_pieces.get("pass_outcome", "") == "Throw In"]),
        f"{visitante_name}_throw_ins": len(visitante_set_pieces[visitante_set_pieces.get("pass_outcome", "") == "Throw In"]),
        "total_set_pieces": len(local_set_pieces) + len(visitante_set_pieces),
        "corner_battle": len(local_corners) - len(visitante_corners)
    }

    # 4. ANÁLISIS GENERAL DE TRANSICIONES
    local_transitions = local_events[local_events["type"].isin(["Carry", "Ball Recovery", "Counter Attack"])]
    visitante_transitions = visitante_events[visitante_events["type"].isin(["Carry", "Ball Recovery", "Counter Attack"])]
    
    transition_metrics = {
        f"{local_name}_recoveries": len(local_transitions[local_transitions["type"] == "Ball Recovery"]),
        f"{visitante_name}_recoveries": len(visitante_transitions[visitante_transitions["type"] == "Ball Recovery"]),
        f"{local_name}_counters": len(local_transitions[local_transitions["type"] == "Counter Attack"]),
        f"{visitante_name}_counters": len(visitante_transitions[visitante_transitions["type"] == "Counter Attack"]),
        
        "total_transitions": len(local_transitions) + len(visitante_transitions),
        "transition_dominance": len(local_transitions) - len(visitante_transitions)
    }

    # Preparar datos sin promedios históricos (no aplicable para análisis general)
    attack_data = {
        "events": pd.concat([local_attack, visitante_attack], ignore_index=True),
        "team_stats": pd.concat([local_team_stats, visitante_team_stats], ignore_index=True),
        "metrics": attack_metrics,
        "previous_avg": None,  # No aplicable para análisis general
        "focus": "general",
        "teams": {"local": local_name, "visitante": visitante_name}
    }
    
    defense_data = {
        "events": pd.concat([local_defense, visitante_defense], ignore_index=True),
        "team_stats": pd.concat([local_team_stats, visitante_team_stats], ignore_index=True),
        "metrics": defense_metrics,
        "previous_avg": None,
        "focus": "general",
        "teams": {"local": local_name, "visitante": visitante_name}
    }
    
    set_piece_data = {
        "events": pd.concat([local_set_pieces, visitante_set_pieces], ignore_index=True),
        "team_stats": pd.concat([local_team_stats, visitante_team_stats], ignore_index=True),
        "metrics": set_piece_metrics,
        "previous_avg": None,
        "focus": "general",
        "teams": {"local": local_name, "visitante": visitante_name}
    }
    
    transition_data = {
        "events": pd.concat([local_transitions, visitante_transitions], ignore_index=True),
        "team_stats": pd.concat([local_team_stats, visitante_team_stats], ignore_index=True),
        "metrics": transition_metrics,
        "previous_avg": None,
        "focus": "general",
        "teams": {"local": local_name, "visitante": visitante_name}
    }

    return attack_data, defense_data, set_piece_data, transition_data