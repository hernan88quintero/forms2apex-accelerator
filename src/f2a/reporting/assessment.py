from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from f2a.analysis.dependencies import (
    build_dependency_graph,
)
from f2a.analysis.planner import (
    build_migration_plan,
)
from f2a.model import FormModel
from f2a.rules.analyzer import analyze_form


@dataclass(frozen=True)
class AssessmentSummary:
    form_name: str

    block_count: int
    item_count: int
    trigger_count: int
    program_unit_count: int
    lov_count: int

    finding_count: int
    builtin_count: int
    behavior_count: int

    graph_node_count: int
    graph_edge_count: int

    total_effort: int

    complexity_summary: tuple[
        tuple[str, int], ...
    ]

    risk_summary: tuple[
        tuple[str, int], ...
    ]

    confidence_summary: tuple[
        tuple[str, int], ...
    ]

    behavior_summary: tuple[
        tuple[str, int], ...
    ]

    migration_stages: tuple[str, ...]

    overall_complexity: str
    overall_risk: str
    assessment_classification: str


def _counter_as_tuple(
    counter: Counter,
) -> tuple[tuple[str, int], ...]:

    return tuple(
        sorted(
            counter.items()
        )
    )

def _highest_level(
    values: Counter,
    priority: tuple[str, ...],
    *,
    default: str,
) -> str:

    for level in priority:
        if values.get(level, 0) > 0:
            return level

    return default


def _get_assessment_classification(
    *,
    overall_complexity: str,
    overall_risk: str,
    behavior_count: int,
) -> str:

    if (
        overall_risk == "HIGH"
        or overall_complexity == "HIGH"
    ):
        return "ASSISTED_MIGRATION"

    if (
        overall_complexity == "MEDIUM"
        or behavior_count > 0
    ):
        return "ASSISTED_MIGRATION"

    return "HIGH_AUTOMATION_CANDIDATE"

def build_assessment_summary(
    model: FormModel,
    *,
    form_name: str,
) -> AssessmentSummary:

    findings = analyze_form(
        model
    )

    graph = build_dependency_graph(
        model,
        form_name=form_name,
    )

    migration_plan = build_migration_plan(
        graph,
        findings,
    )

    complexity_counter = Counter(
        finding.complexity
        for finding in findings
    )

    risk_counter = Counter(
        finding.risk
        for finding in findings
    )

    confidence_counter = Counter(
        finding.confidence
        for finding in findings
    )

    behavior_counter = Counter(
        behavior.name
        for finding in findings
        for behavior in finding.behavior_patterns
    )

    builtin_count = sum(
        len(finding.builtin_details)
        for finding in findings
    )

    behavior_count = sum(
        len(finding.behavior_patterns)
        for finding in findings
    )

    total_effort = sum(
        finding.effort
        for finding in findings
    )

    overall_complexity = _highest_level(
        complexity_counter,
        (
            "HIGH",
            "MEDIUM",
            "LOW",
        ),
        default="LOW",
    )

    overall_risk = _highest_level(
        risk_counter,
        (
            "HIGH",
            "MEDIUM",
            "LOW",
        ),
        default="LOW",
    )

    assessment_classification = (
        _get_assessment_classification(
            overall_complexity=overall_complexity,
            overall_risk=overall_risk,
            behavior_count=behavior_count,
        )
    )

    return AssessmentSummary(
        form_name=form_name,
        block_count=len(model.blocks),
        item_count=model.item_count,
        trigger_count=model.trigger_count,
        program_unit_count=len(
            model.program_units
        ),
        lov_count=len(model.lovs),
        finding_count=len(findings),
        builtin_count=builtin_count,
        behavior_count=behavior_count,
        graph_node_count=len(
            graph.nodes
        ),
        graph_edge_count=len(
            graph.edges
        ),
        total_effort=total_effort,
        complexity_summary=_counter_as_tuple(
            complexity_counter
        ),
        risk_summary=_counter_as_tuple(
            risk_counter
        ),
        confidence_summary=_counter_as_tuple(
            confidence_counter
        ),
        behavior_summary=_counter_as_tuple(
            behavior_counter
        ),
        migration_stages=tuple(
            step.stage
            for step in migration_plan
        ),
        overall_complexity=overall_complexity,
        overall_risk=overall_risk,
        assessment_classification=(
            assessment_classification
        ),
    )


