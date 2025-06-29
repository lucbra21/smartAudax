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

# --------------------------
# Funciones de análisis mejorado
# --------------------------
def get_general_analysis(events):
    """
    Obtiene análisis general del partido incluyendo formaciones y goles.
    
    Args:
        creds: Credenciales de la API
        match_id: ID del partido
        
    Returns:
        dict: Diccionario con formaciones y datos de goles
    """

    print(events.columns)
    goals = events[(events['type'] == 'Shot') & (events['shot_outcome'] == 'Goal')]
    starting_xi = events[events['type'] == 'Starting XI']
    
    print("--------------------------------")
    print(starting_xi)
    # Extract formations
    formations = {}
    for _, row in starting_xi.iterrows():
        team = row['team']
        tactics = row.get('tactics', {})
        formation = tactics.get('formation')
        formations[team] = formation
    
    # Extract goal data
    goal_data = []
    for _, goal in goals.iterrows():
        goal_info = {
            'minute': goal.get('minute', ''),
            'second': goal.get('second', ''),
            'team': goal.get('team', {}).get('name', '') if isinstance(goal.get('team'), dict) else goal.get('team', ''),
            'player': goal.get('player', {}).get('name', '') if isinstance(goal.get('player'), dict) else goal.get('player', '')
        }
        goal_data.append(goal_info)

    return {
        'formations': formations, 
        'goals': goal_data,
        'total_goals': len(goal_data)
    }

def get_general_offensive_analysis(events):
    """
    Obtiene análisis ofensivo general del partido para ambos equipos.
    
    Args:
        creds: Credenciales de la API
        match_id: ID del partido
        
    Returns:
        dict: Diccionario con estadísticas ofensivas generales
    """
    
    # Get all shots and passes
    shots = events[events['type'] == 'Shot']
    passes = events[events['type'] == 'Pass']
    
    # Successful passes are those where pass_outcome is NaN
    successful_passes = passes[passes['pass_outcome'].isna()]
    
    # Long passes are those with pass_length > 20
    long_passes = passes[passes['pass_length'] > 20]
    successful_long_passes = successful_passes[successful_passes['pass_length'] > 20]

    key_stats = {
        'total_shots': len(shots),
        'total_passes': len(passes),
        'successful_passes': len(successful_passes),
        'pass_accuracy': len(successful_passes) / len(passes) if len(passes) > 0 else 0,
        'long_passes': len(long_passes),
        'successful_long_passes': len(successful_long_passes),
        'long_pass_accuracy': len(successful_long_passes) / len(long_passes) if len(long_passes) > 0 else 0,
        'xG_total': shots['shot_statsbomb_xg'].sum().round(2) if 'shot_statsbomb_xg' in shots.columns else 0
    }

    # Get top shooters
    top_shooters = shots['player'].apply(lambda x: x.get('name') if isinstance(x, dict) else x).value_counts().head(3)
    
    # Get top passers
    passes['player_name'] = passes['player'].apply(lambda x: x.get('name') if isinstance(x, dict) else x)
    successful_passes['player_name'] = successful_passes['player'].apply(lambda x: x.get('name') if isinstance(x, dict) else x)
    
    total_passes_per_player = passes['player_name'].value_counts()
    successful_passes_per_player = successful_passes['player_name'].value_counts()
    
    passing_stats = pd.DataFrame({
        'total_passes': total_passes_per_player,
        'successful_passes': successful_passes_per_player
    }).fillna(0)
    
    passing_stats['pass_success_pct'] = (passing_stats['successful_passes'] / passing_stats['total_passes'] * 100).round(1)
    top_passers = passing_stats.nlargest(3, 'total_passes')

    return {
        'key_stats': key_stats,
        'top_shooters': top_shooters,
        'top_passers': top_passers
    }

