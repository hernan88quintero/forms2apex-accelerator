from pathlib import Path
import xml.etree.ElementTree as ET

from f2a.model import (
    Block,
    BlockRelation,
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

def _strip_xml_namespaces(
    root: ET.Element,
) -> None:
    """
    Remove XML namespaces from element tags and attribute names.

    Oracle Forms XML exports may include default or prefixed
    namespaces. The canonical parser works with local tag names,
    so namespace normalization is performed once before parsing.
    """

    for element in root.iter():

        # ------------------------------------------------------
        # Element tag
        # ------------------------------------------------------

        if isinstance(
            element.tag,
            str,
        ):

            if "}" in element.tag:
                element.tag = (
                    element.tag.split(
                        "}",
                        1,
                    )[1]
                )

        # ------------------------------------------------------
        # Attributes
        # ------------------------------------------------------

        if element.attrib:

            normalized_attributes = {}

            for name, value in element.attrib.items():

                local_name = (
                    name.split(
                        "}",
                        1,
                    )[1]
                    if "}" in name
                    else name
                )

                normalized_attributes[
                    local_name
                ] = value

            element.attrib.clear()

            element.attrib.update(
                normalized_attributes
            )

def _normalize_xml_name(
    name: str,
) -> str:
    """
    Normalize XML tag/attribute names so validation
    is insensitive to namespaces, case, underscores,
    and hyphens.
    """

    local_name = (
        name.split(
            "}",
            1,
        )[-1]
    )

    return "".join(
        character
        for character in local_name.lower()
        if character.isalnum()
    )


def _get_xml_attribute(
    element: ET.Element,
    attribute_name: str,
) -> str | None:
    """
    Get an XML attribute using normalized name matching.
    """

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


def _validate_required_names(
    root: ET.Element,
) -> None:
    """
    Validate structural Forms objects that require names.

    Unknown XML elements remain allowed. Only canonical
    Forms objects required by the model are validated.
    """

    required_name_elements = {
        "block": "Block",
        "item": "Item",
        "trigger": "Trigger",
        "programunit": "Program Unit",
        "lov": "LOV",
    }

    for element in root.iter():

        if not isinstance(
            element.tag,
            str,
        ):
            continue

        normalized_tag = (
            _normalize_xml_name(
                element.tag
            )
        )

        entity_label = (
            required_name_elements.get(
                normalized_tag
            )
        )

        if entity_label is None:
            continue

        name = _get_xml_attribute(
            element,
            "Name",
        )

        if (
            name is None
            or not name.strip()
        ):
            raise ValueError(
                "Invalid Oracle Forms XML: "
                f"{entity_label} requires a name."
            )

def _canonical_object_name(
    name: str,
) -> str:
    return name.strip().upper()


def _validate_unique_named_elements(
    root: ET.Element,
    *,
    element_type: str,
    label: str,
) -> None:

    seen_names: set[str] = set()

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
            != element_type
        ):
            continue

        name = _get_xml_attribute(
            element,
            "Name",
        )

        # Required-name validation already handles this.
        if name is None:
            continue

        canonical_name = (
            _canonical_object_name(
                name
            )
        )

        if canonical_name in seen_names:

            raise ValueError(
                "Invalid Oracle Forms XML: "
                f"duplicate {label} name "
                f"'{name.strip()}'."
            )

        seen_names.add(
            canonical_name
        )


def _validate_unique_items_per_block(
    root: ET.Element,
) -> None:

    for block in root.iter():

        if not isinstance(
            block.tag,
            str,
        ):
            continue

        if (
            _normalize_xml_name(
                block.tag
            )
            != "block"
        ):
            continue

        block_name = (
            _get_xml_attribute(
                block,
                "Name",
            )
        )

        seen_items: set[str] = set()

        for element in block.iter():

            if element is block:
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
                != "item"
            ):
                continue

            item_name = (
                _get_xml_attribute(
                    element,
                    "Name",
                )
            )

            if item_name is None:
                continue

            canonical_name = (
                _canonical_object_name(
                    item_name
                )
            )

            if canonical_name in seen_items:

                raise ValueError(
                    "Invalid Oracle Forms XML: "
                    f"duplicate Item name "
                    f"'{item_name.strip()}' "
                    f"in Block "
                    f"'{block_name}'."
                )

            seen_items.add(
                canonical_name
            )


