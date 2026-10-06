# CLAUDE.md

Guidance for Claude Code in this repo.

## What this is
stack-pulse is a data engineering portfolio pipeline. It tracks momentum of data-stack tools (dbt, Airflow, Dagster, …) using GitHub, Stack Overflow and PyPI Stats. The flow is: ingest with Python → BigQuery `raw` → dbt staging/marts → Airflow → Streamlit.

- `docs/BUILD_PLAN.md`: week-by-week plan and the Claude Code setup (hooks/skills/agents). Check it for what the current week should deliver.
- `MEMORY.md`: why each stack decision was made (written in Spanish).

## Commands
```bash
uv sync                                  # install deps (Python 3.12, pinned in .python-version)
uv run pytest                            # tests
uv run ruff check . && uv run ruff format .
uv run python scripts/verify_setup.py    # checks .env, API keys and BigQuery access
pre-commit run --all-files
```

## Conventions
- Python 3.12, httpx (async clients), Pydantic models for every API payload, config only via `ingestion.config.get_settings()`.
- Tests mock HTTP with `respx`. Tests never hit real APIs or BigQuery.
- BigQuery: batch **load jobs** only (never streaming inserts). Raw tables are partitioned by `ingested_at`.
- dbt naming: `stg_<source>__<entity>`, `int_`, `fct_`, `mart_`. Every model gets a `schema.yml` entry with tests.
- Git: branch `feat|chore|docs/<item>` → PR → CI green → merge. Never push to `main` directly.

## Secrets
- Never read or print `.env`, `secrets/`, or `~/.config/gcloud` (blocked by `.claude/settings.json` and `.claude/hooks/guard_bash.py`).
- There are no JSON key files. Local dev uses gcloud Application Default Credentials. CI uses Workload Identity Federation (`scripts/bootstrap_gcp.sh`).
- When you need a new secret, add it to `.env.example` (blank) and `ingestion/config.py` as `SecretStr`.

## Hooks in this repo
- PreToolUse Bash → `guard_bash.py` blocks `bq rm`, `DROP`, `--full-refresh`, prod dbt target, force push, push to main, and reading secrets. If a blocked command is truly needed, ask the user to run it.
- PostToolUse Edit/Write → `ruff_on_edit.py` formats and lint-fixes edited `.py` files. Fix any errors it reports.
