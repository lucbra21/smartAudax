# INSTALACIÓN STATSBOMB
# pip install statsbombpy

# IMPORTACIÓN LIRERÍAS ESPECIFICA STATASBOMB

import pandas as pd
import numpy as np
from statsbombpy import sb
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from dotenv import load_dotenv
import os

# --------------------------
# Funciones de extracción
# --------------------------
def get_credentials():
    SB_USERNAME = os.getenv("STATSBOMB_USERNAME")
    SB_PASSWORD = os.getenv("STATSBOMB_PASSWORD")
    return {"user": SB_USERNAME, "passwd": SB_PASSWORD}

def extract_matches(creds):
    """Extrae los partidos de la competición y temporada indicadas."""
    matches = sb.matches(competition_id=103, season_id=315, creds=creds) # Chile, Primera Division 2025 
    return matches[matches['match_status'] == 'available']

def extract_available_ids(matches):
    """Devuelve una lista de IDs de partidos con estado 'available'."""
    ids = matches['match_id']
    print(len(ids))
    return ids

def extract_player_match_stats(creds, ids):
    """Extrae las estadísticas de jugador para cada partido y las concatena."""
    # Inicia con un partido de referencia para tener la estructura
    player_match_stats = sb.player_match_stats(match_id=3871964, creds=creds)
    for id in ids:
        new_df = sb.player_match_stats(match_id=id, creds=creds)
        player_match_stats = pd.concat([player_match_stats, new_df], ignore_index=True)
        print(f'Partido {id} completado en player_match_stats')
    return player_match_stats

def extract_competitions(creds):
    """Extrae la información de competiciones."""
    return sb.competitions(creds=creds)

def extract_player_season_stats(creds):
    """Extrae las estadísticas de jugadores a nivel de temporada."""
    return sb.player_season_stats(competition_id=103, season_id=107, creds=creds)

def extract_team_season_stats(creds):
    """Extrae las estadísticas de equipos a nivel de temporada."""
    return sb.team_season_stats(competition_id=103, season_id=107, creds=creds)

def extract_events(creds, ids):
    """Extrae los eventos para cada partido y los concatena."""
    events = pd.DataFrame()
    for id in ids:
        new_df = sb.events(match_id=id, creds=creds)
        events = pd.concat([events, new_df], ignore_index=True)
        print(f'Partido {id} completado en events')
    return events

def extract_lineups(creds, ids):
    """
    Extrae los lineups usando el método estándar de la librería.
    Cada llamada devuelve un diccionario, así que se envuelve en lista para generar una fila.
    """
    lineups = pd.DataFrame()
    for id in ids:
        new_data = sb.lineups(match_id=id, creds=creds)
        new_df = pd.DataFrame([new_data])  # Convertir dict a fila de DataFrame
        lineups = pd.concat([lineups, new_df], ignore_index=True)
        print(f'Partido {id} completado en lineups')
    return lineups

