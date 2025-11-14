from utils.rdf_loader import load_graph

PREFIX = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX vocab: <http://example.org/vocab#>
"""

def get_measurements():
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
