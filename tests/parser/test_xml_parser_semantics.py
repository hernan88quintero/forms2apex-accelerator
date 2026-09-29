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


def _find_item_by_name(
    root: ET.Element,
    item_name: str,
) -> ET.Element:

    for element in root.iter():

        if not isinstance(
            element.tag,
            str,
        ):
            continue

        if (
            _normalize_xml_name(element.tag)
            != "item"
        ):
            continue

        name = _get_attribute(
            element,
            "Name",
        )

        if (
            name is not None
            and name.upper()
            == item_name.upper()
        ):
            return element

    raise AssertionError(
        f"Item not found: {item_name}"
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


def test_parser_rejects_duplicate_trigger_in_same_object(
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

    parent = _find_parent(
        root,
        trigger,
    )

    parent.append(
        copy.deepcopy(
            trigger
        )
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "duplicate_trigger.xml",
    )

    with pytest.raises(
        ValueError,
        match="duplicate Trigger name",
    ):
        parse_form_xml(
            modified_file
        )


def test_parser_allows_same_trigger_name_on_different_objects(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    # Source trigger:
    # CUSTOMERS.EMAIL.WHEN-VALIDATE-ITEM
    source_trigger = _find_first(
        root,
        "Trigger",
    )

    # BTN_SAVE already has its own trigger structure,
    # so we reuse its existing trigger container.
    target_item = _find_item_by_name(
        root,
        "BTN_SAVE",
    )

    target_trigger = _find_descendant(
        target_item,
        "Trigger",
    )

    target_trigger_parent = _find_parent(
        root,
        target_trigger,
    )

    target_trigger_parent.append(
        copy.deepcopy(
            source_trigger
        )
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "same_trigger_different_owner.xml",
    )

    parsed = parse_form_xml(
        modified_file
    )

    assert (
        parsed.trigger_count
        == 6
    )


def test_parser_accepts_case_insensitive_lov_reference(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    status_item = _find_item_by_name(
        root,
        "STATUS",
    )

    _set_attribute(
        status_item,
        "LovName",
        "lov_status",
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "case_insensitive_lov.xml",
    )

    parsed = parse_form_xml(
        modified_file
    )

    status = next(
        item
        for block in parsed.blocks
        for item in block.items
        if item.name == "STATUS"
    )

    assert (
        status.lov_name.upper()
        == "LOV_STATUS"
    )

def _find_descendant(
    root: ET.Element,
    tag_name: str,
) -> ET.Element:

    expected_name = _normalize_xml_name(
        tag_name
    )

    for element in root.iter():

        if element is root:
            continue

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
        f"Descendant not found: {tag_name}"
    )

def test_parser_rejects_missing_lov_reference(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    status_item = _find_item_by_name(
        root,
        "STATUS",
    )

    _set_attribute(
        status_item,
        "LovName",
        "LOV_DOES_NOT_EXIST",
    )

    modified_file = _write_xml(
        tree,
        tmp_path,
        "missing_lov_reference.xml",
    )

    with pytest.raises(
        ValueError,
        match="references unknown LOV",
    ):
        parse_form_xml(
            modified_file
        )