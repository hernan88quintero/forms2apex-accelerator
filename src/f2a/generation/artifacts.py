from __future__ import annotations

from dataclasses import (
    asdict,
    dataclass,
)
import json
from pathlib import Path

from f2a.generation.blueprint import (
    ApexMigrationBlueprint,
)


ARTIFACT_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class GeneratedArtifactBundle:
    root_dir: Path
    manifest_path: Path

    page_paths: tuple[
        Path,
        ...
    ]

    migration_plan_path: Path

    lovs_path: Path | None
    relationships_path: Path | None


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


def _write_json(
    path: Path,
    payload: object,
) -> Path:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return path


def _generate_page_artifacts(
    blueprint: ApexMigrationBlueprint,
    *,
    root_dir: Path,
) -> tuple[
    Path,
    ...
]:

    page_paths: list[Path] = []

    pages_dir = (
        root_dir
        / "pages"
    )

    for page in blueprint.pages:

        safe_page_name = _safe_name(
            page.name
        )

        page_path = (
            pages_dir
            / f"{safe_page_name}.json"
        )

        _write_json(
            page_path,
            asdict(
                page
            ),
        )

        page_paths.append(
            page_path
        )

    return tuple(
        page_paths
    )


def _generate_lov_artifact(
    blueprint: ApexMigrationBlueprint,
    *,
    root_dir: Path,
) -> Path | None:

    if not blueprint.lovs:
        return None

    return _write_json(
        (
            root_dir
            / "shared_components"
            / "lovs.json"
        ),
        {
            "lovs": [
                asdict(
                    lov
                )
                for lov in blueprint.lovs
            ]
        },
    )


def _generate_relationship_artifact(
    blueprint: ApexMigrationBlueprint,
    *,
    root_dir: Path,
) -> Path | None:

    if not blueprint.relationships:
        return None

    return _write_json(
        root_dir
        / "relationships.json",
        {
            "relationships": [
                asdict(
                    relationship
                )
                for relationship
                in blueprint.relationships
            ]
        },
    )


def _generate_migration_plan_artifact(
    blueprint: ApexMigrationBlueprint,
    *,
    root_dir: Path,
) -> Path:

    return _write_json(
        root_dir
        / "migration_plan.json",
        {
            "stages": [
                asdict(
                    stage
                )
                for stage in blueprint.stages
            ]
        },
    )


def generate_apex_artifact_bundle(
    blueprint: ApexMigrationBlueprint,
    *,
    output_dir: Path,
) -> GeneratedArtifactBundle:

    safe_form_name = _safe_name(
        blueprint.form_name
    )

    root_dir = (
        output_dir
        / f"{safe_form_name}_apex"
    )

    root_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    page_paths = (
        _generate_page_artifacts(
            blueprint,
            root_dir=root_dir,
        )
    )

    lovs_path = (
        _generate_lov_artifact(
            blueprint,
            root_dir=root_dir,
        )
    )

    relationships_path = (
        _generate_relationship_artifact(
            blueprint,
            root_dir=root_dir,
        )
    )

    migration_plan_path = (
        _generate_migration_plan_artifact(
            blueprint,
            root_dir=root_dir,
        )
    )

    generated_files = [
        str(
            path.relative_to(
                root_dir
            )
        ).replace(
            "\\",
            "/",
        )
        for path in (
            *page_paths,
            migration_plan_path,
        )
    ]

    if lovs_path is not None:
        generated_files.append(
            str(
                lovs_path.relative_to(
                    root_dir
                )
            ).replace(
                "\\",
                "/",
            )
        )

    if relationships_path is not None:
        generated_files.append(
            str(
                relationships_path.relative_to(
                    root_dir
                )
            ).replace(
                "\\",
                "/",
            )
        )

    generated_files.sort()

    manifest = {
        "artifact_schema_version": (
            ARTIFACT_SCHEMA_VERSION
        ),
        "source_blueprint_schema_version": (
            blueprint.schema_version
        ),
        "form_name": (
            blueprint.form_name
        ),
        "page_count": len(
            blueprint.pages
        ),
        "lov_count": len(
            blueprint.lovs
        ),
        "relationship_count": len(
            blueprint.relationships
        ),
        "classification": (
            blueprint.assessment_classification
        ),
        "overall_complexity": (
            blueprint.overall_complexity
        ),
        "overall_risk": (
            blueprint.overall_risk
        ),
        "total_effort": (
            blueprint.total_effort
        ),
        "generated_files": (
            generated_files
        ),
    }

    manifest_path = _write_json(
        root_dir
        / "manifest.json",
        manifest,
    )

    return GeneratedArtifactBundle(
        root_dir=root_dir,
        manifest_path=manifest_path,
        page_paths=page_paths,
        migration_plan_path=(
            migration_plan_path
        ),
        lovs_path=lovs_path,
        relationships_path=(
            relationships_path
        ),
    )