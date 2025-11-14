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
