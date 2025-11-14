
import streamlit as st
import pandas as pd
import sys
import os
# Añadir /src al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from queries.internal import (
    get_measurements, 
    get_measurements_by_station_and_date, 
    get_ozone_episodes, 
    get_measurements_with_linked_data, 
    get_aggregated_statistics,
    get_available_stations,
    get_available_magnitudes
)

st.title("BeSafe – Calidad del Aire 🌍")

# Selector de tipo de consulta
st.sidebar.header("⚙️ Configuración de Consulta")
query_type = st.sidebar.radio(
    "Selecciona el tipo de consulta:",
    ["📊 Medición básica", "🔍 Medición con filtros", "⚠️ Episodios de Ozono", "🔗 Linked Data", "📈 Estadísticas Agregadas"],
    index=0
)

st.sidebar.markdown("---")

# Mostrar interfaz según el tipo de consulta seleccionado
if query_type == "📊 Medición básica":
    st.subheader("📊 Medición básica (Primeras 200)")
    st.info("Esta consulta muestra las primeras 200 mediciones de calidad del aire (solo hora H01)")
    
    if st.button("🔄 Cargar Datos", key="basic"):
        with st.spinner("Cargando datos..."):
            data = get_measurements()
            df = pd.DataFrame(data)
            
            st.success(f"✅ Se cargaron {len(df)} mediciones")
            st.dataframe(df, use_container_width=True)
            
            # Estadísticas básicas
            st.subheader("📈 Estadísticas")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Mediciones", len(df))
            with col2:
                st.metric("Estaciones Únicas", df['estacion'].nunique())
            with col3:
                st.metric("Magnitudes Únicas", df['magnitud'].nunique())

elif query_type == "🔍 Medición con filtros":  # Mediciones con Filtros
    st.subheader("🔍 Medición con filtros")
    st.info("Filtra mediciones por estación y/o fecha. Los filtros son opcionales - puedes usar uno, ambos o ninguno.")
    
    # Cargar opciones disponibles
    with st.spinner("Cargando opciones disponibles..."):
        available_stations = get_available_stations()
    
    # Filtros opcionales en el sidebar
    st.sidebar.subheader("Filtros Opcionales")
    
    use_estacion = st.sidebar.checkbox("Filtrar por Estación", value=False)
    estacion = None
    if use_estacion:
        estacion = st.sidebar.selectbox(
            "Selecciona Estación",
            options=available_stations,
            help="Selecciona una estación del dataset"
        )
    
    use_fecha = st.sidebar.checkbox("Filtrar por Fecha", value=False)
    fecha = None
    if use_fecha:
        fecha_input = st.sidebar.date_input("Fecha")
        if fecha_input:
            fecha = f"{fecha_input}T00:00:00Z"
            st.sidebar.caption(f"Formato ISO: `{fecha}`")
    
    if st.button("🔎 Buscar con filtros", key="filtered"):
        with st.spinner("Ejecutando consulta SPARQL con filtros..."):
            # Ejecutar consulta con los filtros seleccionados
            data = get_measurements_by_station_and_date(
                estacion=estacion if use_estacion else None,
                fecha=fecha if use_fecha else None
            )
            
            if data:
                df = pd.DataFrame(data)
                
                # Mostrar resumen de filtros aplicados
                filters_applied = []
                if estacion:
                    filters_applied.append(f"Estación: {estacion}")
                if fecha:
                    filters_applied.append(f"Fecha: {fecha}")
                
                if filters_applied:
                    st.success(f"✅ Filtros aplicados: {' | '.join(filters_applied)}")
                else:
                    st.info("ℹ️ Sin filtros - mostrando todas las mediciones (límite 500)")
                
                st.success(f"📊 Se encontraron {len(df)} mediciones")
                
                # Mostrar datos con todas las 24 horas
                st.dataframe(df, use_container_width=True)
                
                # Estadísticas
                st.subheader("📈 Estadísticas de Resultados")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Mediciones", len(df))
                with col2:
                    st.metric("Estaciones", df['estacion'].nunique())
                with col3:
                    st.metric("Magnitudes", df['magnitud'].nunique())
                with col4:
                    st.metric("Fechas", df['fecha'].nunique())
                
                # Mostrar gráfico si hay datos horarios
                if len(df) > 0 and 'H01' in df.columns:
                    st.subheader("📉 Visualización de Valores Horarios (Primera Medición)")
                    first_row = df.iloc[0]
                    horas_cols = [f'H{i:02d}' for i in range(1, 25)]
                    valores_horarios = [first_row[h] for h in horas_cols if pd.notna(first_row.get(h))]
                    
                    if valores_horarios:
                        chart_data = pd.DataFrame({
                            'Hora': range(1, len(valores_horarios) + 1),
                            'Valor': valores_horarios
                        })
                        st.line_chart(chart_data.set_index('Hora'))
                        st.caption(f"Estación: {first_row['estacion']} | Magnitud: {first_row['magnitud']} | Fecha: {first_row['fecha']}")
            else:
                st.warning(" ⛔ No se encontraron resultados con los filtros aplicados")
                st.info("💡 Intenta modificar o eliminar algunos filtros")