def _validate_duplicate_objects(
    root: ET.Element,
) -> None:

    _validate_unique_named_elements(
        root,
        element_type="block",
        label="Block",
    )

    _validate_unique_named_elements(
        root,
        element_type="programunit",
        label="Program Unit",
    )

    _validate_unique_named_elements(
        root,
        element_type="lov",
        label="LOV",
    )

    _validate_unique_items_per_block(
        root
    )

    _validate_unique_named_elements(
        root,
        element_type="relation",
        label="Relation",
    )

def _validate_unique_triggers_per_owner(
    root: ET.Element,
) -> None:

    for owner in root.iter():

        seen_triggers: set[str] = set()

        for child in list(owner):

            if not isinstance(
                child.tag,
                str,
            ):
                continue

            if (
                _normalize_xml_name(
                    child.tag
                )
                != "trigger"
            ):
                continue

            trigger_name = (
                _get_xml_attribute(
                    child,
                    "Name",
                )
            )

            # Required-name validation already
            # handles missing names.
            if trigger_name is None:
                continue

            canonical_name = (
                _canonical_object_name(
                    trigger_name
                )
            )

            if canonical_name in seen_triggers:

                owner_name = (
                    _get_xml_attribute(
                        owner,
                        "Name",
                    )
                )

                owner_label = (
                    owner_name.strip()
                    if owner_name
                    else _normalize_xml_name(
                        owner.tag
                    )
                )

                raise ValueError(
                    "Invalid Oracle Forms XML: "
                    f"duplicate Trigger name "
                    f"'{trigger_name.strip()}' "
                    f"in '{owner_label}'."
                )

            seen_triggers.add(
                canonical_name
            )


