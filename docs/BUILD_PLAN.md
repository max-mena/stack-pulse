# stack-pulse — Build Plan

How to take stack-pulse from an empty repo to a live dashboard. It covers the weekly cadence, what to build each week, and where Claude Code agents, skills, hooks and tools fit in.

**Assumptions**
- About 6 h/week: two 2 h weekday sessions plus one 2–3 h weekend block.
- No accounts or credentials exist yet, so Week 0 sets them up.
- The Claude Code configuration (`.claude/`) is committed to the repo.
- Git flow: feature branches with one PR per roadmap item, and CI on every PR.

> **Why not `gh-stack` (stacked PRs)?** Stacked PRs pay off when waiting on review blocks work that depends on it. A solo developer who self-merges small PRs within a day never waits on review, so stacking only adds rebase overhead. Plain feature branches + PRs is the right fit here.

---

## 1. Cadence principles

- **One roadmap item = one branch = one PR.** Keep each PR small enough to finish in 1–2 sessions. Name branches `feat/<item>`, `chore/<item>` or `docs/<item>`.
- **Start collecting data early.** GitHub stars and Stack Overflow counts are point-in-time snapshots, and their history can't be backfilled. So from **Week 2** a GitHub Actions cron runs ingestion daily, and Airflow takes over in Week 7. PyPI (about 180 days of history) and Stack Overflow (queryable by date) can be backfilled later.
- **End every week with something you can show,** and tick the README roadmap checkboxes in the same PR.
- **Keep BigQuery free:**
  - Use batch **load jobs** only (free), never streaming inserts.
  - Partition raw tables by `ingested_at`.
  - Set a GCP budget alert at $1.

---

## 2. Timeline (~6 h/week)

| Week | Goal | Key outputs |
|---|---|---|
| **0** | Accounts + scaffolding | GCP project; BQ datasets `raw` / `staging` / `marts` / `ci`; service account (BigQuery Data Editor + Job User); budget alert; GitHub PAT; Stack Exchange key. `pyproject.toml` (uv), ruff, pytest, pre-commit, `.env.example`, `.gitignore` for keys; `CLAUDE.md` via `/init`; `.claude/` hooks + settings |
| **1** | GitHub client | `ingestion/github_client.py` (async httpx, retry/backoff, rate-limit headers), Pydantic `RepoSnapshot` model, unit tests with mocked HTTP (`respx`) |
| **2** | Load to BigQuery + start collecting | `ingestion/loaders/bigquery.py` (load job from NDJSON, schema derived from Pydantic), `ingestion/cli.py` (`python -m ingestion github`), `.github/workflows/ingest.yml` daily cron using a GCP key secret |
| **3** | dbt foundation | `dbt init`, `sources.yml`, seed `tools.csv` (`tool_id, github_repo, pypi_package, so_tag`), `stg_github__repo_snapshots` + not_null / unique / accepted_range tests, `.github/workflows/dbt-ci.yml` (`dbt build` into `ci` dataset on PR). ✅ **Phase 1 done** |
| **4** | PyPI source | `ingestion/pypi_client.py` + model + tests, 180-day backfill, `stg_pypi__downloads` |
| **5** | Stack Overflow source | `ingestion/stackoverflow_client.py` (honours the API `backoff` field and quota), `stg_stackoverflow__tag_activity` |
| **6** | Marts | `int_tool_daily_signals`, `fct_tool_weekly_metrics`, `mart_tool_rankings`, `mart_tool_wow_diffs`, with dbt tests + docs |
| **7** | Airflow | `docker-compose.yml` (official image, LocalExecutor) on the home server; `dags/stack_pulse_daily.py` (3 ingestions in parallel → `dbt build` → freshness check, alert on failure); disable the Actions cron. ✅ **Phase 2 done** |
| **8–9** | Dashboard | `dashboard/app.py` (Streamlit, cached BQ queries): rankings, tool comparison, weekly diff; deploy to Streamlit Community Cloud. ✅ **Phase 3 done** |
| **10+** | Extras | Weekly digest written by Claude from `mart_tool_wow_diffs`, threshold alerts, dbt docs hosted on GitHub Pages |

**Buffer:** expect about 20% slippage, so the realistic target for the dashboard is **~10–11 weeks**.

---

## 3. Claude Code setup (committed under `.claude/`)

### Hooks — `.claude/settings.json`
These are guardrails that must fire every time, so they're hooks rather than memory or instructions.

| Event | Matcher | Action |
|---|---|---|
| `PostToolUse` | Edit \| Write on `*.py` | `ruff format` + `ruff check --fix` |
| `PostToolUse` | Edit \| Write on `dbt/**/*.sql` | `sqlfluff fix --dialect bigquery` (dbt templater) |
| `PreToolUse` | Bash | Block destructive or costly commands: `bq rm`, `DROP`, `dbt run --target prod`, `--full-refresh` outside CI, `git push --force`, `git push origin main` |
| `PreToolUse` | Read \| Bash | Block reading `.env`, key files under `secrets/`, `~/.config/gcloud` |
| `Stop` *(optional, from Week 2)* | — | `pytest -q -x tests/`, so a session never ends with failing tests |

### Project skills — `.claude/skills/`
Each skill captures a pattern that repeats at least three times.

| Skill | What it does | First used |
|---|---|---|
| `new-source-client` | Scaffolds API client + Pydantic model + respx tests + loader wiring + CLI subcommand, following `github_client.py` | Week 4 (again in Week 5) |
| `new-dbt-model` | Creates model SQL + `schema.yml` entry with required tests and descriptions; enforces naming (`stg_<source>__<entity>`, `int_`, `fct_`, `mart_`) | Week 3 |
| `pipeline-smoke` | Ingests one tool → loads to `ci` → `dbt build --select state:modified+` → prints row counts | Before every PR from Week 3 |

### Project agents — `.claude/agents/`
There are only three agents, each with a narrow read-only role.

| Agent | Tools | Role | When |
|---|---|---|---|
| `api-researcher` | WebFetch, Read | Before writing a client, confirms endpoints, auth, rate limits and pagination, and returns a short spec | Weeks 1, 4, 5 |
| `dbt-reviewer` | Read, Grep | Checks grain, join fan-out, missing tests/docs and naming | Before each dbt PR |
| `data-qa` | Bash (only `bq query --dry_run` / SELECTs) | Checks freshness, row counts and null spikes | After pipeline changes |

### Built-in commands at set points
- `/code-review`: before every merge.
- `/security-review`: in Week 2 (credentials in CI) and before promoting the repo.
- `run` skill: launch and check the Streamlit dashboard.
- `claude-api` skill: the Phase 4 weekly digest.
- `/fewer-permission-prompts`: after Week 2, once there's a history of common commands to allowlist.

### Tooling
uv · ruff · pytest + respx · pre-commit · sqlfluff · dbt-bigquery · gh CLI · gcloud / bq CLI · Docker Compose

---

## 4. Definition of done (every PR)

- [ ] Tests green locally and in CI
- [ ] Hooks / pre-commit pass (ruff, sqlfluff)
- [ ] `/code-review` findings addressed
- [ ] README roadmap checkboxes and docs updated

---

## 5. Open decisions to revisit

- Verify the Airbyte PyPI package (`airbyte` is PyAirbyte, not the platform). Check SO tag volume for newer tools: `sqlmesh` and `elementary` may be very low.
- dbt Cloud free developer seat (listed as a differentiator in `MEMORY.md`): optional, from Week 6.
