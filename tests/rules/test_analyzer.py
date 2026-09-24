from pathlib import Path

from f2a.parser.xml_parser import parse_form_xml
from f2a.rules.analyzer import analyze_form


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)


def get_findings():
    model = parse_form_xml(FIXTURE)

    return analyze_form(model)


def test_analyzer_detects_all_triggers():
    findings = get_findings()

    assert len(findings) == 5


def test_when_validate_item_mapping():
    findings = get_findings()

    finding = next(
        item
        for item in findings
        if (
            item.object_name == "CUSTOMERS.EMAIL"
            and item.trigger_name
            == "WHEN-VALIDATE-ITEM"
        )
    )

    # ----------------------------------------------------------
    # Migration classification
    # ----------------------------------------------------------

    assert finding.scope == "ITEM"
    assert finding.apex_pattern == "APEX_VALIDATION"

    assert finding.complexity == "LOW"
    assert finding.risk == "MEDIUM"
    assert finding.effort == 1
    assert finding.confidence == "HIGH"
    assert finding.automation_level == "ASSISTED"

    # ----------------------------------------------------------
    # Program Unit detection
    # ----------------------------------------------------------

    assert (
        "VALIDATE_EMAIL"
        in finding.referenced_program_units
    )

    # ----------------------------------------------------------
    # Built-in detection
    # ----------------------------------------------------------

    assert (
        "FORM_TRIGGER_FAILURE"
        in finding.builtins
    )

    assert len(finding.builtin_details) == 1

    detail = finding.builtin_details[0]

    assert detail.name == "FORM_TRIGGER_FAILURE"
    assert detail.category == "VALIDATION"
    assert (
        detail.apex_strategy
        == "APEX_VALIDATION_OR_ERROR"
    )
    assert detail.risk == "MEDIUM"

    # ----------------------------------------------------------
    # Recommendation
    # ----------------------------------------------------------

    assert (
        "APEX validation"
        in finding.recommendation
    )


def test_when_button_pressed_mapping():
    findings = get_findings()

    finding = next(
        item
        for item in findings
        if (
            item.object_name == "CONTROL.BTN_SAVE"
            and item.trigger_name
            == "WHEN-BUTTON-PRESSED"
        )
    )

    # ----------------------------------------------------------
    # Migration classification
    # ----------------------------------------------------------

    assert finding.scope == "ITEM"

    assert (
        finding.apex_pattern
        == "APEX_BUTTON_PROCESS"
    )

    assert finding.complexity == "MEDIUM"

    # Base risk del patrón = MEDIUM,
    # pero COMMIT_FORM tiene HIGH.
    # Por eso el riesgo efectivo sube a HIGH.
    assert finding.risk == "HIGH"

    assert finding.effort == 2
    assert finding.confidence == "HIGH"
    assert finding.automation_level == "ASSISTED"

    # ----------------------------------------------------------
    # Program Unit detection
    # ----------------------------------------------------------

    assert (
        "SAVE_CUSTOMER"
        in finding.referenced_program_units
    )

    # ----------------------------------------------------------
    # Built-in detection
    # ----------------------------------------------------------

    assert (
        "COMMIT_FORM"
        in finding.builtins
    )

    assert len(finding.builtin_details) == 1

    detail = finding.builtin_details[0]

    assert detail.name == "COMMIT_FORM"
    assert detail.category == "TRANSACTION"

    assert (
        detail.apex_strategy
        == "APEX_SUBMIT_AND_PROCESS"
    )

    assert detail.risk == "HIGH"

    # ----------------------------------------------------------
    # Recommendation
    # ----------------------------------------------------------

    assert (
        "COMMIT_FORM"
        in finding.recommendation
    )


def test_block_trigger_mappings():
    findings = get_findings()

    pre_insert = next(
        item
        for item in findings
        if item.trigger_name == "PRE-INSERT"
    )

    post_query = next(
        item
        for item in findings
        if item.trigger_name == "POST-QUERY"
    )

    # ----------------------------------------------------------
    # PRE-INSERT
    # ----------------------------------------------------------

    assert pre_insert.scope == "BLOCK"

    assert (
        pre_insert.apex_pattern
        == "APEX_BEFORE_DML"
    )

    assert pre_insert.complexity == "MEDIUM"
    assert pre_insert.risk == "MEDIUM"
    assert pre_insert.effort == 2
    assert pre_insert.confidence == "MEDIUM"
    assert pre_insert.automation_level == "ASSISTED"

    # ----------------------------------------------------------
    # POST-QUERY
    # ----------------------------------------------------------

    assert post_query.scope == "BLOCK"

    assert (
        post_query.apex_pattern
        == "APEX_QUERY_ENRICHMENT"
    )

    assert post_query.complexity == "MEDIUM"
    assert post_query.risk == "MEDIUM"
    assert post_query.effort == 2
    assert post_query.confidence == "MEDIUM"
    assert post_query.automation_level == "ASSISTED"


