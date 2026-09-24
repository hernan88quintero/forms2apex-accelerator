from __future__ import annotations

from dataclasses import dataclass

from f2a.analysis.dependencies import DependencyGraph
from f2a.rules.model import MigrationFinding


@dataclass(frozen=True)
class MigrationPlanStep:
    order: int
    stage: str
    apex_components: tuple[str, ...]
    source_objects: tuple[str, ...]
    reason: str


def _finding_source(
    finding: MigrationFinding,
) -> str:
    return (
        f"{finding.object_name}"
        f"::{finding.trigger_name}"
    )


def _unique_sorted(
    values,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            set(values)
        )
    )


def build_migration_plan(
    graph: DependencyGraph,
    findings: list[MigrationFinding],
) -> tuple[MigrationPlanStep, ...]:

    steps: list[
        tuple[int, str, tuple[str, ...], tuple[str, ...], str]
    ] = []

    # ----------------------------------------------------------
    # 1. Reusable PL/SQL / Program Units
    # ----------------------------------------------------------

    program_units = _unique_sorted(
        node.node_id
        for node in graph.nodes_by_type(
            "PROGRAM_UNIT"
        )
    )

    if program_units:
        steps.append(
            (
                10,
                "REUSABLE_LOGIC",
                (
                    "DATABASE_OR_SHARED_PLSQL",
                ),
                program_units,
                (
                    "Review and migrate reusable Forms Program Units "
                    "before page-level logic that depends on them."
                ),
            )
        )

    # ----------------------------------------------------------
    # 2. Page structure
    # ----------------------------------------------------------

    page_structure = _unique_sorted(
        [
            *(
                node.node_id
                for node in graph.nodes_by_type(
                    "BLOCK"
                )
            ),
            *(
                node.node_id
                for node in graph.nodes_by_type(
                    "ITEM"
                )
            ),
        ]
    )

    if page_structure:
        steps.append(
            (
                20,
                "PAGE_STRUCTURE",
                (
                    "APEX_PAGE_REGIONS_ITEMS",
                ),
                page_structure,
                (
                    "Create the APEX page structure, regions, "
                    "and items required by the migrated logic."
                ),
            )
        )

    # ----------------------------------------------------------
    # 3. Query enrichment
    # ----------------------------------------------------------

    query_findings = [
        finding
        for finding in findings
        if (
            finding.apex_pattern
            == "APEX_QUERY_ENRICHMENT"
        )
    ]

    if query_findings:
        steps.append(
            (
                30,
                "QUERY_ENRICHMENT",
                (
                    "APEX_REGION_SQL",
                    "APEX_COMPUTATION",
                ),
                _unique_sorted(
                    _finding_source(finding)
                    for finding in query_findings
                ),
                (
                    "Translate Forms POST-QUERY enrichment "
                    "into SQL-derived values, joins, "
                    "computations, or appropriate APEX logic."
                ),
            )
        )

    # ----------------------------------------------------------
    # 4. Validations
    # ----------------------------------------------------------

    validation_findings = [
        finding
        for finding in findings
        if (
            finding.apex_pattern
            == "APEX_VALIDATION"
            or any(
                behavior.apex_component
                == "APEX_VALIDATION"
                for behavior
                in finding.behavior_patterns
            )
        )
    ]

    if validation_findings:
        steps.append(
            (
                40,
                "VALIDATIONS",
                (
                    "APEX_VALIDATION",
                ),
                _unique_sorted(
                    _finding_source(finding)
                    for finding in validation_findings
                ),
                (
                    "Implement APEX validations after "
                    "the required items and reusable "
                    "validation logic exist."
                ),
            )
        )

    # ----------------------------------------------------------
    # 5. DML and page processes
    # ----------------------------------------------------------

    process_findings = [
        finding
        for finding in findings
        if (
            finding.apex_pattern
            in {
                "APEX_BEFORE_DML",
                "APEX_BUTTON_PROCESS",
            }
            or any(
                behavior.apex_component
                == "APEX_PAGE_PROCESS"
                for behavior
                in finding.behavior_patterns
            )
        )
    ]

    if process_findings:
        steps.append(
            (
                50,
                "DML_AND_PAGE_PROCESSES",
                (
                    "APEX_PAGE_PROCESS",
                    "APEX_DML_PROCESS",
                ),
                _unique_sorted(
                    _finding_source(finding)
                    for finding in process_findings
                ),
                (
                    "Implement DML preparation, button processing, "
                    "and transaction behavior after reusable logic "
                    "and page structure are available."
                ),
            )
        )

    # ----------------------------------------------------------
    # 6. Page / Region initialization
    # ----------------------------------------------------------

    initialization_findings = [
        finding
        for finding in findings
        if (
            finding.apex_pattern
            == "APEX_PAGE_INITIALIZATION"
            or any(
                behavior.apex_component
                == "APEX_REGION_INITIALIZATION"
                for behavior
                in finding.behavior_patterns
            )
        )
    ]

    if initialization_findings:
        steps.append(
            (
                60,
                "PAGE_INITIALIZATION",
                (
                    "APEX_REGION_INITIALIZATION",
                ),
                _unique_sorted(
                    _finding_source(finding)
                    for finding
                    in initialization_findings
                ),
                (
                    "Configure page initialization, initial queries, "
                    "and region refresh behavior after the target "
                    "page structure has been created."
                ),
            )
        )

    # ----------------------------------------------------------
    # 7. Dynamic Actions
    # ----------------------------------------------------------

    dynamic_action_findings = [
        finding
        for finding in findings
        if any(
            behavior.apex_component
            == "APEX_DYNAMIC_ACTION"
            for behavior
            in finding.behavior_patterns
        )
    ]

    if dynamic_action_findings:
        steps.append(
            (
                70,
                "DYNAMIC_ACTIONS",
                (
                    "APEX_DYNAMIC_ACTION",
                ),
                _unique_sorted(
                    _finding_source(finding)
                    for finding
                    in dynamic_action_findings
                ),
                (
                    "Implement client-side interaction only after "
                    "the referenced APEX items and regions exist."
                ),
            )
        )

    # ----------------------------------------------------------
    # 8. Navigation
    # ----------------------------------------------------------

    navigation_findings = [
        finding
        for finding in findings
        if any(
            behavior.apex_component
            == "APEX_BRANCH_OR_REDIRECT"
            for behavior
            in finding.behavior_patterns
        )
    ]

    if navigation_findings:
        steps.append(
            (
                80,
                "NAVIGATION",
                (
                    "APEX_BRANCH_OR_REDIRECT",
                ),
                _unique_sorted(
                    _finding_source(finding)
                    for finding
                    in navigation_findings
                ),
                (
                    "Implement page navigation after destination "
                    "pages and required state-handling mechanisms "
                    "are defined."
                ),
            )
        )

    ordered_steps = sorted(
        steps,
        key=lambda item: item[0],
    )

    return tuple(
        MigrationPlanStep(
            order=index,
            stage=stage,
            apex_components=components,
            source_objects=source_objects,
            reason=reason,
        )
        for index, (
            _priority,
            stage,
            components,
            source_objects,
            reason,
        ) in enumerate(
            ordered_steps,
            start=1,
        )
    )