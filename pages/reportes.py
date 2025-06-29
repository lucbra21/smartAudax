### APP STREAMLIT

import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import re
from io import BytesIO
from data.extraccion_datos import update_matches_only
import matplotlib.pyplot as plt
import mplsoccer
from mplsoccer import Pitch
# IMPORTS DE FUNCIONES DEL GENERADOR
from common.generador import (
    chatgpt_api,
    generate_prompt_matches,
    generate_prompt_ataque,
    generate_prompt_defensa,
    generate_prompt_pelota_parada,
    generate_prompt_transiciones,
)

from common.match_data import generar_datos


def limpiar_texto_pdf(texto, max_palabra=50):
    """
    Limpia el texto para evitar errores con FPDF, pero sin cortar en líneas.
    """
    
    # Reemplazar caracteres Unicode problemáticos
    texto = texto.replace('–', '-')  # En dash por guión normal
    texto = texto.replace('—', '-')  # Em dash por guión normal
    texto = texto.replace('…', '...')  # Ellipsis por puntos
    texto = texto.replace('"', '"')  # Smart quotes por comillas normales
    texto = texto.replace('"', '"')
    texto = texto.replace(''', "'")  # Smart apostrophe por apóstrofe normal
    texto = texto.replace(''', "'")
    texto = texto.replace('°', ' grados')  # Degree symbol
    texto = texto.replace('×', 'x')  # Multiplication sign
    texto = texto.replace('÷', '/')  # Division sign
    texto = texto.replace('±', '+/-')  # Plus-minus sign
    
    # Reemplazar saltos de línea múltiples por uno solo
    texto = re.sub(r'\n\s*\n', '\n\n', texto)
    
    # Limpiar espacios en blanco
    texto = texto.replace('\t', ' ').replace('\r', '').strip()

    # Dividir solo palabras largas
    palabras = texto.split()
    palabras_procesadas = []
    for palabra in palabras:
        if len(palabra) > max_palabra:
            trozos = [palabra[i:i+max_palabra] for i in range(0, len(palabra), max_palabra)]
            palabras_procesadas.extend(trozos)
        else:
            palabras_procesadas.append(palabra)

    return ' '.join(palabras_procesadas)


def formatear_texto_para_pdf(texto):
    """
    Formatea el texto para el PDF, preservando la estructura pero eliminando marcadores de markdown.
    """
    # Dividir el texto en párrafos
    parrafos = texto.split('\n\n')
    texto_formateado = ""
    
    for parrafo in parrafos:
        # Limpiar marcadores de markdown
        parrafo_limpio = limpiar_texto_pdf(parrafo)
        
        # Añadir el párrafo al texto formateado
        texto_formateado += parrafo_limpio + "\n\n"
    
    return texto_formateado


def actualizar_extraccion():
    """
    Actualiza únicamente el archivo de matches sin extraer todos los datos.
    """
    try:
        update_matches_only()
        return True, "Lista de partidos actualizada exitosamente."
    except Exception as e:
        return False, f"Error al actualizar la lista de partidos: {str(e)}"