def get_general_defensive_analysis(events):
    """
    Obtiene análisis defensivo general del partido para ambos equipos.
    
    Args:
        creds: Credenciales de la API
        match_id: ID del partido
        
    Returns:
        dict: Diccionario con estadísticas defensivas generales
    """
    
    # Get different types of defensive events
    pressures = events[events['type'] == 'Pressure']
    duels = events[events['type'] == 'Duel']
    blocks = events[events['type'] == 'Block']
    interceptions = events[events['type'] == 'Interception']
    ball_recoveries = events[events['type'] == 'Ball Recovery']
    clearances = events[events['type'] == 'Clearance']
    
    successful_pressures = pressures[pressures['counterpress'] == True]
    won_duels = duels[duels['duel_outcome'].apply(lambda x: x == 'Won' or x == "Success In Play")]

    key_stats = {
        'pressures': len(pressures),
        'successful_pressures': len(successful_pressures),
        'pressure_success_rate': len(successful_pressures) / len(pressures) if len(pressures) > 0 else 0,
        'duels': len(duels),
        'won_duels': len(won_duels),
        'duel_success_rate': len(won_duels) / len(duels) if len(duels) > 0 else 0,
        'blocks': len(blocks),
        'interceptions': len(interceptions),
        'ball_recoveries': len(ball_recoveries),
        'clearances': len(clearances)
    }

    # Get top defenders
    pressures_per_player = pressures['player'].value_counts()
    duels_per_player = duels['player'].value_counts()
    interceptions_per_player = interceptions['player'].value_counts()
    
    defensive_stats = pd.DataFrame({
        'pressures': pressures_per_player,
        'duels': duels_per_player,
        'interceptions': interceptions_per_player
    }).fillna(0)
    
    defensive_stats['total_defensive_actions'] = (defensive_stats['pressures'] + 
                                                 defensive_stats['duels'] + 
                                                 defensive_stats['interceptions'])
    
    top_defenders = defensive_stats.nlargest(3, 'total_defensive_actions')

    return {
        'key_stats': key_stats,
        'top_defenders': top_defenders
    }

def get_general_transitions_analysis(events):
    """
    Obtiene análisis de transiciones general del partido para ambos equipos.
    
    Args:
        creds: Credenciales de la API
        match_id: ID del partido
        
    Returns:
        dict: Diccionario con estadísticas de transiciones generales
    """
    
    # Get transition-related events
    ball_recoveries = events[events['type'] == 'Ball Recovery']
    carries = events[events['type'] == 'Carry']
    pressures = events[events['type'] == 'Pressure']
    interceptions = events[events['type'] == 'Interception']
    
    successful_pressures = pressures[pressures['counterpress'] == True]

    key_stats = {
        'ball_recoveries': len(ball_recoveries),
        'carries': len(carries),
        'pressures': len(pressures),
        'successful_pressures': len(successful_pressures),
        'pressure_success_rate': len(successful_pressures) / len(pressures) if len(pressures) > 0 else 0,
        'interceptions': len(interceptions)
    }
    
    # Get top transition players
    recoveries_per_player = ball_recoveries['player'].value_counts()
    carries_per_player = carries['player'].value_counts()
    pressures_per_player = pressures['player'].value_counts()
    
    transition_stats = pd.DataFrame({
        'ball_recoveries': recoveries_per_player,
        'carries': carries_per_player,
        'pressures': pressures_per_player
    }).fillna(0)
    
    transition_stats['total_transition_actions'] = (transition_stats['ball_recoveries'] + 
                                                   transition_stats['carries'] + 
                                                   transition_stats['pressures'])
    
    top_transition_players = transition_stats.nlargest(3, 'total_transition_actions')

    return {
        'key_stats': key_stats,
        'top_transition_players': top_transition_players
    }

