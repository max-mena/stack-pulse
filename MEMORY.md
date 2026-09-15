# stack-pulse — Project Memory

Contexto de decisiones y razonamiento detrás del proyecto. Referencia para retomar trabajo entre sesiones.

---

## Origen del proyecto

### Proyecto anterior: intel-ai-demo-sync-utils

El proyecto que dio origen a stack-pulse fue `intel-ai-demo-sync-utils`, un pipeline ETL construido durante el trabajo en Intel. Hacía lo siguiente:

- Extraía metadata de notebooks de OpenVINO via web scraping (BeautifulSoup)
- Importaba datos desde Smartsheet
- Generaba summaries con un modelo LLM local (TensorFlow + Transformers)
- Almacenaba todo en SQLite via SQLAlchemy
- Exportaba JSON como output final
- Se ejecutaba **manualmente** con `python main.py`

### Por qué no se refactorizó ese proyecto

Se evaluó si valía la pena refactorizarlo y se decidió **crear un proyecto nuevo** por estas razones:

1. Los datos dependían de fuentes internas de Intel (Smartsheet privado, repos internos). Refactorizarlo público requeriría datos mock, lo que le quita autenticidad.
2. El repo original ya cumple su función como evidencia de trabajo ETL real en producción. No necesita ser perfecto técnicamente.
3. Un proyecto nuevo con datos públicos reales y stack moderno demuestra más que el mismo proyecto refactorizado con datos simulados.

### Problemas técnicos identificados en el proyecto Intel

Para referencia, los antipatrones que stack-pulse corrige:

| Problema en intel-ai-demo-sync-utils | Solución en stack-pulse |
|---|---|
| Ejecución manual (`python main.py`) | Airflow DAGs con scheduling |
| Web scraping frágil (BeautifulSoup) | APIs oficiales (GitHub, Stack Overflow, PyPI) |
| Procesamiento fila por fila | Carga columnar batch a BigQuery |
| SQLite como destino | BigQuery (data warehouse real) |
| TensorFlow local para LLM | API externa (Phase 4, opcional) |
| Sin tests | dbt tests + Pydantic validation + GitHub Actions |
| JSON como formato intermedio | BigQuery raw tables → dbt staging → marts |

---

## Contexto de la empresa target

La empresa donde trabaja el usuario compartió una encuesta de tecnologías. stack-pulse fue diseñado para orbitar alrededor de esa lista.

### Lista completa de tecnologías de la encuesta

**Fundamentos:** SQL, Python, JavaScript, Data Modeling, Semantic Layer, Git/Version Control, APIs, Quality Testing, Snowflake Cortex, Machine Learning, Agentic AI/RAG/LLMs

**Visualización:** Power BI, Tableau, Sigma, Looker

**Ingesta/ELT:** Fivetran, HVR, Matillion, Airbyte, Azure Data Factory

**Transformación:** dbt Core, dbt Cloud, Coalesce

**Orquestación:** Airflow, Dagster

**Plataformas de datos:** Snowflake, Databricks, Microsoft Fabric, BigQuery, Amazon Redshift, Azure Synapse

**Cloud:** AWS, Azure, GCP

**Gobierno de datos:** Horizon Catalog, Alation, Atlan, Collibra

**App Development:** Front-end, Back-end, IaC, App Testing, Secure Coding Practices, Streamlit, CI/CD

**Certificaciones:** Snowflake, Databricks, dbt, Coalesce, Power BI, Sigma, Azure, AWS, Matillion

### Estrategia de cobertura

No se intenta cubrir toda la lista (quedaría forzado). Se priorizó:

- **Núcleo exigible** (toda posición lo pide): Python, SQL, dbt Core, Git, APIs, Quality Testing
- **Diferenciadores reales** (separan juniors de seniors): Airflow, BigQuery, dbt Cloud
- **Bonus visible** (demuestran capacidad de ship): Streamlit, CI/CD con GitHub Actions, Pydantic

---

## Decisiones de stack y razonamiento

### Plataforma de datos: BigQuery

- El usuario tiene contacto con Snowflake en el trabajo → no necesita practicarlo en paralelo
- BigQuery tiene **free tier permanente** (10 GB storage + 1 TB queries/mes gratis)
- Aparece en la lista de la empresa target
- GCP es uno de los 3 cloud providers de la encuesta

