from __future__ import annotations

import re

from f2a.model import FormModel
from f2a.rules.builtins import (
    BUILTIN_CATALOG,
    get_builtin_definition,
)
from f2a.rules.model import (
    BuiltinFinding,
    MigrationFinding,
)


TRIGGER_APEX_PATTERNS = {
    ("ITEM", "WHEN-VALIDATE-ITEM"): "APEX_VALIDATION",
    ("ITEM", "WHEN-BUTTON-PRESSED"): "APEX_BUTTON_PROCESS",

    ("BLOCK", "PRE-INSERT"): "APEX_BEFORE_DML",
    ("BLOCK", "POST-QUERY"): "APEX_QUERY_ENRICHMENT",

    ("FORM", "WHEN-NEW-FORM-INSTANCE"): "APEX_PAGE_INITIALIZATION",
}


PATTERN_GUIDANCE = {
    "APEX_VALIDATION": {
        "complexity": "LOW",
        "risk": "LOW",
        "effort": 1,
        "confidence": "HIGH",
        "automation": "ASSISTED",
        "recommendation": (
            "Create an APEX validation and migrate or reuse "
            "the referenced validation logic."
        ),
    },

    "APEX_BUTTON_PROCESS": {
        "complexity": "MEDIUM",
        "risk": "MEDIUM",
        "effort": 2,
        "confidence": "HIGH",
        "automation": "ASSISTED",
        "recommendation": (
            "Create an APEX button with an associated "
            "server-side process."
        ),
    },

    "APEX_BEFORE_DML": {
        "complexity": "MEDIUM",
        "risk": "MEDIUM",
        "effort": 2,
        "confidence": "MEDIUM",
        "automation": "ASSISTED",
        "recommendation": (
            "Move the pre-insert initialization or defaulting "
            "logic to an APEX process or database layer before DML."
        ),
    },

    "APEX_QUERY_ENRICHMENT": {
        "complexity": "MEDIUM",
        "risk": "MEDIUM",
        "effort": 2,
        "confidence": "MEDIUM",
        "automation": "ASSISTED",
        "recommendation": (
            "Replace POST-QUERY logic with SQL-derived columns, "
            "joins, computations, or page processes as appropriate."
        ),
    },

    "APEX_PAGE_INITIALIZATION": {
        "complexity": "MEDIUM",
        "risk": "MEDIUM",
        "effort": 2,
        "confidence": "MEDIUM",
        "automation": "ASSISTED",
        "recommendation": (
            "Replace Forms startup navigation and query behavior "
            "with APEX page initialization, region queries, "
            "and refresh behavior."
        ),
    },

    "MANUAL_REVIEW": {
        "complexity": "HIGH",
        "risk": "HIGH",
        "effort": 3,
        "confidence": "LOW",
        "automation": "MANUAL",
        "recommendation": (
            "No deterministic migration rule is currently defined. "
            "Review the Forms logic and design its APEX equivalent."
        ),
    },
}


# El catálogo es ahora la única fuente de verdad de built-ins conocidos.
KNOWN_FORMS_BUILTINS = tuple(
    BUILTIN_CATALOG.keys()
)


RISK_RANK = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
}


def _contains_token(
    source_code: str,
    token: str,
) -> bool:
    pattern = rf"\b{re.escape(token)}\b"

    return bool(
        re.search(
            pattern,
            source_code,
            flags=re.IGNORECASE,
        )
    )


def _detect_builtins(
    source_code: str,
) -> tuple[str, ...]:
    return tuple(
        builtin
        for builtin in KNOWN_FORMS_BUILTINS
        if _contains_token(
            source_code,
            builtin,
        )
    )


def _detect_program_unit_references(
    source_code: str,
    unit_names: tuple[str, ...],
) -> tuple[str, ...]:
    return tuple(
        unit_name
        for unit_name in unit_names
        if _contains_token(
            source_code,
            unit_name,
        )
    )


def _get_apex_pattern(
    scope: str,
    trigger_name: str,
) -> str:
    return TRIGGER_APEX_PATTERNS.get(
        (
            scope.upper(),
            trigger_name.upper(),
        ),
        "MANUAL_REVIEW",
    )


