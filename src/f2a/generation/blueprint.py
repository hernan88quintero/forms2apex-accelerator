from __future__ import annotations
from f2a.model import (
    Block,
    BlockRelation,
    FormModel,
    Item,
    Lov,
    LovValue,
)

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Sequence

from f2a.analysis.planner import (
    MigrationPlanStep,
)
from f2a.reporting.assessment import (
    AssessmentSummary,
)

BLUEPRINT_SCHEMA_VERSION = "1.4"

@dataclass(frozen=True)
class ApexBlueprintStage:
    order: int
    stage: str

    apex_components: tuple[
        str,
        ...
    ]

    source_objects: tuple[
        str,
        ...
    ]

    reason: str

@dataclass(frozen=True)
class ApexBlueprintItem:
    source_block: str
    source_item: str

    component: str

    source_item_type: str | None
    data_type: str | None

    database_item: bool
    column_name: str | None
    required: bool

    lov_name: str | None

@dataclass(frozen=True)
class ApexBlueprintLovValue:
    return_value: str
    display_value: str
    display_order: int


@dataclass(frozen=True)
class ApexBlueprintLov:
    name: str
    lov_type: str
    component: str
    query_text: str | None

    values: tuple[
        ApexBlueprintLovValue,
        ...
    ]

@dataclass(frozen=True)
class ApexBlueprintRelationship:
    name: str
    relation_type: str

    component: str

    master_block: str
    detail_block: str

    master_item: str | None
    detail_item: str | None

    synchronization: str

@dataclass(frozen=True)
class ApexBlueprintRegion:
    name: str
    source_block: str
    component: str

    data_source: str | None
    records_displayed: int | None

    relation_name: str | None
    relation_role: str | None

    items: tuple[
        ApexBlueprintItem,
        ...
    ]


@dataclass(frozen=True)
class ApexBlueprintPage:
    name: str
    page_type: str

    regions: tuple[
        ApexBlueprintRegion,
        ...
    ]


@dataclass(frozen=True)
class ApexMigrationBlueprint:
    schema_version: str

    form_name: str

    overall_complexity: str
    overall_risk: str
    assessment_classification: str

    total_effort: int

    relation_count: int
    master_detail_relation_count: int

    pages: tuple[
        ApexBlueprintPage,
        ...
    ]

    lovs: tuple[
        ApexBlueprintLov,
        ...
    ]

    relationships: tuple[
        ApexBlueprintRelationship,
        ...
    ]

    stages: tuple[
        ApexBlueprintStage,
        ...
    ]


def _to_blueprint_stage(
    step: MigrationPlanStep,
) -> ApexBlueprintStage:

    return ApexBlueprintStage(
        order=step.order,
        stage=step.stage,
        apex_components=step.apex_components,
        source_objects=step.source_objects,
        reason=step.reason,
    )

def _normalize_name(
    value: str,
) -> str:
    return value.strip().upper()


def _find_relation_metadata(
    model: FormModel,
    block_name: str,
) -> tuple[
    str | None,
    str | None,
]:

    normalized_block = _normalize_name(
        block_name
    )

    for relation in model.relations:

        if (
            _normalize_name(
                relation.master_block
            )
            == normalized_block
        ):
            return (
                relation.name,
                "MASTER",
            )

        if (
            _normalize_name(
                relation.detail_block
            )
            == normalized_block
        ):
            return (
                relation.name,
                "DETAIL",
            )

    return (
        None,
        None,
    )


def _get_region_component(
    *,
    database_block: str | None,
    records_displayed: int | None,
    relation_role: str | None,
) -> str:

    if relation_role == "MASTER":
        return (
            "APEX_FORM_OR_MASTER_REGION"
        )

    if relation_role == "DETAIL":
        return "APEX_INTERACTIVE_GRID"

    if (
        records_displayed is not None
        and records_displayed > 1
    ):
        return "APEX_INTERACTIVE_GRID"

    if (
        database_block is not None
        and database_block.strip().upper()
        == "Y"
    ):
        return "APEX_FORM_REGION"

    return (
        "APEX_STATIC_CONTENT_OR_CONTROL_REGION"
    )

def _normalize_item_type(
    value: str | None,
) -> str:

    if value is None:
        return ""

    normalized = (
        value
        .strip()
        .upper()
        .replace("_", " ")
        .replace("-", " ")
    )

    return " ".join(
        normalized.split()
    )


def _flag_is_yes(
    value: str | None,
) -> bool:

    if value is None:
        return False

    return (
        value.strip().upper()
        == "Y"
    )

