import pandas as pd
import os

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
    
    Args:
        id_partido: ID del partido
        local: Nombre del equipo local
        visitante: Nombre del equipo visitante
        
    Returns:
        tuple: (match_data, attack_data, defense_data, set_piece_data, transition_data)
    """
    # Determinar si Audax Italiano es local o visitante
    es_audax_local = local == "Audax Italiano"
    equipo_analisis = local if es_audax_local else visitante
    equipo_rival = visitante if es_audax_local else local

    # Verificar que los archivos CSV existan
    csv_files = ["outs_data/sb_matches.csv", "outs_data/sb_events.csv", "outs_data/sb_team_match_stats.csv"]
    for file in csv_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"No se encontró el archivo {file}")

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
    # INTEGRACIÓN CON CHATGPT
    # -----------------------

    # Cargar y filtrar los CSV por match_id
    matches_df = pd.read_csv("outs_data/sb_matches.csv", low_memory=False)
    events_df = pd.read_csv("outs_data/sb_events.csv", low_memory=False)
    team_stats_df = pd.read_csv("outs_data/sb_team_match_stats.csv", low_memory=False)

    # Filtrar datos para el partido específico
    match_data = matches_df[matches_df["match_id"] == id_partido]
    events_data = events_df[events_df["match_id"] == id_partido]
    team_stats_data = team_stats_df[team_stats_df["match_id"] == id_partido]

    # Verificar que hay datos para el partido
    if match_data.empty or events_data.empty or team_stats_data.empty:
        raise ValueError(f"No hay datos suficientes para el partido con ID {id_partido}")

    # Filtrar eventos para Audax Italiano
    audax_events = events_data[events_data["team"] == "Audax Italiano"]

    # 1. Dataset para Ataque
    attack_events = audax_events[
        (audax_events["type"] == "Shot") | 
        (audax_events["type"] == "Pass") | 
        (audax_events["type"] == "Carry") |
        (audax_events["type"] == "Dribble") |
        (audax_events["type"] == "Cross") |
        (audax_events["type"] == "Through Ball")
    ]
    
    # Calcular estadísticas avanzadas de ataque
    attack_metrics = {
        # Estadísticas básicas de tiros
        "total_shots": len(attack_events[attack_events["type"] == "Shot"]),
        "shots_on_target": len(attack_events[(attack_events["type"] == "Shot") & 
            (attack_events.get("shot_outcome", "") == "On Target")]),
        "total_xg": attack_events[attack_events["type"] == "Shot"]["shot_statsbomb_xg"].sum() if "shot_statsbomb_xg" in attack_events.columns else 0,
        
        # Análisis por zonas
        "shots_box": len(attack_events[(attack_events["type"] == "Shot") & 
            (attack_events["location_x"] >= 102)]) if "location_x" in attack_events.columns else 0,
        "shots_left": len(attack_events[(attack_events["type"] == "Shot") & 
            (attack_events["location_y"] <= 40)]) if "location_y" in attack_events.columns else 0,
        "shots_center": len(attack_events[(attack_events["type"] == "Shot") & 
            (attack_events["location_y"] > 40) & (attack_events["location_y"] < 60)]) if "location_y" in attack_events.columns else 0,
        "shots_right": len(attack_events[(attack_events["type"] == "Shot") & 
            (attack_events["location_y"] >= 60)]) if "location_y" in attack_events.columns else 0,
        
        # Análisis de pases
        "total_passes": len(attack_events[attack_events["type"] == "Pass"]),
        "successful_passes": len(attack_events[(attack_events["type"] == "Pass") & 
            (attack_events.get("pass_outcome", "") == "Successful")]),
        "passes_final_third": len(attack_events[(attack_events["type"] == "Pass") & 
            (attack_events["location_x"] >= 80)]) if "location_x" in attack_events.columns else 0,
        
        # Análisis de centros
        "total_crosses": len(attack_events[attack_events["type"] == "Cross"]),
        "successful_crosses": len(attack_events[(attack_events["type"] == "Cross") & 
            (attack_events.get("pass_outcome", "") == "Successful")]),
        "crosses_left": len(attack_events[(attack_events["type"] == "Cross") & 
            (attack_events["location_y"] <= 40)]) if "location_y" in attack_events.columns else 0,
        "crosses_right": len(attack_events[(attack_events["type"] == "Cross") & 
            (attack_events["location_y"] >= 60)]) if "location_y" in attack_events.columns else 0,
        
        # Análisis de regates y progresión
        "total_dribbles": len(attack_events[attack_events["type"] == "Dribble"]),
        "successful_dribbles": len(attack_events[(attack_events["type"] == "Dribble") & 
            (attack_events.get("dribble_outcome", "") == "Successful")]),
        "progressive_carries": len(attack_events[(attack_events["type"] == "Carry") & 
            (attack_events.get("carry_progressive", "") == True)]) if "carry_progressive" in attack_events.columns else 0,
        
        # Análisis de pases en profundidad
        "through_balls": len(attack_events[attack_events["type"] == "Through Ball"]),
        "successful_through_balls": len(attack_events[(attack_events["type"] == "Through Ball") & 
            (attack_events.get("pass_outcome", "") == "Successful")]),
        
        # Creación de oportunidades
        "key_passes": len(attack_events[(attack_events["type"] == "Pass") & 
            (attack_events.get("pass_shot_assist", "") == True)]) if "pass_shot_assist" in attack_events.columns else 0,
        "assists": len(attack_events[(attack_events["type"] == "Pass") & 
            (attack_events.get("pass_goal_assist", "") == True)]) if "pass_goal_assist" in attack_events.columns else 0
    }
    
    # 2. Dataset para Defensa
    defense_events = audax_events[
        (audax_events["type"] == "Pressure") | 
        (audax_events["type"] == "Tackle") | 
        (audax_events["type"] == "Interception") |
        (audax_events["type"] == "Block") |
        (audax_events["type"] == "Clearance") |
        (audax_events["type"] == "Ball Recovery")
    ]
    
    # Calcular estadísticas avanzadas de defensa
    defense_metrics = {
        # Presión y recuperación
        "total_pressures": len(defense_events[defense_events["type"] == "Pressure"]),
        "successful_pressures": len(defense_events[(defense_events["type"] == "Pressure") & 
            (defense_events.get("pressure_outcome", "") == "Success")]),
        "pressure_regains": len(defense_events[(defense_events["type"] == "Pressure") & 
            (defense_events.get("pressure_regain", "") == True)]) if "pressure_regain" in defense_events.columns else 0,
        
        # Análisis por zonas de presión
        "pressures_def_third": len(defense_events[(defense_events["type"] == "Pressure") & 
            (defense_events["location_x"] <= 40)]) if "location_x" in defense_events.columns else 0,
        "pressures_mid_third": len(defense_events[(defense_events["type"] == "Pressure") & 
            (defense_events["location_x"] > 40) & (defense_events["location_x"] < 80)]) if "location_x" in defense_events.columns else 0,
        "pressures_att_third": len(defense_events[(defense_events["type"] == "Pressure") & 
            (defense_events["location_x"] >= 80)]) if "location_x" in defense_events.columns else 0,
        
        # Análisis lateral de presión
        "pressures_left": len(defense_events[(defense_events["type"] == "Pressure") & 
            (defense_events["location_y"] <= 40)]) if "location_y" in defense_events.columns else 0,
        "pressures_center": len(defense_events[(defense_events["type"] == "Pressure") & 
            (defense_events["location_y"] > 40) & (defense_events["location_y"] < 60)]) if "location_y" in defense_events.columns else 0,
        "pressures_right": len(defense_events[(defense_events["type"] == "Pressure") & 
            (defense_events["location_y"] >= 60)]) if "location_y" in defense_events.columns else 0,
        
        # Duelos defensivos
        "total_tackles": len(defense_events[defense_events["type"] == "Tackle"]),
        "successful_tackles": len(defense_events[(defense_events["type"] == "Tackle") & 
            (defense_events.get("tackle_outcome", "") == "Success")]),
        "tackles_def_third": len(defense_events[(defense_events["type"] == "Tackle") & 
            (defense_events["location_x"] <= 40)]) if "location_x" in defense_events.columns else 0,
        "tackles_att_third": len(defense_events[(defense_events["type"] == "Tackle") & 
            (defense_events["location_x"] >= 80)]) if "location_x" in defense_events.columns else 0,
        
        # Intercepciones y recuperaciones
        "interceptions": len(defense_events[defense_events["type"] == "Interception"]),
        "ball_recoveries": len(defense_events[defense_events["type"] == "Ball Recovery"]),
        "recovery_def_third": len(defense_events[(defense_events["type"] == "Ball Recovery") & 
            (defense_events["location_x"] <= 40)]) if "location_x" in defense_events.columns else 0,
        "recovery_att_third": len(defense_events[(defense_events["type"] == "Ball Recovery") & 
            (defense_events["location_x"] >= 80)]) if "location_x" in defense_events.columns else 0,
        
        # Acciones defensivas
        "blocks": len(defense_events[defense_events["type"] == "Block"]),
        "shot_blocks": len(defense_events[(defense_events["type"] == "Block") & 
            (defense_events.get("block_type", "") == "Shot")]) if "block_type" in defense_events.columns else 0,
        "pass_blocks": len(defense_events[(defense_events["type"] == "Block") & 
            (defense_events.get("block_type", "") == "Pass")]) if "block_type" in defense_events.columns else 0,
        "clearances": len(defense_events[defense_events["type"] == "Clearance"])
    }
    
    # 3. Dataset para Pelota Parada
    set_piece_events = audax_events[
        (audax_events["type"] == "Free Kick") | 
        (audax_events["type"] == "Corner") | 
        (audax_events["type"] == "Throw In")
    ]
    
    # Calcular estadísticas avanzadas de pelota parada
    set_piece_metrics = {
        # Córners
        "total_corners": len(set_piece_events[set_piece_events["type"] == "Corner"]),
        "successful_corners": len(set_piece_events[(set_piece_events["type"] == "Corner") & 
            (set_piece_events.get("pass_outcome", "") == "Success")]),
        "corners_inswing": len(set_piece_events[(set_piece_events["type"] == "Corner") & 
            (set_piece_events.get("pass_type", "") == "Inswing")]) if "pass_type" in set_piece_events.columns else 0,
        "corners_outswing": len(set_piece_events[(set_piece_events["type"] == "Corner") & 
            (set_piece_events.get("pass_type", "") == "Outswing")]) if "pass_type" in set_piece_events.columns else 0,
        "corners_shot": len(set_piece_events[(set_piece_events["type"] == "Corner") & 
            (set_piece_events.get("pass_shot_assist", "") == True)]) if "pass_shot_assist" in set_piece_events.columns else 0,
        "corners_goal": len(set_piece_events[(set_piece_events["type"] == "Corner") & 
            (set_piece_events.get("pass_goal_assist", "") == True)]) if "pass_goal_assist" in set_piece_events.columns else 0,
        
        # Tiros Libres
        "total_free_kicks": len(set_piece_events[set_piece_events["type"] == "Free Kick"]),
        "successful_free_kicks": len(set_piece_events[(set_piece_events["type"] == "Free Kick") & 
            (set_piece_events.get("pass_outcome", "") == "Success")]),
        "direct_free_kicks": len(set_piece_events[(set_piece_events["type"] == "Free Kick") & 
            (set_piece_events.get("free_kick_type", "") == "Direct")]) if "free_kick_type" in set_piece_events.columns else 0,
        "indirect_free_kicks": len(set_piece_events[(set_piece_events["type"] == "Free Kick") & 
            (set_piece_events.get("free_kick_type", "") == "Indirect")]) if "free_kick_type" in set_piece_events.columns else 0,
        "fk_shots": len(set_piece_events[(set_piece_events["type"] == "Free Kick") & 
            (set_piece_events.get("pass_shot_assist", "") == True)]) if "pass_shot_assist" in set_piece_events.columns else 0,
        "fk_goals": len(set_piece_events[(set_piece_events["type"] == "Free Kick") & 
            (set_piece_events.get("pass_goal_assist", "") == True)]) if "pass_goal_assist" in set_piece_events.columns else 0,
        
        # Saques de Banda
        "total_throw_ins": len(set_piece_events[set_piece_events["type"] == "Throw In"]),
        "successful_throw_ins": len(set_piece_events[(set_piece_events["type"] == "Throw In") & 
            (set_piece_events.get("pass_outcome", "") == "Success")]),
        "attacking_throw_ins": len(set_piece_events[(set_piece_events["type"] == "Throw In") & 
            (set_piece_events["location_x"] >= 80)]) if "location_x" in set_piece_events.columns else 0,
        "throw_ins_final_third": len(set_piece_events[(set_piece_events["type"] == "Throw In") & 
            (set_piece_events["location_x"] >= 60)]) if "location_x" in set_piece_events.columns else 0,
        
        # Efectividad General
        "set_piece_shots": len(set_piece_events[set_piece_events.get("pass_shot_assist", "") == True]) if "pass_shot_assist" in set_piece_events.columns else 0,
        "set_piece_goals": len(set_piece_events[set_piece_events.get("pass_goal_assist", "") == True]) if "pass_goal_assist" in set_piece_events.columns else 0,
        "set_piece_xg": set_piece_events[set_piece_events["type"].isin(["Corner", "Free Kick"])]["shot_statsbomb_xg"].sum() if "shot_statsbomb_xg" in set_piece_events.columns else 0
    }
    
    # 4. Dataset para Transiciones
    transition_events = audax_events[
        (audax_events["type"] == "Carry") | 
        (audax_events["type"] == "Dribble") |
        (audax_events["type"] == "Pressure") |
        (audax_events["type"] == "Ball Recovery") |
        (audax_events["type"] == "Pass") |
        (audax_events["type"] == "Counter Attack")
    ]
    
    # Calcular estadísticas avanzadas de transiciones
    transition_metrics = {
        # Transiciones Ofensivas
        "counter_attacks": len(transition_events[transition_events["type"] == "Counter Attack"]),
        "successful_counters": len(transition_events[(transition_events["type"] == "Counter Attack") & 
            (transition_events.get("counter_attack_outcome", "") == "Success")]) if "counter_attack_outcome" in transition_events.columns else 0,
        "counter_shots": len(transition_events[(transition_events["type"] == "Counter Attack") & 
            (transition_events.get("counter_attack_shot", "") == True)]) if "counter_attack_shot" in transition_events.columns else 0,
        
        # Progresión en Transición
        "progressive_carries": len(transition_events[(transition_events["type"] == "Carry") & 
            (transition_events.get("carry_progressive", "") == True)]) if "carry_progressive" in transition_events.columns else 0,
        "carries_to_final_third": len(transition_events[(transition_events["type"] == "Carry") & 
            (transition_events["location_x"] >= 80)]) if "location_x" in transition_events.columns else 0,
        "successful_dribbles_transition": len(transition_events[(transition_events["type"] == "Dribble") & 
            (transition_events.get("dribble_outcome", "") == "Success")]),
        
        # Recuperación y Presión en Transición
        "high_recoveries": len(transition_events[(transition_events["type"] == "Ball Recovery") & 
            (transition_events["location_x"] >= 80)]) if "location_x" in transition_events.columns else 0,
        "mid_recoveries": len(transition_events[(transition_events["type"] == "Ball Recovery") & 
            (transition_events["location_x"] > 40) & (transition_events["location_x"] < 80)]) if "location_x" in transition_events.columns else 0,
        
        # Presión en Transición
        "transition_pressures": len(transition_events[(transition_events["type"] == "Pressure") & 
            (transition_events.get("pressure_duration", 0) <= 5)]) if "pressure_duration" in transition_events.columns else 0,
        "successful_transition_pressures": len(transition_events[(transition_events["type"] == "Pressure") & 
            (transition_events.get("pressure_duration", 0) <= 5) & 
            (transition_events.get("pressure_outcome", "") == "Success")]) if "pressure_duration" in transition_events.columns else 0,
        
        # Pases en Transición
        "forward_passes_transition": len(transition_events[(transition_events["type"] == "Pass") & 
            (transition_events.get("pass_progressive", "") == True)]) if "pass_progressive" in transition_events.columns else 0,
        "successful_forward_passes": len(transition_events[(transition_events["type"] == "Pass") & 
            (transition_events.get("pass_progressive", "") == True) & 
            (transition_events.get("pass_outcome", "") == "Success")]) if "pass_progressive" in transition_events.columns else 0,
        
        # Velocidad de Transición
        "quick_transitions": len(transition_events[(transition_events["type"].isin(["Carry", "Pass", "Dribble"])) & 
            (transition_events.get("duration", 0) <= 10)]) if "duration" in transition_events.columns else 0,
        "successful_quick_transitions": len(transition_events[(transition_events["type"].isin(["Carry", "Pass", "Dribble"])) & 
            (transition_events.get("duration", 0) <= 10) & 
            (transition_events.get("pass_outcome", "") == "Success")]) if "duration" in transition_events.columns else 0
    }

    # Obtener estadísticas del equipo
    audax_team_stats = team_stats_data[team_stats_data["team_name"] == "Audax Italiano"]
    rival_team_stats = team_stats_data[team_stats_data["team_name"] != "Audax Italiano"]

    # Preparar datos para el análisis
    attack_data = {
        "events": attack_events,
        "team_stats": audax_team_stats,
        "metrics": attack_metrics,
        "previous_avg": calcular_promedio_5_partidos(team_stats_df, matches_df, "Audax Italiano", fecha_partido, [
            "team_match_np_xg", "team_match_np_shots", "team_match_goals",
            "team_match_xa", "team_match_key_passes", "team_match_assists",
            "team_match_passing_ratio", "team_match_crossing_ratio",
            "team_match_shot_touch_ratio"
        ])
    }
    
    defense_data = {
        "events": defense_events,
        "team_stats": audax_team_stats,
        "metrics": defense_metrics,
        "previous_avg": calcular_promedio_5_partidos(team_stats_df, matches_df, "Audax Italiano", fecha_partido, [
            "team_match_tackles", "team_match_interceptions", "team_match_pressures",
            "team_match_pressure_duration_avg", "team_match_counterpressures",
            "team_match_ball_recoveries", "team_match_aerial_ratio",
            "team_match_challenge_ratio"
        ])
    }
    
    set_piece_data = {
        "events": set_piece_events,
        "team_stats": audax_team_stats,
        "metrics": set_piece_metrics,
        "previous_avg": calcular_promedio_5_partidos(team_stats_df, matches_df, "Audax Italiano", fecha_partido, [
            "team_match_crossing_ratio", "team_match_box_cross_ratio",
            "team_match_long_ball_ratio"
        ])
    }
    
    transition_data = {
        "events": transition_events,
        "team_stats": audax_team_stats,
        "metrics": transition_metrics,
        "previous_avg": calcular_promedio_5_partidos(team_stats_df, matches_df, "Audax Italiano", fecha_partido, [
            "team_match_possession", "team_match_counterpressures",
            "team_match_ball_recoveries", "team_match_deep_progressions",
            "team_match_pressure_regains"
        ])
    }

    # Añadir información adicional al match_data
    match_data = {
        "match_info": {
            "id": id_partido,
            "local": local,
            "visitante": visitante,
            "goles_local": goles_local,
            "goles_visitante": goles_visitante,
            "fecha": fecha_partido,
            "es_audax_local": es_audax_local,
            "equipo_rival": equipo_rival
        },
        "raw_data": match_data
    }

    return match_data, attack_data, defense_data, set_piece_data, transition_data