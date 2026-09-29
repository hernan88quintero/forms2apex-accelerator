from pathlib import Path
import copy
import xml.etree.ElementTree as ET

import pytest

from f2a.parser.xml_parser import parse_form_xml


FIXTURE = Path(
    "samples/golden_002/fixtures/f2a_orders_form.xml"
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

    expected = _normalize_xml_name(
        attribute_name
    )

    for actual_name, value in element.attrib.items():

        if (
            _normalize_xml_name(actual_name)
            == expected
        ):
            return value

    return None


def _set_attribute(
    element: ET.Element,
    attribute_name: str,
    value: str,
) -> None:

    expected = _normalize_xml_name(
        attribute_name
    )

    for actual_name in list(
        element.attrib.keys()
    ):

        if (
            _normalize_xml_name(actual_name)
            == expected
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

    expected = _normalize_xml_name(
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
            == expected
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


def test_parser_rejects_relation_with_unknown_master_block(
    tmp_path,
):
    tree = ET.parse(FIXTURE)
    root = tree.getroot()

    relation = _find_first(
        root,
        "Relation",
    )

    _set_attribute(
        relation,
        "MasterBlock",
        "BLOCK_DOES_NOT_EXIST",
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "unknown_master_block.xml",
    )

    with pytest.raises(
        ValueError,
        match="unknown master Block",
    ):
        parse_form_xml(
            modified_file
        )


def test_parser_rejects_relation_with_unknown_detail_block(
    tmp_path,
):
    tree = ET.parse(FIXTURE)
    root = tree.getroot()

    relation = _find_first(
        root,
        "Relation",
    )

    _set_attribute(
        relation,
        "DetailBlock",
        "BLOCK_DOES_NOT_EXIST",
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "unknown_detail_block.xml",
    )

    with pytest.raises(
        ValueError,
        match="unknown detail Block",
    ):
        parse_form_xml(
            modified_file
        )


def test_parser_rejects_relation_with_unknown_master_item(
    tmp_path,
):
    tree = ET.parse(FIXTURE)
    root = tree.getroot()

    relation = _find_first(
        root,
        "Relation",
    )

    _set_attribute(
        relation,
        "MasterItem",
        "ITEM_DOES_NOT_EXIST",
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "unknown_master_item.xml",
    )

    with pytest.raises(
        ValueError,
        match="unknown master Item",
    ):
        parse_form_xml(
            modified_file
        )


def test_parser_rejects_relation_with_unknown_detail_item(
    tmp_path,
):
    tree = ET.parse(FIXTURE)
    root = tree.getroot()

    relation = _find_first(
        root,
        "Relation",
    )

    _set_attribute(
        relation,
        "DetailItem",
        "ITEM_DOES_NOT_EXIST",
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "unknown_detail_item.xml",
    )

    with pytest.raises(
        ValueError,
        match="unknown detail Item",
    ):
        parse_form_xml(
            modified_file
        )


def test_parser_rejects_duplicate_relation_names(
    tmp_path,
):
    tree = ET.parse(FIXTURE)
    root = tree.getroot()

    relation = _find_first(
        root,
        "Relation",
    )

    parent = _find_parent(
        root,
        relation,
    )

    parent.append(
        copy.deepcopy(
            relation
        )
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "duplicate_relation.xml",
    )

    with pytest.raises(
        ValueError,
        match="duplicate Relation name",
    ):
        parse_form_xml(
            modified_file
        )


def test_parser_accepts_case_insensitive_relation_references(
    tmp_path,
):
    tree = ET.parse(FIXTURE)
    root = tree.getroot()

    relation = _find_first(
        root,
        "Relation",
    )

    _set_attribute(
        relation,
        "MasterBlock",
        "orders",
    )

    _set_attribute(
        relation,
        "DetailBlock",
        "order_lines",
    )

    _set_attribute(
        relation,
        "MasterItem",
        "order_id",
    )

    _set_attribute(
        relation,
        "DetailItem",
        "order_id",
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "case_insensitive_relation.xml",
    )

    model = parse_form_xml(
        modified_file
    )

    assert len(
        model.relations
    ) == 1