def generar_visualizaciones_ataque(attack_data, pdf):
    """Genera visualizaciones para la sección de ataque."""
    # Crear figura con dos subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    # 1. Mapa de tiros (mitad del campo para mejor visibilidad)
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='#c7d5cc')
    pitch.draw(ax=ax1)
    
    # Filtrar eventos de tiro
    shots = attack_data[attack_data["type"] == "Shot"].copy()
    
    # Extraer coordenadas de inicio y fin
    shots['start_x'] = shots['location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    shots['start_y'] = shots['location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    shots['end_x'] = shots['shot_end_location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    shots['end_y'] = shots['shot_end_location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    
    # Eliminar filas con coordenadas inválidas
    shots = shots.dropna(subset=['start_x', 'start_y', 'end_x', 'end_y'])
    
    # Separar tiros por resultado
    goals = shots[shots["shot_outcome"] == "Goal"]
    on_target = shots[(shots["shot_outcome"] == "Saved")]
    off_target = shots[shots["shot_outcome"] == "Off T"]
    
    # Plotear tiros
    if not goals.empty:
        pitch.scatter(goals['start_x'], goals['start_y'], ax=ax1, color='green', marker='*', s=200, label='Goles')
        pitch.arrows(
            goals['start_x'], goals['start_y'],
            goals['end_x'], goals['end_y'],
            ax=ax1, color='green', width=2, headwidth=5, headlength=5, alpha=0.6
        )
    
    if not on_target.empty:
        pitch.scatter(on_target['start_x'], on_target['start_y'], ax=ax1, color='yellow', marker='o', s=100, label='A puerta')
        pitch.arrows(
            on_target['start_x'], on_target['start_y'],
            on_target['end_x'], on_target['end_y'],
            ax=ax1, color='yellow', width=2, headwidth=5, headlength=5, alpha=0.6
        )
    
    if not off_target.empty:
        pitch.scatter(off_target['start_x'], off_target['start_y'], ax=ax1, color='red', marker='x', s=100, label='Fuera')
        pitch.arrows(
            off_target['start_x'], off_target['start_y'],
            off_target['end_x'], off_target['end_y'],
            ax=ax1, color='red', width=2, headwidth=5, headlength=5, alpha=0.6
        )
    
    # Configurar vista de mitad del campo (solo zona ofensiva)
    ax1.set_xlim(60, 120)  # Solo mostrar desde la línea media hacia adelante
    ax1.set_title('Mapa de Tiros (Zona Ofensiva)', fontsize=15)
    ax1.legend()
    
    # 2. Mapa de pases progresivos
    pitch2 = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='#c7d5cc')
    pitch2.draw(ax=ax2)
    
    # Filtrar pases
    passes = attack_data[attack_data["type"] == "Pass"].copy()
    
    # Extraer coordenadas de inicio y fin
    passes['start_x'] = passes['location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    passes['start_y'] = passes['location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    passes['end_x'] = passes['pass_end_location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    passes['end_y'] = passes['pass_end_location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    
    # Eliminar filas con coordenadas inválidas
    passes = passes.dropna(subset=['start_x', 'start_y', 'end_x', 'end_y'])
    
    # Calcular pases progresivos
    # Un pase es progresivo si:
    # 1. Se mueve al menos 10 metros hacia adelante
    # 2. El punto final está en el tercio ofensivo del campo
    passes['distance_forward'] = passes['end_x'] - passes['start_x']
    passes['is_progressive'] = (passes['distance_forward'] >= 10) & (passes['end_x'] >= 80)
    
    # Filtrar pases progresivos
    progressive_passes = passes[passes['is_progressive']]
    
    # Separar pases completados e incompletos
    completed_passes = progressive_passes[progressive_passes['pass_outcome'].isna()]
    incomplete_passes = progressive_passes[progressive_passes['pass_outcome'].notna()]
    
    # Plotear pases progresivos completados
    if not completed_passes.empty:
        pitch2.arrows(
            completed_passes['start_x'],
            completed_passes['start_y'],
            completed_passes['end_x'],
            completed_passes['end_y'],
            ax=ax2,
            color='blue',
            width=2,
            headwidth=5,
            headlength=5,
            alpha=0.6,
            label='Completados'
        )
    
    # Plotear pases progresivos incompletos
    if not incomplete_passes.empty:
        pitch2.arrows(
            incomplete_passes['start_x'],
            incomplete_passes['start_y'],
            incomplete_passes['end_x'],
            incomplete_passes['end_y'],
            ax=ax2,
            color='red',
            width=2,
            headwidth=5,
            headlength=5,
            alpha=0.6,
            label='Incompletos'
        )
    
    ax2.set_title('Pases Progresivos', fontsize=15)
    ax2.legend()
    
    # Guardar figura
    plt.tight_layout()
    fig_path = 'temp_attack_viz.png'
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Añadir al PDF
    pdf.image(fig_path, x=10, y=None, w=190)
    os.remove(fig_path)

def generar_visualizaciones_defensa(defense_data, pdf):
    """Genera visualizaciones para la sección de defensa."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    # 1. Línea media de recuperaciones y pérdidas
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='#c7d5cc')
    pitch.draw(ax=ax1)
    
    # Filtrar recuperaciones y pérdidas
    recoveries = defense_data[defense_data["type"] == "Ball Recovery"].copy()
    dispossessions = defense_data[defense_data["type"] == "Dispossessed"].copy()
    
    # Extraer coordenadas
    recoveries['x'] = recoveries['location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    recoveries['y'] = recoveries['location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    dispossessions['x'] = dispossessions['location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    dispossessions['y'] = dispossessions['location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    
    # Eliminar filas con coordenadas inválidas
    recoveries = recoveries.dropna(subset=['x', 'y'])
    dispossessions = dispossessions.dropna(subset=['x', 'y'])
    
    # Plotear recuperaciones y pérdidas
    if not recoveries.empty:
        pitch.scatter(recoveries['x'], recoveries['y'], ax=ax1, color='green', marker='o', s=100, label='Recuperaciones')
        
        # Calcular y mostrar línea promedio de recuperaciones en X (profundidad)
        avg_recovery_x = recoveries['x'].mean()
        
        # Dibujar línea vertical en la posición promedio de recuperaciones
        ax1.axvline(x=avg_recovery_x, color='green', linestyle='-', alpha=0.8, linewidth=5, label=f'Línea Promedio Recuperaciones (X={avg_recovery_x:.1f})')
        
        # Calcular porcentaje de recuperaciones por tercio
        # Tercio defensivo: 0-40, Tercio medio: 40-80, Tercio ofensivo: 80-120
        defensive_third = len(recoveries[recoveries['x'] <= 40])
        middle_third = len(recoveries[(recoveries['x'] > 40) & (recoveries['x'] <= 80)])
        offensive_third = len(recoveries[recoveries['x'] > 80])
        total_recoveries = len(recoveries)
        
        defensive_pct = (defensive_third / total_recoveries) * 100
        middle_pct = (middle_third / total_recoveries) * 100
        offensive_pct = (offensive_third / total_recoveries) * 100
        
        # Mostrar estadísticas de recuperaciones por tercio
        ax1.text(10, 85, f'Recuperaciones por Tercio:\nDefensivo: {defensive_pct:.1f}%\nMedio: {middle_pct:.1f}%\nOfensivo: {offensive_pct:.1f}%', 
                fontsize=10, color='white', bbox=dict(boxstyle="round,pad=0.3", facecolor='green', alpha=0.7))
        
    
    
    ax1.set_title('Recuperaciones', fontsize=15)
    ax1.legend()
    
    # 2. Mapa de presión y forma defensiva
    pitch2 = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='#c7d5cc')
    pitch2.draw(ax=ax2)
    
    # Filtrar presiones y tackles
    pressures = defense_data[defense_data["type"] == "Pressure"].copy()
    tackles = defense_data[defense_data["type"] == "Tackle"].copy()
    interceptions = defense_data[defense_data["type"] == "Interception"].copy()
    
    # Extraer coordenadas
    pressures['x'] = pressures['location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    pressures['y'] = pressures['location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    tackles['x'] = tackles['location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    tackles['y'] = tackles['location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    interceptions['x'] = interceptions['location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    interceptions['y'] = interceptions['location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    
    # Eliminar filas con coordenadas inválidas
    pressures = pressures.dropna(subset=['x', 'y'])
    tackles = tackles.dropna(subset=['x', 'y'])
    interceptions = interceptions.dropna(subset=['x', 'y'])
    
    # Crear mapa de calor de presiones
    if not pressures.empty:
        # Crear bins para el mapa de calor
        bin_statistic = pitch2.bin_statistic(
            pressures['x'],
            pressures['y'],
            statistic='count',
            bins=(6, 4)
        )
        
        # Calcular porcentajes para cada zona
        total_pressures = bin_statistic['statistic'].sum()
        if total_pressures > 0:
            bin_statistic['statistic'] = (bin_statistic['statistic'] / total_pressures) * 100
            
            # Plotear mapa de calor
            pitch2.heatmap(bin_statistic, ax=ax2, cmap='Reds', edgecolors='#22312b', alpha=0.6)
    
    # Plotear tackles e intercepciones
    if not tackles.empty:
        pitch2.scatter(tackles['x'], tackles['y'], ax=ax2, color='orange', marker='s', s=80, label='Tackles', zorder=3)
    if not interceptions.empty:
        pitch2.scatter(interceptions['x'], interceptions['y'], ax=ax2, color='yellow', marker='^', s=80, label='Intercepciones', zorder=3)
    
    # Añadir zonas defensivas
    # Zona de presión alta (último tercio)
    ax2.axvspan(80, 120, alpha=0.2, color='red', label='Zona de Presión Alta')
    # Zona de presión media (tercio medio)
    ax2.axvspan(40, 80, alpha=0.1, color='orange', label='Zona de Presión Media')

    
    ax2.set_title('Mapa de Presión y Forma Defensiva', fontsize=15)
    ax2.legend()
    
    # Guardar figura
    plt.tight_layout()
    fig_path = 'temp_defense_viz.png'
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()

    
    # Añadir al PDF
    pdf.image(fig_path, x=10, y=None, w=190)
    os.remove(fig_path)

def generar_visualizaciones_pelota_parada(set_piece_data, pdf):
    """Genera visualizaciones para la sección de pelota parada."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    # 1. Mapa de córners
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='#c7d5cc')
    pitch.draw(ax=ax1)

    
    # Filtrar córners (pases desde las esquinas)
    corners = set_piece_data[
        (set_piece_data["type"] == "Pass") &
        (
            # Esquina superior derecha
            ((set_piece_data["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) >= 120) &
             (set_piece_data["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 80)) |
            # Esquina superior izquierda
            ((set_piece_data["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) >= 120) &
             (set_piece_data["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 0)) |
            # Esquina inferior derecha
            ((set_piece_data["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) <= 0) &
             (set_piece_data["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 80)) |
            # Esquina inferior izquierda
            ((set_piece_data["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) <= 0) &
             (set_piece_data["location"].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else 0) == 0))
        )
    ].copy()
    
    # Extraer coordenadas de inicio y fin
    corners['start_x'] = corners['location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    corners['start_y'] = corners['location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    corners['end_x'] = corners['pass_end_location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    corners['end_y'] = corners['pass_end_location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    
    # Eliminar filas con coordenadas inválidas
    corners = corners.dropna(subset=['start_x', 'start_y', 'end_x', 'end_y'])
    
    # Separar córners completados e incompletos
    completed_corners = corners[corners.get("pass_outcome", "") == "Success"]
    incomplete_corners = corners[corners.get("pass_outcome", "") != "Success"]
    
    if not completed_corners.empty:
        # Plotear córners completados como flechas verdes
        pitch.arrows(
            completed_corners['start_x'], completed_corners['start_y'],
            completed_corners['end_x'], completed_corners['end_y'],
            ax=ax1, color='green', alpha=0.6,
            width=2, headwidth=5, headlength=5,
            label='Córners completados'
        )
    
    if not incomplete_corners.empty:
        # Plotear córners incompletos como flechas rojas
        pitch.arrows(
            incomplete_corners['start_x'], incomplete_corners['start_y'],
            incomplete_corners['end_x'], incomplete_corners['end_y'],
            ax=ax1, color='red', alpha=0.6,
            width=2, headwidth=5, headlength=5,
            label='Córners incompletos'
        )
    
    ax1.set_title('Córners', fontsize=15)
    ax1.legend()
    
    # 2. Mapa de tiros libres
    pitch2 = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='#c7d5cc')
    pitch2.draw(ax=ax2)
    
    # Filtrar tiros libres (faltas en el último tercio)
    free_kicks = set_piece_data[
        (set_piece_data["type"] == "Foul Won") &
        (set_piece_data["location"].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else 0) >= 80)
    ].copy()
    # Extraer coordenadas
    free_kicks['x'] = free_kicks['location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    free_kicks['y'] = free_kicks['location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    
    # Eliminar filas con coordenadas inválidas
    free_kicks = free_kicks.dropna(subset=['x', 'y'])
    
    if not free_kicks.empty:
        # Plotear tiros libres como puntos
        pitch2.scatter(
            free_kicks['x'], free_kicks['y'],
            ax=ax2, color='red', marker='o', s=100,
            label='Tiros libres'
        )
    
    ax2.set_title('Tiros Libres', fontsize=15)
    ax2.legend()
    
    # Guardar figura
    plt.tight_layout()
    fig_path = 'temp_set_piece_viz.png'
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Añadir al PDF
    pdf.image(fig_path, x=10, y=None, w=190)
    os.remove(fig_path)

def generar_visualizaciones_transiciones(transition_data, pdf):
    """Genera visualizaciones para la sección de transiciones."""
    fig, (ax1) = plt.subplots(1, figsize=(10, 10))
    
    # 1. Mapa de contragolpes y carreras progresivas
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='#c7d5cc')
    pitch.draw(ax=ax1)
    
    # Filtrar contragolpes (recuperaciones seguidas de pases o carreras)
    counter_attacks = transition_data[
        (transition_data["type"].isin(["Ball Recovery", "Interception"])) |
        (transition_data["type"].isin(["Pass", "Carry"]))
    ].copy()
    
    # Agrupar eventos por secuencia
    counter_attacks['sequence'] = counter_attacks.groupby(
        (counter_attacks['type'].isin(['Ball Recovery', 'Interception'])).cumsum()
    ).cumcount()
    
    # Filtrar solo las primeras acciones después de recuperación (secuencia 1)
    counter_attacks = counter_attacks[counter_attacks['sequence'] == 1]
    
    # Extraer coordenadas
    counter_attacks['start_x'] = counter_attacks['location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    counter_attacks['start_y'] = counter_attacks['location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    counter_attacks['end_x'] = counter_attacks['pass_end_location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    counter_attacks['end_y'] = counter_attacks['pass_end_location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    
    # Eliminar filas con coordenadas inválidas
    counter_attacks = counter_attacks.dropna(subset=['start_x', 'start_y', 'end_x', 'end_y'])
    
    if not counter_attacks.empty:
        # Plotear contragolpes como flechas
        pitch.arrows(
            counter_attacks['start_x'], counter_attacks['start_y'],
            counter_attacks['end_x'], counter_attacks['end_y'],
            ax=ax1, color='red', alpha=0.6,
            width=2, headwidth=5, headlength=5,
            label='Contragolpes'
        )
    
    # Filtrar carreras progresivas (avance significativo)
    progressive_carries = transition_data[
        (transition_data["type"] == "Carry")
    ].copy()
    
    # Extraer coordenadas
    progressive_carries['start_x'] = progressive_carries['location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    progressive_carries['start_y'] = progressive_carries['location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    progressive_carries['end_x'] = progressive_carries['carry_end_location'].apply(lambda x: float(x[0]) if isinstance(x, list) and len(x) >= 2 else None)
    progressive_carries['end_y'] = progressive_carries['carry_end_location'].apply(lambda x: float(x[1]) if isinstance(x, list) and len(x) >= 2 else None)
    
    # Eliminar filas con coordenadas inválidas
    progressive_carries = progressive_carries.dropna(subset=['start_x', 'start_y', 'end_x', 'end_y'])
    
    if not progressive_carries.empty:
        # Calcular progresión (avance en el eje x)
        progressive_carries['progression'] = progressive_carries['end_x'] - progressive_carries['start_x']
        
        # Filtrar solo carreras con progresión significativa (> 10 metros)
        progressive_carries = progressive_carries[progressive_carries['progression'] > 10]
        
        if not progressive_carries.empty:
            # Plotear carreras progresivas como flechas
            pitch.arrows(
                progressive_carries['start_x'], progressive_carries['start_y'],
                progressive_carries['end_x'], progressive_carries['end_y'],
                ax=ax1, color='yellow', alpha=0.6,
                width=2, headwidth=5, headlength=5,
                label='Carreras progresivas'
            )
    
    ax1.set_title('Contragolpes y Carreras Progresivas', fontsize=15)
    ax1.legend()
    
    # Guardar figura
    plt.tight_layout()
    fig_path = 'temp_transition_viz.png'
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Añadir al PDF
    pdf.image(fig_path, x=10, y=None, w=190)
    os.remove(fig_path)

def generar_reporte(id_partido, local, visitante):
    # Determine if this is an Audax match for proper labeling
    audax_participa = local == "Audax Italiano" or visitante == "Audax Italiano"

    print(id_partido)
    
    if audax_participa:
        st.write(f"🔍 Generando análisis enfocado en Audax Italiano: {local} vs. {visitante}")
    else:
        st.write(f"📊 Generando análisis general del partido: {local} vs. {visitante}")
    
    # Progress bar para seguimiento
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Paso 1: Obtener datos del partido (incluyendo históricos)
        if audax_participa:
            status_text.text("Obteniendo datos de Audax y estadísticas históricas...")
        else:
            status_text.text("Obteniendo datos del partido...")
        progress_bar.progress(5)
        
        # Obtener todos los datos del partido desde match_data.py
        match_data, attack_data, defense_data, set_piece_data, transition_data, events_audax = generar_datos(id_partido, local, visitante)
        progress_bar.progress(40)
        
        # Extraer información del partido desde match_data
        match_info = match_data["match_info"]
        goles_local = int(match_info["goles_local"])
        goles_visitante = int(match_info["goles_visitante"])
        fecha_partido = match_info["fecha"]
        audax_participa_confirmed = match_info["audax_participa"]
        
        # Paso 2: Crear PDF
        status_text.text("Creando estructura del PDF...")
        progress_bar.progress(45)
        
        # Crear el objeto PDF con configuración personalizada
        pdf = FPDF()
        pdf.add_page()
        
        # Configurar fuentes y colores
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Definir colores de Audax (verde y rojo)
        audax_green = (0, 104, 71)  # RGB para el verde de Audax
        audax_red = (200, 16, 46)   # RGB para el rojo de Audax
        dark_gray = (64, 64, 64)    # RGB para texto oscuro
        
        # Función para añadir el encabezado con logo y número de página
        def add_header():
            # Guardar posición Y actual
            current_y = pdf.get_y()
            
            # Añadir logo en la esquina superior izquierda
            pdf.image("static/escudo_audax.png", x=10, y=10, w=30)
            
            # Añadir número de página en la esquina superior derecha
            pdf.set_font("Arial", "I", 8)
            pdf.set_text_color(*dark_gray)
            pdf.set_y(10)
            pdf.cell(0, 10, f"Pagina {pdf.page_no()}", ln=False, align="R")
            
            # Restaurar posición Y
            pdf.set_y(current_y)
        
        # Función para añadir sección con estilo
        def add_section(title, content):
            # Añadir espacio antes de la sección
            pdf.ln(10)
            
            # Limpiar el título y contenido para evitar errores de Unicode
            title_clean = limpiar_texto_pdf(title)
            content_clean = limpiar_texto_pdf(content)
            
            # Título de sección con estilo
            pdf.set_font("Arial", "B", 16)
            pdf.set_text_color(*audax_green)
            pdf.cell(0, 10, title_clean, ln=True, align="C")
            
            # Línea decorativa
            pdf.set_draw_color(*audax_green)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(5)
            
            # Contenido
            pdf.set_font("Arial", "", 12)
            pdf.set_text_color(*dark_gray)
            pdf.multi_cell(0, 8, content_clean)
        
        # Añadir encabezado a la primera página
        add_header()
        
        # Título principal con estilo
        pdf.set_font("Arial", "B", 24)
        pdf.set_text_color(*audax_green)
        pdf.cell(0, 20, "REPORTE DE ANÁLISIS", ln=True, align="C")
        
        # Información del partido
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(*dark_gray)
        if audax_participa_confirmed:
            es_audax_local = match_info["es_audax_local"]
            equipo_rival = match_info["equipo_rival"]
            pdf.cell(0, 15, f"AUDAX ITALIANO {'(Local)' if es_audax_local else '(Visitante)'}", ln=True, align="C")
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 12, f"vs. {equipo_rival}", ln=True, align="C")
        else:
            pdf.cell(0, 15, f"{local} vs. {visitante}", ln=True, align="C")
        
        # Resultado y fecha
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Resultado: {goles_local}-{goles_visitante}", ln=True, align="C")
        pdf.set_font("Arial", "", 14)
        pdf.cell(0, 10, f"Fecha: {fecha_partido}", ln=True, align="C")
        
        # Obtener análisis
        status_text.text("Preparando análisis...")
        progress_bar.progress(50)
        
        # Obtener prompts y realizar análisis
        prompt_match = generate_prompt_matches()
        prompt_ataque = generate_prompt_ataque()
        prompt_defensa = generate_prompt_defensa()
        prompt_pelota_parada = generate_prompt_pelota_parada()
        prompt_transiciones = generate_prompt_transiciones()
        
        # Realizar análisis con ChatGPT
        if audax_participa_confirmed:
            status_text.text("Analizando rendimiento de Audax...")
        else:
            status_text.text("Analizando rendimiento general...")
        progress_bar.progress(55)
        
        try:
            print(match_data)
            res_match = chatgpt_api(prompt_match, match_data)
        except Exception as e:
            res_match = f"[ERROR al analizar match]: {str(e)}"

        if audax_participa_confirmed:
            status_text.text("Analizando ataque de Audax...")
        else:
            status_text.text("Analizando fase ofensiva...")
        progress_bar.progress(65)
        try:
            res_ataque = chatgpt_api(prompt_ataque, attack_data)
        except Exception as e:
            res_ataque = f"[ERROR al analizar ataque]: {str(e)}"

        if audax_participa_confirmed:
            status_text.text("Analizando defensa de Audax...")
        else:
            status_text.text("Analizando fase defensiva...")
        progress_bar.progress(75)
        try:
            res_defensa = chatgpt_api(prompt_defensa, defense_data)
        except Exception as e:
            res_defensa = f"[ERROR al analizar defensa]: {str(e)}"

        if audax_participa_confirmed:
            status_text.text("Analizando pelota parada de Audax...")
        else:
            status_text.text("Analizando pelota parada del partido...")
        progress_bar.progress(80)
        try:
            res_pelota_parada = chatgpt_api(prompt_pelota_parada, set_piece_data)
        except Exception as e:
            res_pelota_parada = f"[ERROR al analizar pelota parada]: {str(e)}"

        if audax_participa_confirmed:
            status_text.text("Analizando transiciones de Audax...")
        else:
            status_text.text("Analizando transiciones del partido...")
        progress_bar.progress(85)
        try:
            res_transiciones = chatgpt_api(prompt_transiciones, transition_data)
        except Exception as e:
            res_transiciones = f"[ERROR al analizar transiciones]: {str(e)}"

        if audax_participa_confirmed:
            status_text.text("Generando conclusión del partido...")
        else:
            status_text.text("Generando conclusión general...")
        progress_bar.progress(90)

        progress_bar.progress(95)
        # Paso 5: Generar PDF final
        status_text.text("Generando PDF final...")
        

        add_section("Análisis General", res_match)

        # Añadir visualizaciones de ataque en la misma página
        add_section("Análisis Ofensivo", res_ataque)
        generar_visualizaciones_ataque(events_audax, pdf)
        
        # Añadir sección de defensa
        add_section("Análisis Defensivo", res_defensa)
        generar_visualizaciones_defensa(events_audax, pdf)
        
        # Añadir sección de pelota parada
        add_section("Análisis de Pelota Parada", res_pelota_parada)
        generar_visualizaciones_pelota_parada(events_audax, pdf)
        
        # Añadir sección de transiciones
        add_section("Análisis de Transiciones", res_transiciones)
        generar_visualizaciones_transiciones(events_audax, pdf)
                
        # Generar el nombre del archivo
        if audax_participa_confirmed:
            es_audax_local = match_info["es_audax_local"]
            equipo_rival = match_info["equipo_rival"]
            nombre_archivo = f"reporte_audax_{'local' if es_audax_local else 'visitante'}_{equipo_rival}_{fecha_partido}.pdf"
        else:
            nombre_archivo = f"reporte_general_{local}_{visitante}_{fecha_partido}.pdf"
        
        # Guardar el PDF en un buffer de memoria
        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)
        
        progress_bar.progress(100)
        status_text.text("¡Reporte completado!")
        
        # Mostrar el botón de descarga
        if audax_participa_confirmed:
            st.success("✅ Reporte de Audax Italiano generado exitosamente")
            button_text = "📥 Descargar reporte de Audax"
        else:
            st.success("✅ Reporte general del partido generado exitosamente")
            button_text = "📥 Descargar reporte general"
            
        st.download_button(
            button_text,
            data=pdf_buffer,
            file_name=nombre_archivo,
            mime="application/pdf"
        )
        
        progress_bar.empty()
        status_text.empty()
            
    except Exception as e:
        st.error(f"Error al generar el reporte: {str(e)}")


def main():
    st.set_page_config(page_title="Reportes Post-Partido", layout="wide", initial_sidebar_state="collapsed")
    

    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:

        st.image("static/escudo_audax.png", width=80)

    with col2:
        st.markdown("<h1 style='text-align: center;'>REPORTES POST-PARTIDO</h1>", unsafe_allow_html=True)
    
    
    # Información sobre el sistema dual
    st.info("""
    🎯 **Sistema de Análisis Inteligente**: 
    - 🟢 **Partidos de Audax**: Análisis enfocado con comparación histórica
    - 🔵 **Otros partidos**: Análisis general para scouting
    """)
    
    # Cargar datos de partidos
    if not os.path.exists("outs_data/sb_matches.csv"):
        st.error("❌ No se encontró el archivo de partidos. Por favor actualiza los datos primero.")
        return
    
    df_matches = pd.read_csv("outs_data/sb_matches.csv")
    if df_matches.empty:
        st.error("❌ No hay datos de partidos disponibles")
        return

    # Separar partidos según participación de Audax para mostrar estadísticas
    audax_matches = df_matches[
        (df_matches["home_team"] == "Audax Italiano") | 
        (df_matches["away_team"] == "Audax Italiano")
    ]
    
    non_audax_matches = df_matches[
        (df_matches["home_team"] != "Audax Italiano") & 
        (df_matches["away_team"] != "Audax Italiano")
    ]

    # Mostrar estadísticas del dataset
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📈 Total de Partidos", len(df_matches))
    with col2:
        st.metric("🟢 Partidos de Audax", len(audax_matches))
    with col3:
        st.metric("🔵 Otros Partidos", len(non_audax_matches))

    # Botón para actualizar partidos
    if st.button("🔄 Actualizar Partidos", help="Actualiza la lista de partidos desde StatsBomb API"):
        with st.spinner("Actualizando lista de partidos..."):
            try:
                update_matches_only()
                st.success("✅ Lista de partidos actualizada exitosamente")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al actualizar: {str(e)}")

    st.markdown("---")
    
    # Filtros en una misma línea usando columnas
    st.subheader("🔍 Filtros")
    col_filtro1, col_filtro2, col_filtro3 = st.columns([2, 2, 1])
    
    with col_filtro1:
        filtro_equipo = st.text_input("Equipo", key="filtro_equipo", placeholder="Ingrese equipo (ej: Audax Italiano)")
    with col_filtro2:
        # Convertir la columna de fecha a datetime si no lo está ya
        df_matches['match_date'] = pd.to_datetime(df_matches['match_date'])
        min_date = df_matches['match_date'].min()
        max_date = df_matches['match_date'].max()
        
        try:
            fecha_inicio, fecha_fin = st.date_input(
                "Rango de Fechas",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="filtro_fecha",
                format="DD/MM/YYYY"
            )
        except:
            fecha_inicio, fecha_fin = None, None
    
    # Aplicar filtros
    df_filtrado = df_matches.copy()
    df_filtrado = df_filtrado.sort_values(by="match_date", ascending=False)
    
    if fecha_inicio is not None and fecha_fin is not None:
        df_filtrado = df_filtrado[
            (df_filtrado["match_date"].dt.date >= fecha_inicio) & 
            (df_filtrado["match_date"].dt.date <= fecha_fin)
        ]
    if filtro_equipo:
        df_filtrado = df_filtrado[
            df_filtrado["away_team"].str.contains(filtro_equipo, case=False, na=False) | 
            df_filtrado["home_team"].str.contains(filtro_equipo, case=False, na=False)
        ]

    st.markdown("---")

    # Mostrar la tabla con botón de reporte para cada fila
    st.subheader("📋 Lista de Partidos")
    
    if df_filtrado.empty:
        st.warning("⚠️ No se encontraron partidos con los filtros aplicados")
        return
    
    # Encabezados de la tabla
    col_header1, col_header2, col_header3, col_header4, col_header5 = st.columns([2, 2.5, 2.5, 1.5, 1.5])
    with col_header1:
        st.write("**Fecha**")
    with col_header2:
        st.write("**Local**")
    with col_header3:
        st.write("**Visitante**")
    with col_header4:
        st.write("**Resultado**")
    with col_header5:
        st.write("**Acción**")
    
    st.markdown("---")
    
    # Mostrar cada partido
    for i, row in df_filtrado.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 2.5, 2.5, 1.5, 1.5])
        
        # Determinar si es partido de Audax para mostrar indicador
        es_audax = row["home_team"] == "Audax Italiano" or row["away_team"] == "Audax Italiano"
        
        with col1:
            st.write(row["match_date"].strftime("%d/%m/%Y"))
        
        with col2:
            if row["home_team"] == "Audax Italiano":
                # Audax jugando como local
                audax_score = int(row['home_score'])
                rival_score = int(row['away_score'])
                
                if audax_score > rival_score:
                    indicator = "🟢"  # Victoria
                elif audax_score == rival_score:
                    indicator = "🟡"  # Empate
                else:
                    indicator = "🔴"  # Derrota
                    
                st.write(f"{indicator} **{row['home_team']}**")
            else:
                st.write(row["home_team"])
        
        with col3:
            if row["away_team"] == "Audax Italiano":
                # Audax jugando como visitante
                audax_score = int(row['away_score'])
                rival_score = int(row['home_score'])
                
                if audax_score > rival_score:
                    indicator = "🟢"  # Victoria
                elif audax_score == rival_score:
                    indicator = "🟡"  # Empate
                else:
                    indicator = "🔴"  # Derrota
                    
                st.write(f"{indicator} **{row['away_team']}**")
            else:
                st.write(row["away_team"])
        
        with col4:
            st.write(f"{int(row['home_score'])}-{int(row['away_score'])}")
        
        with col5:
            # Botón con texto diferente según si es Audax o no
            button_text = "Generar Reporte"
            if es_audax:
                button_help = "Generar análisis enfocado en Audax Italiano"
            else:
                button_help = "Generar análisis general del partido"
                
            if st.button(button_text, key=f"reporte_{i}", help=button_help):
                generar_reporte(row["match_id"], row["home_team"], row["away_team"])
        
        # Añadir una línea sutil entre partidos
        if i < len(df_filtrado) - 1:
            st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()


# python -m streamlit run app_streamlit.py PARA FUNCIONAMIENTO