from f2a.rules.behaviors import (
    detect_behavior_patterns,
)


def get_names(builtins):
    return {
        behavior.name
        for behavior in detect_behavior_patterns(
            builtins
        )
    }


def test_validation_failure_behavior():
    names = get_names(
        ("FORM_TRIGGER_FAILURE",)
    )

    assert "VALIDATION_FAILURE" in names


def test_commit_form_behavior():
    behaviors = detect_behavior_patterns(
        ("COMMIT_FORM",)
    )

    assert len(behaviors) == 1

    behavior = behaviors[0]

    assert behavior.name == "SUBMIT_TRANSACTION"
    assert (
        behavior.apex_component
        == "APEX_PAGE_PROCESS"
    )
    assert behavior.confidence == "HIGH"


def test_initial_query_behavior():
    names = get_names(
        (
            "GO_BLOCK",
            "EXECUTE_QUERY",
        )
    )

    assert "INITIAL_QUERY" in names


def test_query_filter_behavior():
    names = get_names(
        (
            "ENTER_QUERY",
            "EXECUTE_QUERY",
        )
    )

    assert "QUERY_FILTER" in names


def test_form_navigation_behavior():
    names = get_names(
        ("CALL_FORM",)
    )

    assert "FORM_NAVIGATION" in names


def test_ui_property_behavior():
    names = get_names(
        ("SET_ITEM_PROPERTY",)
    )

    assert "UI_PROPERTY_CHANGE" in names


def test_message_behavior():
    names = get_names(
        ("MESSAGE",)
    )

    assert "USER_MESSAGE" in names


def test_multiple_behaviors_can_be_detected():
    names = get_names(
        (
            "COMMIT_FORM",
            "MESSAGE",
            "SET_ITEM_PROPERTY",
        )
    )

    assert names == {
        "SUBMIT_TRANSACTION",
        "USER_MESSAGE",
        "UI_PROPERTY_CHANGE",
    }


def test_unknown_builtin_produces_no_behavior():
    behaviors = detect_behavior_patterns(
        ("SOMETHING_UNKNOWN",)
    )

    assert behaviors == ()