import os
from pathlib import Path

import pytest

from f2a.parser.xml_parser import parse_form_xml
from f2a.persistence.oracle_repository import OracleRepository


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)

FORM_ID = 1

DB_USER = os.getenv("F2A_DB_USER", "F2A_OWNER")
DB_DSN = os.getenv(
    "F2A_DB_DSN",
    "localhost:1521/FREEPDB1",
)
DB_PASSWORD = os.getenv("F2A_DB_PASSWORD")


@pytest.fixture
def repository():
    if not DB_PASSWORD:
        pytest.skip(
            "F2A_DB_PASSWORD is not defined."
        )

    with OracleRepository(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN,
    ) as repo:
        yield repo


@pytest.mark.integration
def test_database_connection(repository):
    info = repository.get_database_info()

    assert info["user"] == "F2A_OWNER"
    assert info["container"] == "FREEPDB1"


@pytest.mark.integration
def test_oracle_counts_match_golden_sample(repository):
    model = parse_form_xml(FIXTURE)

    expected = {
        "blocks": len(model.blocks),
        "items": model.item_count,
        "triggers": model.trigger_count,
        "program_units": len(model.program_units),
        "lovs": len(model.lovs),
    }

    actual = repository.get_form_counts(
        FORM_ID
    )

    assert actual == expected


@pytest.mark.integration
@pytest.mark.dbwrite
def test_replace_form_model_is_idempotent(repository):
    if os.getenv("F2A_RUN_DB_WRITE_TESTS") != "1":
        pytest.skip(
            "Database write tests are disabled. "
            "Set F2A_RUN_DB_WRITE_TESTS=1 to enable them."
        )

    model = parse_form_xml(FIXTURE)

    expected = {
        "blocks": len(model.blocks),
        "items": model.item_count,
        "triggers": model.trigger_count,
        "program_units": len(model.program_units),
        "lovs": len(model.lovs),
    }

    # First import
    repository.replace_form_model(
        form_id=FORM_ID,
        model=model,
    )

    first = repository.get_form_counts(
        FORM_ID
    )

    assert first == expected

    # Second import
    repository.replace_form_model(
        form_id=FORM_ID,
        model=model,
    )

    second = repository.get_form_counts(
        FORM_ID
    )

    assert second == expected

    # Most important idempotence assertion
    assert second == first