def _get_item_component(
    item: Item,
) -> str:

    item_type = _normalize_item_type(
        item.item_type
    )

    data_type = _normalize_item_type(
        item.data_type
    )

    if item_type == "PUSH BUTTON":
        return "APEX_BUTTON"

    if item_type == "LIST ITEM":
        return "APEX_SELECT_LIST"

    if item_type == "CHECK BOX":
        return "APEX_SINGLE_CHECKBOX"

    if item_type == "RADIO GROUP":
        return "APEX_RADIO_GROUP"

    if item_type == "DISPLAY ITEM":
        return "APEX_DISPLAY_ONLY"

    if item_type == "TEXT AREA":
        return "APEX_TEXTAREA"

    if item_type == "HIDDEN ITEM":
        return "APEX_HIDDEN"

    if item_type == "TEXT ITEM":

        if data_type in {
            "NUMBER",
            "INTEGER",
            "FLOAT",
        }:
            return "APEX_NUMBER_FIELD"

        if data_type in {
            "DATE",
            "DATETIME",
        }:
            return "APEX_DATE_PICKER"

        return "APEX_TEXT_FIELD"

    return "APEX_PAGE_ITEM_UNRESOLVED"

def _build_items(
    block: Block,
) -> tuple[
    ApexBlueprintItem,
    ...
]:

    return tuple(
        ApexBlueprintItem(
            source_block=block.name,
            source_item=item.name,
            component=(
                _get_item_component(
                    item
                )
            ),
            source_item_type=(
                item.item_type
            ),
            data_type=item.data_type,
            database_item=(
                _flag_is_yes(
                    item.database_item
                )
            ),
            column_name=(
                item.column_name
            ),
            required=(
                _flag_is_yes(
                    item.required
                )
            ),
            lov_name=item.lov_name,
        )
        for item in block.items
    )

def _build_regions(
    model: FormModel,
) -> tuple[
    ApexBlueprintRegion,
    ...
]:

    regions: list[
        ApexBlueprintRegion
    ] = []

    for block in model.blocks:

        (
            relation_name,
            relation_role,
        ) = _find_relation_metadata(
            model,
            block.name,
        )

        component = _get_region_component(
            database_block=block.database_block,
            records_displayed=(
                block.records_displayed
            ),
            relation_role=relation_role,
        )

        regions.append(
            ApexBlueprintRegion(
                name=(
                    f"{block.name}_REGION"
                ),
                source_block=block.name,
                component=component,
                data_source=block.data_source,
                records_displayed=(
                    block.records_displayed
                ),
                relation_name=relation_name,
                relation_role=relation_role,
                items=_build_items(
                    block
                ),
            )
        )

    return tuple(
        regions
    )


def _build_pages(
    model: FormModel,
    *,
    form_name: str,
) -> tuple[
    ApexBlueprintPage,
    ...
]:

    has_master_detail = any(
        (
            relation.relation_type
            .strip()
            .upper()
            == "MASTER_DETAIL"
        )
        for relation in model.relations
    )

    page_type = (
        "APEX_MASTER_DETAIL_PAGE"
        if has_master_detail
        else "APEX_STANDARD_PAGE"
    )

    return (
        ApexBlueprintPage(
            name=form_name,
            page_type=page_type,
            regions=_build_regions(
                model
            ),
        ),
    )

def _get_lov_component(
    lov: Lov,
) -> str:

    lov_type = (
        lov.lov_type
        .strip()
        .upper()
    )

    if lov_type == "STATIC":
        return "APEX_STATIC_LOV"

    if (
        lov.query_text is not None
        and lov.query_text.strip()
    ):
        return "APEX_SQL_QUERY_LOV"

    return "APEX_LOV_UNRESOLVED"


def _to_blueprint_lov_value(
    value: LovValue,
) -> ApexBlueprintLovValue:

    return ApexBlueprintLovValue(
        return_value=value.return_value,
        display_value=value.display_value,
        display_order=value.display_order,
    )


def _to_blueprint_lov(
    lov: Lov,
) -> ApexBlueprintLov:

    return ApexBlueprintLov(
        name=lov.name,
        lov_type=lov.lov_type,
        component=_get_lov_component(
            lov
        ),
        query_text=lov.query_text,
        values=tuple(
            _to_blueprint_lov_value(
                value
            )
            for value in lov.values
        ),
    )

