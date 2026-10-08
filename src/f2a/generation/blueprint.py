from __future__ import annotations
from f2a.model import FormModel

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


BLUEPRINT_SCHEMA_VERSION = "1.1"


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
class ApexBlueprintRegion:
    name: str
    source_block: str
    component: str

    data_source: str | None
    records_displayed: int | None

    relation_name: str | None
    relation_role: str | None


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