def get_general_set_pieces_analysis(events):
    """
    Obtiene análisis de pelota parada general del partido para ambos equipos.
    
    Args:
        creds: Credenciales de la API
        match_id: ID del partido
        
    Returns:
        dict: Diccionario con estadísticas de pelota parada generales
    """
    
    free_kicks = events[events['type'] == 'Foul Won']

    # Analyze set pieces using play_pattern column
    corners = events[(events['play_pattern'] == 'From Corner') & (events['type'] == 'Pass')]

    shots_from_free_kicks = events[(events['type'] == 'Shot') & (events['play_pattern'] == 'From Free Kick')]
    
    # Get passes from free kicks by checking next events after free kicks
    passes_from_free_kicks = pd.DataFrame()
    for _, free_kick in free_kicks.iterrows():
        # Get the next event after this free kick
        next_event = events[events['id'] > free_kick['id']].iloc[0] if len(events[events['id'] > free_kick['id']]) > 0 else None
        if next_event is not None and next_event['type'] == 'Pass' and pd.isna(next_event.get('pass_outcome')):
            passes_from_free_kicks = pd.concat([passes_from_free_kicks, pd.DataFrame([next_event])], ignore_index=True)
    
    # Get shots from corners by checking next events after corners
    shots_from_corners = pd.DataFrame()
    for _, corner in corners.iterrows():
        # Get the next event after this corner
        next_event = events[events['id'] > corner['id']].iloc[0] if len(events[events['id'] > corner['id']]) > 0 else None
        if next_event is not None and next_event['type'] == 'Shot':
            shots_from_corners = pd.concat([shots_from_corners, pd.DataFrame([next_event])], ignore_index=True)
    
    print(shots_from_corners)
    
    
    # Analyze passes from set pieces
    
    # Analyze successful passes from set pieces
    if not corners.empty:
        successful_passes_corners = corners[corners['pass_outcome'].isna()]
    else:
        successful_passes_corners = pd.DataFrame()
    if not passes_from_free_kicks.empty:
        successful_passes_free_kicks = passes_from_free_kicks[passes_from_free_kicks['pass_outcome'].isna()]
    else:
        successful_passes_free_kicks = pd.DataFrame()
    
    # Analyze goals from set pieces
    if not shots_from_corners.empty:
        goals_from_corners = shots_from_corners[shots_from_corners['shot_outcome'].apply(lambda x: x == 'Goal' if x else False)]
    else:
        goals_from_corners = pd.DataFrame()
    if not shots_from_free_kicks.empty:
        goals_from_free_kicks = shots_from_free_kicks[shots_from_free_kicks['type'].apply(lambda x: x == 'Goal' if x else False)]
    else:
        goals_from_free_kicks = pd.DataFrame()
    
    # Analyze crosses
    crosses = events[events['pass_cross'] == True]
    successful_crosses = crosses[crosses['pass_outcome'].isna()]
    
    key_stats = {
        'total_set_piece_events': len(corners) + len(free_kicks),
        'corners': len(corners),
        'free_kicks': len(free_kicks),
        'shots_from_free_kicks': len(shots_from_free_kicks),
        'goals_from_corners': len(goals_from_corners),
        'goals_from_free_kicks': len(goals_from_free_kicks),
        'total_goals_from_set_pieces': len(goals_from_corners) + len(goals_from_free_kicks),
        'passes_from_free_kicks': len(passes_from_free_kicks),
        'successful_passes_corners': len(successful_passes_corners),
        'successful_passes_free_kicks': len(successful_passes_free_kicks),
        'free_kick_pass_accuracy': len(successful_passes_free_kicks) / len(passes_from_free_kicks) if len(passes_from_free_kicks) > 0 else 0,
        'crosses': len(crosses),
        'successful_crosses': len(successful_crosses),
        'cross_accuracy': len(successful_crosses) / len(crosses) if len(crosses) > 0 else 0
    }

    return {
        'key_stats': key_stats,
    }

def get_offensive_analysis(events):
    """
    Obtiene análisis ofensivo detallado del partido para Audax Italiano.
    
    Args:
        creds: Credenciales de la API
        match_id: ID del partido
        
    Returns:
        dict: Diccionario con estadísticas ofensivas y top jugadores
    """
    events_audax = events[events['team'] == 'Audax Italiano']
    shots = events_audax[events_audax['type'] == 'Shot']
    passes = events_audax[events_audax['type'] == 'Pass']
    
    
    # Successful passes are those where pass_outcome is NaN (no outcome means successful)
    successful_passes = passes[passes['pass_outcome'].isna()]
    
    # Long passes are those with pass_length > 20
    long_passes = passes[passes['pass_length'] > 20]
    successful_long_passes = successful_passes[successful_passes['pass_length'] > 20]

    key_stats = {
        'total_shots': len(shots),
        'total_passes': len(passes),
        'successful_passes': len(successful_passes),
        'pass_accuracy': len(successful_passes) / len(passes) if len(passes) > 0 else 0,
        'long_passes': len(long_passes),
        'successful_long_passes': len(successful_long_passes),
        'long_pass_accuracy': len(successful_long_passes) / len(long_passes) if len(long_passes) > 0 else 0,
        'xG_total': shots['shot_statsbomb_xg'].sum().round(2) if 'shot_statsbomb_xg' in shots.columns else 0
    }

    # Get top shooters
    top_shooters = shots['player'].apply(lambda x: x.get('name') if isinstance(x, dict) else x).value_counts().head(3)
    
    # Calculate passing statistics for each player
    # Extract player names from passes
    passes['player_name'] = passes['player'].apply(lambda x: x.get('name') if isinstance(x, dict) else x)
    successful_passes['player_name'] = successful_passes['player'].apply(lambda x: x.get('name') if isinstance(x, dict) else x)
    
    # Count total passes and successful passes per player
    total_passes_per_player = passes['player_name'].value_counts()
    successful_passes_per_player = successful_passes['player_name'].value_counts()
    
    # Create a DataFrame with passing statistics
    passing_stats = pd.DataFrame({
        'total_passes': total_passes_per_player,
        'successful_passes': successful_passes_per_player
    }).fillna(0)
    
    # Calculate pass success percentage
    passing_stats['pass_success_pct'] = (passing_stats['successful_passes'] / passing_stats['total_passes'] * 100).round(1)
    
    # Get top passers by total passes
    top_passers_total = passing_stats.nlargest(3, 'total_passes')
    
    # Get top passers by success percentage (minimum 5 passes)
    top_passers_accuracy = passing_stats[passing_stats['total_passes'] >= 5].nlargest(3, 'pass_success_pct')


    return {
        'key_stats': key_stats,
        'top_shooters': top_shooters,
        'top_passers_total': top_passers_total,
        'top_passers_accuracy': top_passers_accuracy,
        'all_passing_stats': passing_stats
    }