def _get_lov_component(
    lov: Lov,
) -> str:

    lov_type = (
        lov.lov_type
        .strip()
        .upper()
    )

    if lov_type == "STATIC":
        return "APEX_STATIC_LOV"

    if (
        lov.query_text is not None
        and lov.query_text.strip()
    ):
        return "APEX_SQL_QUERY_LOV"

    return "APEX_LOV_UNRESOLVED"


def _to_blueprint_lov_value(
    value: LovValue,
) -> ApexBlueprintLovValue:

    return ApexBlueprintLovValue(
        return_value=value.return_value,
        display_value=value.display_value,
        display_order=value.display_order,
    )


def _to_blueprint_lov(
    lov: Lov,
) -> ApexBlueprintLov:

    return ApexBlueprintLov(
        name=lov.name,
        lov_type=lov.lov_type,
        component=_get_lov_component(
            lov
        ),
        query_text=lov.query_text,
        values=tuple(
            _to_blueprint_lov_value(
                value
            )
            for value in lov.values
        ),
    )


def _build_lovs(
    model: FormModel,
) -> tuple[
    ApexBlueprintLov,
    ...
]:

    return tuple(
        _to_blueprint_lov(
            lov
        )
        for lov in model.lovs
    )

def _get_relationship_component(
    relation: BlockRelation,
) -> str:

    relation_type = (
        relation.relation_type
        .strip()
        .upper()
    )

    if relation_type == "MASTER_DETAIL":
        return "APEX_MASTER_DETAIL"

    return "APEX_RELATION_UNRESOLVED"


def _get_relationship_synchronization(
    relation: BlockRelation,
) -> str:

    relation_type = (
        relation.relation_type
        .strip()
        .upper()
    )

    if relation_type == "MASTER_DETAIL":
        return (
            "DETAIL_REFRESH_ON_MASTER_CHANGE"
        )

    return "MANUAL_REVIEW"


def _to_blueprint_relationship(
    relation: BlockRelation,
) -> ApexBlueprintRelationship:

    return ApexBlueprintRelationship(
        name=relation.name,
        relation_type=relation.relation_type,
        component=(
            _get_relationship_component(
                relation
            )
        ),
        master_block=relation.master_block,
        detail_block=relation.detail_block,
        master_item=relation.master_item,
        detail_item=relation.detail_item,
        synchronization=(
            _get_relationship_synchronization(
                relation
            )
        ),
    )


def _build_relationships(
    model: FormModel,
) -> tuple[
    ApexBlueprintRelationship,
    ...
]:

    return tuple(
        _to_blueprint_relationship(
            relation
        )
        for relation in model.relations
    )

def build_apex_blueprint(
    summary: AssessmentSummary,
    migration_plan: Sequence[
        MigrationPlanStep
    ],
    *,
    model: FormModel | None = None,
) -> ApexMigrationBlueprint:

    stages = tuple(
        _to_blueprint_stage(
            step
        )
        for step in migration_plan
    )

    pages = (
        _build_pages(
            model,
            form_name=summary.form_name,
        )
        if model is not None
        else ()
    )

    lovs = (
        _build_lovs(
            model
        )
        if model is not None
        else ()
    )

    relationships = (
        _build_relationships(
            model
        )
        if model is not None
        else ()
    )

    return ApexMigrationBlueprint(
        schema_version=(
            BLUEPRINT_SCHEMA_VERSION
        ),
        form_name=summary.form_name,
        overall_complexity=(
            summary.overall_complexity
        ),
        overall_risk=(
            summary.overall_risk
        ),
        assessment_classification=(
            summary.assessment_classification
        ),
        total_effort=summary.total_effort,
        relation_count=(
            summary.relation_count
        ),
        master_detail_relation_count=(
            summary.master_detail_relation_count
        ),
        pages=pages,
        lovs=lovs,
        relationships=relationships,
        stages=stages,
    )

def render_apex_blueprint_json(
    blueprint: ApexMigrationBlueprint,
) -> str:

    return json.dumps(
        asdict(
            blueprint
        ),
        indent=2,
        ensure_ascii=False,
    )


def _safe_filename(
    value: str,
) -> str:

    return "".join(
        character
        if (
            character.isalnum()
            or character in {
                "_",
                "-",
            }
        )
        else "_"
        for character in value
    )


def generate_apex_blueprint_file(
    blueprint: ApexMigrationBlueprint,
    *,
    output_dir: Path,
) -> Path:

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_name = _safe_filename(
        blueprint.form_name
    )

    output_path = (
        output_dir
        / f"{safe_name}_blueprint.json"
    )

    output_path.write_text(
        render_apex_blueprint_json(
            blueprint
        ),
        encoding="utf-8",
    )

    return output_path