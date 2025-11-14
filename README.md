si es la primera vez q ejecutas el proyecto, hacer: pip install -r requirements.txt
de este modo instalas las librerias necesarias

# 🌿 BeSafe – Linked Data Web App  
### *Aplicación web para consultar nuestro RDF mediante SPARQL*  
**Grupo 10 – Semantic Web – UPM**

---

## 📌 1. ¿Qué es BeSafe?

**BeSafe** es una aplicación web sencilla (en **Streamlit**) que permite:

- Cargar el **RDF generado con RML/OpenRefine**
- Ejecutar **consultas SPARQL** sobre los datos
- Mostrar resultados en una interfaz clara
- Demostrar el uso de **Linked Data**, incluyendo enlaces `owl:sameAs` a Wikidata/DBpedia
- Servir como demo funcional en la **presentación final**

La aplicación funciona **100% en local**, como indicó el profesor.

---

## 📂 2. Estructura del Proyecto

```text
BeSafe-Linked-Data/
│
├── data/
│ ├── alertas-with-links.ttl ← RDF REAL que usa la app
│ └── besafe-ontology.ttl ← ontología (documentación)
│
├── docs/
│ └── … ← mockups, requisitos, documentación
│
├── src/
│ ├── queries/
│ │ ├── internal.py ← consultas SPARQL al RDF local
│ │ └── wikidata.py ← consultas externas (opcional)
│ │
│ ├── utils/
│ │ ├── rdf_loader.py ← carga del grafo RDF con rdflib
│ │ ├── parser.py ← parseo de fechas/horas
│ │ └── alerts.py ← reglas de semáforo (opcional)
│ │
│ └── main.py ← pruebas desde terminal
│
├── streamlit_app/
│ └── Home.py ← interfaz web principal
│
├── requirements.txt ← dependencias
└── README.md ← este documento
```

---

## 🧠 3. Concepto clave: Ontología vs RDF Real  
### ❗ Punto importante para todo el grupo

Definimos una ontología propia:

besafe:Estacion
besafe:MedicionHoraria
besafe:EpisodioOzono


Pero el **RDF real** generado mediante RML **NO** usa esa ontología.

En el TTL final vemos:

@prefix ns0: http://example.org/vocab# .

Con clases como:

ns0:MedicionAire
ns0:MedicionMeteorologica
ns0:EpisodioOzono


Y propiedades como:


ns0:estacion
ns0:magnitud
ns0:fecha
ns0:H01 ... H24


### Entonces… ¿qué implica esto?

✔ La **ontología** sirve para documentación y requisitos  
✔ El **RDF real es el que consulta la aplicación**  
✔ Esto es completamente normal en un proyecto de Linked Data  
✔ Nuestra app ya usa correctamente el vocabulario real (`ns0:`)

---

## 🧩 4. Funcionalidad implementada

### ✔ Carga del RDF
- Se carga `alertas-with-links.ttl` con `rdflib.Graph()`
- Sin errores → dataset bien formado

### ✔ Ejecución de SPARQL en local
Ejemplo ya funcionando:


SELECT ?estacion ?fecha ?magnitud ?valor
WHERE {
  ?m a ns0:MedicionAire ;
     ns0:estacion ?estacion ;
     ns0:fecha ?fecha ;
     ns0:magnitud ?magnitud ;
     ns0:H01 ?valor .
}
LIMIT 10

### ✔ Conversión a pandas y visualización

La tabla se muestra en Streamlit correctamente.

### ✔ Interfaz web inicial

Al ejecutar: **streamlit run streamlit_app/Home.py**

Se muestra:
Título, Primeras mediciones del RDF, Tabla formateada

---

## 🚀 5. Qué falta por implementar

Mínimo obligatorio para presentación

- Botones con consultas SPARQL
- Visualización de resultados
- Alguna consulta usando enlaces owl:sameAs
- Interfaz básica y clara

Opcional (si da tiempo)

- Mapa con pydeck
- Gráficas
- Panel de episodios
- Consultas dinámicas a Wikidata

---

## 🧪 6. Cómo ejecutar la aplicación

1. Instalar dependencias - ejecutar en terminal del proyecto raíz: pip install -r requirements.txt
2. Ejecutar Streamlit: streamlit run streamlit_app/Home.py
3. Se abrirá en el navegador

---

## 👥 7. Reparto de trabajo sugerido

| Persona | Carpeta / Área | Tareas asignadas |
|--------|----------------|------------------|
| **A** | `src/queries/` | Implementar consultas SPARQL internas, funciones para queries dinámicas y (si da tiempo) consultas externas a Wikidata. |
| **B** | `src/utils/` | Procesamiento de fechas/horas, normalización, funciones auxiliares para la app, reglas de semáforo (opcional). |
| **C** | `streamlit_app/` | Desarrollo de la interfaz Streamlit: botones, selectores, tablas y visualización de resultados. |
| **D** | `docs/` | Requisitos, mockups, memoria, análisis, documentación final y apoyo a la presentación. |
| **E** | `data/` | Mantenimiento del RDF, revisión de RML/OpenRefine, verificación de TTL y validación del grafo. |

**Nota:** Todos pueden contribuir transversalmente, pero esta asignación sirve para avanzar de forma paralela y rápida.

---

## 🏁 8. Estado actual del proyecto

### ✔ Lo que ya está hecho
- Estructura completa del proyecto (`data`, `src`, `streamlit_app`, `docs`).
- Carga del RDF real (`alertas-with-links.ttl`) usando **rdflib** sin errores.
- Primera consulta SPARQL funcionando correctamente en local.
- Conversión de resultados a pandas y visualización en Streamlit.
- Interfaz web inicial ejecutándose correctamente en `localhost:8501`.
- Módulos internos creados: `rdf_loader`, `internal.py`, estructura de paquetes.
- Sistema funcionando aunque el RDF use `ns0:` (vocabulario generado por RML) → **esto está bien** y es el que debemos usar.

### ✔ Base completamente lista para:
- Añadir botones con consultas SPARQL.
- Mostrar resultados de manera interactiva.
- Integrar un par de consultas externas a Wikidata (si da tiempo).
- Crear la demo para la presentación final.

---

