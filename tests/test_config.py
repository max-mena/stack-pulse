import pytest
from pydantic import ValidationError

from ingestion.config import Settings

REQUIRED = {
    "GITHUB_TOKEN": "ghp_test",
    "STACKEXCHANGE_KEY": "se_test",
    "GCP_PROJECT_ID": "stack-pulse-test",
}


@pytest.fixture
def env(monkeypatch):
    for key, value in REQUIRED.items():
        monkeypatch.setenv(key, value)
    for key in ("BQ_LOCATION", "BQ_RAW_DATASET"):
        monkeypatch.delenv(key, raising=False)
    return monkeypatch


def test_loads_required_values_and_defaults(env):
    settings = Settings(_env_file=None)

    assert settings.gcp_project_id == "stack-pulse-test"
    assert settings.bq_location == "US"
    assert settings.bq_raw_dataset == "raw"


def test_tokens_are_masked_in_repr(env):
    settings = Settings(_env_file=None)

    assert "ghp_test" not in repr(settings)
    assert settings.github_token.get_secret_value() == "ghp_test"


def test_missing_required_value_fails(env):
    env.delenv("GITHUB_TOKEN")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
