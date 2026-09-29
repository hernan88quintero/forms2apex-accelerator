from __future__ import annotations

from dataclasses import dataclass

from f2a.model import (
    BlockRelation,
    FormModel,
)


@dataclass(frozen=True)
class RelationMigrationAdvice:
    relation_name: str

    relation_type: str

    master_block: str
    detail_block: str

    master_item: str | None
    detail_item: str | None

    apex_pattern: str

    master_component: str
    detail_component: str

    synchronization: str

    automation_level: str
    complexity: str
    risk: str

    rationale: str


def _master_detail_advice(
    relation: BlockRelation,
) -> RelationMigrationAdvice:

    return RelationMigrationAdvice(
        relation_name=relation.name,
        relation_type=relation.relation_type,

        master_block=relation.master_block,
        detail_block=relation.detail_block,

        master_item=relation.master_item,
        detail_item=relation.detail_item,

        apex_pattern="APEX_MASTER_DETAIL",

        master_component=(
            "APEX_FORM_OR_MASTER_REGION"
        ),

        detail_component=(
            "APEX_INTERACTIVE_GRID"
        ),

        synchronization=(
            "DETAIL_REFRESH_ON_MASTER_CHANGE"
        ),

        automation_level="ASSISTED",
        complexity="MEDIUM",
        risk="MEDIUM",

        rationale=(
            "Translate the Oracle Forms "
            "master/detail block relationship "
            "into an APEX master region with a "
            "dependent detail region. Preserve "
            "the relationship key and refresh "
            "the detail component when the "
            "master record changes."
        ),
    )


def analyze_relation(
    relation: BlockRelation,
) -> RelationMigrationAdvice:

    relation_type = (
        relation.relation_type
        .strip()
        .upper()
    )

    if relation_type == "MASTER_DETAIL":
        return _master_detail_advice(
            relation
        )

    return RelationMigrationAdvice(
        relation_name=relation.name,
        relation_type=relation.relation_type,

        master_block=relation.master_block,
        detail_block=relation.detail_block,

        master_item=relation.master_item,
        detail_item=relation.detail_item,

        apex_pattern="APEX_RELATION_REVIEW",

        master_component="MANUAL_REVIEW",
        detail_component="MANUAL_REVIEW",

        synchronization="MANUAL_REVIEW",

        automation_level="MANUAL",
        complexity="HIGH",
        risk="HIGH",

        rationale=(
            "The Forms relation type is not "
            "currently mapped to a supported "
            "APEX migration pattern and "
            "requires manual analysis."
        ),
    )


def analyze_relations(
    model: FormModel,
) -> tuple[
    RelationMigrationAdvice,
    ...
]:

    return tuple(
        analyze_relation(
            relation
        )
        for relation in model.relations
    )