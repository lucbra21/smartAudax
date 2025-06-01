# SmartAudax - Sistema de Análisis Táctico Inteligente

## 🎯 Descripción del Proyecto

SmartAudax es un sistema avanzado de análisis táctico de fútbol desarrollado específicamente para **Audax Italiano**. El sistema ofrece dos tipos de análisis complementarios:

### 🟢 Análisis Enfocado en Audax Italiano
- **Cuando participan**: Análisis detallado del rendimiento de Audax vs. el rival
- **Comparación histórica**: Métricas actuales vs. promedio de últimos 5 partidos
- **Recomendaciones específicas**: Para el cuerpo técnico de Audax
- **Datos dinámicos**: Extracción en tiempo real desde StatsBomb API

### 🔵 Análisis General de Partidos
- **Scouting de rivales**: Cuando Audax no participa en el partido
- **Comparación entre equipos**: Análisis táctico general del encuentro
- **Observaciones técnicas**: Para preparación de futuros enfrentamientos
- **Sin datos históricos**: Enfoque en el partido específico

## 📊 Características Principales

### Análisis Táctico Completo
- **Rendimiento Ofensivo**: xG, tiros, pases clave, centros, regates
- **Rendimiento Defensivo**: Presiones, tackles, intercepciones, recuperaciones
- **Pelota Parada**: Córners, tiros libres, saques de banda
- **Transiciones**: Contragolpes, cambios de fase, velocidad de juego

### Optimización de Datos
- **Almacenamiento mínimo**: Solo 27KB vs. 137MB del sistema anterior (99.98% reducción)
- **Datos frescos**: Extracción dinámica desde StatsBomb API
- **Archivo único**: Solo `sb_matches.csv` se mantiene localmente
- **Análisis histórico**: Últimos 5 partidos de Audax en tiempo real

## 🚀 Instalación y Configuración

### Prerrequisitos
```bash
pip install streamlit pandas fpdf openai requests beautifulsoup4
```

### Variables de Entorno
Crear archivo `.env`:
```
STATSBOMB_USER=tu_usuario
STATSBOMB_PASSWORD=tu_password
OPENAI_API_KEY=tu_api_key_openai
```

### Estructura del Proyecto
```
smartAudax/
├── main.py                    # Aplicación principal Streamlit
├── pages/
│   └── reportes.py           # Interfaz de generación de reportes
├── common/
│   ├── match_data.py         # Procesamiento dinámico de datos
│   └── generador.py          # Generación de prompts y análisis
├── data/
│   └── extraccion_datos.py   # Extracción desde StatsBomb API
└── outs_data/
    └── sb_matches.csv        # Único archivo almacenado (27KB)
```

## 🎮 Uso del Sistema

### 1. Iniciar la Aplicación
```bash
streamlit run main.py
```

### 2. Actualizar Lista de Partidos
- Usar botón "🔄 Actualizar Partidos" para sincronizar con StatsBomb
- Se actualiza solo la lista de partidos (sin datos completos)

### 3. Seleccionar Tipo de Análisis

#### Para Partidos de Audax Italiano:
1. Seleccionar "🟢 Partidos de Audax Italiano (Análisis Enfocado)"
2. Elegir partido de la lista
3. Generar reporte enfocado en Audax con comparaciones históricas

#### Para Otros Partidos (Scouting):
1. Seleccionar "🔵 Otros Partidos (Análisis General)"
2. Elegir partido sin participación de Audax
3. Generar análisis comparativo general

### 4. Generar Reporte PDF
- El sistema descarga automáticamente los datos específicos del partido
- Calcula métricas en tiempo real
- Genera reporte PDF con análisis técnico profesional

## 🔧 Funcionalidades Técnicas

### Extracción Dinámica de Datos
```python
# Solo para partidos de Audax - incluye análisis histórico
match_data, attack_data, defense_data, set_piece_data, transition_data = generar_datos(
    match_id, "Audax Italiano", "Rival"
)

# Para análisis general - sin datos históricos
match_data, attack_data, defense_data, set_piece_data, transition_data = generar_datos(
    match_id, "Equipo A", "Equipo B"
)
```

