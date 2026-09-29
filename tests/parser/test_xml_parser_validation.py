from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from f2a.parser.xml_parser import parse_form_xml


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)


def _local_name(
    tag: str,
) -> str:
    return tag.split(
        "}",
        1,
    )[-1]


def _normalize_xml_name(
    name: str,
) -> str:
    local_name = _local_name(
        name
    )

    return "".join(
        character
        for character in local_name.lower()
        if character.isalnum()
    )


def _find_first(
    root: ET.Element,
    tag_name: str,
) -> ET.Element:

    expected_name = (
        _normalize_xml_name(
            tag_name
        )
    )

    for element in root.iter():

        if not isinstance(
            element.tag,
            str,
        ):
            continue

        if (
            _normalize_xml_name(
                element.tag
            )
            == expected_name
        ):
            return element

    raise AssertionError(
        f"Element not found: {tag_name}"
    )


def _remove_attribute(
    element: ET.Element,
    attribute_name: str,
) -> bool:

    expected_name = (
        _normalize_xml_name(
            attribute_name
        )
    )

    for actual_name in list(
        element.attrib.keys()
    ):

        if (
            _normalize_xml_name(
                actual_name
            )
            == expected_name
        ):

            del element.attrib[
                actual_name
            ]

            return True

    return False


def _write_modified_xml(
    tree: ET.ElementTree,
    tmp_path,
    filename: str,
) -> Path:

    output_path = (
        tmp_path
        / filename
    )

    tree.write(
        output_path,
        encoding="utf-8",
        xml_declaration=True,
    )

    return output_path


def test_parser_rejects_block_without_name(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    block = _find_first(
        root,
        "Block",
    )

    assert _remove_attribute(
        block,
        "Name",
    )

    modified_file = _write_modified_xml(
        tree,
        tmp_path,
        "block_without_name.xml",
    )

    with pytest.raises(
        ValueError,
        match="Block.*name",
    ):
        parse_form_xml(
            modified_file
        )


def test_parser_rejects_item_without_name(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    item = _find_first(
        root,
        "Item",
    )

    assert _remove_attribute(
        item,
        "Name",
    )

    modified_file = _write_modified_xml(
        tree,
        tmp_path,
        "item_without_name.xml",
    )

    with pytest.raises(
        ValueError,
        match="Item.*name",
    ):
        parse_form_xml(
            modified_file
        )


def test_parser_rejects_trigger_without_name(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    trigger = _find_first(
        root,
        "Trigger",
    )

    assert _remove_attribute(
        trigger,
        "Name",
    )

    modified_file = _write_modified_xml(
        tree,
        tmp_path,
        "trigger_without_name.xml",
    )

    with pytest.raises(
        ValueError,
        match="Trigger.*name",
    ):
        parse_form_xml(
            modified_file
        )


def test_parser_rejects_program_unit_without_name(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    program_unit = _find_first(
        root,
        "ProgramUnit",
    )

    assert _remove_attribute(
        program_unit,
        "Name",
    )

    modified_file = _write_modified_xml(
        tree,
        tmp_path,
        "program_unit_without_name.xml",
    )

    with pytest.raises(
        ValueError,
        match="Program Unit.*name",
    ):
        parse_form_xml(
            modified_file
        )


def test_parser_rejects_lov_without_name(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    lov = _find_first(
        root,
        "LOV",
    )

    assert _remove_attribute(
        lov,
        "Name",
    )

    modified_file = _write_modified_xml(
        tree,
        tmp_path,
        "lov_without_name.xml",
    )

    with pytest.raises(
        ValueError,
        match="LOV.*name",
    ):
        parse_form_xml(
            modified_file
        )