from pathlib import Path

from f2a.parser.xml_parser import parse_form_xml
from f2a.reporting.assessment import (
    build_assessment_summary,
    render_assessment_markdown,
)


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)


def get_model():
    return parse_form_xml(
        FIXTURE
    )


def test_assessment_inventory():
    summary = build_assessment_summary(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert summary.form_name == "F2A_CUSTOMERS_FORM"

    assert summary.block_count == 2
    assert summary.item_count == 7
    assert summary.trigger_count == 5
    assert summary.program_unit_count == 2
    assert summary.lov_count == 1


def test_assessment_analysis_counts():
    summary = build_assessment_summary(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert summary.finding_count == 5
    assert summary.builtin_count == 4
    assert summary.behavior_count == 3

    assert summary.graph_node_count == 21
    assert summary.graph_edge_count == 20


def test_assessment_effort():
    summary = build_assessment_summary(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert summary.total_effort == 9


def test_assessment_risk_summary():
    summary = build_assessment_summary(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert summary.risk_summary == (
        ("HIGH", 1),
        ("MEDIUM", 4),
    )


def test_assessment_behavior_summary():
    summary = build_assessment_summary(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert summary.behavior_summary == (
        ("INITIAL_QUERY", 1),
        ("SUBMIT_TRANSACTION", 1),
        ("VALIDATION_FAILURE", 1),
    )


def test_assessment_migration_plan():
    summary = build_assessment_summary(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert summary.migration_stages == (
        "REUSABLE_LOGIC",
        "PAGE_STRUCTURE",
        "QUERY_ENRICHMENT",
        "VALIDATIONS",
        "DML_AND_PAGE_PROCESSES",
        "PAGE_INITIALIZATION",
    )


def test_markdown_report_contains_key_sections():
    report = render_assessment_markdown(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert (
        "# Forms2APEX Migration Assessment"
        in report
    )

    assert "## Executive Summary" in report
    assert "## Inventory" in report
    assert "## Complexity" in report
    assert "## Risk" in report
    assert "## Detected Behaviors" in report
    assert "## Migration Findings" in report
    assert "## Dependency Analysis" in report

    assert (
        "## Suggested Migration Plan"
        in report
    )

    assert (
        "**Total effort points:** 9"
        in report
    )

    assert (
        "### 1. REUSABLE_LOGIC"
        in report
    )

def test_markdown_contains_migration_findings():
    report = render_assessment_markdown(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert "## Migration Findings" in report

    assert (
        "CUSTOMERS.EMAIL — WHEN-VALIDATE-ITEM"
        in report
    )

    assert (
        "CONTROL.BTN_SAVE — WHEN-BUTTON-PRESSED"
        in report
    )

    assert (
        "F2A_CUSTOMERS_FORM — WHEN-NEW-FORM-INSTANCE"
        in report
    )


def test_markdown_contains_builtin_details():
    report = render_assessment_markdown(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert "FORM_TRIGGER_FAILURE" in report
    assert "COMMIT_FORM" in report
    assert "GO_BLOCK" in report
    assert "EXECUTE_QUERY" in report

    assert "APEX_VALIDATION_OR_ERROR" in report
    assert "APEX_SUBMIT_AND_PROCESS" in report


def test_markdown_contains_behavior_details():
    report = render_assessment_markdown(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert "VALIDATION_FAILURE" in report
    assert "SUBMIT_TRANSACTION" in report
    assert "INITIAL_QUERY" in report

    assert "APEX_VALIDATION" in report
    assert "APEX_PAGE_PROCESS" in report

    assert (
        "APEX_REGION_INITIALIZATION"
        in report
    )

def test_markdown_contains_detailed_migration_plan():
    report = render_assessment_markdown(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert "### 1. REUSABLE_LOGIC" in report
    assert "### 2. PAGE_STRUCTURE" in report
    assert "### 3. QUERY_ENRICHMENT" in report
    assert "### 4. VALIDATIONS" in report

    assert (
        "### 5. DML_AND_PAGE_PROCESSES"
        in report
    )

    assert (
        "### 6. PAGE_INITIALIZATION"
        in report
    )


def test_markdown_plan_contains_apex_components():
    report = render_assessment_markdown(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert (
        "`DATABASE_OR_SHARED_PLSQL`"
        in report
    )

    assert (
        "`APEX_PAGE_REGIONS_ITEMS`"
        in report
    )

    assert "`APEX_VALIDATION`" in report
    assert "`APEX_PAGE_PROCESS`" in report

    assert (
        "`APEX_REGION_INITIALIZATION`"
        in report
    )


def test_markdown_plan_contains_source_objects():
    report = render_assessment_markdown(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert (
        "`PROGRAM_UNIT:SAVE_CUSTOMER`"
        in report
    )

    assert (
        "`PROGRAM_UNIT:VALIDATE_EMAIL`"
        in report
    )

    assert (
        "`CUSTOMERS.EMAIL::WHEN-VALIDATE-ITEM`"
        in report
    )

    assert (
        "`CONTROL.BTN_SAVE::WHEN-BUTTON-PRESSED`"
        in report
    )

    assert (
        "`F2A_CUSTOMERS_FORM::WHEN-NEW-FORM-INSTANCE`"
        in report
    )


def test_markdown_plan_contains_rationale():
    report = render_assessment_markdown(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert "**Rationale:**" in report

    assert (
        "Review and migrate reusable Forms Program Units"
        in report
    )

def test_assessment_overall_classification():
    summary = build_assessment_summary(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert summary.overall_complexity == "MEDIUM"
    assert summary.overall_risk == "HIGH"

    assert (
        summary.assessment_classification
        == "ASSISTED_MIGRATION"
    )


def test_markdown_contains_executive_assessment():
    report = render_assessment_markdown(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert "## Executive Assessment" in report

    assert (
        "| Overall Complexity | MEDIUM |"
        in report
    )

    assert (
        "| Overall Risk | HIGH |"
        in report
    )

    assert (
        "| Migration Classification | "
        "ASSISTED_MIGRATION |"
        in report
    )

    assert "### Technical Conclusion" in report


def test_markdown_contains_assisted_conclusion():
    report = render_assessment_markdown(
        get_model(),
        form_name="F2A_CUSTOMERS_FORM",
    )

    assert (
        "suitable for an assisted "
        "Forms-to-APEX migration"
        in report
    )