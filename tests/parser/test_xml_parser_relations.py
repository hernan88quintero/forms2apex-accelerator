from pathlib import Path

from f2a.parser.xml_parser import (
    parse_form_xml,
)


GOLDEN_001 = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)

GOLDEN_002 = Path(
    "samples/golden_002/fixtures/f2a_orders_form.xml"
)


def test_golden_001_has_no_relations():
    model = parse_form_xml(
        GOLDEN_001
    )

    assert model.relations == []


def test_golden_002_contains_master_detail_relation():
    model = parse_form_xml(
        GOLDEN_002
    )

    assert len(
        model.relations
    ) == 1

    relation = model.relations[0]

    assert (
        relation.name
        == "ORDERS_ORDER_LINES"
    )

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

    assert (
        relation.relation_type
        == "MASTER_DETAIL"
    )


def test_relation_references_existing_blocks():
    model = parse_form_xml(
        GOLDEN_002
    )

    relation = model.relations[0]

    block_names = {
        block.name
        for block in model.blocks
    }

    assert (
        relation.master_block
        in block_names
    )

    assert (
        relation.detail_block
        in block_names
    )


def test_relation_references_existing_items():
    model = parse_form_xml(
        GOLDEN_002
    )

    relation = model.relations[0]

    master = next(
        block
        for block in model.blocks
        if (
            block.name
            == relation.master_block
        )
    )

    detail = next(
        block
        for block in model.blocks
        if (
            block.name
            == relation.detail_block
        )
    )

    master_items = {
        item.name
        for item in master.items
    }

    detail_items = {
        item.name
        for item in detail.items
    }

    assert (
        relation.master_item
        in master_items
    )

    assert (
        relation.detail_item
        in detail_items
    )