def _build_builtin_findings(
    builtins: tuple[str, ...],
) -> tuple[BuiltinFinding, ...]:

    details: list[BuiltinFinding] = []

    for builtin_name in builtins:
        definition = get_builtin_definition(
            builtin_name
        )

        if definition is None:
            continue

        details.append(
            BuiltinFinding(
                name=definition.name,
                category=definition.category,
                apex_strategy=definition.apex_strategy,
                risk=definition.risk,
            )
        )

    return tuple(details)


def _calculate_effective_risk(
    base_risk: str,
    builtin_details: tuple[BuiltinFinding, ...],
) -> str:

    effective_risk = base_risk

    for detail in builtin_details:
        if (
            RISK_RANK.get(detail.risk, 0)
            > RISK_RANK.get(effective_risk, 0)
        ):
            effective_risk = detail.risk

    return effective_risk


def _get_migration_guidance(
    apex_pattern: str,
    builtins: tuple[str, ...],
) -> tuple[str, str, int, str, str, str]:

    guidance = PATTERN_GUIDANCE.get(
        apex_pattern,
        PATTERN_GUIDANCE["MANUAL_REVIEW"],
    )

    complexity = guidance["complexity"]
    risk = guidance["risk"]
    effort = guidance["effort"]
    confidence = guidance["confidence"]
    automation = guidance["automation"]
    recommendation = guidance["recommendation"]

    if "FORM_TRIGGER_FAILURE" in builtins:
        recommendation += (
            " Convert FORM_TRIGGER_FAILURE into an APEX "
            "validation failure or appropriate APEX error."
        )

    if "COMMIT_FORM" in builtins:
        recommendation += (
            " Do not migrate COMMIT_FORM literally; use "
            "APEX submit/process transaction semantics."
        )

    if (
        "GO_BLOCK" in builtins
        or "EXECUTE_QUERY" in builtins
    ):
        recommendation += (
            " Forms navigation/query built-ins must be translated "
            "to APEX page, region, query, or refresh semantics."
        )

    return (
        complexity,
        risk,
        effort,
        confidence,
        automation,
        recommendation,
    )


def analyze_form(
    model: FormModel,
) -> list[MigrationFinding]:

    findings: list[MigrationFinding] = []

    units_by_name = {
        unit.name.upper(): unit
        for unit in model.program_units
    }

    unit_names = tuple(
        units_by_name.keys()
    )

    def analyze_trigger(
        *,
        scope: str,
        object_name: str,
        trigger,
    ) -> None:

        source_code = trigger.source_code or ""

        referenced_units = (
            _detect_program_unit_references(
                source_code,
                unit_names,
            )
        )

        # Analiza el trigger y también los Program Units
        # invocados directamente por él.
        expanded_source = source_code

        for unit_name in referenced_units:
            unit = units_by_name[unit_name]

            expanded_source += "\n"
            expanded_source += unit.source_code or ""

        builtins = _detect_builtins(
            expanded_source
        )

        builtin_details = _build_builtin_findings(
            builtins
        )

        apex_pattern = _get_apex_pattern(
            scope,
            trigger.name,
        )

        (
            complexity,
            base_risk,
            effort,
            confidence,
            automation_level,
            recommendation,
        ) = _get_migration_guidance(
            apex_pattern,
            builtins,
        )

        risk = _calculate_effective_risk(
            base_risk,
            builtin_details,
        )

        finding = MigrationFinding(
            scope=scope,
            object_name=object_name,
            trigger_name=trigger.name,
            apex_pattern=apex_pattern,
            complexity=complexity,
            risk=risk,
            effort=effort,
            confidence=confidence,
            automation_level=automation_level,
            recommendation=recommendation,
            builtins=builtins,
            builtin_details=builtin_details,
            referenced_program_units=referenced_units,
        )

        findings.append(finding)

    # ----------------------------------------------------------
    # ITEM y BLOCK triggers
    # ----------------------------------------------------------

    for block in model.blocks:

        for item in block.items:

            for trigger in item.triggers:

                analyze_trigger(
                    scope="ITEM",
                    object_name=(
                        f"{block.name}.{item.name}"
                    ),
                    trigger=trigger,
                )

        for trigger in block.triggers:

            analyze_trigger(
                scope="BLOCK",
                object_name=block.name,
                trigger=trigger,
            )

    # ----------------------------------------------------------
    # FORM triggers
    # ----------------------------------------------------------

    for trigger in model.form_triggers:

        analyze_trigger(
            scope="FORM",
            object_name="FORM",
            trigger=trigger,
        )

    return findings