def _render_counter_section(
    title: str,
    values: tuple[tuple[str, int], ...],
) -> list[str]:

    lines = [
        f"## {title}",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]

    if not values:
        lines.append(
            "| None | 0 |"
        )
    else:
        for name, count in values:
            lines.append(
                f"| {name} | {count} |"
            )

    lines.append("")

    return lines

def _format_values(
    values: tuple[str, ...],
) -> str:

    if not values:
        return "-"

    return ", ".join(values)

def _render_findings_section(
    findings,
    *,
    form_name: str,
) -> list[str]:

    lines: list[str] = [
        "## Migration Findings",
        "",
    ]

    if not findings:
        lines.extend(
            [
                "No migration findings were detected.",
                "",
            ]
        )

        return lines

    for index, finding in enumerate(
        findings,
        start=1,
    ):
        
        display_object_name = (
            form_name
            if finding.scope == "FORM"
            else finding.object_name
        )

        lines.extend(
            [
                (
                    f"### {index}. "
                    f"{display_object_name} — "
                    f"{finding.trigger_name}"
                ),
                "",
                "| Property | Value |",
                "|---|---|",
                f"| Scope | {finding.scope} |",
                (
                    f"| APEX Pattern | "
                    f"{finding.apex_pattern} |"
                ),
                (
                    f"| Complexity | "
                    f"{finding.complexity} |"
                ),
                f"| Risk | {finding.risk} |",
                f"| Effort | {finding.effort} |",
                (
                    f"| Confidence | "
                    f"{finding.confidence} |"
                ),
                (
                    f"| Automation | "
                    f"{finding.automation_level} |"
                ),
                "",
                "**Referenced Program Units:**",
                "",
                (
                    _format_values(
                        finding.referenced_program_units
                    )
                ),
                "",
                "**Forms Built-ins:**",
                "",
                _format_values(
                    finding.builtins
                ),
                "",
            ]
        )

        # ------------------------------------------------------
        # Built-in details
        # ------------------------------------------------------

        if finding.builtin_details:

            lines.extend(
                [
                    "**Built-in Analysis:**",
                    "",
                    (
                        "| Built-in | Category | "
                        "APEX Strategy | Risk |"
                    ),
                    "|---|---|---|---|",
                ]
            )

            for detail in finding.builtin_details:

                lines.append(
                    (
                        f"| {detail.name} "
                        f"| {detail.category} "
                        f"| {detail.apex_strategy} "
                        f"| {detail.risk} |"
                    )
                )

            lines.append("")

        # ------------------------------------------------------
        # Behavior details
        # ------------------------------------------------------

        if finding.behavior_patterns:

            lines.extend(
                [
                    "**Detected Behaviors:**",
                    "",
                    (
                        "| Behavior | Target APEX Component | "
                        "Automation | Confidence |"
                    ),
                    "|---|---|---|---|",
                ]
            )

            for behavior in finding.behavior_patterns:

                lines.append(
                    (
                        f"| {behavior.name} "
                        f"| {behavior.apex_component} "
                        f"| {behavior.automation_level} "
                        f"| {behavior.confidence} |"
                    )
                )

            lines.append("")

        lines.extend(
            [
                "**Migration Recommendation:**",
                "",
                finding.recommendation,
                "",
            ]
        )

    return lines

def _display_plan_source_object(
    source_object: str,
    *,
    form_name: str,
) -> str:

    if source_object.startswith(
        "FORM::"
    ):
        return source_object.replace(
            "FORM::",
            f"{form_name}::",
            1,
        )

    return source_object

def _render_migration_plan_section(
    migration_plan,
    *,
    form_name: str,
) -> list[str]:

    lines: list[str] = [
        "## Suggested Migration Plan",
        "",
    ]

    if not migration_plan:
        lines.extend(
            [
                "No migration plan could be generated.",
                "",
            ]
        )

        return lines

    for step in migration_plan:

        lines.extend(
            [
                f"### {step.order}. {step.stage}",
                "",
                "**Target APEX Components:**",
                "",
            ]
        )

        for component in step.apex_components:
            lines.append(
                f"- `{component}`"
            )

        lines.extend(
            [
                "",
                "**Source Objects:**",
                "",
            ]
        )

        for source_object in step.source_objects:

            display_object = (
                _display_plan_source_object(
                    source_object,
                    form_name=form_name,
                )
            )

            lines.append(
                f"- `{display_object}`"
            )

        lines.extend(
            [
                "",
                "**Rationale:**",
                "",
                step.reason,
                "",
            ]
        )

    return lines

