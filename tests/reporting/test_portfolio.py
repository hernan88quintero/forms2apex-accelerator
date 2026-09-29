from pathlib import Path

from f2a.parser.xml_parser import parse_form_xml
from f2a.reporting.assessment import (
    build_assessment_summary,
)
from f2a.reporting.portfolio import (
    build_portfolio_summary,
    generate_portfolio_file,
    render_portfolio_markdown,
)


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)

GOLDEN_002 = Path(
    "samples/golden_002/fixtures/f2a_orders_form.xml"
)

def get_relation_summaries():

    customers_model = parse_form_xml(
        FIXTURE
    )

    orders_model = parse_form_xml(
        GOLDEN_002
    )

    customers = build_assessment_summary(
        customers_model,
        form_name="F2A_CUSTOMERS_FORM",
    )

    orders = build_assessment_summary(
        orders_model,
        form_name="F2A_ORDERS_FORM",
    )

    return (
        customers,
        orders,
    )

def get_summaries():
    model = parse_form_xml(
        FIXTURE
    )

    customers = build_assessment_summary(
        model,
        form_name="CUSTOMERS",
    )

    orders = build_assessment_summary(
        model,
        form_name="ORDERS",
    )

    return (
        customers,
        orders,
    )


def test_portfolio_totals():
    portfolio = build_portfolio_summary(
        get_summaries(),
        total_files=2,
        failed_forms=0,
    )

    assert portfolio.total_files == 2
    assert portfolio.successful_forms == 2
    assert portfolio.failed_forms == 0

    assert portfolio.total_findings == 10
    assert portfolio.total_builtins == 8
    assert portfolio.total_behaviors == 6
    assert portfolio.total_effort == 18


def test_portfolio_distributions():
    portfolio = build_portfolio_summary(
        get_summaries(),
        total_files=2,
        failed_forms=0,
    )

    assert portfolio.complexity_summary == (
        ("MEDIUM", 2),
    )

    assert portfolio.risk_summary == (
        ("HIGH", 2),
    )

    assert portfolio.classification_summary == (
        ("ASSISTED_MIGRATION", 2),
    )


def test_portfolio_markdown_contains_forms():
    portfolio = build_portfolio_summary(
        get_summaries(),
        total_files=2,
        failed_forms=0,
    )

    report = render_portfolio_markdown(
        portfolio
    )

    assert (
        "# Forms2APEX Portfolio Assessment"
        in report
    )

    assert "CUSTOMERS" in report
    assert "ORDERS" in report

    assert (
        "| Total Effort Points | 18 |"
        in report
    )


def test_generate_portfolio_file(
    tmp_path,
):
    output_path = generate_portfolio_file(
        get_summaries(),
        total_files=2,
        failed_forms=0,
        output_dir=tmp_path,
    )

    assert output_path.exists()

    assert (
        output_path.name
        == "F2A_PORTFOLIO_SUMMARY.md"
    )

    content = output_path.read_text(
        encoding="utf-8"
    )

    assert "CUSTOMERS" in content
    assert "ORDERS" in content

def test_portfolio_migration_waves():
    portfolio = build_portfolio_summary(
        get_summaries(),
        total_files=2,
        failed_forms=0,
    )

    assert portfolio.migration_waves == (
        ("CUSTOMERS", "WAVE_3"),
        ("ORDERS", "WAVE_3"),
    )

def test_portfolio_markdown_contains_waves():
    portfolio = build_portfolio_summary(
        get_summaries(),
        total_files=2,
        failed_forms=0,
    )

    report = render_portfolio_markdown(
        portfolio
    )

    assert (
        "## Suggested Migration Waves"
        in report
    )

    assert (
        "| CUSTOMERS | WAVE_3 |"
        in report
    )

    assert (
        "| ORDERS | WAVE_3 |"
        in report
    )

def test_portfolio_relationship_totals():
    portfolio = build_portfolio_summary(
        get_relation_summaries(),
        total_files=2,
        failed_forms=0,
    )

    assert (
        portfolio.forms_with_relationships
        == 1
    )

    assert (
        portfolio.master_detail_forms
        == 1
    )

    assert (
        portfolio.total_relationships
        == 1
    )


def test_portfolio_markdown_contains_relationship_metrics():
    portfolio = build_portfolio_summary(
        get_relation_summaries(),
        total_files=2,
        failed_forms=0,
    )

    report = render_portfolio_markdown(
        portfolio
    )

    assert (
        "| Forms with Relationships | 1 |"
        in report
    )

    assert (
        "| Master/Detail Forms | 1 |"
        in report
    )

    assert (
        "| Total Relationships | 1 |"
        in report
    )


def test_portfolio_forms_table_contains_relation_counts():
    portfolio = build_portfolio_summary(
        get_relation_summaries(),
        total_files=2,
        failed_forms=0,
    )

    report = render_portfolio_markdown(
        portfolio
    )

    lines = report.splitlines()

    customers_row = next(
        line
        for line in lines
        if line.startswith(
            "| F2A_CUSTOMERS_FORM "
        )
    )

    orders_row = next(
        line
        for line in lines
        if line.startswith(
            "| F2A_ORDERS_FORM "
        )
    )

    customers_cells = [
        cell.strip()
        for cell in customers_row
        .strip("|")
        .split("|")
    ]

    orders_cells = [
        cell.strip()
        for cell in orders_row
        .strip("|")
        .split("|")
    ]

    # Column 4 = Relationships
    assert customers_cells[4] == "0"
    assert orders_cells[4] == "1"


def test_portfolio_forms_are_rendered_before_waves():
    portfolio = build_portfolio_summary(
        get_relation_summaries(),
        total_files=2,
        failed_forms=0,
    )

    report = render_portfolio_markdown(
        portfolio
    )

    forms_position = report.index(
        "## Forms"
    )

    customers_position = report.index(
        "| F2A_CUSTOMERS_FORM "
    )

    waves_position = report.index(
        "## Suggested Migration Waves"
    )

    assert (
        forms_position
        < customers_position
        < waves_position
    )