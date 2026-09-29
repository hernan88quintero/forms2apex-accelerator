from pathlib import Path

from f2a.parser.xml_parser import parse_form_xml
from f2a.reporting.assessment import (
    render_assessment_markdown,
)


FIXTURE = Path(
    "samples/golden_002/fixtures/f2a_orders_form.xml"
)


def get_model():
    return parse_form_xml(
        FIXTURE
    )


def test_golden_002_fixture_exists():
    assert FIXTURE.exists()


def test_golden_002_parses():
    model = get_model()

    block_names = {
        block.name
        for block in model.blocks
    }

    assert "ORDERS" in block_names
    assert "ORDER_LINES" in block_names
    assert "CONTROL" in block_names


def test_golden_002_contains_master_and_detail_items():
    model = get_model()

    orders = next(
        block
        for block in model.blocks
        if block.name == "ORDERS"
    )

    order_lines = next(
        block
        for block in model.blocks
        if block.name == "ORDER_LINES"
    )

    order_item_names = {
        item.name
        for item in orders.items
    }

    line_item_names = {
        item.name
        for item in order_lines.items
    }

    assert "ORDER_ID" in order_item_names
    assert "CUSTOMER_ID" in order_item_names
    assert "ORDER_DATE" in order_item_names

    assert "LINE_ID" in line_item_names
    assert "ORDER_ID" in line_item_names
    assert "PRODUCT_ID" in line_item_names
    assert "QUANTITY" in line_item_names


def test_golden_002_contains_distinct_lovs():
    model = get_model()

    lov_names = {
        lov.name
        for lov in model.lovs
    }

    assert "LOV_ORDER_STATUS" in lov_names
    assert "LOV_LINE_STATUS" in lov_names


def test_golden_002_contains_program_units():
    model = get_model()

    unit_names = {
        unit.name
        for unit in model.program_units
    }

    assert "VALIDATE_ORDER" in unit_names
    assert "SAVE_ORDER" in unit_names


def test_golden_002_generates_assessment():
    model = get_model()

    report = render_assessment_markdown(
        model,
        form_name="F2A_ORDERS_FORM",
    )

    assert (
        "# Forms2APEX Migration Assessment"
        in report
    )

    assert "F2A_ORDERS_FORM" in report
    assert "ORDERS" in report
    assert "ORDER_LINES" in report

    assert (
        "## Suggested Migration Plan"
        in report
    )

def test_golden_002_contains_master_detail_relation():
    model = get_model()

    assert len(
        model.relations
    ) == 1

    relation = model.relations[0]

    assert (
        relation.master_block
        == "ORDERS"
    )

    assert (
        relation.detail_block
        == "ORDER_LINES"
    )

    assert (
        relation.master_item
        == "ORDER_ID"
    )

    assert (
        relation.detail_item
        == "ORDER_ID"
    )