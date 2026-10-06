"""Check that the local environment can reach every data source and BigQuery.

Usage: uv run python scripts/verify_setup.py
"""

import sys
from collections.abc import Callable

import httpx

from ingestion.config import Settings, get_settings

TIMEOUT = httpx.Timeout(15.0)


def check_github(settings: Settings) -> str:
    resp = httpx.get(
        "https://api.github.com/rate_limit",
        headers={"Authorization": f"Bearer {settings.github_token.get_secret_value()}"},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    core = resp.json()["resources"]["core"]
    if core["limit"] < 5000:
        raise RuntimeError(f"limit is {core['limit']}; token not applied?")
    return f"{core['remaining']}/{core['limit']} requests left"


def check_stackexchange(settings: Settings) -> str:
    resp = httpx.get(
        "https://api.stackexchange.com/2.3/info",
        params={"site": "stackoverflow", "key": settings.stackexchange_key.get_secret_value()},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    body = resp.json()
    if body["quota_max"] < 10000:
        raise RuntimeError(f"quota_max is {body['quota_max']}; key not applied?")
    return f"{body['quota_remaining']}/{body['quota_max']} daily quota left"


def check_pypistats(_: Settings) -> str:
    resp = httpx.get("https://pypistats.org/api/packages/dbt-core/recent", timeout=TIMEOUT)
    resp.raise_for_status()
    return f"dbt-core last week: {resp.json()['data']['last_week']:,} downloads"


def check_bigquery(settings: Settings) -> str:
    from google.cloud import bigquery

    client = bigquery.Client(project=settings.gcp_project_id, location=settings.bq_location)
    list(client.query("SELECT 1").result())
    dataset = client.get_dataset(settings.bq_raw_dataset)
    return f"query ok, dataset {dataset.full_dataset_id} in {dataset.location}"


CHECKS: dict[str, Callable[[Settings], str]] = {
    "GitHub API": check_github,
    "Stack Exchange API": check_stackexchange,
    "PyPI Stats API": check_pypistats,
    "BigQuery": check_bigquery,
}


def main() -> int:
    try:
        settings = get_settings()
    except Exception as exc:
        print(f"✗ Settings: {exc}\n  Copy .env.example to .env and fill it in.")
        return 1
    print("✓ Settings loaded")

    failed = 0
    for name, check in CHECKS.items():
        try:
            print(f"✓ {name}: {check(settings)}")
        except Exception as exc:
            failed += 1
            print(f"✗ {name}: {exc}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