def extract_team_match_stats(player_match_stats):
    """
    A partir de las estadísticas de jugador, se agrupa y se calcula la suma (o promedio)
    para generar las estadísticas de equipo por partido, con las correcciones necesarias.
    """
    # Primero, agrupamos las estadísticas sumando o usando el agregado apropiado
    # Se eliminan las columnas duplicadas y se corrigen los métodos de agregación
    print(f"Partido en team_match_stats")
    team_match_stats = player_match_stats.groupby(['match_id', 'team_name',
                                               'team_id', 'account_id']).agg({'player_match_minutes':'sum',
                                                                              'player_match_np_xg_per_shot':'sum',
                                                                              'player_match_np_xg':'sum',
                                                                              'player_match_np_shots':'sum',
                                                                              'player_match_goals':'sum',
                                                                              'player_match_xa':'sum',
                                                                              'player_match_key_passes':'sum',
                                                                              'player_match_np_xg':'sum',
                                                                              'player_match_assists':'sum',
                                                                              'player_match_through_balls':'sum',                                                                              
                                                                              'player_match_passes_into_box':'sum',
                                                                              'player_match_touches_inside_box':'sum',
                                                                              'player_match_tackles':'sum',
                                                                              'player_match_interceptions':'sum',
                                                                              'player_match_possession':'sum',
                                                                              'player_match_dribbles_faced':'sum',
                                                                              'player_match_touches_inside_box':'sum',
                                                                              'player_match_dribbles':'sum',
                                                                              'player_match_challenge_ratio':'mean',
                                                                              'player_match_fouls':'sum',                                                                              
                                                                              'player_match_dispossessions':'sum',
                                                                              'player_match_long_balls':'sum',
                                                                              'player_match_successful_long_balls':'sum',
                                                                              'player_match_long_ball_ratio':'mean',
                                                                              'player_match_shots_blocked':'sum',                                                                              
                                                                              'player_match_clearances':'sum',
                                                                              'player_match_aerials':'sum',
                                                                              'player_match_successful_aerials':'sum',
                                                                              'player_match_aerial_ratio':'mean',
                                                                              'player_match_passes':'sum',                                                                              
                                                                              'player_match_successful_passes':'sum',
                                                                              'player_match_passing_ratio':'mean',
                                                                              'player_match_op_passes':'sum',
                                                                              'player_match_forward_passes':'sum',
                                                                              'player_match_backward_passes':'sum',                                                                              
                                                                              'player_match_sideways_passes':'sum',
                                                                              'player_match_op_f3_passes':'sum',
                                                                              'player_match_op_f3_forward_passes':'sum',
                                                                              'player_match_op_f3_backward_passes':'sum',
                                                                              'player_match_op_f3_sideways_passes':'sum',                                                                              
                                                                              'player_match_np_shots_on_target':'sum',
                                                                              'player_match_crosses':'sum',
                                                                              'player_match_successful_crosses':'sum',
                                                                              'player_match_crossing_ratio':'mean',
                                                                              'player_match_penalties_won':'sum',                                                                              
                                                                              'player_match_passes_inside_box':'sum',
                                                                              'player_match_op_xa':'sum',
                                                                              'player_match_op_assists':'sum',
                                                                              'player_match_pressured_long_balls':'sum',
                                                                              'player_match_unpressured_long_balls':'sum',                                                                              
                                                                              'player_match_aggressive_actions':'sum',
                                                                              'player_match_turnovers':'sum',
                                                                              'player_match_crosses_into_box':'sum',
                                                                              'player_match_sp_xa':'sum',
                                                                              'player_match_op_shots':'sum',                                                                              
                                                                              'player_match_touches':'sum',
                                                                              'player_match_pressure_regains':'sum',
                                                                              'player_match_box_cross_ratio':'mean',
                                                                              'player_match_deep_progressions':'sum',
                                                                              'player_match_shot_touch_ratio':'mean',                                                                              
                                                                              'player_match_fouls_won':'sum',
                                                                              'player_match_xgchain':'sum',
                                                                              'player_match_op_xgchain':'sum',
                                                                              'player_match_xgbuildup':'sum',
                                                                              'player_match_op_xgbuildup':'sum',                                                                              
                                                                              'player_match_xgchain_per_possession':'sum',
                                                                              'player_match_op_xgchain_per_possession':'sum',
                                                                              'player_match_xgbuildup_per_possession':'sum',
                                                                              'player_match_op_xgbuildup_per_possession':'sum',
                                                                              'player_match_pressures':'sum',                                                                              
                                                                              'player_match_pressure_duration_total':'sum',
                                                                              'player_match_pressure_duration_avg':'sum',
                                                                              'player_match_pressured_action_fails':'sum',
                                                                              'player_match_counterpressures':'sum',
                                                                              'player_match_counterpressure_duration_total':'sum',                                                                              
                                                                              'player_match_counterpressure_duration_avg':'sum',
                                                                              'player_match_counterpressured_action_fails':'sum',
                                                                              'player_match_obv':'sum',
                                                                              'player_match_obv_pass':'sum',
                                                                              'player_match_obv_shot':'sum',                                                                              
                                                                              'player_match_obv_defensive_action':'sum',
                                                                              'player_match_obv_dribble_carry':'sum',
                                                                              'player_match_obv_gk':'sum',
                                                                              'player_match_deep_completions':'sum',
                                                                              'player_match_ball_recoveries':'sum',                                                                              
                                                                              'player_match_np_psxg':'sum',
                                                                              'player_match_penalties_faced':'sum',
                                                                              'player_match_penalties_conceded':'sum',
                                                                              'player_match_fhalf_ball_recoveries':'sum'})

    team_match_stats.reset_index(inplace=True)
    
    # Renombrar columnas
    rename_dict = {col: col.replace('player_match_', 'team_match_') for col in team_match_stats.columns}
    team_match_stats.rename(columns=rename_dict, inplace=True)
    
    # Recalcular ratios correctamente
    # 1. np_xg_per_shot
    team_match_stats['team_match_np_xg_per_shot'] = team_match_stats['team_match_np_xg'] / team_match_stats['team_match_np_shots'].replace(0, np.nan)
    
    # 2. long_ball_ratio
    team_match_stats['team_match_long_ball_ratio'] = team_match_stats['team_match_successful_long_balls'] / team_match_stats['team_match_long_balls'].replace(0, np.nan)
    
    # 3. aerial_ratio
    team_match_stats['team_match_aerial_ratio'] = team_match_stats['team_match_successful_aerials'] / team_match_stats['team_match_aerials'].replace(0, np.nan)
    
    # 4. passing_ratio
    team_match_stats['team_match_passing_ratio'] = team_match_stats['team_match_successful_passes'] / team_match_stats['team_match_passes'].replace(0, np.nan)
    
    # 5. crossing_ratio
    team_match_stats['team_match_crossing_ratio'] = team_match_stats['team_match_successful_crosses'] / team_match_stats['team_match_crosses'].replace(0, np.nan)
    
    # 6. box_cross_ratio
    team_match_stats['team_match_box_cross_ratio'] = team_match_stats['team_match_crosses_into_box'] / team_match_stats['team_match_crosses'].replace(0, np.nan)
    
    # 7. shot_touch_ratio
    team_match_stats['team_match_shot_touch_ratio'] = team_match_stats['team_match_np_shots'] / team_match_stats['team_match_touches'].replace(0, np.nan)
    
    # 8. challenge_ratio - definido como el ratio de desafíos ganados vs. enfrentados
    # Asumimos que no tenemos datos explícitos sobre desafíos ganados, así que tendríamos que calcularlo de otra forma
    # Por simplicidad, lo mantenemos como un cálculo basado en los tackles exitosos vs. intentados
    
    # 9. Recalcular promedios de duración para presiones y contrapresiones
    team_match_stats['team_match_pressure_duration_avg'] = team_match_stats['team_match_pressure_duration_total'] / team_match_stats['team_match_pressures'].replace(0, np.nan)
    
    team_match_stats['team_match_counterpressure_duration_avg'] = team_match_stats['team_match_counterpressure_duration_total'] / team_match_stats['team_match_counterpressures'].replace(0, np.nan)
    
    # 10. Recalcular métricas por posesión
    team_match_stats['team_match_xgchain_per_possession'] = team_match_stats['team_match_xgchain'] / team_match_stats['team_match_possession'].replace(0, np.nan)
    
    team_match_stats['team_match_op_xgchain_per_possession'] = team_match_stats['team_match_op_xgchain'] / team_match_stats['team_match_possession'].replace(0, np.nan)
    
    team_match_stats['team_match_xgbuildup_per_possession'] = team_match_stats['team_match_xgbuildup'] / team_match_stats['team_match_possession'].replace(0, np.nan)
    
    team_match_stats['team_match_op_xgbuildup_per_possession'] = team_match_stats['team_match_op_xgbuildup'] / team_match_stats['team_match_possession'].replace(0, np.nan)
    
    return team_match_stats

