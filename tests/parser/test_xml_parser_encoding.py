from pathlib import Path
import xml.etree.ElementTree as ET

from f2a.parser.xml_parser import parse_form_xml


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)


def _replace_exact_payload(
    root: ET.Element,
    old_value: str,
    new_value: str,
) -> bool:
    """
    Replace the first XML attribute or text payload
    whose value exactly matches old_value.
    """

    for element in root.iter():

        if (
            element.text is not None
            and element.text.strip() == old_value
        ):
            element.text = new_value
            return True

        for attribute_name, value in list(
            element.attrib.items()
        ):

            if value == old_value:

                element.attrib[
                    attribute_name
                ] = new_value

                return True

    return False


def _append_to_payload_containing(
    root: ET.Element,
    marker: str,
    suffix: str,
) -> bool:
    """
    Append text to the first XML payload containing
    the requested marker.

    Works whether Forms source code is represented
    as element text or as an XML attribute.
    """

    for element in root.iter():

        if (
            element.text is not None
            and marker in element.text
        ):
            element.text += suffix
            return True

        for attribute_name, value in list(
            element.attrib.items()
        ):

            if marker in value:

                element.attrib[
                    attribute_name
                ] = (
                    value
                    + suffix
                )

                return True

    return False


def _find_lov_display_value(
    model,
    expected_value: str,
):
    return next(
        value
        for lov in model.lovs
        for value in lov.values
        if value.display_value
        == expected_value
    )


def test_parser_preserves_utf8_text(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    display_value = (
        "Acción válida para José y el niño"
    )

    assert _replace_exact_payload(
        root,
        "Active",
        display_value,
    )

    modified_file = (
        tmp_path
        / "utf8_form.xml"
    )

    tree.write(
        modified_file,
        encoding="utf-8",
        xml_declaration=True,
    )

    parsed = parse_form_xml(
        modified_file
    )

    value = _find_lov_display_value(
        parsed,
        display_value,
    )

    assert (
        value.display_value
        == display_value
    )


def test_parser_preserves_multiline_plsql_unicode(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    unicode_comment = (
        "\n"
        "-- Validación de correo electrónico\n"
        "-- Acción inválida para José, Peña y Muñoz\n"
    )

    assert _append_to_payload_containing(
        root,
        "FORM_TRIGGER_FAILURE",
        unicode_comment,
    )

    modified_file = (
        tmp_path
        / "unicode_plsql.xml"
    )

    tree.write(
        modified_file,
        encoding="utf-8",
        xml_declaration=True,
    )

    parsed = parse_form_xml(
        modified_file
    )

    validate_email = next(
        unit
        for unit in parsed.program_units
        if unit.name
        == "VALIDATE_EMAIL"
    )

    assert (
        "Validación de correo electrónico"
        in validate_email.source_code
    )

    assert (
        "Acción inválida para José, Peña y Muñoz"
        in validate_email.source_code
    )


def test_parser_supports_iso_8859_1_xml(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    display_value = (
        "Información válida: "
        "año, niño, acción"
    )

    assert _replace_exact_payload(
        root,
        "Active",
        display_value,
    )

    modified_file = (
        tmp_path
        / "latin1_form.xml"
    )

    tree.write(
        modified_file,
        encoding="iso-8859-1",
        xml_declaration=True,
    )

    parsed = parse_form_xml(
        modified_file
    )

    value = _find_lov_display_value(
        parsed,
        display_value,
    )

    assert (
        value.display_value
        == display_value
    )


def test_parser_decodes_xml_reserved_characters(
    tmp_path,
):
    tree = ET.parse(
        FIXTURE
    )

    root = tree.getroot()

    display_value = (
        "Acción & revisión <manual> > automática"
    )

    assert _replace_exact_payload(
        root,
        "Active",
        display_value,
    )

    modified_file = (
        tmp_path
        / "xml_entities_form.xml"
    )

    tree.write(
        modified_file,
        encoding="utf-8",
        xml_declaration=True,
    )

    parsed = parse_form_xml(
        modified_file
    )

    value = _find_lov_display_value(
        parsed,
        display_value,
    )

    assert (
        value.display_value
        == display_value
    )