def test_form_trigger_mapping():
    findings = get_findings()

    finding = next(
        item
        for item in findings
        if (
            item.trigger_name
            == "WHEN-NEW-FORM-INSTANCE"
        )
    )

    # ----------------------------------------------------------
    # Migration classification
    # ----------------------------------------------------------

    assert finding.scope == "FORM"

    assert (
        finding.apex_pattern
        == "APEX_PAGE_INITIALIZATION"
    )

    assert finding.complexity == "MEDIUM"
    assert finding.risk == "MEDIUM"
    assert finding.effort == 2
    assert finding.confidence == "MEDIUM"
    assert finding.automation_level == "ASSISTED"

    # ----------------------------------------------------------
    # Built-ins
    # ----------------------------------------------------------

    assert "GO_BLOCK" in finding.builtins
    assert "EXECUTE_QUERY" in finding.builtins

    assert len(finding.builtin_details) == 2

    details_by_name = {
        detail.name: detail
        for detail in finding.builtin_details
    }

    go_block = details_by_name["GO_BLOCK"]

    assert go_block.category == "NAVIGATION"
    assert (
        go_block.apex_strategy
        == "APEX_REGION_NAVIGATION"
    )
    assert go_block.risk == "MEDIUM"

    execute_query = details_by_name["EXECUTE_QUERY"]

    assert execute_query.category == "QUERY"
    assert (
        execute_query.apex_strategy
        == "APEX_REGION_QUERY_OR_REFRESH"
    )
    assert execute_query.risk == "MEDIUM"

    # ----------------------------------------------------------
    # Recommendation
    # ----------------------------------------------------------

    assert (
        "Forms navigation/query"
        in finding.recommendation
    )

def test_behavior_pattern_metadata():
    findings = get_findings()

    btn_save = next(
        item
        for item in findings
        if (
            item.object_name == "CONTROL.BTN_SAVE"
            and item.trigger_name
            == "WHEN-BUTTON-PRESSED"
        )
    )

    submit_behavior = next(
        behavior
        for behavior in btn_save.behavior_patterns
        if behavior.name == "SUBMIT_TRANSACTION"
    )

    assert (
        submit_behavior.apex_component
        == "APEX_PAGE_PROCESS"
    )
    assert (
        submit_behavior.automation_level
        == "ASSISTED"
    )
    assert submit_behavior.confidence == "HIGH"

    form_trigger = next(
        item
        for item in findings
        if (
            item.trigger_name
            == "WHEN-NEW-FORM-INSTANCE"
        )
    )

    initial_query = next(
        behavior
        for behavior in form_trigger.behavior_patterns
        if behavior.name == "INITIAL_QUERY"
    )

    assert (
        initial_query.apex_component
        == "APEX_REGION_INITIALIZATION"
    )
    assert initial_query.confidence == "HIGH"

    validation = next(
        item
        for item in findings
        if (
            item.object_name == "CUSTOMERS.EMAIL"
            and item.trigger_name
            == "WHEN-VALIDATE-ITEM"
        )
    )

    validation_behavior = next(
        behavior
        for behavior in validation.behavior_patterns
        if behavior.name == "VALIDATION_FAILURE"
    )

    assert (
        validation_behavior.apex_component
        == "APEX_VALIDATION"
    )


def test_triggers_without_known_behavior_remain_empty():
    findings = get_findings()

    pre_insert = next(
        item
        for item in findings
        if item.trigger_name == "PRE-INSERT"
    )

    post_query = next(
        item
        for item in findings
        if item.trigger_name == "POST-QUERY"
    )

    assert pre_insert.behavior_patterns == ()
    assert post_query.behavior_patterns == ()
    
def test_behavior_patterns_are_attached_to_findings():
    findings = get_findings()

    validate_email = next(
        item
        for item in findings
        if (
            item.object_name == "CUSTOMERS.EMAIL"
            and item.trigger_name
            == "WHEN-VALIDATE-ITEM"
        )
    )

    validate_behaviors = {
        behavior.name
        for behavior in validate_email.behavior_patterns
    }

    assert validate_behaviors == {
        "VALIDATION_FAILURE"
    }

    btn_save = next(
        item
        for item in findings
        if (
            item.object_name == "CONTROL.BTN_SAVE"
            and item.trigger_name
            == "WHEN-BUTTON-PRESSED"
        )
    )

    save_behaviors = {
        behavior.name
        for behavior in btn_save.behavior_patterns
    }

    assert save_behaviors == {
        "SUBMIT_TRANSACTION"
    }

    form_trigger = next(
        item
        for item in findings
        if (
            item.trigger_name
            == "WHEN-NEW-FORM-INSTANCE"
        )
    )

    form_behaviors = {
        behavior.name
        for behavior in form_trigger.behavior_patterns
    }

    assert form_behaviors == {
        "INITIAL_QUERY"
    }


def test_behavior_pattern_metadata():
    findings = get_findings()

    btn_save = next(
        item
        for item in findings
        if (
            item.object_name == "CONTROL.BTN_SAVE"
            and item.trigger_name
            == "WHEN-BUTTON-PRESSED"
        )
    )

    submit_behavior = next(
        behavior
        for behavior in btn_save.behavior_patterns
        if behavior.name == "SUBMIT_TRANSACTION"
    )

    assert (
        submit_behavior.apex_component
        == "APEX_PAGE_PROCESS"
    )

    assert (
        submit_behavior.automation_level
        == "ASSISTED"
    )

    assert submit_behavior.confidence == "HIGH"

    form_trigger = next(
        item
        for item in findings
        if (
            item.trigger_name
            == "WHEN-NEW-FORM-INSTANCE"
        )
    )

    initial_query = next(
        behavior
        for behavior in form_trigger.behavior_patterns
        if behavior.name == "INITIAL_QUERY"
    )

    assert (
        initial_query.apex_component
        == "APEX_REGION_INITIALIZATION"
    )

    assert initial_query.confidence == "HIGH"

    validation = next(
        item
        for item in findings
        if (
            item.object_name == "CUSTOMERS.EMAIL"
            and item.trigger_name
            == "WHEN-VALIDATE-ITEM"
        )
    )

    validation_behavior = next(
        behavior
        for behavior in validation.behavior_patterns
        if behavior.name == "VALIDATION_FAILURE"
    )

    assert (
        validation_behavior.apex_component
        == "APEX_VALIDATION"
    )