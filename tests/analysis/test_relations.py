from pathlib import Path

from f2a.analysis.relations import (
    analyze_relations,
)
from f2a.parser.xml_parser import (
    parse_form_xml,
)


GOLDEN_001 = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)

GOLDEN_002 = Path(
    "samples/golden_002/fixtures/f2a_orders_form.xml"
)


def test_form_without_relations_produces_no_advice():
    model = parse_form_xml(
        GOLDEN_001
    )

    advice = analyze_relations(
        model
    )

    assert advice == ()


def test_master_detail_relation_is_detected():
    model = parse_form_xml(
        GOLDEN_002
    )

    advice = analyze_relations(
        model
    )

    assert len(advice) == 1

    relation = advice[0]

    assert (
        relation.relation_name
        == "ORDERS_ORDER_LINES"
    )

    assert (
        relation.relation_type
        == "MASTER_DETAIL"
    )


def test_master_detail_source_objects():
    model = parse_form_xml(
        GOLDEN_002
    )

    relation = analyze_relations(
        model
    )[0]

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


def test_master_detail_apex_mapping():
    model = parse_form_xml(
        GOLDEN_002
    )

    relation = analyze_relations(
        model
    )[0]

    assert (
        relation.apex_pattern
        == "APEX_MASTER_DETAIL"
    )

    assert (
        relation.master_component
        == "APEX_FORM_OR_MASTER_REGION"
    )

    assert (
        relation.detail_component
        == "APEX_INTERACTIVE_GRID"
    )

    assert (
        relation.synchronization
        == "DETAIL_REFRESH_ON_MASTER_CHANGE"
    )


def test_master_detail_migration_guidance():
    model = parse_form_xml(
        GOLDEN_002
    )

    relation = analyze_relations(
        model
    )[0]

    assert (
        relation.automation_level
        == "ASSISTED"
    )

    assert (
        relation.complexity
        == "MEDIUM"
    )

    assert (
        relation.risk
        == "MEDIUM"
    )

    assert (
        "master/detail"
        in relation.rationale
    )

    assert (
        "refresh"
        in relation.rationale
    )