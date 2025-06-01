### APP STREAMLIT

import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import re
from io import BytesIO
from data.extraccion_datos import update_matches_only
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
    """
    Actualiza únicamente el archivo de matches sin extraer todos los datos.
    """
    try:
        update_matches_only()
        return True, "Lista de partidos actualizada exitosamente."
    except Exception as e:
        return False, f"Error al actualizar la lista de partidos: {str(e)}"


def generar_reporte(id_partido, local, visitante):
    # Determine if this is an Audax match for proper labeling
    audax_participa = local == "Audax Italiano" or visitante == "Audax Italiano"
    
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
        # (Esto ahora incluye la extracción dinámica de los últimos 5 partidos)
        match_data, attack_data, defense_data, set_piece_data, transition_data = generar_datos(id_partido, local, visitante)
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
        
        # Crear el objeto PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        
        # Título adaptado según participación de Audax
        if audax_participa_confirmed:
            es_audax_local = match_info["es_audax_local"]
            equipo_rival = match_info["equipo_rival"]
            if es_audax_local:
                pdf.set_font("Helvetica", "B", 18)
                pdf.cell(0, 15, f"REPORTE AUDAX ITALIANO (Local)", ln=True, align="C")
                pdf.set_font("Helvetica", "B", 16)
                pdf.cell(0, 12, f"vs. {equipo_rival}", ln=True, align="C")
            else:
                pdf.set_font("Helvetica", "B", 18)
                pdf.cell(0, 15, f"REPORTE AUDAX ITALIANO (Visitante)", ln=True, align="C")
                pdf.set_font("Helvetica", "B", 16)
                pdf.cell(0, 12, f"vs. {equipo_rival}", ln=True, align="C")
        else:
            pdf.set_font("Helvetica", "B", 18)
            pdf.cell(0, 15, f"REPORTE GENERAL", ln=True, align="C")
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 12, f"{local} vs. {visitante}", ln=True, align="C")
        
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"Resultado: {local} {goles_local}-{goles_visitante} {visitante}", ln=True, align="C")
        pdf.cell(0, 10, f"Fecha: {fecha_partido}", ln=True, align="C")
        pdf.ln(10)

        # Paso 3: Obtener prompts
        status_text.text("Preparando análisis...")
        progress_bar.progress(50)
        
        prompt_match = generate_prompt_matches()
        prompt_ataque = generate_prompt_ataque()
        prompt_defensa = generate_prompt_defensa()
        prompt_pelota_parada = generate_prompt_pelota_parada()
        prompt_transiciones = generate_prompt_transiciones()

        # Paso 4: Realizar análisis con ChatGPT
        if audax_participa_confirmed:
            status_text.text("Analizando rendimiento de Audax...")
        else:
            status_text.text("Analizando rendimiento general...")
        progress_bar.progress(55)
        try:
            res_match = chatgpt_api(prompt_match, match_data["raw_data"])
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
            status_text.text("Analizando situaciones de pelota parada...")
        progress_bar.progress(85)
        try:
            res_pelota_parada = chatgpt_api(prompt_pelota_parada, set_piece_data)
        except Exception as e:
            res_pelota_parada = f"[ERROR al analizar pelota parada]: {str(e)}"

        if audax_participa_confirmed:
            status_text.text("Analizando transiciones de Audax...")
        else:
            status_text.text("Analizando transiciones del partido...")
        try:
            res_transiciones = chatgpt_api(prompt_transiciones, transition_data)
        except Exception as e:
            res_transiciones = f"[ERROR al analizar transiciones]: {str(e)}"

        progress_bar.progress(95)
        # Paso 5: Generar PDF final
        status_text.text("Generando PDF final...")
        
        # Títulos adaptados para las secciones del PDF
        if audax_participa_confirmed:
            titulo_general = "Análisis del Rendimiento de Audax Italiano"
            titulo_ataque = "Rendimiento Ofensivo de Audax"
            titulo_defensa = "Rendimiento Defensivo de Audax"
            titulo_pelota_parada = "Pelota Parada - Audax Italiano"
            titulo_transiciones = "Transiciones - Audax Italiano"
        else:
            titulo_general = "Análisis General del Partido"
            titulo_ataque = "Fase Ofensiva del Partido"
            titulo_defensa = "Fase Defensiva del Partido"
            titulo_pelota_parada = "Situaciones de Pelota Parada"
            titulo_transiciones = "Transiciones del Partido"

        # Añadir respuestas al PDF
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, titulo_general, ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 10, formatear_texto_para_pdf(res_match))
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, titulo_ataque, ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 10, formatear_texto_para_pdf(res_ataque))
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, titulo_defensa, ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 10, formatear_texto_para_pdf(res_defensa))
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, titulo_pelota_parada, ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 10, formatear_texto_para_pdf(res_pelota_parada))
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, titulo_transiciones, ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 10, formatear_texto_para_pdf(res_transiciones))

        # Generar el nombre del archivo adaptado
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
        
        # Mostrar el botón de descarga con texto adaptado
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