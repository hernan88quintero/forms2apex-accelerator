from pathlib import Path

from f2a.analysis.dependencies import (
    build_dependency_graph,
)
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


def test_dependency_graph_node_counts():
    graph = get_graph()

    assert len(
        graph.nodes_by_type("FORM")
    ) == 1

    assert len(
        graph.nodes_by_type("BLOCK")
    ) == 2

    assert len(
        graph.nodes_by_type("ITEM")
    ) == 7

    assert len(
        graph.nodes_by_type("TRIGGER")
    ) == 5

    assert len(
        graph.nodes_by_type("PROGRAM_UNIT")
    ) == 2

    assert len(
        graph.nodes_by_type("BUILTIN")
    ) == 4


def test_form_contains_blocks():
    graph = get_graph()

    assert graph.has_edge(
        "FORM:F2A_CUSTOMERS_FORM",
        "BLOCK:CUSTOMERS",
        "CONTAINS",
    )

    assert graph.has_edge(
        "FORM:F2A_CUSTOMERS_FORM",
        "BLOCK:CONTROL",
        "CONTAINS",
    )


def test_block_contains_items():
    graph = get_graph()

    assert graph.has_edge(
        "BLOCK:CUSTOMERS",
        "ITEM:CUSTOMERS.EMAIL",
        "CONTAINS",
    )

    assert graph.has_edge(
        "BLOCK:CONTROL",
        "ITEM:CONTROL.BTN_SAVE",
        "CONTAINS",
    )


def test_validate_email_dependency_chain():
    graph = get_graph()

    trigger_id = (
        "TRIGGER:ITEM:"
        "CUSTOMERS.EMAIL:"
        "WHEN-VALIDATE-ITEM"
    )

    assert graph.has_edge(
        "ITEM:CUSTOMERS.EMAIL",
        trigger_id,
        "HAS_TRIGGER",
    )

    assert graph.has_edge(
        trigger_id,
        "PROGRAM_UNIT:VALIDATE_EMAIL",
        "CALLS_PROGRAM_UNIT",
    )

    assert graph.has_edge(
        "PROGRAM_UNIT:VALIDATE_EMAIL",
        "BUILTIN:FORM_TRIGGER_FAILURE",
        "USES_BUILTIN",
    )


def test_save_customer_dependency_chain():
    graph = get_graph()

    trigger_id = (
        "TRIGGER:ITEM:"
        "CONTROL.BTN_SAVE:"
        "WHEN-BUTTON-PRESSED"
    )

    assert graph.has_edge(
        "ITEM:CONTROL.BTN_SAVE",
        trigger_id,
        "HAS_TRIGGER",
    )

    assert graph.has_edge(
        trigger_id,
        "PROGRAM_UNIT:SAVE_CUSTOMER",
        "CALLS_PROGRAM_UNIT",
    )

    assert graph.has_edge(
        "PROGRAM_UNIT:SAVE_CUSTOMER",
        "BUILTIN:COMMIT_FORM",
        "USES_BUILTIN",
    )


def test_form_trigger_uses_query_builtins():
    graph = get_graph()

    trigger_id = (
        "TRIGGER:FORM:"
        "F2A_CUSTOMERS_FORM:"
        "WHEN-NEW-FORM-INSTANCE"
    )

    assert graph.has_edge(
        "FORM:F2A_CUSTOMERS_FORM",
        trigger_id,
        "HAS_TRIGGER",
    )

    assert graph.has_edge(
        trigger_id,
        "BUILTIN:GO_BLOCK",
        "USES_BUILTIN",
    )

    assert graph.has_edge(
        trigger_id,
        "BUILTIN:EXECUTE_QUERY",
        "USES_BUILTIN",
    )


def test_dependency_graph_total_size():
    graph = get_graph()

    assert len(graph.nodes) == 21
    assert len(graph.edges) == 20

def test_find_validation_dependency_path():
    graph = get_graph()

    path = graph.find_path(
        "ITEM:CUSTOMERS.EMAIL",
        "BUILTIN:FORM_TRIGGER_FAILURE",
    )

    assert path == (
        "ITEM:CUSTOMERS.EMAIL",
        (
            "TRIGGER:ITEM:"
            "CUSTOMERS.EMAIL:"
            "WHEN-VALIDATE-ITEM"
        ),
        "PROGRAM_UNIT:VALIDATE_EMAIL",
        "BUILTIN:FORM_TRIGGER_FAILURE",
    )


def test_find_save_dependency_path():
    graph = get_graph()

    path = graph.find_path(
        "ITEM:CONTROL.BTN_SAVE",
        "BUILTIN:COMMIT_FORM",
    )

    assert path == (
        "ITEM:CONTROL.BTN_SAVE",
        (
            "TRIGGER:ITEM:"
            "CONTROL.BTN_SAVE:"
            "WHEN-BUTTON-PRESSED"
        ),
        "PROGRAM_UNIT:SAVE_CUSTOMER",
        "BUILTIN:COMMIT_FORM",
    )


def test_reachable_from_save_button():
    graph = get_graph()

    reachable = set(
        graph.reachable_from(
            "ITEM:CONTROL.BTN_SAVE"
        )
    )

    assert (
        "TRIGGER:ITEM:"
        "CONTROL.BTN_SAVE:"
        "WHEN-BUTTON-PRESSED"
    ) in reachable

    assert (
        "PROGRAM_UNIT:SAVE_CUSTOMER"
        in reachable
    )

    assert (
        "BUILTIN:COMMIT_FORM"
        in reachable
    )


def test_commit_form_impact():
    graph = get_graph()

    dependents = set(
        graph.dependents_of(
            "BUILTIN:COMMIT_FORM"
        )
    )

    assert (
        "PROGRAM_UNIT:SAVE_CUSTOMER"
        in dependents
    )

    assert (
        "TRIGGER:ITEM:"
        "CONTROL.BTN_SAVE:"
        "WHEN-BUTTON-PRESSED"
    ) in dependents

    assert (
        "ITEM:CONTROL.BTN_SAVE"
        in dependents
    )

    assert (
        "BLOCK:CONTROL"
        in dependents
    )

    assert (
        "FORM:F2A_CUSTOMERS_FORM"
        in dependents
    )


def test_direct_dependencies():
    graph = get_graph()

    trigger_id = (
        "TRIGGER:FORM:"
        "F2A_CUSTOMERS_FORM:"
        "WHEN-NEW-FORM-INSTANCE"
    )

    dependencies = set(
        graph.direct_dependencies_of(
            trigger_id
        )
    )

    assert dependencies == {
        "BUILTIN:EXECUTE_QUERY",
        "BUILTIN:GO_BLOCK",
    }


def test_direct_dependents():
    graph = get_graph()

    dependents = graph.direct_dependents_of(
        "PROGRAM_UNIT:VALIDATE_EMAIL"
    )

    assert dependents == (
        (
            "TRIGGER:ITEM:"
            "CUSTOMERS.EMAIL:"
            "WHEN-VALIDATE-ITEM"
        ),
    )


def test_find_path_returns_none_when_unrelated():
    graph = get_graph()

    path = graph.find_path(
        "ITEM:CUSTOMERS.EMAIL",
        "BUILTIN:COMMIT_FORM",
    )

    assert path is None


def test_find_path_to_same_node():
    graph = get_graph()

    path = graph.find_path(
        "PROGRAM_UNIT:SAVE_CUSTOMER",
        "PROGRAM_UNIT:SAVE_CUSTOMER",
    )

    assert path == (
        "PROGRAM_UNIT:SAVE_CUSTOMER",
    )