elif query_type == "⚠️ Episodios de Ozono":
    st.subheader("⚠️ Episodios de Ozono - Protocolo de Alta Contaminación")
    st.info("Consulta los episodios de activación del protocolo por alta contaminación de ozono")
    
    # Filtros opcionales para episodios en el sidebar
    st.sidebar.subheader("Filtros de fecha (Opcionales)")
    
    use_fecha_inicio = st.sidebar.checkbox("Filtrar desde", value=False, key="ozone_inicio")
    fecha_inicio = None
    if use_fecha_inicio:
        fecha_inicio_input = st.sidebar.date_input("Fecha de inicio", key="fecha_inicio")
        if fecha_inicio_input:
            fecha_inicio = f"{fecha_inicio_input}T00:00:00Z"
            st.sidebar.caption(f"Desde: `{fecha_inicio}`")
    
    use_fecha_fin = st.sidebar.checkbox("Filtrar hasta", value=False, key="ozone_fin")
    fecha_fin = None
    if use_fecha_fin:
        fecha_fin_input = st.sidebar.date_input("Fecha de fin", key="fecha_fin")
        if fecha_fin_input:
            fecha_fin = f"{fecha_fin_input}T23:59:59Z"
            st.sidebar.caption(f"Hasta: `{fecha_fin}`")
    
    if st.button("🔍 Consultar Episodios", key="ozone"):
        with st.spinner("Buscando episodios de ozono..."):
            data = get_ozone_episodes(
                fecha_inicio=fecha_inicio if use_fecha_inicio else None,
                fecha_fin=fecha_fin if use_fecha_fin else None
            )
            
            if data:
                df = pd.DataFrame(data)
                
                # Mostrar resumen de filtros
                filters_applied = []
                if fecha_inicio:
                    filters_applied.append(f"Desde: {fecha_inicio}")
                if fecha_fin:
                    filters_applied.append(f"Hasta: {fecha_fin}")
                
                if filters_applied:
                    st.success(f"✅ Filtros aplicados: {' | '.join(filters_applied)}")
                else:
                    st.info("ℹ️ Sin filtros - mostrando todos los episodios")
                
                st.success(f"⚠️ Se encontraron {len(df)} episodios de ozono")
                
                # Mostrar tabla de episodios
                st.dataframe(df, use_container_width=True)
                
                # Mostrar detalles de cada episodio
                st.subheader("📋 Detalles de Episodios")
                for idx, row in df.iterrows():
                    with st.expander(f"Episodio {idx + 1}: {row['fecha_inicio']} → {row['fecha_fin']}"):
                        st.markdown(f"**🔗 URI:** `{row['episodio_uri']}`")
                        st.markdown(f"**📅 Fecha Inicio:** {row['fecha_inicio']}")
                        st.markdown(f"**📅 Fecha Fin:** {row['fecha_fin']}")
                        st.markdown(f"**📊 Escenario:** {row['escenario']}")
                        if row['medida_poblacion']:
                            st.markdown(f"**👥 Medidas para la Población:**")
                            # Dividir por el separador " | " que usamos en GROUP_CONCAT
                            medidas_texto = str(row['medida_poblacion'])
                            if ' | ' in medidas_texto:
                                medidas = medidas_texto.split(' | ')
                                for medida in medidas:
                                    st.markdown(f"- {medida.strip()}")
                            else:
                                # Si es una sola medida, mostrarla directamente
                                st.markdown(f"- {medidas_texto}")
                
                # Estadísticas
                st.subheader("📈 Estadísticas de Episodios")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Episodios", len(df))
                with col2:
                    if 'escenario' in df.columns:
                        escenarios_unicos = df['escenario'].nunique()
                        st.metric("Tipos de Escenario", escenarios_unicos)
            else:
                st.warning("⚠️ No se encontraron episodios con los filtros aplicados")
                st.info("💡 Intenta ampliar el rango de fechas o eliminar filtros")

