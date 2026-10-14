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
from f2a.generation.blueprint import (
    build_apex_blueprint,
)
from f2a.generation.sql_renderer import (
    SQL_RENDERER_MODE,
    SQL_RENDERER_VERSION,
    generate_apex_sql_scaffold_file,
    render_apex_sql_scaffold,
)
from f2a.parser.xml_parser import (
    parse_form_xml,
)
from f2a.reporting.assessment import (
    build_assessment_summary,
)
from f2a.rules.analyzer import (
    analyze_form,
)


GOLDEN_001 = Path(
    "samples/golden_001/fixtures/"
    "f2a_customers_form.xml"
)

GOLDEN_002 = Path(
    "samples/golden_002/fixtures/"
    "f2a_orders_form.xml"
)


def _build_blueprint(
    fixture: Path,
    form_name: str,
):
    model = parse_form_xml(
        fixture
    )

    summary = build_assessment_summary(
        model,
        form_name=form_name,
    )

    graph = build_dependency_graph(
        model,
        form_name=form_name,
    )

    findings = analyze_form(
        model
    )

    relations = analyze_relations(
        model
    )

    migration_plan = build_migration_plan(
        graph,
        findings,
        relations,
    )

    return build_apex_blueprint(
        summary,
        migration_plan,
        model=model,
    )


def test_sql_renderer_contains_header():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    content = render_apex_sql_scaffold(
        blueprint
    )

    assert (
        "Forms2APEX Accelerator - "
        "APEX SQL Scaffold"
        in content
    )

    assert (
        f"SQL renderer version: "
        f"{SQL_RENDERER_VERSION}"
        in content
    )

    assert (
        f"Renderer mode: "
        f"{SQL_RENDERER_MODE}"
        in content
    )


def test_sql_renderer_contains_page_region_and_item():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    content = render_apex_sql_scaffold(
        blueprint
    )

    assert (
        "F2A|PAGE|"
        in content
    )

    assert (
        "name=F2A_CUSTOMERS_FORM"
        in content
    )

    assert (
        "source_block=CUSTOMERS"
        in content
    )

    assert (
        "source_item=CUSTOMER_ID"
        in content
    )

    assert (
        "component=APEX_NUMBER_FIELD"
        in content
    )


def test_sql_renderer_contains_lov_metadata():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    content = render_apex_sql_scaffold(
        blueprint
    )

    assert "F2A|LOV|" in content
    assert "name=LOV_STATUS" in content

    assert (
        "component=APEX_STATIC_LOV"
        in content
    )

    assert (
        "return_value=ACTIVE"
        in content
    )

    assert (
        "return_value=INACTIVE"
        in content
    )


def test_sql_renderer_contains_relationship():
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    content = render_apex_sql_scaffold(
        blueprint
    )

    assert (
        "F2A|RELATIONSHIP|"
        in content
    )

    assert (
        "name=ORDERS_ORDER_LINES"
        in content
    )

    assert (
        "component=APEX_MASTER_DETAIL"
        in content
    )


def test_sql_renderer_generates_file(
    tmp_path,
):
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    output_path = (
        generate_apex_sql_scaffold_file(
            blueprint,
            root_dir=tmp_path,
        )
    )

    assert output_path.exists()

    assert (
        output_path
        == (
            tmp_path
            / "sql"
            / "F2A_ORDERS_FORM_scaffold.sql"
        )
    )