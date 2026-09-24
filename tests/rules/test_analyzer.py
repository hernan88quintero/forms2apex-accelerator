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

    assert finding.complexity == "LOW"
    assert finding.automation_level == "ASSISTED"

    assert (
        "APEX validation"
        in finding.recommendation
    )

    assert finding.scope == "ITEM"
    assert finding.apex_pattern == "APEX_VALIDATION"

    assert (
        "VALIDATE_EMAIL"
        in finding.referenced_program_units
    )

    assert (
        "FORM_TRIGGER_FAILURE"
        in finding.builtins
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

    assert finding.complexity == "MEDIUM"
    assert finding.automation_level == "ASSISTED"

    assert (
        "COMMIT_FORM"
        in finding.recommendation
    )

    assert finding.scope == "ITEM"

    assert (
        finding.apex_pattern
        == "APEX_BUTTON_PROCESS"
    )

    assert (
        "SAVE_CUSTOMER"
        in finding.referenced_program_units
    )

    assert (
        "COMMIT_FORM"
        in finding.builtins
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

    assert pre_insert.scope == "BLOCK"

    assert (
        pre_insert.apex_pattern
        == "APEX_BEFORE_DML"
    )

    assert post_query.scope == "BLOCK"

    assert (
        post_query.apex_pattern
        == "APEX_QUERY_ENRICHMENT"
    )


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

    assert finding.complexity == "MEDIUM"
    assert finding.automation_level == "ASSISTED"

    assert (
        "Forms navigation/query"
        in finding.recommendation
    )

    assert finding.scope == "FORM"

    assert (
        finding.apex_pattern
        == "APEX_PAGE_INITIALIZATION"
    )

    assert "GO_BLOCK" in finding.builtins
    assert "EXECUTE_QUERY" in finding.builtins