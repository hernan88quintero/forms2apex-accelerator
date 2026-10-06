from pathlib import Path

from f2a.analysis.dependencies import (
    build_dependency_graph,
)
from f2a.analysis.planner import (
    build_migration_plan,
)
from f2a.analysis.relations import (
    analyze_relations,
)
from f2a.parser.xml_parser import parse_form_xml
from f2a.rules.analyzer import analyze_form


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)

GOLDEN_002 = Path(
    "samples/golden_002/fixtures/f2a_orders_form.xml"
)

def get_relation_plan():
    model = parse_form_xml(
        GOLDEN_002
    )

    graph = build_dependency_graph(
        model,
        form_name="F2A_ORDERS_FORM",
    )

    findings = analyze_form(
        model
    )

    relations = analyze_relations(
        model
    )

    return build_migration_plan(
        graph,
        findings,
        relations,
    )


def get_plan():
    model = parse_form_xml(FIXTURE)

    graph = build_dependency_graph(
        model,
        form_name="F2A_CUSTOMERS_FORM",
    )

    findings = analyze_form(model)

    return build_migration_plan(
        graph,
        findings,
    )


def test_migration_plan_has_expected_stages():
    plan = get_plan()

    stages = tuple(
        step.stage
        for step in plan
    )

    assert stages == (
        "REUSABLE_LOGIC",
        "PAGE_STRUCTURE",
        "QUERY_ENRICHMENT",
        "VALIDATIONS",
        "DML_AND_PAGE_PROCESSES",
        "PAGE_INITIALIZATION",
    )


def test_migration_plan_order_is_sequential():
    plan = get_plan()

    assert tuple(
        step.order
        for step in plan
    ) == (
        1,
        2,
        3,
        4,
        5,
        6,
    )


def test_reusable_logic_is_first():
    plan = get_plan()

    step = plan[0]

    assert step.stage == "REUSABLE_LOGIC"

    assert step.apex_components == (
        "DATABASE_OR_SHARED_PLSQL",
    )

    assert (
        "PROGRAM_UNIT:VALIDATE_EMAIL"
        in step.source_objects
    )

    assert (
        "PROGRAM_UNIT:SAVE_CUSTOMER"
        in step.source_objects
    )


def test_page_structure_contains_blocks_and_items():
    plan = get_plan()

    step = next(
        item
        for item in plan
        if item.stage == "PAGE_STRUCTURE"
    )

    assert (
        "BLOCK:CUSTOMERS"
        in step.source_objects
    )

    assert (
        "BLOCK:CONTROL"
        in step.source_objects
    )

    assert (
        "ITEM:CUSTOMERS.EMAIL"
        in step.source_objects
    )

    assert (
        "ITEM:CONTROL.BTN_SAVE"
        in step.source_objects
    )


def test_validation_step_contains_email_validation():
    plan = get_plan()

    step = next(
        item
        for item in plan
        if item.stage == "VALIDATIONS"
    )

    assert step.apex_components == (
        "APEX_VALIDATION",
    )

    assert (
        "CUSTOMERS.EMAIL::WHEN-VALIDATE-ITEM"
        in step.source_objects
    )


def test_process_step_contains_save_button_and_pre_insert():
    plan = get_plan()

    step = next(
        item
        for item in plan
        if (
            item.stage
            == "DML_AND_PAGE_PROCESSES"
        )
    )

    assert (
        "CONTROL.BTN_SAVE::WHEN-BUTTON-PRESSED"
        in step.source_objects
    )

    assert (
        "CUSTOMERS::PRE-INSERT"
        in step.source_objects
    )


def test_initialization_step_contains_form_trigger():
    plan = get_plan()

    step = next(
        item
        for item in plan
        if (
            item.stage
            == "PAGE_INITIALIZATION"
        )
    )

    assert (
        "FORM::WHEN-NEW-FORM-INSTANCE"
        in step.source_objects
    )


def test_golden_sample_has_no_dynamic_action_stage():
    plan = get_plan()

    stages = {
        step.stage
        for step in plan
    }

    assert "DYNAMIC_ACTIONS" not in stages
    assert "NAVIGATION" not in stages

def test_master_detail_plan_contains_structure_stage():
    plan = get_relation_plan()

    stages = tuple(
        step.stage
        for step in plan
    )

    assert (
        "MASTER_DETAIL_STRUCTURE"
        in stages
    )


def test_master_detail_stage_follows_page_structure():
    plan = get_relation_plan()

    stages = [
        step.stage
        for step in plan
    ]

    page_index = stages.index(
        "PAGE_STRUCTURE"
    )

    relation_index = stages.index(
        "MASTER_DETAIL_STRUCTURE"
    )

    assert (
        relation_index
        == page_index + 1
    )


def test_master_detail_stage_contains_apex_components():
    plan = get_relation_plan()

    step = next(
        item
        for item in plan
        if (
            item.stage
            == "MASTER_DETAIL_STRUCTURE"
        )
    )

    assert step.apex_components == (
        "APEX_MASTER_DETAIL",
        "APEX_FORM_OR_MASTER_REGION",
        "APEX_INTERACTIVE_GRID",
    )


def test_master_detail_stage_contains_source_objects():
    plan = get_relation_plan()

    step = next(
        item
        for item in plan
        if (
            item.stage
            == "MASTER_DETAIL_STRUCTURE"
        )
    )

    assert (
        "RELATION:ORDERS_ORDER_LINES"
        in step.source_objects
    )

    assert (
        "BLOCK:ORDERS"
        in step.source_objects
    )

    assert (
        "BLOCK:ORDER_LINES"
        in step.source_objects
    )


def test_master_detail_plan_order_is_sequential():
    plan = get_relation_plan()

    assert tuple(
        step.order
        for step in plan
    ) == tuple(
        range(
            1,
            len(plan) + 1,
        )
    )