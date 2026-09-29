from pathlib import Path
import copy
import xml.etree.ElementTree as ET

import pytest

from f2a.parser.xml_parser import parse_form_xml


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)


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

    for actual_name, value in (
        element.attrib.items()
    ):

        if (
            _normalize_xml_name(
                actual_name
            )
            == expected_name
        ):
            return value

    return None


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
            _normalize_xml_name(
                element.tag
            )
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

        for candidate in list(
            parent
        ):

            if candidate is child:
                return parent

    raise AssertionError(
        "Parent element not found."
    )


def _write_xml(
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


def test_parser_rejects_duplicate_blocks(
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

    parent = _find_parent(
        root,
        block,
    )

    parent.append(
        copy.deepcopy(
            block
        )
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "duplicate_block.xml",
    )

    with pytest.raises(
        ValueError,
        match="duplicate Block name",
    ):
        parse_form_xml(
            modified_file
        )


def test_parser_rejects_duplicate_items_in_same_block(
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

    parent = _find_parent(
        root,
        item,
    )

    parent.append(
        copy.deepcopy(
            item
        )
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "duplicate_item.xml",
    )

    with pytest.raises(
        ValueError,
        match="duplicate Item name",
    ):
        parse_form_xml(
            modified_file
        )


def test_parser_rejects_duplicate_program_units(
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

    parent = _find_parent(
        root,
        program_unit,
    )

    parent.append(
        copy.deepcopy(
            program_unit
        )
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "duplicate_program_unit.xml",
    )

    with pytest.raises(
        ValueError,
        match="duplicate Program Unit name",
    ):
        parse_form_xml(
            modified_file
        )


def test_parser_rejects_duplicate_lovs(
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

    parent = _find_parent(
        root,
        lov,
    )

    parent.append(
        copy.deepcopy(
            lov
        )
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "duplicate_lov.xml",
    )

    with pytest.raises(
        ValueError,
        match="duplicate LOV name",
    ):
        parse_form_xml(
            modified_file
        )