def _render_executive_assessment(
    summary: AssessmentSummary,
) -> list[str]:

    lines = [
        "## Executive Assessment",
        "",
        "| Indicator | Result |",
        "|---|---|",
        (
            f"| Overall Complexity | "
            f"{summary.overall_complexity} |"
        ),
        (
            f"| Overall Risk | "
            f"{summary.overall_risk} |"
        ),
        (
            f"| Migration Classification | "
            f"{summary.assessment_classification} |"
        ),
        (
            f"| Estimated Effort Points | "
            f"{summary.total_effort} |"
        ),
        "",
    ]

    if (
        summary.assessment_classification
        == "ASSISTED_MIGRATION"
    ):
        lines.extend(
            [
                "### Technical Conclusion",
                "",
                (
                    "The form is suitable for an assisted "
                    "Forms-to-APEX migration. Structural "
                    "elements and several migration patterns "
                    "can be identified automatically, while "
                    "business logic, transaction behavior, "
                    "and runtime semantics should be reviewed "
                    "during implementation."
                ),
                "",
            ]
        )

    else:
        lines.extend(
            [
                "### Technical Conclusion",
                "",
                (
                    "The form presents a relatively simple "
                    "migration profile and is a strong candidate "
                    "for a higher level of automated conversion."
                ),
                "",
            ]
        )

    return lines

def render_assessment_markdown(
    model: FormModel,
    *,
    form_name: str,
) -> str:

    summary = build_assessment_summary(
        model,
        form_name=form_name,
    )

    findings = analyze_form(
        model
    )

    graph = build_dependency_graph(
        model,
        form_name=form_name,
    )

    migration_plan = build_migration_plan(
        graph,
        findings,
    )

    lines: list[str] = [
        f"# Forms2APEX Migration Assessment — "
        f"{summary.form_name}",
        "",
        "Generated by Forms2APEX Accelerator.",
        "",
        "## Executive Summary",
        "",
        (
            f"The form contains "
            f"{summary.block_count} blocks, "
            f"{summary.item_count} items, "
            f"{summary.trigger_count} triggers, "
            f"{summary.program_unit_count} program units, "
            f"and {summary.lov_count} LOVs."
        ),
        "",
        (
            f"The analysis identified "
            f"{summary.finding_count} migration findings, "
            f"{summary.builtin_count} Forms built-in usages, "
            f"and {summary.behavior_count} behavior patterns."
        ),
        "",
        "## Inventory",
        "",
        "| Object Type | Count |",
        "|---|---:|",
        f"| Blocks | {summary.block_count} |",
        f"| Items | {summary.item_count} |",
        f"| Triggers | {summary.trigger_count} |",
        (
            f"| Program Units | "
            f"{summary.program_unit_count} |"
        ),
        f"| LOVs | {summary.lov_count} |",
        "",
    ]

    lines.extend(
            _render_executive_assessment(
                summary
            )
        )

    lines.extend(
        _render_counter_section(
            "Complexity",
            summary.complexity_summary,
        )
    )

    lines.extend(
        _render_counter_section(
            "Risk",
            summary.risk_summary,
        )
    )

    lines.extend(
        _render_counter_section(
            "Confidence",
            summary.confidence_summary,
        )
    )

    lines.extend(
        _render_counter_section(
            "Detected Behaviors",
            summary.behavior_summary,
        )
    )

    lines.extend(
        _render_findings_section(
            findings,
            form_name=summary.form_name,
        )
    )

    lines.extend(
        [
            "## Dependency Analysis",
            "",
            "| Metric | Value |",
            "|---|---:|",
            (
                f"| Dependency Nodes | "
                f"{summary.graph_node_count} |"
            ),
            (
                f"| Dependency Edges | "
                f"{summary.graph_edge_count} |"
            ),
            "",
            "## Estimated Migration Effort",
            "",
            (
                f"**Total effort points:** "
                f"{summary.total_effort}"
            ),
            "",
        ]
    )

    lines.extend(
        _render_migration_plan_section(
            migration_plan,
            form_name=summary.form_name,
        )
    )

    lines.extend(
        [
            "## Assessment Status",
            "",
            "**Analysis completed successfully.**",
            "",
        ]
    )

    return "\n".join(lines)