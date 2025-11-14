from utils.rdf_loader import load_graph

PREFIX = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX vocab: <http://example.org/vocab#>
"""

def get_measurements():
    """
    Obtiene las primeras 200 mediciones de calidad del aire (solo hora H01).
    Consulta básica para verificar que el RDF se carga correctamente.
    """
    g = load_graph()

    query = PREFIX + """
    SELECT ?estacion ?fecha ?magnitud ?valor
    WHERE {
        ?m a vocab:MedicionAire ;
           vocab:estacion ?estacion ;
           vocab:fecha ?fecha ;
           vocab:magnitud ?magnitud ;
           vocab:H01 ?valor .
    }
    LIMIT 200
    """

    results = []
    for row in g.query(query):
        results.append({
            "estacion": str(row.estacion),
            "fecha": str(row.fecha),
            "magnitud": str(row.magnitud),
            "valor": float(row.valor),
        })
    return results


def get_measurements_by_station_and_date(estacion=None, fecha=None):
    """
    Obtiene mediciones de calidad del aire filtradas por estación y/o fecha.
    
    Args:
        estacion (str, optional): ID de la estación (ej: "11", "102")
        fecha (str, optional): Fecha en formato ISO (ej: "2025-07-07T00:00:00Z")
    
    Returns:
        list: Lista de diccionarios con las mediciones y todas las horas (H01-H24)
    
    Ejemplos:
        get_measurements_by_station_and_date(estacion="11")
        get_measurements_by_station_and_date(fecha="2025-07-07T00:00:00Z")
        get_measurements_by_station_and_date(estacion="11", fecha="2025-07-07T00:00:00Z")
    """
    g = load_graph()
    
    # Construir filtros dinámicos
    filters = []
    if estacion:
        filters.append(f'?estacion = "{estacion}"')
    if fecha:
        filters.append(f'?fecha = "{fecha}"^^xsd:dateTime')
    
    filter_clause = "FILTER (" + " && ".join(filters) + ")" if filters else ""
    
    query = PREFIX + """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?estacion ?fecha ?magnitud ?puntoMuestreo
           ?h01 ?h02 ?h03 ?h04 ?h05 ?h06 ?h07 ?h08 ?h09 ?h10 ?h11 ?h12
           ?h13 ?h14 ?h15 ?h16 ?h17 ?h18 ?h19 ?h20 ?h21 ?h22 ?h23 ?h24
    WHERE {
        ?m a vocab:MedicionAire ;
           vocab:estacion ?estacion ;
           vocab:fecha ?fecha ;
           vocab:magnitud ?magnitud .
        
        OPTIONAL { ?m vocab:puntoMuestreo ?puntoMuestreo }
        OPTIONAL { ?m vocab:H01 ?h01 }
        OPTIONAL { ?m vocab:H02 ?h02 }
        OPTIONAL { ?m vocab:H03 ?h03 }
        OPTIONAL { ?m vocab:H04 ?h04 }
        OPTIONAL { ?m vocab:H05 ?h05 }
        OPTIONAL { ?m vocab:H06 ?h06 }
        OPTIONAL { ?m vocab:H07 ?h07 }
        OPTIONAL { ?m vocab:H08 ?h08 }
        OPTIONAL { ?m vocab:H09 ?h09 }
        OPTIONAL { ?m vocab:H10 ?h10 }
        OPTIONAL { ?m vocab:H11 ?h11 }
        OPTIONAL { ?m vocab:H12 ?h12 }
        OPTIONAL { ?m vocab:H13 ?h13 }
        OPTIONAL { ?m vocab:H14 ?h14 }
        OPTIONAL { ?m vocab:H15 ?h15 }
        OPTIONAL { ?m vocab:H16 ?h16 }
        OPTIONAL { ?m vocab:H17 ?h17 }
        OPTIONAL { ?m vocab:H18 ?h18 }
        OPTIONAL { ?m vocab:H19 ?h19 }
        OPTIONAL { ?m vocab:H20 ?h20 }
        OPTIONAL { ?m vocab:H21 ?h21 }
        OPTIONAL { ?m vocab:H22 ?h22 }
        OPTIONAL { ?m vocab:H23 ?h23 }
        OPTIONAL { ?m vocab:H24 ?h24 }
        
        """ + filter_clause + """
    }
    ORDER BY ?fecha ?estacion ?magnitud
    LIMIT 500
    """
    
    results = []
    for row in g.query(query):
        # Construir diccionario con todas las horas
        measurement = {
            "estacion": str(row.estacion),
            "fecha": str(row.fecha),
            "magnitud": str(row.magnitud),
            "puntoMuestreo": str(row.puntoMuestreo) if row.puntoMuestreo else None,
        }
        
        # Añadir valores horarios (convertir a float si existen)
        for i in range(1, 25):
            hora_var = f"h{i:02d}"
            hora_value = getattr(row, hora_var, None)
            measurement[f"H{i:02d}"] = float(hora_value) if hora_value else None
        
        results.append(measurement)
    
    return results


def get_ozone_episodes(fecha_inicio=None, fecha_fin=None):
    """
    Obtiene episodios de ozono (activaciones del protocolo por alta contaminación).
    
    Args:
        fecha_inicio (str, optional): Filtrar desde esta fecha (formato ISO, ej: "2025-07-08T00:00:00Z")
        fecha_fin (str, optional): Filtrar hasta esta fecha (formato ISO)
    
    Returns:
        list: Lista de diccionarios con información de cada episodio de ozono
    
    Ejemplos:
        get_ozone_episodes()  # Todos los episodios
        get_ozone_episodes(fecha_inicio="2025-07-08T00:00:00Z")
        get_ozone_episodes(fecha_inicio="2025-07-01T00:00:00Z", fecha_fin="2025-07-31T23:59:59Z")
    """
    g = load_graph()
    
    # Construir filtros dinámicos, considerando que las fechas son opcionales, evitando crear 4 consultas separadas
    filters = []
    if fecha_inicio:
        filters.append(f'?fechaInicio >= "{fecha_inicio}"^^xsd:dateTime')
    if fecha_fin:
        filters.append(f'?fechaFin <= "{fecha_fin}"^^xsd:dateTime')
    
    filter_clause = "FILTER (" + " && ".join(filters) + ")" if filters else ""
    
    query = PREFIX + """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?episodio ?fechaInicio ?fechaFin ?escenario ?medidaPoblacion
    WHERE {
        ?episodio a vocab:EpisodioOzono ;
                  vocab:inicio ?fechaInicio ;
                  vocab:fin ?fechaFin .
        
        OPTIONAL { ?episodio vocab:escenario ?escenario }
        OPTIONAL { ?episodio vocab:medidaPoblacion ?medidaPoblacion }
        
        """ + filter_clause + """
    }
    ORDER BY DESC(?fechaInicio)
    """
    
    results = []
    for row in g.query(query):
        results.append({
            "episodio_uri": str(row.episodio),
            "fecha_inicio": str(row.fechaInicio),
            "fecha_fin": str(row.fechaFin),
            "escenario": str(row.escenario) if row.escenario else None,
            "medida_poblacion": str(row.medidaPoblacion) if row.medidaPoblacion else None,
        })
    
    return results


def get_measurements_with_linked_data(estacion=None, magnitud=None, limit=100):
    """
    Obtiene mediciones de calidad del aire junto con sus enlaces a recursos externos (owl:sameAs).
    Esta consulta demuestra el concepto de Linked Data conectando con Wikidata.
    
    Args:
        estacion (str, optional): ID de la estación para filtrar (ej: "36", "60")
        magnitud (str, optional): Código de magnitud para filtrar (ej: "10" para partículas)
        limit (int, optional): Número máximo de resultados (default: 100)
    
    Returns:
        list: Lista de diccionarios con mediciones y enlaces externos
    
    Ejemplos:
        get_measurements_with_linked_data()  # Todos los enlaces disponibles
        get_measurements_with_linked_data(estacion="36")  # Enlaces de una estación específica
        get_measurements_with_linked_data(magnitud="10", limit=50)  # Enlaces por magnitud
    """
    g = load_graph()
    
    # Construir filtros dinámicos
    filters = []
    if estacion:
        filters.append(f'?estacion = "{estacion}"')
    if magnitud:
        filters.append(f'?magnitud = "{magnitud}"')
    
    filter_clause = "FILTER (" + " && ".join(filters) + ")" if filters else ""
    
    query = PREFIX + """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    
    SELECT ?medicion ?estacion ?fecha ?magnitud ?puntoMuestreo ?enlaceExterno
    WHERE {
        ?medicion a vocab:MedicionAire ;
                  vocab:estacion ?estacion ;
                  vocab:fecha ?fecha ;
                  vocab:magnitud ?magnitud .
        
        OPTIONAL { ?medicion vocab:puntoMuestreo ?puntoMuestreo }
        
        # owl:sameAs conecta nuestra medición con recursos de Wikidata (Linked Data)
        OPTIONAL { ?medicion owl:sameAs ?enlaceExterno }
        
        """ + filter_clause + """
    }
    ORDER BY ?fecha ?estacion
    LIMIT """ + str(limit) + """
    """
    
    results = []
    for row in g.query(query):
        results.append({
            "medicion_uri": str(row.medicion),
            "estacion": str(row.estacion),
            "fecha": str(row.fecha),
            "magnitud": str(row.magnitud),
            "punto_muestreo": str(row.puntoMuestreo) if row.puntoMuestreo else None,
            "enlace_wikidata": str(row.enlaceExterno) if row.enlaceExterno else None,
        })
    
    return results