elif query_type == "🔗 Linked Data":
    st.subheader("🔗 Linked Data - Enlaces a Wikidata")
    st.info("Consulta que demuestra el concepto de Linked Data usando owl:sameAs para conectar con recursos externos de Wikidata")
    
    # Cargar opciones disponibles
    with st.spinner("Cargando opciones disponibles..."):
        available_stations = get_available_stations()
        available_magnitudes = get_available_magnitudes()
    
    # Filtros opcionales en el sidebar
    st.sidebar.subheader("Filtros Opcionales")
    
    use_estacion_ld = st.sidebar.checkbox("Filtrar por Estación", value=False, key="ld_estacion")
    estacion_ld = None
    if use_estacion_ld:
        estacion_ld = st.sidebar.selectbox(
            "Selecciona Estación",
            options=available_stations,
            help="Filtra mediciones de una estación específica",
            key="ld_est_input"
        )
    
    use_magnitud = st.sidebar.checkbox("Filtrar por Magnitud", value=False, key="ld_magnitud")
    magnitud = None
    if use_magnitud:
        magnitud = st.sidebar.selectbox(
            "Selecciona Magnitud",
            options=available_magnitudes,
            help="Filtra por tipo de contaminante (10=partículas, 12=NO₂, etc.)",
            key="ld_mag_input"
        )
    
    limit_ld = st.sidebar.slider("Número de resultados", min_value=10, max_value=200, value=50, step=10, key="ld_limit")
    
    if st.button("🔎 Consultar Linked Data", key="linked_data"):
        with st.spinner("Consultando enlaces externos (owl:sameAs)..."):
            data = get_measurements_with_linked_data(
                estacion=estacion_ld if use_estacion_ld else None,
                magnitud=magnitud if use_magnitud else None,
                limit=limit_ld
            )
            
            if data:
                df = pd.DataFrame(data)
                
                # Mostrar resumen de filtros
                filters_applied = []
                if estacion_ld:
                    filters_applied.append(f"Estación: {estacion_ld}")
                if magnitud:
                    filters_applied.append(f"Magnitud: {magnitud}")
                filters_applied.append(f"Límite: {limit_ld}")
                
                st.success(f"✅ Filtros aplicados: {' | '.join(filters_applied)}")
                st.success(f"🔗 Se encontraron {len(df)} mediciones con enlaces")
                
                # Mostrar tabla completa
                st.dataframe(df, use_container_width=True)
                
                # Análisis de enlaces
                st.subheader("📊 Análisis de Enlaces Externos")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Mediciones", len(df))
                with col2:
                    st.metric("Estaciones", df['estacion'].nunique())
                with col3:
                    st.metric("Magnitudes", df['magnitud'].nunique())
                with col4:
                    enlaces_unicos = df['enlace_wikidata'].nunique() if 'enlace_wikidata' in df.columns else 0
                    st.metric("Enlaces Únicos", enlaces_unicos)
                
                # Mostrar ejemplos de enlaces
                if 'enlace_wikidata' in df.columns:
                    st.subheader("🌐 Ejemplos de Enlaces a Wikidata")
                    enlaces_ejemplo = df[df['enlace_wikidata'].notna()].head(5)
                    
                    for idx, row in enlaces_ejemplo.iterrows():
                        with st.expander(f"Medición {idx + 1}: Estación {row['estacion']} - Magnitud {row['magnitud']}"):
                            st.markdown(f"**📍 URI Local:** `{row['medicion_uri']}`")
                            st.markdown(f"**🔗 Enlace Wikidata:** [{row['enlace_wikidata']}]({row['enlace_wikidata']})")
                            st.markdown(f"**📅 Fecha:** {row['fecha']}")
                            st.markdown(f"**📊 Punto Muestreo:** {row['punto_muestreo']}")
                            st.caption("El enlace owl:sameAs conecta nuestra medición con un concepto en Wikidata, demostrando Linked Data")
                
                # Información sobre Linked Data
                st.info("""
                **💡 ¿Qué es Linked Data?**
                
                Esta consulta demuestra el concepto de **Linked Data** usando la propiedad `owl:sameAs` 
                que conecta nuestros recursos locales con recursos externos en Wikidata. Esto permite:
                - ✅ Enriquecer nuestros datos con información externa
                - ✅ Interoperabilidad entre diferentes fuentes de datos
                - ✅ Navegación entre datasets relacionados
                - ✅ Reutilización de identificadores comunes
                """)
            else:
                st.warning("⚠️ No se encontraron mediciones con los filtros aplicados")
                st.info("💡 Intenta modificar o eliminar los filtros")

