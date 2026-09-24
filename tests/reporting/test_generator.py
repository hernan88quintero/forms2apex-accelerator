from pathlib import Path

from f2a.parser.xml_parser import parse_form_xml
from f2a.reporting.generator import (
    generate_assessment_file,
)


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)


def test_generate_assessment_file(
    tmp_path,
):
    model = parse_form_xml(
        FIXTURE
    )

    output_path = generate_assessment_file(
        model,
        form_name="F2A_CUSTOMERS_FORM",
        output_dir=tmp_path,
    )

    assert output_path.exists()

    assert (
        output_path.name
        == "F2A_CUSTOMERS_FORM_assessment.md"
    )

    content = output_path.read_text(
        encoding="utf-8"
    )

    assert (
        "# Forms2APEX Migration Assessment"
        in content
    )

    assert (
        "F2A_CUSTOMERS_FORM"
        in content
    )

    assert (
        "## Executive Summary"
        in content
    )

    assert (
        "## Suggested Migration Plan"
        in content
    )

    assert (
        "**Total effort points:** 9"
        in content
    )


def test_generator_creates_output_directory(
    tmp_path,
):
    model = parse_form_xml(
        FIXTURE
    )

    output_dir = (
        tmp_path
        / "nested"
        / "reports"
    )

    assert not output_dir.exists()

    output_path = generate_assessment_file(
        model,
        form_name="F2A_CUSTOMERS_FORM",
        output_dir=output_dir,
    )

    assert output_dir.exists()
    assert output_path.exists()