def get_defensive_analysis(events):
    """
    Obtiene análisis defensivo detallado del partido para Audax Italiano.
    
    Args:
        creds: Credenciales de la API
        match_id: ID del partido
        
    Returns:
        dict: Diccionario con estadísticas defensivas y top defensores
    """
    events_audax = events[events['team'] == 'Audax Italiano']
    
    # Get different types of defensive events
    pressures = events_audax[events_audax['type'] == 'Pressure']
    duels = events_audax[events_audax['type'] == 'Duel']
    blocks = events_audax[events_audax['type'] == 'Block']
    interceptions = events_audax[events_audax['type'] == 'Interception']
    ball_recoveries = events_audax[events_audax['type'] == 'Ball Recovery']
    clearances = events_audax[events_audax['type'] == 'Clearance']
    

    successful_pressures = pressures[pressures['counterpress'] == True]


    won_duels = duels[duels['duel_outcome'].apply(lambda x: x == 'Won' or x == "Success In Play")]
    
    # Aerial duels
    aerial_duels = len(events[events['duel_type'].apply(lambda x: x == 'Aerial Lost')])
    won_aerial_duels = aerial_duels - len(duels[duels['duel_type'].apply(lambda x: x == 'Aerial Lost')])

    key_stats = {
        'pressures': len(pressures),
        'successful_pressures': len(successful_pressures),
        'pressure_success_rate': len(successful_pressures) / len(pressures) if len(pressures) > 0 else 0,
        'duels': len(duels),
        'won_duels': len(won_duels),
        'duel_success_rate': len(won_duels) / len(duels) if len(duels) > 0 else 0,
        'aerial_duels': aerial_duels,
        'won_aerial_duels': won_aerial_duels,
        'aerial_success_rate': won_aerial_duels / aerial_duels if aerial_duels > 0 else 0,
        'blocks': len(blocks),
        'interceptions': len(interceptions),
        'ball_recoveries': len(ball_recoveries),
        'clearances': len(clearances)
    }




    # Count defensive actions per player
    pressures_per_player = pressures['player'].value_counts()
    successful_pressures_per_player = successful_pressures['player'].value_counts()
    duels_per_player = duels['player'].value_counts()
    won_duels_per_player = won_duels['player'].value_counts()
    blocks_per_player = blocks['player'].value_counts()
    interceptions_per_player = interceptions['player'].value_counts()
    ball_recoveries_per_player = ball_recoveries['player'].value_counts()
    clearances_per_player = clearances['player'].value_counts()

    
    # Create comprehensive defensive stats DataFrame
    defensive_stats = pd.DataFrame({
        'pressures': pressures_per_player,
        'successful_pressures': successful_pressures_per_player,
        'duels': duels_per_player,
        'won_duels': won_duels_per_player,
        'blocks': blocks_per_player,
        'interceptions': interceptions_per_player,
        'ball_recoveries': ball_recoveries_per_player,
        'clearances': clearances_per_player
    }).fillna(0)
    
    # Calculate success rates
    defensive_stats['pressure_success_rate'] = (defensive_stats['successful_pressures'] / defensive_stats['pressures'] * 100).round(1)
    defensive_stats['duel_success_rate'] = (defensive_stats['won_duels'] / defensive_stats['duels'] * 100).round(1)
    
    # Calculate total defensive actions
    defensive_stats['total_defensive_actions'] = (defensive_stats['pressures'] + defensive_stats['duels'] + 
                                                 defensive_stats['blocks'] + defensive_stats['interceptions'] + 
                                                 defensive_stats['ball_recoveries'] + defensive_stats['clearances'])
    
    # Get top defenders by different metrics
    top_defenders_total_actions = defensive_stats.nlargest(3, 'total_defensive_actions')
    top_defenders_pressures = defensive_stats.nlargest(3, 'pressures')
    top_defenders_duels = defensive_stats.nlargest(3, 'duels')
    top_defenders_interceptions = defensive_stats.nlargest(3, 'interceptions')


    return {
        'key_stats': key_stats,
        'top_defenders_total_actions': top_defenders_total_actions,
        'top_defenders_pressures': top_defenders_pressures,
        'top_defenders_duels': top_defenders_duels,
        'top_defenders_interceptions': top_defenders_interceptions,
        'all_defensive_stats': defensive_stats
    }

