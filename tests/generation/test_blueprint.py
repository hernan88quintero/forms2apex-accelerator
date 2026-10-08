import json
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
    BLUEPRINT_SCHEMA_VERSION,
    build_apex_blueprint,
    generate_apex_blueprint_file,
    render_apex_blueprint_json,
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
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)

GOLDEN_002 = Path(
    "samples/golden_002/fixtures/f2a_orders_form.xml"
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


def test_customers_blueprint_has_no_relationships():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    assert (
        blueprint.schema_version
        == BLUEPRINT_SCHEMA_VERSION
    )

    assert (
        blueprint.form_name
        == "F2A_CUSTOMERS_FORM"
    )

    assert blueprint.relation_count == 0

    assert (
        blueprint.master_detail_relation_count
        == 0
    )

    stages = {
        stage.stage
        for stage in blueprint.stages
    }

    assert (
        "MASTER_DETAIL_STRUCTURE"
        not in stages
    )


def test_orders_blueprint_contains_master_detail_metadata():
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    assert blueprint.relation_count == 1

    assert (
        blueprint.master_detail_relation_count
        == 1
    )

    assert (
        blueprint.assessment_classification
        == "ASSISTED_MIGRATION"
    )


def test_orders_blueprint_contains_master_detail_stage():
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    stage = next(
        stage
        for stage in blueprint.stages
        if (
            stage.stage
            == "MASTER_DETAIL_STRUCTURE"
        )
    )

    assert (
        "APEX_MASTER_DETAIL"
        in stage.apex_components
    )

    assert (
        "APEX_FORM_OR_MASTER_REGION"
        in stage.apex_components
    )

    assert (
        "APEX_INTERACTIVE_GRID"
        in stage.apex_components
    )

    assert (
        "RELATION:ORDERS_ORDER_LINES"
        in stage.source_objects
    )


def test_blueprint_can_be_rendered_as_json():
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    content = render_apex_blueprint_json(
        blueprint
    )

    parsed = json.loads(
        content
    )

    assert (
        parsed["schema_version"]
        == "1.1"
    )

    assert (
        parsed["form_name"]
        == "F2A_ORDERS_FORM"
    )

    assert (
        parsed[
            "master_detail_relation_count"
        ]
        == 1
    )

    stages = {
        stage["stage"]
        for stage in parsed["stages"]
    }

    assert (
        "MASTER_DETAIL_STRUCTURE"
        in stages
    )


def test_blueprint_file_is_generated(
    tmp_path,
):
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    output_path = (
        generate_apex_blueprint_file(
            blueprint,
            output_dir=tmp_path,
        )
    )

    assert output_path.exists()

    assert (
        output_path.name
        == "F2A_ORDERS_FORM_blueprint.json"
    )

    content = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        content["form_name"]
        == "F2A_ORDERS_FORM"
    )

    assert (
        content["relation_count"]
        == 1
    )

def test_customers_blueprint_contains_page():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    assert len(blueprint.pages) == 1

    page = blueprint.pages[0]

    assert (
        page.name
        == "F2A_CUSTOMERS_FORM"
    )

    assert (
        page.page_type
        == "APEX_STANDARD_PAGE"
    )


def test_customers_blueprint_contains_regions():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    page = blueprint.pages[0]

    source_blocks = {
        region.source_block
        for region in page.regions
    }

    assert "CUSTOMERS" in source_blocks
    assert "CONTROL" in source_blocks


def test_orders_blueprint_is_master_detail_page():
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    page = blueprint.pages[0]

    assert (
        page.page_type
        == "APEX_MASTER_DETAIL_PAGE"
    )


def test_orders_blueprint_maps_master_detail_regions():
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    page = blueprint.pages[0]

    master = next(
        region
        for region in page.regions
        if region.source_block == "ORDERS"
    )

    detail = next(
        region
        for region in page.regions
        if (
            region.source_block
            == "ORDER_LINES"
        )
    )

    assert (
        master.component
        == "APEX_FORM_OR_MASTER_REGION"
    )

    assert master.relation_role == "MASTER"

    assert (
        master.relation_name
        == "ORDERS_ORDER_LINES"
    )

    assert (
        detail.component
        == "APEX_INTERACTIVE_GRID"
    )

    assert detail.relation_role == "DETAIL"

    assert (
        detail.relation_name
        == "ORDERS_ORDER_LINES"
    )


def test_blueprint_json_contains_pages_and_regions():
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    parsed = json.loads(
        render_apex_blueprint_json(
            blueprint
        )
    )

    assert len(parsed["pages"]) == 1

    page = parsed["pages"][0]

    assert (
        page["page_type"]
        == "APEX_MASTER_DETAIL_PAGE"
    )

    assert (
        len(page["regions"])
        >= 2
    )

    region_components = {
        region["component"]
        for region in page["regions"]
    }

    assert (
        "APEX_FORM_OR_MASTER_REGION"
        in region_components
    )

    assert (
        "APEX_INTERACTIVE_GRID"
        in region_components
    )