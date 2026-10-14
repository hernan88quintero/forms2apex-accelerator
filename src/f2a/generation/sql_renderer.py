from __future__ import annotations

from pathlib import Path

from f2a.generation.blueprint import (
    ApexMigrationBlueprint,
)


SQL_RENDERER_VERSION = "1.0"
SQL_RENDERER_MODE = "SCAFFOLD"


def _safe_name(
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


def _metadata_value(
    value: object | None,
) -> str:

    if value is None:
        return ""

    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def _metadata_line(
    component_type: str,
    **fields: object,
) -> str:

    payload = "|".join(
        (
            f"{name}="
            f"{_metadata_value(value)}"
        )
        for name, value in fields.items()
    )

    if not payload:
        return (
            f"-- F2A|{component_type}"
        )

    return (
        f"-- F2A|{component_type}|"
        f"{payload}"
    )


def render_apex_sql_scaffold(
    blueprint: ApexMigrationBlueprint,
) -> str:

    lines: list[str] = [
        "-- Forms2APEX Accelerator - APEX SQL Scaffold",
        (
            "-- SQL renderer version: "
            f"{SQL_RENDERER_VERSION}"
        ),
        (
            "-- Renderer mode: "
            f"{SQL_RENDERER_MODE}"
        ),
        (
            "-- Source blueprint schema: "
            f"{blueprint.schema_version}"
        ),
        "--",
        (
            "-- This is an intermediate migration scaffold."
        ),
        (
            "-- It does not call version-specific "
            "Oracle APEX import APIs yet."
        ),
        "",
        "set define off",
        (
            "whenever sqlerror "
            "exit failure rollback"
        ),
        "",
        (
            "prompt Forms2APEX SQL scaffold - "
            f"{blueprint.form_name}"
        ),
        "",
        _metadata_line(
            "FORM",
            name=blueprint.form_name,
            blueprint_schema=(
                blueprint.schema_version
            ),
            classification=(
                blueprint.assessment_classification
            ),
            complexity=(
                blueprint.overall_complexity
            ),
            risk=blueprint.overall_risk,
            effort=blueprint.total_effort,
        ),
    ]

    for page in blueprint.pages:

        lines.extend(
            [
                "",
                (
                    f"prompt Page: "
                    f"{page.name}"
                ),
                _metadata_line(
                    "PAGE",
                    name=page.name,
                    page_type=page.page_type,
                ),
            ]
        )

        for region in page.regions:

            lines.append(
                _metadata_line(
                    "REGION",
                    page=page.name,
                    name=region.name,
                    source_block=(
                        region.source_block
                    ),
                    component=(
                        region.component
                    ),
                    data_source=(
                        region.data_source
                    ),
                    relation_name=(
                        region.relation_name
                    ),
                    relation_role=(
                        region.relation_role
                    ),
                )
            )

            for item in region.items:

                lines.append(
                    _metadata_line(
                        "ITEM",
                        region=region.name,
                        source_block=(
                            item.source_block
                        ),
                        source_item=(
                            item.source_item
                        ),
                        component=(
                            item.component
                        ),
                        data_type=(
                            item.data_type
                        ),
                        database_item=(
                            "Y"
                            if item.database_item
                            else "N"
                        ),
                        column_name=(
                            item.column_name
                        ),
                        required=(
                            "Y"
                            if item.required
                            else "N"
                        ),
                        lov_name=item.lov_name,
                    )
                )

    if blueprint.lovs:

        lines.extend(
            [
                "",
                "prompt Shared LOVs",
            ]
        )

        for lov in blueprint.lovs:

            lines.append(
                _metadata_line(
                    "LOV",
                    name=lov.name,
                    lov_type=lov.lov_type,
                    component=lov.component,
                    query_text=(
                        lov.query_text
                    ),
                )
            )

            for value in lov.values:

                lines.append(
                    _metadata_line(
                        "LOV_VALUE",
                        lov_name=lov.name,
                        return_value=(
                            value.return_value
                        ),
                        display_value=(
                            value.display_value
                        ),
                        display_order=(
                            value.display_order
                        ),
                    )
                )

    if blueprint.relationships:

        lines.extend(
            [
                "",
                "prompt Relationships",
            ]
        )

        for relationship in (
            blueprint.relationships
        ):

            lines.append(
                _metadata_line(
                    "RELATIONSHIP",
                    name=(
                        relationship.name
                    ),
                    relation_type=(
                        relationship.relation_type
                    ),
                    component=(
                        relationship.component
                    ),
                    master_block=(
                        relationship.master_block
                    ),
                    detail_block=(
                        relationship.detail_block
                    ),
                    master_item=(
                        relationship.master_item
                    ),
                    detail_item=(
                        relationship.detail_item
                    ),
                    synchronization=(
                        relationship.synchronization
                    ),
                )
            )

    if blueprint.stages:

        lines.extend(
            [
                "",
                "prompt Migration Plan",
            ]
        )

        for stage in blueprint.stages:

            lines.append(
                _metadata_line(
                    "STAGE",
                    order=stage.order,
                    stage=stage.stage,
                    apex_components=(
                        ",".join(
                            stage.apex_components
                        )
                    ),
                    source_objects=(
                        ",".join(
                            stage.source_objects
                        )
                    ),
                    reason=stage.reason,
                )
            )

    lines.extend(
        [
            "",
            (
                "prompt Forms2APEX SQL "
                "scaffold generation complete"
            ),
            "",
        ]
    )

    return "\n".join(
        lines
    )


def generate_apex_sql_scaffold_file(
    blueprint: ApexMigrationBlueprint,
    *,
    root_dir: Path,
) -> Path:

    sql_dir = (
        root_dir
        / "sql"
    )

    sql_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_name = _safe_name(
        blueprint.form_name
    )

    output_path = (
        sql_dir
        / f"{safe_name}_scaffold.sql"
    )

    output_path.write_text(
        render_apex_sql_scaffold(
            blueprint
        ),
        encoding="utf-8",
    )

    return output_path