def get_transitions_analysis(events):
    """
    Obtiene análisis de transiciones del partido para Audax Italiano.
    
    Args:
        creds: Credenciales de la API
        match_id: ID del partido
        
    Returns:
        dict: Diccionario con estadísticas de transiciones
    """
    events_audax = events[events['team'] == 'Audax Italiano']
    
    # Get transition-related events
    ball_recoveries = events_audax[events_audax['type'] == 'Ball Recovery']
    carries = events_audax[events_audax['type'] == 'Carry']
    pressures = events_audax[events_audax['type'] == 'Pressure']
    interceptions = events_audax[events_audax['type'] == 'Interception']
    
    # Filter successful pressures (counterpress)
    successful_pressures = pressures[pressures['counterpress'] == True]
    
    # Analyze carries by field zones
    # Assuming location is [x, y] where x is distance from goal (0-100)
    carries_from_def_3rd = carries[carries['location'].apply(lambda x: x[0] < 33 if x else False)]
    carries_from_mid_3rd = carries[carries['location'].apply(lambda x: 33 <= x[0] <= 66 if x else False)]
    carries_from_att_3rd = carries[carries['location'].apply(lambda x: x[0] > 66 if x else False)]
    
    # Analyze ball recoveries by field zones
    recoveries_in_def_3rd = ball_recoveries[ball_recoveries['location'].apply(lambda x: x[0] < 33 if x else False)]
    recoveries_in_mid_3rd = ball_recoveries[ball_recoveries['location'].apply(lambda x: 33 <= x[0] <= 66 if x else False)]
    recoveries_in_att_3rd = ball_recoveries[ball_recoveries['location'].apply(lambda x: x[0] > 66 if x else False)]

    key_stats = {
        'ball_recoveries': len(ball_recoveries),
        'recoveries_def_3rd': len(recoveries_in_def_3rd),
        'recoveries_mid_3rd': len(recoveries_in_mid_3rd),
        'recoveries_att_3rd': len(recoveries_in_att_3rd),
        'carries': len(carries),
        'carries_from_def_3rd': len(carries_from_def_3rd),
        'carries_from_mid_3rd': len(carries_from_mid_3rd),
        'carries_from_att_3rd': len(carries_from_att_3rd),
        'pressures': len(pressures),
        'successful_pressures': len(successful_pressures),
        'pressure_success_rate': len(successful_pressures) / len(pressures) if len(pressures) > 0 else 0,
        'interceptions': len(interceptions)
    }
    
    # Count transition actions per player
    recoveries_per_player = ball_recoveries['player'].value_counts()
    carries_per_player = carries['player'].value_counts()
    pressures_per_player = pressures['player'].value_counts()
    successful_pressures_per_player = successful_pressures['player'].value_counts()
    interceptions_per_player = interceptions['player'].value_counts()
    
    # Create comprehensive transition stats DataFrame
    transition_stats = pd.DataFrame({
        'ball_recoveries': recoveries_per_player,
        'carries': carries_per_player,
        'pressures': pressures_per_player,
        'successful_pressures': successful_pressures_per_player,
        'interceptions': interceptions_per_player
    }).fillna(0)
    
    # Calculate success rates
    transition_stats['pressure_success_rate'] = (transition_stats['successful_pressures'] / transition_stats['pressures'] * 100).round(1)
    
    # Calculate total transition actions
    transition_stats['total_transition_actions'] = (transition_stats['ball_recoveries'] + transition_stats['carries'] + 
                                                   transition_stats['pressures'] + transition_stats['interceptions'])
    
    # Get top players by different transition metrics
    top_transition_players = transition_stats.nlargest(3, 'total_transition_actions')
    top_recovery_players = transition_stats.nlargest(3, 'ball_recoveries')
    top_carry_players = transition_stats.nlargest(3, 'carries')
    top_pressure_players = transition_stats.nlargest(3, 'pressures')

    return {
        'key_stats': key_stats,
        'top_transition_players': top_transition_players,
        'top_recovery_players': top_recovery_players,
        'top_carry_players': top_carry_players,
        'top_pressure_players': top_pressure_players,
        'all_transition_stats': transition_stats
    }