# --------------------------
# Función de exportación a CSV
# --------------------------
def export_csv(df, filepath):
    df.to_csv(filepath, encoding='utf-8', index=False)
    print(f'Exportado {filepath}')

# --------------------------
# Función principal
# --------------------------
def main():
    creds = get_credentials()

    # Extracción de datos
    matches = extract_matches(creds)
    available_ids = extract_available_ids(matches)
    
    player_match_stats = extract_player_match_stats(creds, available_ids)
    competitions = extract_competitions(creds)
    player_season_stats = extract_player_season_stats(creds)
    team_season_stats = extract_team_season_stats(creds)
    team_match_stats = extract_team_match_stats(player_match_stats)
    events = extract_events(creds, available_ids)
    lineups = extract_lineups(creds, available_ids)
    
    # Exportación a CSV (ajusta las rutas según necesites)
    export_csv(matches, 'outs_data/sb_matches.csv')
    export_csv(player_match_stats, 'outs_data/sb_player_match_stats.csv')
    export_csv(competitions, 'outs_data/sb_competitions.csv')
    export_csv(player_season_stats, 'outs_data/sb_player_season_stats.csv')
    export_csv(team_season_stats, 'outs_data/sb_team_season_stats.csv')
    export_csv(team_match_stats, 'outs_data/sb_team_match_stats.csv')
    export_csv(events, 'outs_data/sb_events.csv')
    export_csv(lineups, 'outs_data/sb_lineups.csv')
    
