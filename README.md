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
│         httpx · Pydantic · pydantic-settings          │
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
├── pyproject.toml          # uv-managed dependencies
└── uv.lock
```

## Roadmap

### Phase 1 — Foundation (current)
- [x] Project structure and repository setup
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

**Requirements:** [uv](https://docs.astral.sh/uv/) (installs Python 3.12 for you), [Google Cloud CLI](https://cloud.google.com/sdk/docs/install), Docker + Docker Compose (for Airflow, Phase 2), a Google Cloud project with billing linked (usage stays within the free tier), a GitHub fine-grained token (public repos, read-only), and a [Stack Exchange app key](https://stackapps.com/apps/oauth/register).

```bash
# 1. Dependencies and git hooks
uv sync
uv run pre-commit install

# 2. Secrets: fill in the blanks (the file is gitignored)
cp .env.example .env

# 3. Google Cloud auth. Uses your own account locally, no key files
gcloud auth login
gcloud auth application-default login

# 4. Create the BigQuery dataset, service account and GitHub Actions identity (idempotent)
GCP_PROJECT_ID=<your-project> ./scripts/bootstrap_gcp.sh

# 5. Check everything is reachable
uv run python scripts/verify_setup.py
```

CI authenticates to BigQuery through **Workload Identity Federation**, with no long-lived keys. Step 4 prints the three `gh variable set` commands to run.

## License

MIT