def get_set_pieces_analysis(events):
    """
    Obtiene análisis de pelota parada general del partido para ambos equipos.
    
    Args:
        creds: Credenciales de la API
        match_id: ID del partido
        
    Returns:
        dict: Diccionario con estadísticas de pelota parada generales
    """

    events = events[events['team'] == 'Audax Italiano'].reset_index(drop=True)
    
    free_kicks = events[events['type'] == 'Foul Won']

    # Analyze set pieces using play_pattern column
    corners = events[(events['play_pattern'] == 'From Corner') & (events['type'] == 'Pass')]

    shots_from_free_kicks = events[(events['type'] == 'Shot') & (events['play_pattern'] == 'From Free Kick')]
    
    # Get passes from free kicks by checking next events after free kicks
    passes_from_free_kicks = pd.DataFrame()
    for _, free_kick in free_kicks.iterrows():
        # Get the next event after this free kick
        next_event = events[events['id'] > free_kick['id']].iloc[0] if len(events[events['id'] > free_kick['id']]) > 0 else None
        if next_event is not None and next_event['type'] == 'Pass' and pd.isna(next_event.get('pass_outcome')):
            passes_from_free_kicks = pd.concat([passes_from_free_kicks, pd.DataFrame([next_event])], ignore_index=True)
    
    # Get shots from corners by checking next events after corners
    shots_from_corners = pd.DataFrame()
    for _, corner in corners.iterrows():
        # Get the next event after this corner
        next_event = events[events['id'] > corner['id']].iloc[0] if len(events[events['id'] > corner['id']]) > 0 else None
        if next_event is not None and next_event['type'] == 'Shot':
            shots_from_corners = pd.concat([shots_from_corners, pd.DataFrame([next_event])], ignore_index=True)
    
    print(shots_from_corners)
    
    
    # Analyze passes from set pieces
    
    # Analyze successful passes from set pieces
    if not corners.empty:
        successful_passes_corners = corners[corners['pass_outcome'].isna()]
    else:
        successful_passes_corners = pd.DataFrame()
    if not passes_from_free_kicks.empty:
        successful_passes_free_kicks = passes_from_free_kicks[passes_from_free_kicks['pass_outcome'].isna()]
    else:
        successful_passes_free_kicks = pd.DataFrame()
    
    # Analyze goals from set pieces
    if not shots_from_corners.empty:
        goals_from_corners = shots_from_corners[shots_from_corners['shot_outcome'].apply(lambda x: x == 'Goal' if x else False)]
    else:
        goals_from_corners = pd.DataFrame()
    if not shots_from_free_kicks.empty:
        goals_from_free_kicks = shots_from_free_kicks[shots_from_free_kicks['type'].apply(lambda x: x == 'Goal' if x else False)]
    else:
        goals_from_free_kicks = pd.DataFrame()
    
    # Analyze crosses
    crosses = events[events['pass_cross'] == True]
    successful_crosses = crosses[crosses['pass_outcome'].isna()]
    
    key_stats = {
        'total_set_piece_events': len(corners) + len(free_kicks),
        'corners': len(corners),
        'free_kicks': len(free_kicks),
        'shots_from_free_kicks': len(shots_from_free_kicks),
        'goals_from_corners': len(goals_from_corners),
        'goals_from_free_kicks': len(goals_from_free_kicks),
        'total_goals_from_set_pieces': len(goals_from_corners) + len(goals_from_free_kicks),
        'passes_from_free_kicks': len(passes_from_free_kicks),
        'successful_passes_corners': len(successful_passes_corners),
        'successful_passes_free_kicks': len(successful_passes_free_kicks),
        'free_kick_pass_accuracy': len(successful_passes_free_kicks) / len(passes_from_free_kicks) if len(passes_from_free_kicks) > 0 else 0,
        'crosses': len(crosses),
        'successful_crosses': len(successful_crosses),
        'cross_accuracy': len(successful_crosses) / len(crosses) if len(crosses) > 0 else 0
    }

    return {
        'key_stats': key_stats,
    }
