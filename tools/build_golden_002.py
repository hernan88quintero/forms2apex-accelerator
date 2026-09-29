from __future__ import annotations

import copy
import xml.etree.ElementTree as ET
from pathlib import Path


SOURCE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)

TARGET = Path(
    "samples/golden_002/fixtures/f2a_orders_form.xml"
)


def normalize_name(
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


def get_attribute(
    element: ET.Element,
    name: str,
) -> str | None:

    expected = normalize_name(
        name
    )

    for actual_name, value in element.attrib.items():

        if (
            normalize_name(actual_name)
            == expected
        ):
            return value

    return None


def set_attribute(
    element: ET.Element,
    name: str,
    value: str,
) -> None:

    expected = normalize_name(
        name
    )

    for actual_name in list(
        element.attrib.keys()
    ):

        if (
            normalize_name(actual_name)
            == expected
        ):
            element.attrib[
                actual_name
            ] = value

            return

    element.set(
        name,
        value,
    )


def find_all(
    root: ET.Element,
    tag_name: str,
) -> list[ET.Element]:

    expected = normalize_name(
        tag_name
    )

    return [
        element
        for element in root.iter()
        if (
            isinstance(
                element.tag,
                str,
            )
            and normalize_name(
                element.tag
            )
            == expected
        )
    ]


def find_by_name(
    root: ET.Element,
    tag_name: str,
    object_name: str,
) -> ET.Element:

    for element in find_all(
        root,
        tag_name,
    ):

        name = get_attribute(
            element,
            "Name",
        )

        if (
            name is not None
            and name.upper()
            == object_name.upper()
        ):
            return element

    raise RuntimeError(
        f"{tag_name} not found: {object_name}"
    )


def find_parent(
    root: ET.Element,
    child: ET.Element,
) -> ET.Element:

    for parent in root.iter():

        for candidate in list(
            parent
        ):

            if candidate is child:
                return parent

    raise RuntimeError(
        "Parent not found."
    )


def rename_item(
    block: ET.Element,
    old_name: str,
    new_name: str,
    *,
    column_name: str | None = None,
    data_type: str | None = None,
    lov_name: str | None = None,
) -> None:

    item = find_by_name(
        block,
        "Item",
        old_name,
    )

    set_attribute(
        item,
        "Name",
        new_name,
    )

    if column_name is not None:
        set_attribute(
            item,
            "ColumnName",
            column_name,
        )

    if data_type is not None:
        set_attribute(
            item,
            "DataType",
            data_type,
        )

    if lov_name is not None:
        set_attribute(
            item,
            "LovName",
            lov_name,
        )


def main() -> None:

    tree = ET.parse(
        SOURCE
    )

    root = tree.getroot()

    # ----------------------------------------------------------
    # MASTER BLOCK: CUSTOMERS -> ORDERS
    # ----------------------------------------------------------

    customers = find_by_name(
        root,
        "Block",
        "CUSTOMERS",
    )

    set_attribute(
        customers,
        "Name",
        "ORDERS",
    )

    set_attribute(
        customers,
        "DataSource",
        "ORDERS",
    )

    rename_item(
        customers,
        "CUSTOMER_ID",
        "ORDER_ID",
        column_name="ORDER_ID",
        data_type="NUMBER",
    )

    rename_item(
        customers,
        "FIRST_NAME",
        "CUSTOMER_ID",
        column_name="CUSTOMER_ID",
        data_type="NUMBER",
    )

    rename_item(
        customers,
        "LAST_NAME",
        "ORDER_DATE",
        column_name="ORDER_DATE",
        data_type="DATE",
    )

    rename_item(
        customers,
        "EMAIL",
        "CUSTOMER_EMAIL",
        column_name="CUSTOMER_EMAIL",
        data_type="VARCHAR2",
    )

    rename_item(
        customers,
        "STATUS",
        "STATUS",
        column_name="STATUS",
        data_type="VARCHAR2",
        lov_name="LOV_ORDER_STATUS",
    )

    # ----------------------------------------------------------
    # DETAIL BLOCK
    # Clone master structure and give it a different identity.
    # ----------------------------------------------------------

    order_lines = copy.deepcopy(
        customers
    )

    set_attribute(
        order_lines,
        "Name",
        "ORDER_LINES",
    )

    set_attribute(
        order_lines,
        "DataSource",
        "ORDER_LINES",
    )

    rename_item(
        order_lines,
        "ORDER_ID",
        "LINE_ID",
        column_name="LINE_ID",
        data_type="NUMBER",
    )

    rename_item(
        order_lines,
        "CUSTOMER_ID",
        "ORDER_ID",
        column_name="ORDER_ID",
        data_type="NUMBER",
    )

    rename_item(
        order_lines,
        "ORDER_DATE",
        "PRODUCT_ID",
        column_name="PRODUCT_ID",
        data_type="NUMBER",
    )

    rename_item(
        order_lines,
        "CUSTOMER_EMAIL",
        "QUANTITY",
        column_name="QUANTITY",
        data_type="NUMBER",
    )

    rename_item(
        order_lines,
        "STATUS",
        "LINE_STATUS",
        column_name="LINE_STATUS",
        data_type="VARCHAR2",
        lov_name="LOV_LINE_STATUS",
    )

    blocks_parent = find_parent(
        root,
        customers,
    )

    blocks_parent.append(
        order_lines
    )

    # ----------------------------------------------------------
    # CONTROL
    # ----------------------------------------------------------

    control = find_by_name(
        root,
        "Block",
        "CONTROL",
    )

    rename_item(
        control,
        "BTN_SAVE",
        "BTN_SAVE_ORDER",
    )

    rename_item(
        control,
        "BTN_CANCEL",
        "BTN_QUERY_ORDERS",
    )

    # ----------------------------------------------------------
    # PROGRAM UNITS
    # ----------------------------------------------------------

    validate_email = find_by_name(
        root,
        "ProgramUnit",
        "VALIDATE_EMAIL",
    )

    set_attribute(
        validate_email,
        "Name",
        "VALIDATE_ORDER",
    )

    save_customer = find_by_name(
        root,
        "ProgramUnit",
        "SAVE_CUSTOMER",
    )

    set_attribute(
        save_customer,
        "Name",
        "SAVE_ORDER",
    )

    # Preserve whatever XML field actually contains source code.
    for element in (
        validate_email,
        save_customer,
    ):

        for attribute_name, value in list(
            element.attrib.items()
        ):

            if (
                "customer"
                in value.lower()
            ):
                element.attrib[
                    attribute_name
                ] = (
                    value
                    .replace(
                        "CUSTOMER",
                        "ORDER",
                    )
                    .replace(
                        "customer",
                        "order",
                    )
                )

        if (
            element.text
            and "customer"
            in element.text.lower()
        ):
            element.text = (
                element.text
                .replace(
                    "CUSTOMER",
                    "ORDER",
                )
                .replace(
                    "customer",
                    "order",
                )
            )

    # ----------------------------------------------------------
    # LOVs
    # Existing LOV becomes order status.
    # Clone it for line status.
    # ----------------------------------------------------------

    lov_status = find_by_name(
        root,
        "LOV",
        "LOV_STATUS",
    )

    set_attribute(
        lov_status,
        "Name",
        "LOV_ORDER_STATUS",
    )

    line_status_lov = copy.deepcopy(
        lov_status
    )

    set_attribute(
        line_status_lov,
        "Name",
        "LOV_LINE_STATUS",
    )

    lov_parent = find_parent(
        root,
        lov_status,
    )

    lov_parent.append(
        line_status_lov
    )

    # ----------------------------------------------------------
    # Write Golden #002
    # ----------------------------------------------------------

    TARGET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ----------------------------------------------------------
    # MASTER / DETAIL RELATION
    # ----------------------------------------------------------

    relation = ET.SubElement(
        root,
        "Relation",
    )

    relation.set(
        "Name",
        "ORDERS_ORDER_LINES",
    )

    relation.set(
        "MasterBlock",
        "ORDERS",
    )

    relation.set(
        "DetailBlock",
        "ORDER_LINES",
    )

    relation.set(
        "MasterItem",
        "ORDER_ID",
    )

    relation.set(
        "DetailItem",
        "ORDER_ID",
    )

    tree.write(
        TARGET,
        encoding="utf-8",
        xml_declaration=True,
    )

    print(
        f"Golden Sample #002 generated: {TARGET}"
    )


if __name__ == "__main__":
    main()