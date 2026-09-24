from pathlib import Path

from f2a.parser.xml_parser import parse_form_xml
from f2a.rules.analyzer import analyze_form


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)


def format_values(values: tuple[str, ...]) -> str:
    if not values:
        return "-"

    return ", ".join(values)


def main() -> None:

    print()
    print("Forms2APEX Accelerator - Migration Analysis")
    print("=" * 60)
    print(f"Fixture : {FIXTURE}")

    model = parse_form_xml(FIXTURE)
    findings = analyze_form(model)

    # FormModel todavía no almacena el nombre del Form.
    # Por ahora lo derivamos del nombre del fixture.
    form_name = FIXTURE.stem.upper()

    print()
    print(f"Form     : {form_name}")
    print(f"Findings : {len(findings)}")
    print()

    for index, finding in enumerate(
        findings,
        start=1,
    ):
        print("-" * 60)
        print(f"[{index}] {finding.object_name}")
        print()

        print(f"Scope          : {finding.scope}")
        print(f"Forms Trigger  : {finding.trigger_name}")
        print(f"APEX Pattern   : {finding.apex_pattern}")
        print(f"Complexity     : {finding.complexity}")
        print(f"Risk           : {finding.risk}")
        print(f"Effort         : {finding.effort}")
        print(f"Confidence     : {finding.confidence}")
        print(f"Automation     : {finding.automation_level}")

        print(
            "Program Units  : "
            f"{format_values(finding.referenced_program_units)}"
        )

        print(
            "Forms Builtins : "
            f"{format_values(finding.builtins)}"
        )

        print()
        print("Recommendation:")
        print(finding.recommendation)

    print("-" * 60)

    # --------------------------------------------------------------
    # Summary by APEX Pattern
    # --------------------------------------------------------------

    print()
    print("Summary by APEX Pattern")
    print("=" * 60)

    patterns: dict[str, int] = {}

    for finding in findings:
        patterns[finding.apex_pattern] = (
            patterns.get(
                finding.apex_pattern,
                0,
            )
            + 1
        )

    for pattern, count in sorted(
        patterns.items()
    ):
        print(f"{pattern:<30} {count}")

    # --------------------------------------------------------------
    # Summary by Complexity
    # --------------------------------------------------------------

    print()
    print("Summary by Complexity")
    print("=" * 60)

    complexities: dict[str, int] = {}

    for finding in findings:
        complexities[finding.complexity] = (
            complexities.get(
                finding.complexity,
                0,
            )
            + 1
        )

    for complexity, count in sorted(
        complexities.items()
    ):
        print(f"{complexity:<30} {count}")

    # --------------------------------------------------------------
    # Summary by Risk
    # --------------------------------------------------------------

    print()
    print("Summary by Risk")
    print("=" * 60)

    risks: dict[str, int] = {}

    for finding in findings:
        risks[finding.risk] = (
            risks.get(
                finding.risk,
                0,
            )
            + 1
        )

    for risk, count in sorted(
        risks.items()
    ):
        print(f"{risk:<30} {count}")

    # --------------------------------------------------------------
    # Summary by Confidence
    # --------------------------------------------------------------

    print()
    print("Summary by Confidence")
    print("=" * 60)

    confidences: dict[str, int] = {}

    for finding in findings:
        confidences[finding.confidence] = (
            confidences.get(
                finding.confidence,
                0,
            )
            + 1
        )

    for confidence, count in sorted(
        confidences.items()
    ):
        print(f"{confidence:<30} {count}")

    # --------------------------------------------------------------
    # Summary by Automation
    # --------------------------------------------------------------

    print()
    print("Summary by Automation Level")
    print("=" * 60)

    automation_levels: dict[str, int] = {}

    for finding in findings:
        automation_levels[
            finding.automation_level
        ] = (
            automation_levels.get(
                finding.automation_level,
                0,
            )
            + 1
        )

    for automation_level, count in sorted(
        automation_levels.items()
    ):
        print(f"{automation_level:<30} {count}")

    # --------------------------------------------------------------
    # Total effort
    # --------------------------------------------------------------

    total_effort = sum(
        finding.effort
        for finding in findings
    )

    print()
    print("Estimated Migration Effort")
    print("=" * 60)
    print(f"Total effort points : {total_effort}")
    print(f"Total findings      : {len(findings)}")

    print()
    print("Migration analysis: OK")


if __name__ == "__main__":
    main()