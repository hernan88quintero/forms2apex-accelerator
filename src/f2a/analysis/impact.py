from __future__ import annotations

from dataclasses import dataclass

from f2a.analysis.dependencies import DependencyGraph


@dataclass(frozen=True)
class ImpactReport:
    target_node: str

    direct_dependents: tuple[str, ...]
    transitive_dependents: tuple[str, ...]

    affected_forms: tuple[str, ...]
    affected_blocks: tuple[str, ...]
    affected_items: tuple[str, ...]
    affected_triggers: tuple[str, ...]
    affected_program_units: tuple[str, ...]

    impact_scope: str


def _filter_nodes_by_type(
    graph: DependencyGraph,
    node_ids: tuple[str, ...],
    node_type: str,
) -> tuple[str, ...]:

    result: list[str] = []

    for node_id in node_ids:
        node = graph.get_node(node_id)

        if node is None:
            continue

        if node.node_type == node_type:
            result.append(node_id)

    return tuple(sorted(result))


def _calculate_impact_scope(
    *,
    forms: tuple[str, ...],
    blocks: tuple[str, ...],
    items: tuple[str, ...],
) -> str:

    if forms:
        return "FORM"

    if blocks:
        return "BLOCK"

    if items:
        return "ITEM"

    return "LOCAL"


def analyze_impact(
    graph: DependencyGraph,
    target_node: str,
) -> ImpactReport:

    direct_dependents = (
        graph.direct_dependents_of(
            target_node
        )
    )

    transitive_dependents = (
        graph.dependents_of(
            target_node
        )
    )

    affected_forms = _filter_nodes_by_type(
        graph,
        transitive_dependents,
        "FORM",
    )

    affected_blocks = _filter_nodes_by_type(
        graph,
        transitive_dependents,
        "BLOCK",
    )

    affected_items = _filter_nodes_by_type(
        graph,
        transitive_dependents,
        "ITEM",
    )

    affected_triggers = _filter_nodes_by_type(
        graph,
        transitive_dependents,
        "TRIGGER",
    )

    affected_program_units = _filter_nodes_by_type(
        graph,
        transitive_dependents,
        "PROGRAM_UNIT",
    )

    impact_scope = _calculate_impact_scope(
        forms=affected_forms,
        blocks=affected_blocks,
        items=affected_items,
    )

    return ImpactReport(
        target_node=target_node,
        direct_dependents=direct_dependents,
        transitive_dependents=transitive_dependents,
        affected_forms=affected_forms,
        affected_blocks=affected_blocks,
        affected_items=affected_items,
        affected_triggers=affected_triggers,
        affected_program_units=affected_program_units,
        impact_scope=impact_scope,
    )