def _validate_lov_references(
    root: ET.Element,
) -> None:

    lov_names: set[str] = set()

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
            != "lov"
        ):
            continue

        lov_name = _get_xml_attribute(
            element,
            "Name",
        )

        if lov_name:
            lov_names.add(
                _canonical_object_name(
                    lov_name
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
            != "item"
        ):
            continue

        lov_reference = (
            _get_xml_attribute(
                element,
                "LovName",
            )
        )

        if (
            lov_reference is None
            or not lov_reference.strip()
        ):
            continue

        canonical_reference = (
            _canonical_object_name(
                lov_reference
            )
        )

        if canonical_reference not in lov_names:

            item_name = (
                _get_xml_attribute(
                    element,
                    "Name",
                )
            )

            raise ValueError(
                "Invalid Oracle Forms XML: "
                f"Item '{item_name}' references "
                f"unknown LOV "
                f"'{lov_reference.strip()}'."
            )


def _validate_semantic_integrity(
    root: ET.Element,
) -> None:

    _validate_unique_triggers_per_owner(
        root
    )

    _validate_lov_references(
        root
    )

def _validate_relation_integrity(
    root: ET.Element,
) -> None:

    blocks: dict[
        str,
        ET.Element,
    ] = {}

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
            != "block"
        ):
            continue

        block_name = _get_xml_attribute(
            element,
            "Name",
        )

        if block_name:
            blocks[
                _canonical_object_name(
                    block_name
                )
            ] = element

    for relation in root.iter():

        if not isinstance(
            relation.tag,
            str,
        ):
            continue

        if (
            _normalize_xml_name(
                relation.tag
            )
            != "relation"
        ):
            continue

        relation_name = (
            _get_xml_attribute(
                relation,
                "Name",
            )
            or "<unnamed>"
        )

        master_block_name = (
            _get_xml_attribute(
                relation,
                "MasterBlock",
            )
        )

        detail_block_name = (
            _get_xml_attribute(
                relation,
                "DetailBlock",
            )
        )

        master_item_name = (
            _get_xml_attribute(
                relation,
                "MasterItem",
            )
        )

        detail_item_name = (
            _get_xml_attribute(
                relation,
                "DetailItem",
            )
        )

        if (
            master_block_name is None
            or detail_block_name is None
        ):
            # _parse_relations gives the detailed
            # required-field error.
            continue

        master_key = (
            _canonical_object_name(
                master_block_name
            )
        )

        detail_key = (
            _canonical_object_name(
                detail_block_name
            )
        )

        if master_key not in blocks:

            raise ValueError(
                "Invalid Oracle Forms XML: "
                f"Relation '{relation_name}' "
                f"references unknown master Block "
                f"'{master_block_name}'."
            )

        if detail_key not in blocks:

            raise ValueError(
                "Invalid Oracle Forms XML: "
                f"Relation '{relation_name}' "
                f"references unknown detail Block "
                f"'{detail_block_name}'."
            )

        master_block = blocks[
            master_key
        ]

        detail_block = blocks[
            detail_key
        ]

        def block_item_names(
            block: ET.Element,
        ) -> set[str]:

            names: set[str] = set()

            for element in block.iter():

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

                item_name = (
                    _get_xml_attribute(
                        element,
                        "Name",
                    )
                )

                if item_name:

                    names.add(
                        _canonical_object_name(
                            item_name
                        )
                    )

            return names

        if master_item_name:

            if (
                _canonical_object_name(
                    master_item_name
                )
                not in block_item_names(
                    master_block
                )
            ):

                raise ValueError(
                    "Invalid Oracle Forms XML: "
                    f"Relation '{relation_name}' "
                    f"references unknown master Item "
                    f"'{master_item_name}'."
                )

        if detail_item_name:

            if (
                _canonical_object_name(
                    detail_item_name
                )
                not in block_item_names(
                    detail_block
                )
            ):

                raise ValueError(
                    "Invalid Oracle Forms XML: "
                    f"Relation '{relation_name}' "
                    f"references unknown detail Item "
                    f"'{detail_item_name}'."
                )

def _parse_relations(
    root: ET.Element,
) -> list[BlockRelation]:

    relations: list[
        BlockRelation
    ] = []

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
            != "relation"
        ):
            continue

        name = _get_xml_attribute(
            element,
            "Name",
        )

        master_block = _get_xml_attribute(
            element,
            "MasterBlock",
        )

        detail_block = _get_xml_attribute(
            element,
            "DetailBlock",
        )

        master_item = _get_xml_attribute(
            element,
            "MasterItem",
        )

        detail_item = _get_xml_attribute(
            element,
            "DetailItem",
        )

        if (
            name is None
            or not name.strip()
        ):
            raise ValueError(
                "Invalid Oracle Forms XML: "
                "Relation requires a name."
            )

        if (
            master_block is None
            or not master_block.strip()
        ):
            raise ValueError(
                "Invalid Oracle Forms XML: "
                f"Relation '{name}' requires "
                "a master block."
            )

        if (
            detail_block is None
            or not detail_block.strip()
        ):
            raise ValueError(
                "Invalid Oracle Forms XML: "
                f"Relation '{name}' requires "
                "a detail block."
            )

        relations.append(
            BlockRelation(
                name=name.strip(),
                master_block=(
                    master_block.strip()
                ),
                detail_block=(
                    detail_block.strip()
                ),
                master_item=(
                    master_item.strip()
                    if master_item
                    else None
                ),
                detail_item=(
                    detail_item.strip()
                    if detail_item
                    else None
                ),
            )
        )

    return relations

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

    _strip_xml_namespaces(
    root
        )
    
    _validate_required_names(
    root
        )
    
    _validate_duplicate_objects(
    root
        )
    
    _validate_semantic_integrity(
    root
    )

    _validate_relation_integrity(
    root
    )

    relations = _parse_relations(
    root
    )

    model = FormModel(relations=relations,)

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