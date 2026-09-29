from pathlib import Path
import xml.etree.ElementTree as ET

from f2a.parser.xml_parser import parse_form_xml


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)


def _apply_namespace(
    root,
    namespace: str,
) -> None:

    for element in root.iter():

        if not isinstance(
            element.tag,
            str,
        ):
            continue

        local_name = (
            element.tag.split(
                "}",
                1,
            )[-1]
        )

        element.tag = (
            f"{{{namespace}}}"
            f"{local_name}"
        )


def test_parser_supports_default_xml_namespace(
    tmp_path,
):
    baseline = parse_form_xml(
        FIXTURE
    )

    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    namespace = (
        "urn:forms2apex:test:oracle-forms"
    )

    ET.register_namespace(
        "",
        namespace,
    )

    _apply_namespace(
        root,
        namespace,
    )

    namespaced_file = (
        tmp_path
        / "namespaced_form.xml"
    )

    tree.write(
        namespaced_file,
        encoding="utf-8",
        xml_declaration=True,
    )

    parsed = parse_form_xml(
        namespaced_file
    )

    assert len(
        parsed.blocks
    ) == len(
        baseline.blocks
    )

    assert (
        parsed.item_count
        == baseline.item_count
    )

    assert (
        parsed.trigger_count
        == baseline.trigger_count
    )

    assert len(
        parsed.program_units
    ) == len(
        baseline.program_units
    )

    assert len(
        parsed.lovs
    ) == len(
        baseline.lovs
    )

    assert [
        block.name
        for block in parsed.blocks
    ] == [
        block.name
        for block in baseline.blocks
    ]

    assert [
        unit.name
        for unit in parsed.program_units
    ] == [
        unit.name
        for unit in baseline.program_units
    ]