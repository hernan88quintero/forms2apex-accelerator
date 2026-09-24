from f2a.rules.builtins import (
    BUILTIN_CATALOG,
    get_builtin_apex_strategy,
    get_builtin_category,
    get_builtin_definition,
    is_known_builtin,
)


def test_builtin_catalog_has_core_entries():
    assert "GO_BLOCK" in BUILTIN_CATALOG
    assert "EXECUTE_QUERY" in BUILTIN_CATALOG
    assert "COMMIT_FORM" in BUILTIN_CATALOG
    assert "FORM_TRIGGER_FAILURE" in BUILTIN_CATALOG


def test_navigation_builtin():
    definition = get_builtin_definition(
        "GO_BLOCK"
    )

    assert definition is not None
    assert definition.category == "NAVIGATION"
    assert (
        definition.apex_strategy
        == "APEX_REGION_NAVIGATION"
    )
    assert definition.risk == "MEDIUM"


def test_transaction_builtin():
    definition = get_builtin_definition(
        "COMMIT_FORM"
    )

    assert definition is not None
    assert definition.category == "TRANSACTION"
    assert (
        definition.apex_strategy
        == "APEX_SUBMIT_AND_PROCESS"
    )
    assert definition.risk == "HIGH"


def test_validation_builtin():
    assert (
        get_builtin_category(
            "FORM_TRIGGER_FAILURE"
        )
        == "VALIDATION"
    )

    assert (
        get_builtin_apex_strategy(
            "FORM_TRIGGER_FAILURE"
        )
        == "APEX_VALIDATION_OR_ERROR"
    )


def test_builtin_lookup_is_case_insensitive():
    assert is_known_builtin("go_block")
    assert is_known_builtin("Go_Block")
    assert is_known_builtin("GO_BLOCK")


def test_unknown_builtin():
    assert not is_known_builtin(
        "SOMETHING_UNKNOWN"
    )

    assert (
        get_builtin_definition(
            "SOMETHING_UNKNOWN"
        )
        is None
    )