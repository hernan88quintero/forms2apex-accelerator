from pathlib import Path
import sys

from f2a.parser.xml_parser import parse_form_xml


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)


def main() -> None:
    print()
    print("Forms2APEX Accelerator - XML Parser")
    print("-----------------------------------")
    print(f"Fixture : {FIXTURE}")
    print()

    model = parse_form_xml(FIXTURE)

    actual = {
        "blocks": len(model.blocks),
        "items": model.item_count,
        "triggers": model.trigger_count,
        "program-units": len(model.program_units),
        "lovs": len(model.lovs),
    }

    print("Parsed model")
    print("-----------------------------------")

    all_ok = True

    for key, value in actual.items():
        expected = model.expected_results.get(key)
        ok = expected == value

        if not ok:
            all_ok = False

        status = "OK" if ok else "ERROR"

        print(
            f"{key:15} "
            f"actual={value:<3} "
            f"expected={expected!s:<3} "
            f"[{status}]"
        )

    print()
    print("Blocks")
    print("-----------------------------------")

    for block in model.blocks:
        print(
            f"{block.name:15} "
            f"items={len(block.items):<2} "
            f"triggers={len(block.triggers)}"
        )

    print()
    print("Program Units")
    print("-----------------------------------")

    for unit in model.program_units:
        print(
            f"{unit.name:20} "
            f"{unit.unit_type}"
        )

    print()
    print("LOVs")
    print("-----------------------------------")

    for lov in model.lovs:
        print(
            f"{lov.name:20} "
            f"values={len(lov.values)}"
        )

    print()
    print("-----------------------------------")

    if all_ok:
        print("Golden Sample validation: OK")
        return

    print("Golden Sample validation: ERROR")
    sys.exit(1)


if __name__ == "__main__":
    main()