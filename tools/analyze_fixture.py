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


def increment_counter(
    counter: dict[str, int],
    key: str,
) -> None:
    counter[key] = counter.get(key, 0) + 1


def main() -> None:

    print()
    print("Forms2APEX Accelerator - Migration Analysis")
    print("=" * 70)
    print(f"Fixture : {FIXTURE}")

    model = parse_form_xml(FIXTURE)
    findings = analyze_form(model)

    # FormModel todavía no almacena el nombre del formulario.
    # Por ahora lo derivamos del nombre del fixture.
    form_name = FIXTURE.stem.upper()

    print()
    print(f"Form     : {form_name}")
    print(f"Findings : {len(findings)}")
    print()

    # ----------------------------------------------------------
    # Finding detail
    # ----------------------------------------------------------

    for index, finding in enumerate(
        findings,
        start=1,
    ):
        print("-" * 70)
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

        # ------------------------------------------------------
        # Built-in semantic detail
        # ------------------------------------------------------

        if finding.builtin_details:

            print()
            print("Built-in Analysis:")

            for detail in finding.builtin_details:
                print(
                    f"  - {detail.name}"
                )
                print(
                    f"    Category      : {detail.category}"
                )
                print(
                    f"    APEX Strategy : {detail.apex_strategy}"
                )
                print(
                    f"    Risk          : {detail.risk}"
                )

        print()
        print("Recommendation:")
        print(finding.recommendation)

    print("-" * 70)

    # ----------------------------------------------------------
    # Summary counters
    # ----------------------------------------------------------

    patterns: dict[str, int] = {}
    complexities: dict[str, int] = {}
    risks: dict[str, int] = {}
    confidences: dict[str, int] = {}
    automation_levels: dict[str, int] = {}

    builtin_categories: dict[str, int] = {}
    builtin_strategies: dict[str, int] = {}
    builtin_usage: dict[str, int] = {}

    for finding in findings:

        increment_counter(
            patterns,
            finding.apex_pattern,
        )

        increment_counter(
            complexities,
            finding.complexity,
        )

        increment_counter(
            risks,
            finding.risk,
        )

        increment_counter(
            confidences,
            finding.confidence,
        )

        increment_counter(
            automation_levels,
            finding.automation_level,
        )

        for detail in finding.builtin_details:

            increment_counter(
                builtin_categories,
                detail.category,
            )

            increment_counter(
                builtin_strategies,
                detail.apex_strategy,
            )

            increment_counter(
                builtin_usage,
                detail.name,
            )

    # ----------------------------------------------------------
    # Summary by APEX Pattern
    # ----------------------------------------------------------

    print()
    print("Summary by APEX Pattern")
    print("=" * 70)

    for pattern, count in sorted(
        patterns.items()
    ):
        print(f"{pattern:<40} {count}")

    # ----------------------------------------------------------
    # Summary by Complexity
    # ----------------------------------------------------------

    print()
    print("Summary by Complexity")
    print("=" * 70)

    for complexity, count in sorted(
        complexities.items()
    ):
        print(f"{complexity:<40} {count}")

    # ----------------------------------------------------------
    # Summary by Risk
    # ----------------------------------------------------------

    print()
    print("Summary by Risk")
    print("=" * 70)

    for risk, count in sorted(
        risks.items()
    ):
        print(f"{risk:<40} {count}")

    # ----------------------------------------------------------
    # Summary by Confidence
    # ----------------------------------------------------------

    print()
    print("Summary by Confidence")
    print("=" * 70)

    for confidence, count in sorted(
        confidences.items()
    ):
        print(f"{confidence:<40} {count}")

    # ----------------------------------------------------------
    # Summary by Automation
    # ----------------------------------------------------------

    print()
    print("Summary by Automation Level")
    print("=" * 70)

    for automation_level, count in sorted(
        automation_levels.items()
    ):
        print(f"{automation_level:<40} {count}")

    # ----------------------------------------------------------
    # Built-in categories
    # ----------------------------------------------------------

    print()
    print("Summary by Forms Built-in Category")
    print("=" * 70)

    if builtin_categories:
        for category, count in sorted(
            builtin_categories.items()
        ):
            print(f"{category:<40} {count}")
    else:
        print("No Forms built-ins detected.")

    # ----------------------------------------------------------
    # Built-in usage
    # ----------------------------------------------------------

    print()
    print("Forms Built-in Usage")
    print("=" * 70)

    if builtin_usage:
        for builtin_name, count in sorted(
            builtin_usage.items()
        ):
            print(f"{builtin_name:<40} {count}")
    else:
        print("No Forms built-ins detected.")

    # ----------------------------------------------------------
    # APEX migration strategies from built-ins
    # ----------------------------------------------------------

    print()
    print("Built-in APEX Strategies")
    print("=" * 70)

    if builtin_strategies:
        for strategy, count in sorted(
            builtin_strategies.items()
        ):
            print(f"{strategy:<40} {count}")
    else:
        print("No built-in migration strategies detected.")

    # ----------------------------------------------------------
    # Migration effort
    # ----------------------------------------------------------

    total_effort = sum(
        finding.effort
        for finding in findings
    )

    print()
    print("Estimated Migration Effort")
    print("=" * 70)

    print(
        f"Total effort points : {total_effort}"
    )

    print(
        f"Total findings      : {len(findings)}"
    )

    print(
        "Built-ins detected  : "
        f"{sum(builtin_usage.values())}"
    )

    print()
    print("Migration analysis: OK")


if __name__ == "__main__":
    main()