### Orquestador: Apache Airflow

- El usuario ya usa Airflow en el trabajo → consolidar conocimiento existente
- Es **gratuito y open source** (self-hosted con Docker Compose)
- Es el orquestador más reconocido en entornos enterprise
- Aparece explícitamente en la lista de la encuesta

Alternativa evaluada: Dagster (más fácil de levantar localmente) — descartado porque Airflow aporta más al portfolio dado el contexto laboral.

### Ingesta: Python con httpx + Pydantic

- `httpx` sobre `requests`: soporte nativo async, más moderno
- Pydantic para validación de schema en ingesta → cubre "Quality Testing" de la encuesta
- Sin herramientas de ingesta managed (Fivetran, Airbyte) porque requieren licencia o empresa

### Enfoque de desarrollo: iterativo

- Empezar con algo funcional básico (Phase 1)
- Iterar por fases
- No over-engineer desde el inicio

---

## Concepto del proyecto

### Qué hace stack-pulse

Pipeline de datos que trackea la salud y adopción de herramientas del ecosistema moderno de data engineering, usando señales de fuentes públicas.

**Pregunta que responde:** ¿Qué herramientas están ganando momentum y cuáles están desacelerando?

### Fuentes de datos

| Fuente | Qué se extrae |
|---|---|
| GitHub API | Stars, forks, issues abiertos, frecuencia de commits, contributors |
| Stack Overflow API | Volumen de preguntas, answer rate, tags en tendencia |
| PyPI Stats API | Descargas semanales de paquetes Python |

Todas las fuentes son **públicas y gratuitas**.

### Herramientas trackeadas (lista inicial)

`dbt-core` · `apache-airflow` · `dagster` · `prefect` · `airbyte` · `great-expectations` · `polars` · `duckdb` · `sqlmesh` · `elementary-data`

### Por qué este dominio

1. Los datos son sobre las mismas herramientas que evalúan en la empresa target
2. Demuestra conocimiento del ecosistema, no solo del código
3. Es técnico, no genérico (no otro análisis de ventas o películas)
4. Los datos cambian semanalmente → el proyecto puede mantenerse vivo
5. El resultado es genuinamente interesante y útil

---

## Roadmap

### Phase 1 — Foundation
- [ ] GitHub API client con Pydantic validation
- [ ] BigQuery: dataset raw + script de carga
- [ ] dbt: staging models iniciales + tests básicos

### Phase 2 — Pipeline completo
- [ ] Clientes para Stack Overflow API y PyPI Stats API
- [ ] dbt marts: snapshots semanales, rankings, diffs semana a semana
- [ ] Airflow DAG que orquesta el pipeline completo
- [ ] GitHub Actions: correr dbt tests en cada PR

### Phase 3 — Dashboard
- [ ] Streamlit app conectada a BigQuery
- [ ] Vista de comparación entre herramientas
- [ ] Resumen semanal de tendencias

### Phase 4 — Extras (si se llega)
- [ ] Digest semanal generado con LLM (Gemini API o Claude) → cubre "Agentic AI/RAG/LLMs" de la encuesta
- [ ] Alertas en cambios significativos de tendencia
- [ ] dbt docs site hosteado

---

## Estado actual del repo (Sep 2026)

- Repo creado: https://github.com/max-mena/stack-pulse
- README con arquitectura, stack, fuentes, estructura de carpetas y roadmap
- Sin código aún — siguiente paso es Phase 1
- Lenguaje del repo: inglés (alcance internacional)

---

## Otros repos del perfil (contexto)

Tras la limpieza del perfil GitHub:

| Repo | Estado | Notas |
|---|---|---|
| intel-ai-demo-sync-utils | Activo | Trabajo real en Intel, el origen de stack-pulse |
| intel-ai-repository | Activo | Frontend React/TS del sistema Intel |
| ImageHandler | Activo | Python GUI, funcional |
| lemon-app | Activo | Capstone Meta/Coursera React |
| max-mena-SD.github.io | Activo | Portfolio .NET/C# |
| grafico-proyeccion | Archivado | Experimento vacío |
| SnowCoreProLearn | Archivado | Notas de certificación |
| open_notebooks | Eliminado | Fork sin contribución propia |

Todos los READMEs de repos activos fueron mejorados en la misma sesión.
