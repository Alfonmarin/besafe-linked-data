# 🌐 BeSafe – Linked Open Data para alertas medioambientales

## 🧩 Descripción general
Consiste en la **creación, limpieza, transformación y vinculación de datos abiertos** relacionados con la **calidad del aire y condiciones meteorológicas en la Comunidad de Madrid**, siguiendo el **proceso completo de generación de datos enlazados (Linked Open Data)**.

El objetivo final es construir una aplicación conceptual llamada **BeSafe**, que notifique a los ciudadanos sobre **alertas ambientales** cuando los niveles de contaminación (ozono, NO₂ o partículas) superen valores críticos y **no sea recomendable realizar deporte al aire libre**.

---

## 🎯 Objetivos principales
- Seleccionar datasets abiertos de **Smart Cities** y **medio ambiente**.  
- Analizar, limpiar y transformar los datos siguiendo las **buenas prácticas de Linked Data**.  
- Desarrollar una **ontología ligera (OWL)** para representar los conceptos de calidad del aire, contaminación y meteorología.  
- Generar **RML mappings** para transformar los datos CSV a RDF.  
- Enlazar los datos con recursos externos (e.g., DBpedia, Wikidata).  
- Escribir consultas **SPARQL** para validar y explotar la información generada.

---

## ⚙️ Tecnologías y herramientas utilizadas
| Categoría | Herramienta / Tecnología |
|------------|--------------------------|
| **Lenguajes** | RDF, Turtle, RML, YAML, HTML, JSON, CSV |
| **Ontología** | OWL (Turtle syntax) |
| **Modelado de datos** | RMLMapper, Morph-KGC |
| **Limpieza y vinculación** | OpenRefine |
| **Consulta y verificación** | SPARQL |
| **Repositorios y publicación** | GitHub, GitHub Pages (para dataset final) |

---

## 🧱 Estructura del proyecto
| Carpeta / Archivo | Descripción |
|--------------------|-------------|
| **`/csv/`** | Datasets originales y transformados: calidad del aire, meteorología y activación de protocolos de contaminación. |
| **`/openrefine/`** | Archivos JSON con las operaciones de limpieza y reconciliación de datos. |
| **`/ontology/`** | Ontología del dominio (**besafe-ontology.ttl**) y ejemplos instanciados. |
| **`/mappings/`** | Archivos RML (`.rml`, `.yml`) para transformar CSV en RDF. |
| **`/rdf/`** | Datos RDF generados (`.ttl`) y consultas SPARQL (`.sparql`). |
| **`/requirements/`** | Documentos HTML de requisitos de datasets y aplicación. |
| **`analysis.html`** | Análisis del dataset y de la licencia de datos. |
| **`queries.sparql`** | Consultas SPARQL de validación. |
| **`selfAssessmentHandsOnX.md`** | Autoevaluaciones de cada entrega semanal (1–5). |
| **`README.md`** | Descripción general del proyecto. |

---

## 🧩 Ciclo de trabajo y entregas

### 🟢 Hands-On 1 — Selección y requisitos del dataset
- Búsqueda de datasets en el dominio de *Smart Cities*.  
- Selección de **tres datasets oficiales de la Comunidad de Madrid**:  
  - Calidad del aire (horarios).  
  - Meteorología.  
  - Activación de protocolos por contaminación.  
- Definición de la aplicación **BeSafe**.  
- Documentos: `datasetRequirements.html` y `applicationRequirements.html`.

---

### 🟡 Hands-On 2 — Ontología y estrategia de nombrado
- Análisis de los datasets y sus licencias.  
- Definición de URIs, dominios, namespaces y estrategia de nombrado.  
- Creación de la ontología **besafe-ontology.ttl**, con clases como:  
  - `AirQuality`, `Pollutant`, `WeatherCondition`, `Alert`, `Location`.  
- Ejemplo instanciado en `besafe-example.ttl`.

---

### 🟠 Hands-On 3 — Limpieza y normalización con OpenRefine
- Limpieza de los datasets (`*.json` con las operaciones).  
- Eliminación de inconsistencias y normalización de nombres de estaciones.  
- Generación de archivos `*-updated.csv` con datos listos para RDF.  

---

### 🔵 Hands-On 4 — Mapeo y transformación a RDF
- Definición de los **RML mappings** (`alertas_mapping.rml`).  
- Uso de **RMLMapper / Morph-KGC** para transformar los CSV en RDF Turtle (`alertas.ttl`).  
- Creación de consultas SPARQL de verificación (`queries.sparql`).

---

### 🟣 Hands-On 5 — Enlazado con datasets externos
- Reconciliación con **DBpedia** y **Wikidata** mediante OpenRefine.  
- Generación de archivos `*-with-links.csv`, `*-with-links.rml` y `*-with-links.ttl`.  
- Verificación de enlaces con `queries-with-links.sparql`.  
- Los datos finales enlazados permiten integrar alertas ambientales con información global sobre estaciones, ubicaciones y contaminantes.
