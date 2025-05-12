### APP STREAMLIT

import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import re
from io import BytesIO
from data.extraccion_datos import main as extraccion_datos
# IMPORTS DE FUNCIONES DEL GENERADOR
from common.generador import (
    chatgpt_api,
    generate_prompt_matches,
    generate_prompt_ataque,
    generate_prompt_defensa,
    generate_prompt_pelota_parada,
    generate_prompt_transiciones
)

from common.match_data import generar_datos


def limpiar_texto_pdf(texto, max_palabra=50):
    """
    Limpia el texto para evitar errores con FPDF, pero sin cortar en líneas.
    """
    # Convertir marcadores de markdown a texto plano
    texto = texto.replace('**', '')  # Negrita
    texto = texto.replace('*', '')   # Cursiva
    texto = texto.replace('`', '')   # Código
    texto = texto.replace('#', '')   # Encabezados
    texto = texto.replace('>', '')   # Citas
    texto = texto.replace('-', '')   # Listas
    texto = texto.replace('+', '')   # Listas
    texto = texto.replace('1.', '')  # Listas numeradas
    texto = texto.replace('2.', '')
    texto = texto.replace('3.', '')
    texto = texto.replace('4.', '')
    texto = texto.replace('5.', '')
    texto = texto.replace('6.', '')
    texto = texto.replace('7.', '')
    texto = texto.replace('8.', '')
    texto = texto.replace('9.', '')
    texto = texto.replace('0.', '')
    
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
    extraccion_datos()
    return True, "Extracción completada exitosamente."


def generar_reporte(id_partido, local, visitante):
    st.write(f"Generando reporte del partido {local} vs. {visitante}...")
    
    try:
        # Obtener todos los datos del partido desde match_data.py
        match_data, attack_data, defense_data, set_piece_data, transition_data = generar_datos(id_partido, local, visitante)
        
        # Extraer información del partido desde match_data
        match_info = match_data["match_info"]
        goles_local = match_info["goles_local"]
        goles_visitante = match_info["goles_visitante"]
        fecha_partido = match_info["fecha"]
        es_audax_local = match_info["es_audax_local"]
        equipo_rival = match_info["equipo_rival"]
        
        # Crear el objeto PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 15, f"{local} {goles_local}-{goles_visitante} {visitante}", ln=True, align="C")
        pdf.cell(0, 10, f"Fecha: {fecha_partido}", ln=True, align="C")
        pdf.ln(10)

        # Obtener los prompts
        prompt_match = generate_prompt_matches()
        prompt_ataque = generate_prompt_ataque()
        prompt_defensa = generate_prompt_defensa()
        prompt_pelota_parada = generate_prompt_pelota_parada()
        prompt_transiciones = generate_prompt_transiciones()

        # Realizar las consultas a la API
        try:
            res_match = chatgpt_api(prompt_match, match_data["raw_data"])
        except Exception as e:
            res_match = f"[ERROR al analizar match]: {str(e)}"

        try:
            res_ataque = chatgpt_api(prompt_ataque, attack_data)
        except Exception as e:
            res_ataque = f"[ERROR al analizar ataque]: {str(e)}"

        try:
            res_defensa = chatgpt_api(prompt_defensa, defense_data)
        except Exception as e:
            res_defensa = f"[ERROR al analizar defensa]: {str(e)}"

        try:
            res_pelota_parada = chatgpt_api(prompt_pelota_parada, set_piece_data)
        except Exception as e:
            res_pelota_parada = f"[ERROR al analizar pelota parada]: {str(e)}"

        try:
            res_transiciones = chatgpt_api(prompt_transiciones, transition_data)
        except Exception as e:
            res_transiciones = f"[ERROR al analizar transiciones]: {str(e)}"

        # Añadir respuestas al PDF
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Resumen General del partido", ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 10, formatear_texto_para_pdf(res_match))
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Análisis de Ataque", ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 10, formatear_texto_para_pdf(res_ataque))
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Análisis de Defensa", ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 10, formatear_texto_para_pdf(res_defensa))
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Análisis de Pelota Parada", ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 10, formatear_texto_para_pdf(res_pelota_parada))
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Análisis de Transiciones", ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 10, formatear_texto_para_pdf(res_transiciones))

        # Generar el nombre del archivo
        nombre_archivo = f"reporte_audax_{'local' if es_audax_local else 'visitante'}_{equipo_rival}_{fecha_partido}.pdf"
        
        # Guardar el PDF en un buffer de memoria
        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)

        # Mostrar el botón de descarga en Streamlit
        st.download_button(
            "Descargar reporte PDF",
            data=pdf_buffer,
            file_name=nombre_archivo,
            mime="application/pdf"
        )
            
    except Exception as e:
        st.error(f"Error al generar el reporte: {str(e)}")


def main():
    st.set_page_config(page_title="Reportes Post-Partido", layout="wide", initial_sidebar_state="collapsed")
    
    # Encabezado con imagen, título y botón de actualizar
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.image("static/escudo_audax.png", width=80)
    with col2:
        st.markdown("<h1 style='text-align: center;'>REPORTES POST-PARTIDO</h1>", unsafe_allow_html=True)
    
    # Cargar el CSV de matches
    try:
        df = pd.read_csv("outs_data/sb_matches.csv")
    except Exception as e:
        st.error(f"Error al cargar el CSV de matches: {e}")
        st.stop()
    
    st.markdown("---")
    
    # Filtros en una misma línea usando columnas
    st.subheader("Filtros")
    col_filtro1, col_filtro2, col_filtro3 = st.columns([2, 2, 1])
    
    with col_filtro1:
        filtro_equipo = st.text_input("Equipo", key="filtro_equipo", placeholder="Ingrese equipo")
    with col_filtro2:
        # Convertir la columna de fecha a datetime si no lo está ya
        df['match_date'] = pd.to_datetime(df['match_date'])
        min_date = df['match_date'].min()
        max_date = df['match_date'].max()
        
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
    df_filtrado = df.copy()
    df_filtrado = df_filtrado.sort_values(by="match_date", ascending=False)
    
    if fecha_inicio is not None and fecha_fin is not None:
        df_filtrado = df_filtrado[
            (df_filtrado["match_date"].dt.date >= fecha_inicio) & 
            (df_filtrado["match_date"].dt.date <= fecha_fin)
        ]
    if filtro_equipo:
        df_filtrado = df_filtrado[df_filtrado["away_team"].str.contains(filtro_equipo, case=False, na=False) | df_filtrado["home_team"].str.contains(filtro_equipo, case=False, na=False)]
    
    st.markdown("---")
    
    # Mostrar la tabla con botón de reporte para cada fila
    st.subheader("Lista de Partidos")
    for i, row in df_filtrado.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        col1.write(row["match_date"].strftime("%d/%m/%Y"))
        col2.write(row["home_team"])
        col3.write(row["away_team"])
        if col4.button("Generar Reporte", key=f"reporte_{i}"):
            generar_reporte(row["match_id"], row["home_team"], row["away_team"])


if __name__ == "__main__":
    main()


# python -m streamlit run app_streamlit.py PARA FUNCIONAMIENTO