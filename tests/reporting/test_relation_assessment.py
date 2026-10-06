from pathlib import Path

from f2a.parser.xml_parser import (
    parse_form_xml,
)
from f2a.reporting.assessment import (
    build_assessment_summary,
    render_assessment_markdown,
)


GOLDEN_001 = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)

GOLDEN_002 = Path(
    "samples/golden_002/fixtures/f2a_orders_form.xml"
)


def _render(
    fixture: Path,
    form_name: str,
) -> str:

    model = parse_form_xml(
        fixture
    )

    return render_assessment_markdown(
        model,
        form_name=form_name,
    )


def test_form_without_relations_reports_none():
    report = _render(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    assert (
        "## Master / Detail Relationships"
        in report
    )

    assert (
        "No explicit master/detail "
        "relationships were detected."
        in report
    )


def test_master_detail_section_is_rendered():
    report = _render(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    assert (
        "## Master / Detail Relationships"
        in report
    )

    assert (
        "### ORDERS_ORDER_LINES"
        in report
    )


def test_master_detail_source_objects_are_rendered():
    report = _render(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    assert (
        "| Master | `ORDERS.ORDER_ID` |"
        in report
    )

    assert (
        "| Detail | `ORDER_LINES.ORDER_ID` |"
        in report
    )


def test_master_detail_apex_architecture_is_rendered():
    report = _render(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    assert (
        "| Pattern | `APEX_MASTER_DETAIL` |"
        in report
    )

    assert (
        "| Master Component | "
        "`APEX_FORM_OR_MASTER_REGION` |"
        in report
    )

    assert (
        "| Detail Component | "
        "`APEX_INTERACTIVE_GRID` |"
        in report
    )

    assert (
        "| Synchronization | "
        "`DETAIL_REFRESH_ON_MASTER_CHANGE` |"
        in report
    )


def test_master_detail_guidance_is_rendered():
    report = _render(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    assert (
        "| Automation | ASSISTED |"
        in report
    )

    assert (
        "| Complexity | MEDIUM |"
        in report
    )

    assert (
        "| Risk | MEDIUM |"
        in report
    )

    assert (
        "master/detail"
        in report
    )

    assert (
        "refresh"
        in report
    )

def test_master_detail_relation_is_counted_in_inventory():
        report = _render(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

        assert (
            "| Relationships | 1 |"
            in report
        )


def test_form_without_relations_reports_zero_inventory():
    report = _render(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    assert (
        "| Relationships | 0 |"
        in report
    )
def test_master_detail_is_in_summary_migration_plan():
    model = parse_form_xml(
        GOLDEN_002
    )

    summary = build_assessment_summary(
        model,
        form_name="F2A_ORDERS_FORM",
    )

    assert (
        "MASTER_DETAIL_STRUCTURE"
        in summary.migration_stages
    )


def test_master_detail_is_rendered_in_migration_plan():
    report = _render(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    assert (
        "MASTER_DETAIL_STRUCTURE"
        in report
    )

    assert (
        "`APEX_MASTER_DETAIL`"
        in report
    )

    assert (
        "`APEX_FORM_OR_MASTER_REGION`"
        in report
    )

    assert (
        "`APEX_INTERACTIVE_GRID`"
        in report
    )

    assert (
        "`RELATION:ORDERS_ORDER_LINES`"
        in report
    )

    assert (
        "`BLOCK:ORDERS`"
        in report
    )

    assert (
        "`BLOCK:ORDER_LINES`"
        in report
    )