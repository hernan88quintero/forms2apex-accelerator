from pathlib import Path

from f2a.parser.xml_parser import parse_form_xml
from f2a.reporting.generator import (
    generate_assessment_file,
)


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)

OUTPUT_DIR = Path(
    "output"
)


def main() -> None:

    print()
    print(
        "Forms2APEX Accelerator - Assessment Generator"
    )
    print("=" * 60)

    print(
        f"Source : {FIXTURE}"
    )

    model = parse_form_xml(
        FIXTURE
    )

    form_name = (
        FIXTURE.stem.upper()
    )

    output_path = generate_assessment_file(
        model,
        form_name=form_name,
        output_dir=OUTPUT_DIR,
    )

    print(
        f"Form   : {form_name}"
    )

    print(
        f"Output : {output_path}"
    )

    print()
    print(
        "Assessment generation: OK"
    )


if __name__ == "__main__":
    main()