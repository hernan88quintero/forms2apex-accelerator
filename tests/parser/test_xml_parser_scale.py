from pathlib import Path
import copy
import xml.etree.ElementTree as ET

from f2a.parser.xml_parser import parse_form_xml
from f2a.reporting.assessment import (
    render_assessment_markdown,
)


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)

EXTRA_BLOCKS = 50


def _normalize_xml_name(
    name: str,
) -> str:
    local_name = name.split(
        "}",
        1,
    )[-1]

    return "".join(
        character
        for character in local_name.lower()
        if character.isalnum()
    )


def _get_attribute(
    element: ET.Element,
    attribute_name: str,
) -> str | None:

    expected_name = _normalize_xml_name(
        attribute_name
    )

    for actual_name, value in element.attrib.items():

        if (
            _normalize_xml_name(actual_name)
            == expected_name
        ):
            return value

    return None


def _set_attribute(
    element: ET.Element,
    attribute_name: str,
    value: str,
) -> None:

    expected_name = _normalize_xml_name(
        attribute_name
    )

    for actual_name in list(
        element.attrib.keys()
    ):

        if (
            _normalize_xml_name(actual_name)
            == expected_name
        ):
            element.attrib[
                actual_name
            ] = value
            return

    element.set(
        attribute_name,
        value,
    )


def _find_first(
    root: ET.Element,
    tag_name: str,
) -> ET.Element:

    expected_name = _normalize_xml_name(
        tag_name
    )

    for element in root.iter():

        if not isinstance(
            element.tag,
            str,
        ):
            continue

        if (
            _normalize_xml_name(element.tag)
            == expected_name
        ):
            return element

    raise AssertionError(
        f"Element not found: {tag_name}"
    )


def _find_parent(
    root: ET.Element,
    child: ET.Element,
) -> ET.Element:

    for parent in root.iter():

        for candidate in list(parent):

            if candidate is child:
                return parent

    raise AssertionError(
        "Parent element not found."
    )


def _build_large_fixture(
    tmp_path,
) -> Path:

    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    source_block = _find_first(
        root,
        "Block",
    )

    source_name = _get_attribute(
        source_block,
        "Name",
    )

    assert source_name is not None

    parent = _find_parent(
        root,
        source_block,
    )

    for index in range(
        1,
        EXTRA_BLOCKS + 1,
    ):
        cloned_block = copy.deepcopy(
            source_block
        )

        _set_attribute(
            cloned_block,
            "Name",
            f"{source_name}_{index:03d}",
        )

        parent.append(
            cloned_block
        )

    large_file = (
        tmp_path
        / "large_form.xml"
    )

    tree.write(
        large_file,
        encoding="utf-8",
        xml_declaration=True,
    )

    return large_file


def _count_block_triggers(
    block,
) -> int:

    return (
        len(block.triggers)
        + sum(
            len(item.triggers)
            for item in block.items
        )
    )


def test_parser_supports_large_form(
    tmp_path,
):
    baseline = parse_form_xml(
        FIXTURE
    )

    source_block = baseline.blocks[0]

    large_file = _build_large_fixture(
        tmp_path
    )

    parsed = parse_form_xml(
        large_file
    )

    expected_blocks = (
        len(baseline.blocks)
        + EXTRA_BLOCKS
    )

    expected_items = (
        baseline.item_count
        + (
            EXTRA_BLOCKS
            * len(source_block.items)
        )
    )

    expected_triggers = (
        baseline.trigger_count
        + (
            EXTRA_BLOCKS
            * _count_block_triggers(
                source_block
            )
        )
    )

    assert len(
        parsed.blocks
    ) == expected_blocks

    assert (
        parsed.item_count
        == expected_items
    )

    assert (
        parsed.trigger_count
        == expected_triggers
    )

    assert (
        parsed.blocks[-1].name
        == "CUSTOMERS_050"
    )


def test_large_form_can_generate_assessment(
    tmp_path,
):
    large_file = _build_large_fixture(
        tmp_path
    )

    model = parse_form_xml(
        large_file
    )

    report = render_assessment_markdown(
        model,
        form_name="LARGE_TEST_FORM",
    )

    assert (
        "# Forms2APEX Migration Assessment"
        in report
    )

    assert (
        "LARGE_TEST_FORM"
        in report
    )

    assert (
        "CUSTOMERS_050"
        in report
    )

    assert (
        "## Suggested Migration Plan"
        in report
    )

    assert (
        "## Executive Assessment"
        in report
    )