### Análisis Histórico Automático
- **Identificación automática**: Encuentra últimos 5 partidos de Audax antes del partido actual
- **Extracción dinámica**: Descarga datos históricos en tiempo real
- **Cálculo de promedios**: Métricas comparativas automáticas
- **Solo para Audax**: No se aplica en análisis general

### Tipos de Métricas Analizadas

#### Ofensivas
- Expected Goals (xG), Expected Assists (xA)
- Tiros totales, tiros a puerta, tiros en el área
- Pases clave, asistencias, pases progresivos
- Centros exitosos, regates completados
- Carries progresivos, throughballs

#### Defensivas
- Presiones totales y exitosas por zona
- Tackles, intercepciones, recuperaciones
- Bloqueos, despejes, duelos aéreos
- Presiones en tercio ofensivo rival
- Velocidad de transición defensiva

#### Pelota Parada
- Córners: totales, exitosos, por zona
- Tiros libres: directos, indirectos, efectividad
- Saques de banda: en tercio ofensivo, progresivos
- Conversión de pelotas paradas en tiros/goles

#### Transiciones
- Contragolpes exitosos
- Recuperaciones en campo rival
- Velocidad de cambio de fase
- Presiones inmediatas tras pérdida
- Carries y pases progresivos en transición

## 📈 Optimizaciones del Sistema

### Antes vs. Después
| Aspecto | Sistema Anterior | Sistema Actual |
|---------|------------------|----------------|
| **Almacenamiento** | 137MB (8 archivos CSV) | 27KB (1 archivo CSV) |
| **Datos** | Estáticos/desactualizados | Dinámicos/tiempo real |
| **Análisis** | Solo enfoque Audax | Dual: Audax + General |
| **Históricos** | Pre-calculados | Dinámicos (últimos 5) |
| **Flexibilidad** | Limitada | Completa adaptabilidad |

### Beneficios de la Optimización
1. **99.98% reducción** en almacenamiento local
2. **Datos siempre frescos** desde StatsBomb API
3. **Análisis dual** para diferentes necesidades
4. **Automatización completa** del análisis histórico
5. **Escalabilidad** para nuevos partidos instantáneamente

## 🎯 Casos de Uso

### Para el Cuerpo Técnico de Audax
- **Post-partido**: Análisis inmediato del rendimiento vs. histórico
- **Preparación**: Identificar patrones y áreas de mejora
- **Comparación**: Evolución del equipo a través del tiempo
- **Tácticas**: Ajustes basados en métricas específicas

### Para Scouting y Análisis de Rivales
- **Observación**: Análisis de equipos que enfrentará Audax
- **Preparación**: Identificar fortalezas y debilidades de futuros rivales
- **Tendencias**: Patrones tácticos de equipos de la liga
- **Estrategia**: Información para preparar próximos encuentros

## 🔍 Testing y Validación

### Pruebas Automatizadas
```bash
python test_analysis_types.py
```

Verificaciones incluidas:
- ✅ Detección correcta de partidos con/sin Audax
- ✅ Análisis enfocado para partidos de Audax
- ✅ Análisis general para otros partidos
- ✅ Extracción de datos históricos (solo Audax)
- ✅ Generación de métricas específicas
- ✅ Estructura correcta de datos de salida

## 📞 Soporte y Mantenimiento

### Actualizaciones del Sistema
- **Lista de partidos**: Usar botón de actualización en la interfaz
- **Datos dinámicos**: Se actualizan automáticamente con cada análisis
- **Nuevas funcionalidades**: Sistema modular permite expansión fácil

### Resolución de Problemas
1. **Error de credenciales**: Verificar variables de entorno
2. **Falta archivo CSV**: Usar botón "Actualizar Partidos"
3. **Error de API**: Verificar conexión a internet y límites de StatsBomb
4. **Datos faltantes**: Algunos partidos pueden no tener datos completos en StatsBomb

---

**Desarrollado específicamente para Audax Italiano** 🟢⚪
*Sistema de análisis táctico profesional con tecnología de vanguardia*