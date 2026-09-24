from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BehaviorPattern:
    name: str
    apex_component: str
    automation_level: str
    confidence: str
    recommendation: str


def _has_any(
    builtins: set[str],
    candidates: set[str],
) -> bool:
    return bool(
        builtins.intersection(candidates)
    )


def detect_behavior_patterns(
    builtins: tuple[str, ...],
) -> tuple[BehaviorPattern, ...]:

    detected: list[BehaviorPattern] = []

    builtin_set = {
        name.upper()
        for name in builtins
    }

    # ----------------------------------------------------------
    # Validation failure
    # ----------------------------------------------------------

    if "FORM_TRIGGER_FAILURE" in builtin_set:
        detected.append(
            BehaviorPattern(
                name="VALIDATION_FAILURE",
                apex_component="APEX_VALIDATION",
                automation_level="ASSISTED",
                confidence="HIGH",
                recommendation=(
                    "Convert the Forms validation failure "
                    "into an APEX validation or explicit "
                    "APEX error handling."
                ),
            )
        )

    # ----------------------------------------------------------
    # Transaction / submit
    # ----------------------------------------------------------

    if "COMMIT_FORM" in builtin_set:
        detected.append(
            BehaviorPattern(
                name="SUBMIT_TRANSACTION",
                apex_component="APEX_PAGE_PROCESS",
                automation_level="ASSISTED",
                confidence="HIGH",
                recommendation=(
                    "Replace COMMIT_FORM with APEX submit "
                    "and page process transaction semantics."
                ),
            )
        )

    # ----------------------------------------------------------
    # Initial query/navigation behavior
    # ----------------------------------------------------------

    if {
        "GO_BLOCK",
        "EXECUTE_QUERY",
    }.issubset(builtin_set):
        detected.append(
            BehaviorPattern(
                name="INITIAL_QUERY",
                apex_component="APEX_REGION_INITIALIZATION",
                automation_level="ASSISTED",
                confidence="HIGH",
                recommendation=(
                    "Translate block navigation followed by "
                    "EXECUTE_QUERY into region initialization, "
                    "SQL source, or refresh behavior."
                ),
            )
        )

    # ----------------------------------------------------------
    # Enter Query + Execute Query
    # ----------------------------------------------------------

    if {
        "ENTER_QUERY",
        "EXECUTE_QUERY",
    }.issubset(builtin_set):
        detected.append(
            BehaviorPattern(
                name="QUERY_FILTER",
                apex_component="APEX_SEARCH_OR_FILTER",
                automation_level="ASSISTED",
                confidence="MEDIUM",
                recommendation=(
                    "Translate Forms Enter Query behavior "
                    "into APEX report filters, page items, "
                    "or search criteria."
                ),
            )
        )

    # ----------------------------------------------------------
    # Form-to-form navigation
    # ----------------------------------------------------------

    if _has_any(
        builtin_set,
        {
            "CALL_FORM",
            "OPEN_FORM",
            "NEW_FORM",
        },
    ):
        detected.append(
            BehaviorPattern(
                name="FORM_NAVIGATION",
                apex_component="APEX_BRANCH_OR_REDIRECT",
                automation_level="ASSISTED",
                confidence="MEDIUM",
                recommendation=(
                    "Replace Forms cross-form navigation "
                    "with an APEX branch, redirect, or "
                    "application page navigation."
                ),
            )
        )

    # ----------------------------------------------------------
    # Item navigation
    # ----------------------------------------------------------

    if _has_any(
        builtin_set,
        {
            "GO_ITEM",
            "NEXT_ITEM",
            "PREVIOUS_ITEM",
        },
    ):
        detected.append(
            BehaviorPattern(
                name="ITEM_NAVIGATION",
                apex_component="APEX_DYNAMIC_ACTION",
                automation_level="ASSISTED",
                confidence="MEDIUM",
                recommendation=(
                    "Translate Forms item navigation into "
                    "APEX focus management or a Dynamic Action."
                ),
            )
        )

    # ----------------------------------------------------------
    # UI property manipulation
    # ----------------------------------------------------------

    if _has_any(
        builtin_set,
        {
            "SET_ITEM_PROPERTY",
            "SET_BLOCK_PROPERTY",
        },
    ):
        detected.append(
            BehaviorPattern(
                name="UI_PROPERTY_CHANGE",
                apex_component="APEX_DYNAMIC_ACTION",
                automation_level="ASSISTED",
                confidence="MEDIUM",
                recommendation=(
                    "Translate Forms runtime property changes "
                    "into APEX Dynamic Actions, conditions, "
                    "CSS, JavaScript, or region configuration."
                ),
            )
        )

    # ----------------------------------------------------------
    # Messaging
    # ----------------------------------------------------------

    if _has_any(
        builtin_set,
        {
            "MESSAGE",
            "SHOW_ALERT",
        },
    ):
        detected.append(
            BehaviorPattern(
                name="USER_MESSAGE",
                apex_component="APEX_NOTIFICATION_OR_DIALOG",
                automation_level="ASSISTED",
                confidence="HIGH",
                recommendation=(
                    "Translate Forms messages or alerts into "
                    "APEX success messages, errors, dialogs, "
                    "or confirmation actions."
                ),
            )
        )

    return tuple(detected)