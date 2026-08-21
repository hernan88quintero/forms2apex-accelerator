from pathlib import Path
import xml.etree.ElementTree as ET

from f2a.model import (
    Block,
    FormModel,
    Item,
    Lov,
    LovValue,
    ProgramUnit,
    Trigger,
)


def _source_code(element: ET.Element) -> str:
    """
    Extract source-code content from an XML element.

    ElementTree automatically exposes CDATA content as normal text.
    """
    node = element.find("source-code")

    if node is None or node.text is None:
        return ""

    return node.text.strip()


def _records_displayed(value: str | None) -> int | None:
    if value is None:
        return None

    return int(value)


def parse_form_xml(file_path: str | Path) -> FormModel:
    """
    Parse a Forms2APEX synthetic Oracle Forms XML fixture
    into the Python canonical model.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"XML fixture not found: {file_path}"
        )

    tree = ET.parse(file_path)
    root = tree.getroot()

    model = FormModel()

    # ------------------------------------------------------------------
    # BLOCKS
    # ------------------------------------------------------------------
    for block_node in root.findall("./blocks/block"):

        block = Block(
            name=block_node.get("name", ""),
            block_type=block_node.get("type"),
            database_block=block_node.get("database-block"),
            data_source=block_node.get("data-source"),
            records_displayed=_records_displayed(
                block_node.get("records-displayed")
            ),
        )

        # --------------------------------------------------------------
        # ITEMS
        # --------------------------------------------------------------
        for item_node in block_node.findall("./items/item"):

            item = Item(
                name=item_node.get("name", ""),
                item_type=item_node.get("type"),
                data_type=item_node.get("data-type"),
                database_item=item_node.get("database-item"),
                column_name=item_node.get("column-name"),
                required=(item_node.get("required") or "N").upper(),
                lov_name=item_node.get("lov-name"),
            )

            # ----------------------------------------------------------
            # ITEM TRIGGERS
            # ----------------------------------------------------------
            for trigger_node in item_node.findall("./triggers/trigger"):

                item.triggers.append(
                    Trigger(
                        name=trigger_node.get("name", ""),
                        level="ITEM",
                        source_code=_source_code(trigger_node),
                    )
                )

            block.items.append(item)

        # --------------------------------------------------------------
        # BLOCK TRIGGERS
        # --------------------------------------------------------------
        for trigger_node in block_node.findall("./triggers/trigger"):

            block.triggers.append(
                Trigger(
                    name=trigger_node.get("name", ""),
                    level="BLOCK",
                    source_code=_source_code(trigger_node),
                )
            )

        model.blocks.append(block)

    # ------------------------------------------------------------------
    # FORM TRIGGERS
    # ------------------------------------------------------------------
    for trigger_node in root.findall("./form-triggers/trigger"):

        model.form_triggers.append(
            Trigger(
                name=trigger_node.get("name", ""),
                level="FORM",
                source_code=_source_code(trigger_node),
            )
        )

    # ------------------------------------------------------------------
    # PROGRAM UNITS
    # ------------------------------------------------------------------
    for unit_node in root.findall("./program-units/program-unit"):

        model.program_units.append(
            ProgramUnit(
                name=unit_node.get("name", ""),
                unit_type=unit_node.get("type", ""),
                source_code=_source_code(unit_node),
            )
        )

    # ------------------------------------------------------------------
    # LOVs
    # ------------------------------------------------------------------
    for lov_node in root.findall("./lovs/lov"):

        lov = Lov(
            name=lov_node.get("name", "")
        )

        for position, value_node in enumerate(
            lov_node.findall("./values/value"),
            start=1,
        ):

            lov.values.append(
                LovValue(
                    return_value=value_node.get(
                        "return-value",
                        ""
                    ),
                    display_value=value_node.get(
                        "display-value",
                        ""
                    ),
                    display_order=position,
                )
            )

        model.lovs.append(lov)

    # ------------------------------------------------------------------
    # EXPECTED RESULTS
    # ------------------------------------------------------------------
    expected_node = root.find("./expected-results")

    if expected_node is not None:

        for child in expected_node:

            if child.text is not None:

                model.expected_results[
                    child.tag
                ] = int(
                    child.text.strip()
                )

    return model