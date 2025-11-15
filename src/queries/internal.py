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
    
    # Usar GROUP_CONCAT para agrupar múltiples medidas de población en una sola fila
    query = PREFIX + """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?episodio ?fechaInicio ?fechaFin ?escenario 
           (GROUP_CONCAT(?medida; separator=" | ") AS ?medidaPoblacion)
    WHERE {
        ?episodio a vocab:EpisodioOzono ;
                  vocab:inicio ?fechaInicio ;
                  vocab:fin ?fechaFin .
        
        OPTIONAL { ?episodio vocab:escenario ?escenario }
        OPTIONAL { ?episodio vocab:medidaPoblacion ?medida }
        
        """ + filter_clause + """
    }
    GROUP BY ?episodio ?fechaInicio ?fechaFin ?escenario
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


def get_measurements_with_linked_data(limit=20, estacion=None, magnitud=None):
    """
    Devuelve mediciones junto con enlaces owl:sameAs enriquecidos:
    - Enlace original (si existe en la medición)
    - Enlace a la magnitud (gas)
    - Enlace a la estación (wikidata del barrio o zona)
    Permite filtrar por estación y magnitud.
    """

    # Construimos el cuerpo del WHERE
    where_block = """
        ?medicion a ns0:MedicionAire ;
                 ns0:estacion ?est ;
                 ns0:magnitud ?mag ;
                 ns0:fecha ?fecha ;
                 ns0:H01 ?valor ;
                 ns0:puntoMuestreo ?punto .

        OPTIONAL {
            ?medicion owl:sameAs ?link_medicion .
        }

        OPTIONAL {
            BIND( IRI(CONCAT("http://example.org/vocab/magnitud/", STR(?mag))) AS ?magnitud_uri )
            ?magnitud_uri owl:sameAs ?link_magnitud .
        }

        OPTIONAL {
            BIND( IRI(CONCAT("http://example.org/resource/Estacion/", STR(?est))) AS ?estacion_uri )
            ?estacion_uri owl:sameAs ?link_estacion .
        }
    """

    # Añadimos filtros según lo que haya elegido el usuario en la UI
    if estacion is not None:
        # En el RDF las estaciones son literales tipo "36"
        where_block += f'\n        FILTER(?est = "{estacion}")'

    if magnitud is not None:
        # Igual para la magnitud: "8", "10", "12", etc.
        where_block += f'\n        FILTER(?mag = "{magnitud}")'

    # Montamos la query completa
    query = f"""
    PREFIX ns0: <http://example.org/vocab#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT ?medicion ?est ?mag ?fecha ?valor ?punto
           ?link_medicion ?link_magnitud ?link_estacion
    WHERE {{
    {where_block}
    }}
    LIMIT {limit}
    """

    g = load_graph()
    results = g.query(query)

    rows = []
    for r in results:
        rows.append({
            "medicion": str(r["medicion"]),
            "estacion": str(r["est"]),
            "magnitud": str(r["mag"]),
            "fecha": str(r["fecha"]),
            "valor": float(r["valor"]),
            "punto": str(r["punto"]),
            "link_medicion": str(r["link_medicion"]) if r["link_medicion"] else None,
            "link_magnitud": str(r["link_magnitud"]) if r["link_magnitud"] else None,
            "link_estacion": str(r["link_estacion"]) if r["link_estacion"] else None
        })

    return rows





def get_aggregated_statistics(estacion=None, magnitud=None, fecha=None):
    """
    Obtiene estadísticas agregadas de calidad del aire (promedio, máximo, mínimo, conteo).
    Demuestra el uso de funciones de agregación en SPARQL: AVG, MAX, MIN, COUNT.
    
    Args:
        estacion (str, optional): ID de la estación para filtrar (ej: "11", "36")
        magnitud (str, optional): Código de magnitud para filtrar (ej: "10", "12")
        fecha (str, optional): Fecha para filtrar (formato ISO)
    
    Returns:
        list: Lista de diccionarios con estadísticas agregadas por estación y magnitud
    
    Ejemplos:
        get_aggregated_statistics()  # Todas las estadísticas
        get_aggregated_statistics(estacion="11")  # Estadísticas de una estación
        get_aggregated_statistics(magnitud="10")  # Estadísticas de una magnitud
    """
    g = load_graph()
    
    # Construir filtros dinámicos
    filters = []
    if estacion:
        filters.append(f'?estacion = "{estacion}"')
    if magnitud:
        filters.append(f'?magnitud = "{magnitud}"')
    if fecha:
        filters.append(f'?fecha = "{fecha}"^^xsd:dateTime')
    
    filter_clause = "FILTER (" + " && ".join(filters) + ")" if filters else ""
    
    # Consulta de agregación con AVG, MAX, MIN, COUNT
    query = PREFIX + """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?estacion ?magnitud
           (COUNT(?m) AS ?total_mediciones)
           (AVG(?valor) AS ?promedio)
           (MAX(?valor) AS ?maximo)
           (MIN(?valor) AS ?minimo)
    WHERE {
        ?m a vocab:MedicionAire ;
           vocab:estacion ?estacion ;
           vocab:fecha ?fecha ;
           vocab:magnitud ?magnitud ;
           vocab:H01 ?valor .
        
        """ + filter_clause + """
    }
    GROUP BY ?estacion ?magnitud
    ORDER BY ?estacion ?magnitud
    """
    
    results = []
    for row in g.query(query):
        results.append({
            "estacion": str(row.estacion),
            "magnitud": str(row.magnitud),
            "total_mediciones": int(row.total_mediciones) if row.total_mediciones else 0,
            "promedio": round(float(row.promedio), 2) if row.promedio else None,
            "maximo": float(row.maximo) if row.maximo else None,
            "minimo": float(row.minimo) if row.minimo else None,
        })
    
    return results


def get_available_stations():
    """
    Obtiene la lista de estaciones únicas disponibles en el dataset.
    Útil para poblar desplegables en la interfaz.
    
    Returns:
        list: Lista de IDs de estaciones ordenadas numéricamente
    """
    g = load_graph()
    
    query = PREFIX + """
    SELECT DISTINCT ?estacion
    WHERE {
        ?m a vocab:MedicionAire ;
           vocab:estacion ?estacion .
    }
    ORDER BY ?estacion
    """
    
    stations = []
    for row in g.query(query):
        stations.append(str(row.estacion))
    
    # Ordenar numéricamente (en caso de que sean números)
    try:
        stations_sorted = sorted(stations, key=lambda x: int(x))
        return stations_sorted
    except ValueError:
        # Si no son todos números, devolver ordenación alfabética
        return sorted(stations)


def get_available_magnitudes():
    """
    Obtiene la lista de magnitudes (contaminantes) únicas disponibles en el dataset.
    Útil para poblar desplegables en la interfaz.
    
    Returns:
        list: Lista de códigos de magnitud ordenados numéricamente
    """
    g = load_graph()
    
    query = PREFIX + """
    SELECT DISTINCT ?magnitud
    WHERE {
        ?m a vocab:MedicionAire ;
           vocab:magnitud ?magnitud .
    }
    ORDER BY ?magnitud
    """
    
    magnitudes = []
    for row in g.query(query):
        magnitudes.append(str(row.magnitud))
    
    # Ordenar numéricamente (en caso de que sean números)
    try:
        magnitudes_sorted = sorted(magnitudes, key=lambda x: int(x))
        return magnitudes_sorted
    except ValueError:
        # Si no son todos números, devolver ordenación alfabética
        return sorted(magnitudes)

