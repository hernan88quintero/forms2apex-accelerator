from pathlib import Path
import xml.etree.ElementTree as ET

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
    """
    Normalizes XML names so tests are not sensitive
    to case, underscores or hyphens.

    Examples:
        DataType
        data_type
        data-type

    all become:
        datatype
    """

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

def _get_attribute(
    element: ET.Element,
    attribute_name: str,
) -> str | None:

    expected_name = (
        _normalize_xml_name(
            attribute_name
        )
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
            _normalize_xml_name(
                element.tag
            )
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

def test_parser_ignores_unknown_elements(
    tmp_path,
):
    baseline = parse_form_xml(
        FIXTURE
    )

    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    unknown = ET.SubElement(
        root,
        "UnknownOracleFormsMetadata",
    )

    unknown.set(
        "SomeProperty",
        "SomeValue",
    )

    ET.SubElement(
        unknown,
        "NestedUnknownElement",
    ).text = "ignored"

    modified_file = (
        tmp_path
        / "unknown_elements.xml"
    )

    tree.write(
        modified_file,
        encoding="utf-8",
        xml_declaration=True,
    )

    parsed = parse_form_xml(
        modified_file
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


def test_parser_ignores_unknown_attributes(
    tmp_path,
):
    baseline = parse_form_xml(
        FIXTURE
    )

    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    block = _find_first(
        root,
        "Block",
    )

    block.set(
        "FutureOracleProperty",
        "TEST_VALUE",
    )

    item = _find_first(
        root,
        "Item",
    )

    item.set(
        "AnotherUnknownProperty",
        "12345",
    )

    modified_file = (
        tmp_path
        / "unknown_attributes.xml"
    )

    tree.write(
        modified_file,
        encoding="utf-8",
        xml_declaration=True,
    )

    parsed = parse_form_xml(
        modified_file
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


def test_parser_accepts_missing_optional_item_attributes(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    # STATUS contains all three optional attributes
    # we want to validate:
    # DataType, ColumnName and LovName.
    item = _find_item_by_name(
        root,
        "STATUS",
    )

    optional_attributes = (
        "DataType",
        "ColumnName",
        "LovName",
    )

    for attribute in optional_attributes:

        removed = _remove_attribute(
            item,
            attribute,
        )

        assert removed, (
            f"Expected fixture attribute "
            f"not found: {attribute}"
        )

    modified_file = (
        tmp_path
        / "missing_optional_item_attributes.xml"
    )

    tree.write(
        modified_file,
        encoding="utf-8",
        xml_declaration=True,
    )

    parsed = parse_form_xml(
        modified_file
    )

    assert len(
        parsed.blocks
    ) == 2

    assert (
        parsed.item_count
        == 7
    )

    parsed_status = next(
        parsed_item
        for block in parsed.blocks
        for parsed_item in block.items
        if parsed_item.name == "STATUS"
    )

    assert parsed_status.data_type is None
    assert parsed_status.column_name is None
    assert parsed_status.lov_name is None


def test_parser_accepts_unknown_content_with_namespace(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    namespace = (
        "urn:oracle:forms:test"
    )

    ET.register_namespace(
        "",
        namespace,
    )

    for element in root.iter():

        if isinstance(
            element.tag,
            str,
        ):

            element.tag = (
                f"{{{namespace}}}"
                f"{_local_name(element.tag)}"
            )

    extra = ET.SubElement(
        root,
        f"{{{namespace}}}FutureFormsFeature",
    )

    extra.set(
        "Enabled",
        "Y",
    )

    namespaced_file = (
        tmp_path
        / "namespace_with_unknown_content.xml"
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
    ) == 2

    assert (
        parsed.item_count
        == 7
    )

    assert (
        parsed.trigger_count
        == 5
    )

    assert len(
        parsed.program_units
    ) == 2

    assert len(
        parsed.lovs
    ) == 1