# stack-pulse

A data engineering pipeline that tracks the health and adoption of modern data stack tools — using public data from GitHub, Stack Overflow, and PyPI to answer: *which tools are gaining momentum, and which are slowing down?*

## Why this project

The data engineering ecosystem evolves fast. This project treats tooling trends as a first-class data problem: ingest signals from public sources, transform them into clean models, and surface insights through a live dashboard.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Data Sources                       │
│  GitHub API   Stack Overflow API   PyPI Stats API   │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│               Ingestion (Python)                     │
│         httpx · Pydantic · python-dotenv            │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│            Data Platform (BigQuery)                  │
│              Raw → Staging → Marts                  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│             Transformation (dbt Core)                │
│        Models · Tests · Documentation               │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│           Orchestration (Apache Airflow)             │
│              DAGs · Scheduling · Alerts             │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              Dashboard (Streamlit)                   │
│         Trends · Rankings · Weekly diffs            │
└─────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Tool |
|---|---|
| Ingestion | Python 3.12, httpx, Pydantic |
| Data platform | BigQuery (Google Cloud free tier) |
| Transformation | dbt Core |
| Orchestration | Apache Airflow (Docker Compose) |
| Data quality | dbt tests + Pydantic schema validation |
| Dashboard | Streamlit |
| CI/CD | GitHub Actions |
| Version control | Git / GitHub |

## Data Sources

| Source | What we track |
|---|---|
| [GitHub API](https://docs.github.com/en/rest) | Stars, forks, open issues, commit frequency, contributors |
| [Stack Overflow API](https://api.stackexchange.com/) | Question volume, answer rate, tags trending |
| [PyPI Stats API](https://pypistats.org/api/) | Weekly download counts for Python packages |

## Tools tracked

`dbt-core` · `apache-airflow` · `dagster` · `prefect` · `airbyte` · `great-expectations` · `polars` · `duckdb` · `sqlmesh` · `elementary-data`

## Project Structure

```
stack-pulse/
├── dags/                   # Airflow DAGs
├── ingestion/              # API clients and raw data loaders
│   ├── github_client.py
│   ├── stackoverflow_client.py
│   └── pypi_client.py
├── dbt/                    # dbt project
│   ├── models/
│   │   ├── staging/        # Clean raw sources
│   │   └── marts/          # Business-ready models
│   └── tests/
├── dashboard/              # Streamlit app
│   └── app.py
├── tests/                  # Python unit tests
├── .github/workflows/      # CI/CD — dbt test on PR
├── docker-compose.yml      # Airflow local setup
├── .env.example
└── requirements.txt
```

## Roadmap

### Phase 1 — Foundation (current)
- [ ] Project structure and repository setup
- [ ] GitHub API client with Pydantic validation
- [ ] BigQuery raw dataset and loading script
- [ ] Initial dbt staging models + basic tests

### Phase 2 — Pipeline
- [ ] Stack Overflow and PyPI clients
- [ ] dbt marts: weekly snapshots, rankings, diffs
- [ ] Airflow DAG orchestrating the full pipeline
- [ ] GitHub Actions: run dbt tests on every PR

### Phase 3 — Dashboard
- [ ] Streamlit app connected to BigQuery
- [ ] Tool comparison view
- [ ] Weekly trend summary

### Phase 4 — Extras
- [ ] LLM-generated weekly digest (Gemini API or Claude)
- [ ] Alerting on significant trend changes
- [ ] dbt documentation site (hosted)

## Setup

> Full setup guide coming in Phase 1.

Requirements:
- Python 3.12+
- Docker + Docker Compose (for Airflow)
- Google Cloud account (BigQuery free tier)
- GitHub personal access token
- Stack Overflow API key (free)

## License

MIT
