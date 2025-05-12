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
load_dotenv() 
def get_credentials():
    #SB_USERNAME = os.getenv("STATSBOMB_USERNAME")
    #SB_PASSWORD = os.getenv("STATSBOMB_PASSWORD")
    SB_USERNAME = "plataforma@audaxitaliano.cl"
    SB_PASSWORD = "1kC6oQjp"
    return {"user": SB_USERNAME, "passwd": SB_PASSWORD}

def extract_matches(creds):
    """Extrae los partidos de la competición y temporada indicadas."""
    matches = sb.matches(competition_id=103, season_id=107, creds=creds)
    return matches

def extract_available_ids(matches):
    """Devuelve una lista de IDs de partidos con estado 'available'."""
    ids = matches[matches['match_status'] == 'available']['match_id']
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

def extract_lineups_by_team(creds):
    """
    Alternativa: Extrae los lineups para equipos específicos (por ejemplo, 'Audax Italiano' y 'Coquimbo Unido')
    y los concatena.
    """
    teams = ['Audax Italiano', 'Coquimbo Unido']
    df_list = []
    for team in teams:
        df_team = sb.lineups(match_id=3871967, creds=creds)[team]
        df_list.append(df_team)
    df2 = pd.concat(df_list, ignore_index=True)
    return df2

def extract_team_match_stats(player_match_stats):
    """
    A partir de las estadísticas de jugador, se agrupa y se calcula la suma (o promedio)
    para generar las estadísticas de equipo por partido, con las correcciones necesarias.
    """
    # Primero, agrupamos las estadísticas sumando o usando el agregado apropiado
    # Se eliminan las columnas duplicadas y se corrigen los métodos de agregación
    sum_columns = [
        'player_match_minutes', 'player_match_np_xg', 'player_match_np_shots', 
        'player_match_goals', 'player_match_xa', 'player_match_key_passes',
        'player_match_assists', 'player_match_through_balls', 'player_match_passes_into_box',
        'player_match_touches_inside_box', 'player_match_tackles', 'player_match_interceptions',
        'player_match_possession', 'player_match_dribbles_faced', 'player_match_dribbles',
        'player_match_fouls', 'player_match_dispossessions', 'player_match_long_balls',
        'player_match_successful_long_balls', 'player_match_shots_blocked', 'player_match_clearances',
        'player_match_aerials', 'player_match_successful_aerials', 'player_match_passes',
        'player_match_successful_passes', 'player_match_op_passes', 'player_match_forward_passes',
        'player_match_backward_passes', 'player_match_sideways_passes', 'player_match_op_f3_passes',
        'player_match_op_f3_forward_passes', 'player_match_op_f3_backward_passes', 
        'player_match_op_f3_sideways_passes', 'player_match_np_shots_on_target', 'player_match_crosses',
        'player_match_successful_crosses', 'player_match_penalties_won', 'player_match_op_xa',
        'player_match_op_assists', 'player_match_pressured_long_balls', 'player_match_unpressured_long_balls',
        'player_match_aggressive_actions', 'player_match_turnovers', 'player_match_crosses_into_box',
        'player_match_sp_xa', 'player_match_op_shots', 'player_match_touches', 'player_match_pressure_regains',
        'player_match_deep_progressions', 'player_match_fouls_won', 'player_match_xgchain',
        'player_match_op_xgchain', 'player_match_xgbuildup', 'player_match_op_xgbuildup',
        'player_match_pressures', 'player_match_pressure_duration_total', 'player_match_pressured_action_fails',
        'player_match_counterpressures', 'player_match_counterpressure_duration_total',
        'player_match_counterpressured_action_fails', 'player_match_obv', 'player_match_obv_pass',
        'player_match_obv_shot', 'player_match_obv_defensive_action', 'player_match_obv_dribble_carry',
        'player_match_obv_gk', 'player_match_deep_completions', 'player_match_ball_recoveries',
        'player_match_np_psxg', 'player_match_penalties_faced', 'player_match_penalties_conceded',
        'player_match_fhalf_ball_recoveries'
    ]
    
    # Crear diccionario de agregación
    agg_dict = {col: 'sum' for col in sum_columns}
    
    # Agrupar y agregar
    team_match_stats = player_match_stats.groupby(['match_id', 'team_name', 'team_id', 'account_id']).agg(agg_dict)
    team_match_stats.reset_index(inplace=True)
    
    # Renombrar columnas
    rename_dict = {col: col.replace('player_match_', 'team_match_') for col in sum_columns}
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
    # Si prefieres el método alternativo:
    # lineups_alt = extract_lineups_by_team(creds)
    
    # Exportación a CSV (ajusta las rutas según necesites)
    export_csv(matches, 'sb_matches.csv')
    export_csv(player_match_stats, 'sb_player_match_stats.csv')
    export_csv(competitions, 'sb_competitions.csv')
    export_csv(player_season_stats, 'sb_player_season_stats.csv')
    export_csv(team_season_stats, 'sb_team_season_stats.csv')
    export_csv(team_match_stats, 'sb_team_match_stats.csv')
    export_csv(events, 'sb_events.csv')
    export_csv(lineups, 'sb_lineups.csv')
    
if __name__ == '__main__':
    main()
