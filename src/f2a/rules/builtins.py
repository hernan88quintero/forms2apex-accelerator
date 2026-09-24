from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BuiltinDefinition:
    name: str
    category: str
    apex_strategy: str
    risk: str


BUILTIN_CATALOG: dict[str, BuiltinDefinition] = {
    # ----------------------------------------------------------
    # Navigation
    # ----------------------------------------------------------
    "GO_BLOCK": BuiltinDefinition(
        name="GO_BLOCK",
        category="NAVIGATION",
        apex_strategy="APEX_REGION_NAVIGATION",
        risk="MEDIUM",
    ),
    "GO_ITEM": BuiltinDefinition(
        name="GO_ITEM",
        category="NAVIGATION",
        apex_strategy="APEX_ITEM_FOCUS_OR_NAVIGATION",
        risk="MEDIUM",
    ),
    "NEXT_ITEM": BuiltinDefinition(
        name="NEXT_ITEM",
        category="NAVIGATION",
        apex_strategy="APEX_ITEM_NAVIGATION",
        risk="MEDIUM",
    ),
    "PREVIOUS_ITEM": BuiltinDefinition(
        name="PREVIOUS_ITEM",
        category="NAVIGATION",
        apex_strategy="APEX_ITEM_NAVIGATION",
        risk="MEDIUM",
    ),

    # ----------------------------------------------------------
    # Record navigation
    # ----------------------------------------------------------
    "FIRST_RECORD": BuiltinDefinition(
        name="FIRST_RECORD",
        category="RECORD_NAVIGATION",
        apex_strategy="APEX_REPORT_OR_REGION_NAVIGATION",
        risk="MEDIUM",
    ),
    "LAST_RECORD": BuiltinDefinition(
        name="LAST_RECORD",
        category="RECORD_NAVIGATION",
        apex_strategy="APEX_REPORT_OR_REGION_NAVIGATION",
        risk="MEDIUM",
    ),
    "NEXT_RECORD": BuiltinDefinition(
        name="NEXT_RECORD",
        category="RECORD_NAVIGATION",
        apex_strategy="APEX_REPORT_OR_REGION_NAVIGATION",
        risk="MEDIUM",
    ),
    "PREVIOUS_RECORD": BuiltinDefinition(
        name="PREVIOUS_RECORD",
        category="RECORD_NAVIGATION",
        apex_strategy="APEX_REPORT_OR_REGION_NAVIGATION",
        risk="MEDIUM",
    ),

    # ----------------------------------------------------------
    # Query
    # ----------------------------------------------------------
    "EXECUTE_QUERY": BuiltinDefinition(
        name="EXECUTE_QUERY",
        category="QUERY",
        apex_strategy="APEX_REGION_QUERY_OR_REFRESH",
        risk="MEDIUM",
    ),
    "ENTER_QUERY": BuiltinDefinition(
        name="ENTER_QUERY",
        category="QUERY",
        apex_strategy="APEX_SEARCH_OR_FILTER",
        risk="MEDIUM",
    ),

    # ----------------------------------------------------------
    # Transaction
    # ----------------------------------------------------------
    "COMMIT_FORM": BuiltinDefinition(
        name="COMMIT_FORM",
        category="TRANSACTION",
        apex_strategy="APEX_SUBMIT_AND_PROCESS",
        risk="HIGH",
    ),
    "CLEAR_FORM": BuiltinDefinition(
        name="CLEAR_FORM",
        category="TRANSACTION",
        apex_strategy="APEX_CLEAR_PAGE_OR_BRANCH",
        risk="MEDIUM",
    ),
    "EXIT_FORM": BuiltinDefinition(
        name="EXIT_FORM",
        category="TRANSACTION",
        apex_strategy="APEX_BRANCH_OR_REDIRECT",
        risk="MEDIUM",
    ),

    # ----------------------------------------------------------
    # Messaging / validation
    # ----------------------------------------------------------
    "MESSAGE": BuiltinDefinition(
        name="MESSAGE",
        category="MESSAGING",
        apex_strategy="APEX_SUCCESS_OR_ERROR_MESSAGE",
        risk="LOW",
    ),
    "SHOW_ALERT": BuiltinDefinition(
        name="SHOW_ALERT",
        category="MESSAGING",
        apex_strategy="APEX_DIALOG_OR_CONFIRMATION",
        risk="MEDIUM",
    ),
    "FORM_TRIGGER_FAILURE": BuiltinDefinition(
        name="FORM_TRIGGER_FAILURE",
        category="VALIDATION",
        apex_strategy="APEX_VALIDATION_OR_ERROR",
        risk="MEDIUM",
    ),

    # ----------------------------------------------------------
    # Item / Block properties
    # ----------------------------------------------------------
    "SET_ITEM_PROPERTY": BuiltinDefinition(
        name="SET_ITEM_PROPERTY",
        category="UI_PROPERTY",
        apex_strategy="APEX_DYNAMIC_ACTION_OR_JAVASCRIPT",
        risk="MEDIUM",
    ),
    "SET_BLOCK_PROPERTY": BuiltinDefinition(
        name="SET_BLOCK_PROPERTY",
        category="UI_PROPERTY",
        apex_strategy="APEX_REGION_CONFIGURATION",
        risk="HIGH",
    ),

    # ----------------------------------------------------------
    # Cross-form navigation
    # ----------------------------------------------------------
    "CALL_FORM": BuiltinDefinition(
        name="CALL_FORM",
        category="FORM_NAVIGATION",
        apex_strategy="APEX_BRANCH_OR_REDIRECT",
        risk="HIGH",
    ),
    "OPEN_FORM": BuiltinDefinition(
        name="OPEN_FORM",
        category="FORM_NAVIGATION",
        apex_strategy="APEX_BRANCH_OR_REDIRECT",
        risk="HIGH",
    ),
    "NEW_FORM": BuiltinDefinition(
        name="NEW_FORM",
        category="FORM_NAVIGATION",
        apex_strategy="APEX_BRANCH_OR_REDIRECT",
        risk="HIGH",
    ),
}


def get_builtin_definition(
    name: str,
) -> BuiltinDefinition | None:
    return BUILTIN_CATALOG.get(
        name.upper()
    )


def get_builtin_category(
    name: str,
) -> str | None:
    definition = get_builtin_definition(name)

    if definition is None:
        return None

    return definition.category


def get_builtin_apex_strategy(
    name: str,
) -> str | None:
    definition = get_builtin_definition(name)

    if definition is None:
        return None

    return definition.apex_strategy


def is_known_builtin(
    name: str,
) -> bool:
    return name.upper() in BUILTIN_CATALOG