def extract_matches_only(creds):
    """
    Extrae únicamente los datos de matches para actualizar la lista disponible.
    """
    matches = extract_matches(creds)
    return matches

def extract_match_specific_data(creds, match_id):
    """
    Extrae datos específicos para un partido único sin almacenar en archivos.
    
    Args:
        creds: Credenciales de la API
        match_id: ID del partido específico
        
    Returns:
        dict: Diccionario con todos los datos del partido
    """
    # Obtener datos específicos del partido
    player_match_stats = extract_player_match_stats(creds, [match_id])
    team_match_stats = extract_team_match_stats(player_match_stats)
    events = extract_events(creds, [match_id])
    lineups = extract_lineups(creds, [match_id])

    match_data = {
        "player_match_stats": player_match_stats,
        "team_match_stats": team_match_stats,
        "events": events,
        "lineups": lineups
    }
    
    return match_data

def update_matches_only():
    """
    Actualiza únicamente el archivo de matches sin extraer todo el resto de datos.
    """
    creds = get_credentials()
    matches = extract_matches_only(creds)
    export_csv(matches, 'outs_data/sb_matches.csv')
    print("Archivo de matches actualizado exitosamente.")

def extract_historical_team_stats(creds, match_ids):
    """
    Extrae estadísticas de equipo para múltiples partidos específicos.
    
    Args:
        creds: Credenciales de la API
        match_ids: Lista de IDs de partidos
        
    Returns:
        pd.DataFrame: DataFrame con estadísticas de equipo de todos los partidos
    """
    all_team_stats = pd.DataFrame()
    
    for match_id in match_ids:
        try:
            print(f'Obteniendo estadísticas históricas para partido {match_id}...')
            # Obtener estadísticas de jugadores para este partido
            player_match_stats = extract_player_match_stats(creds, [match_id])
            # Convertir a estadísticas de equipo
            team_match_stats = extract_team_match_stats(player_match_stats)
            # Concatenar con el DataFrame principal
            all_team_stats = pd.concat([all_team_stats, team_match_stats], ignore_index=True)
        except Exception as e:
            print(f'Error al obtener datos del partido {match_id}: {e}')
            continue
    
    return all_team_stats

if __name__ == '__main__':
    main()
