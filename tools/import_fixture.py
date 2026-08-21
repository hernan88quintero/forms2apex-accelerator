from getpass import getpass
from pathlib import Path
import sys

from f2a.parser.xml_parser import parse_form_xml
from f2a.persistence.oracle_repository import OracleRepository


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)

FORM_ID = 1


def get_model_counts(model) -> dict[str, int]:
    return {
        "blocks": len(model.blocks),
        "items": model.item_count,
        "triggers": model.trigger_count,
        "program_units": len(model.program_units),
        "lovs": len(model.lovs),
    }


def get_expected_counts(model) -> dict[str, int]:
    return {
        "blocks": model.expected_results.get("blocks"),
        "items": model.expected_results.get("items"),
        "triggers": model.expected_results.get("triggers"),
        "program_units": model.expected_results.get("program-units"),
        "lovs": model.expected_results.get("lovs"),
    }


def print_counts(
    title: str,
    counts: dict[str, int],
) -> None:

    print()
    print(title)
    print("------------------------------------------")
    print(f"Blocks        : {counts['blocks']}")
    print(f"Items         : {counts['items']}")
    print(f"Triggers      : {counts['triggers']}")
    print(f"Program Units : {counts['program_units']}")
    print(f"LOVs          : {counts['lovs']}")


def main() -> None:

    print()
    print("Forms2APEX Accelerator - Fixture Import")
    print("------------------------------------------")
    print(f"Fixture : {FIXTURE}")
    print(f"Form ID : {FORM_ID}")

    # --------------------------------------------------------------
    # 1. Parse XML
    # --------------------------------------------------------------
    model = parse_form_xml(FIXTURE)

    actual = get_model_counts(model)
    expected = get_expected_counts(model)

    print_counts(
        "Parsed XML",
        actual,
    )

    # --------------------------------------------------------------
    # 2. Validate Golden Sample before touching Oracle
    # --------------------------------------------------------------
    if actual != expected:

        print_counts(
            "Expected",
            expected,
        )

        print()
        print("Golden Sample validation: ERROR")
        print("Oracle was NOT modified.")

        sys.exit(1)

    print()
    print("Golden Sample validation: OK")

    # --------------------------------------------------------------
    # 3. Connect to Oracle
    # --------------------------------------------------------------
    password = getpass(
        "Password F2A_OWNER: "
    )

    with OracleRepository(
        user="F2A_OWNER",
        password=password,
    ) as repository:

        info = repository.get_database_info()

        print()
        print("Oracle")
        print("------------------------------------------")
        print(f"User      : {info['user']}")
        print(f"Container : {info['container']}")

        # ----------------------------------------------------------
        # 4. Current database state
        # ----------------------------------------------------------
        before = repository.get_form_counts(
            FORM_ID
        )

        print_counts(
            "Before import",
            before,
        )

        # ----------------------------------------------------------
        # 5. Replace canonical model transactionally
        # ----------------------------------------------------------
        print()
        print("Importing canonical model...")

        repository.replace_form_model(
            form_id=FORM_ID,
            model=model,
        )

        # ----------------------------------------------------------
        # 6. Validate resulting Oracle state
        # ----------------------------------------------------------
        after = repository.get_form_counts(
            FORM_ID
        )

        print_counts(
            "After import",
            after,
        )

    # --------------------------------------------------------------
    # 7. Final validation
    # --------------------------------------------------------------
    if after != expected:

        print()
        print("End-to-end validation: ERROR")
        print("Oracle counts do not match Golden Sample.")

        sys.exit(1)

    print()
    print("------------------------------------------")
    print("End-to-end validation: OK")
    print("XML -> Python Model -> Oracle: SUCCESS")


if __name__ == "__main__":
    main()