elif query_type == "📈 Estadísticas Agregadas":
    st.subheader("📈 Estadísticas Agregadas - AVG, MAX, MIN, COUNT")
    st.info("Consulta que demuestra funciones de agregación en SPARQL: promedio, máximo, mínimo y conteo por estación y magnitud")
    
    # Cargar opciones disponibles
    with st.spinner("Cargando opciones disponibles..."):
        available_stations = get_available_stations()
        available_magnitudes = get_available_magnitudes()
    
    # Filtros opcionales en el sidebar
    st.sidebar.subheader("Filtros Opcionales")
    
    use_estacion_agg = st.sidebar.checkbox("Filtrar por Estación", value=False, key="agg_estacion")
    estacion_agg = None
    if use_estacion_agg:
        estacion_agg = st.sidebar.selectbox(
            "Selecciona Estación",
            options=available_stations,
            key="agg_est_input"
        )
    
    use_magnitud_agg = st.sidebar.checkbox("Filtrar por Magnitud", value=False, key="agg_magnitud")
    magnitud_agg = None
    if use_magnitud_agg:
        magnitud_agg = st.sidebar.selectbox(
            "Selecciona Magnitud",
            options=available_magnitudes,
            key="agg_mag_input"
        )
    
    if st.button("📊 Calcular Estadísticas", key="aggregated"):
        with st.spinner("Calculando estadísticas agregadas con SPARQL..."):
            data = get_aggregated_statistics(
                estacion=estacion_agg if use_estacion_agg else None,
                magnitud=magnitud_agg if use_magnitud_agg else None
            )
            
            if data:
                df = pd.DataFrame(data)
                
                # Mostrar resumen de filtros
                filters_applied = []
                if estacion_agg:
                    filters_applied.append(f"Estación: {estacion_agg}")
                if magnitud_agg:
                    filters_applied.append(f"Magnitud: {magnitud_agg}")
                
                if filters_applied:
                    st.success(f"✅ Filtros aplicados: {' | '.join(filters_applied)}")
                else:
                    st.info("ℹ️ Sin filtros - mostrando todas las agrupaciones")
                
                st.success(f"📊 Se calcularon estadísticas para {len(df)} agrupaciones (estación + magnitud)")
                
                # Mostrar tabla completa
                st.dataframe(df, use_container_width=True)
                
                # Métricas generales
                st.subheader("📊 Resumen General")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Agrupaciones", len(df))
                with col2:
                    st.metric("Estaciones Únicas", df['estacion'].nunique())
                with col3:
                    st.metric("Magnitudes Únicas", df['magnitud'].nunique())
                with col4:
                    total_mediciones = df['total_mediciones'].sum()
                    st.metric("Total Mediciones", total_mediciones)
                
                # Análisis por estación
                st.subheader("🏢 Top 5 Estaciones por Promedio Más Alto")
                top_stations = df.nlargest(5, 'promedio')[['estacion', 'magnitud', 'promedio', 'maximo', 'minimo']]
                st.dataframe(top_stations, use_container_width=True)
                
                # Gráficos
                if len(df) > 0:
                    st.subheader("📉 Visualización de Promedios")
                    
                    # Gráfico de barras: promedio por estación-magnitud
                    df_chart = df.copy()
                    df_chart['estacion_magnitud'] = df_chart['estacion'] + '-' + df_chart['magnitud']
                    df_chart = df_chart.set_index('estacion_magnitud')
                    
                    # Mostrar solo los primeros 20 para no saturar
                    st.bar_chart(df_chart[['promedio']].head(20))
                    st.caption("Promedio de valores por Estación-Magnitud (primeras 20 agrupaciones)")
                
                # Información sobre agregación
                st.info("""
                **💡 Funciones de Agregación SPARQL**
                
                Esta consulta utiliza las siguientes funciones de agregación:
                - **COUNT(?)** - Cuenta el número de mediciones
                - **AVG(?)** - Calcula el promedio de los valores
                - **MAX(?)** - Encuentra el valor máximo
                - **MIN(?)** - Encuentra el valor mínimo
                - **GROUP BY** - Agrupa resultados por estación y magnitud
                
                Estas funciones permiten análisis estadísticos directamente en SPARQL sin necesidad
                de procesar los datos en la aplicación.
                """)
            else:
                st.warning("⚠️ No se encontraron estadísticas con los filtros aplicados")
                st.info("💡 Intenta modificar o eliminar los filtros")

st.sidebar.markdown("---")
st.sidebar.caption("💡 Proyecto BeSafe - Semantic Web")
