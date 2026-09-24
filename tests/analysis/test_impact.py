from pathlib import Path

from f2a.analysis.dependencies import (
    build_dependency_graph,
)
from f2a.analysis.impact import analyze_impact
from f2a.parser.xml_parser import parse_form_xml


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)


def get_graph():
    model = parse_form_xml(FIXTURE)

    return build_dependency_graph(
        model,
        form_name="F2A_CUSTOMERS_FORM",
    )


def test_commit_form_impact_report():
    graph = get_graph()

    report = analyze_impact(
        graph,
        "BUILTIN:COMMIT_FORM",
    )

    assert report.target_node == "BUILTIN:COMMIT_FORM"

    assert report.direct_dependents == (
        "PROGRAM_UNIT:SAVE_CUSTOMER",
    )

    assert (
        "PROGRAM_UNIT:SAVE_CUSTOMER"
        in report.transitive_dependents
    )

    assert (
        "ITEM:CONTROL.BTN_SAVE"
        in report.transitive_dependents
    )

    assert (
        "BLOCK:CONTROL"
        in report.transitive_dependents
    )

    assert (
        "FORM:F2A_CUSTOMERS_FORM"
        in report.transitive_dependents
    )

    assert report.impact_scope == "FORM"


def test_commit_form_structured_impact():
    graph = get_graph()

    report = analyze_impact(
        graph,
        "BUILTIN:COMMIT_FORM",
    )

    assert report.affected_forms == (
        "FORM:F2A_CUSTOMERS_FORM",
    )

    assert report.affected_blocks == (
        "BLOCK:CONTROL",
    )

    assert report.affected_items == (
        "ITEM:CONTROL.BTN_SAVE",
    )

    assert report.affected_program_units == (
        "PROGRAM_UNIT:SAVE_CUSTOMER",
    )

    assert len(
        report.affected_triggers
    ) == 1

    assert (
        "TRIGGER:ITEM:"
        "CONTROL.BTN_SAVE:"
        "WHEN-BUTTON-PRESSED"
        in report.affected_triggers
    )


def test_validation_failure_impact():
    graph = get_graph()

    report = analyze_impact(
        graph,
        "BUILTIN:FORM_TRIGGER_FAILURE",
    )

    assert report.affected_program_units == (
        "PROGRAM_UNIT:VALIDATE_EMAIL",
    )

    assert report.affected_items == (
        "ITEM:CUSTOMERS.EMAIL",
    )

    assert report.affected_blocks == (
        "BLOCK:CUSTOMERS",
    )

    assert report.affected_forms == (
        "FORM:F2A_CUSTOMERS_FORM",
    )

    assert report.impact_scope == "FORM"


def test_go_block_impact():
    graph = get_graph()

    report = analyze_impact(
        graph,
        "BUILTIN:GO_BLOCK",
    )

    assert report.direct_dependents == (
        (
            "TRIGGER:FORM:"
            "F2A_CUSTOMERS_FORM:"
            "WHEN-NEW-FORM-INSTANCE"
        ),
    )

    assert report.affected_forms == (
        "FORM:F2A_CUSTOMERS_FORM",
    )

    assert report.affected_blocks == ()
    assert report.affected_items == ()
    assert report.affected_program_units == ()

    assert report.impact_scope == "FORM"


def test_unreferenced_node_has_local_impact():
    graph = get_graph()

    report = analyze_impact(
        graph,
        "BUILTIN:SOMETHING_UNUSED",
    )

    assert report.direct_dependents == ()
    assert report.transitive_dependents == ()

    assert report.affected_forms == ()
    assert report.affected_blocks == ()
    assert report.affected_items == ()
    assert report.affected_triggers == ()
    assert report.affected_program_units == ()

    assert report.impact_scope == "LOCAL"