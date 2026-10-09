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
        == "1.4"
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

def test_customers_blueprint_contains_all_items():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    page = blueprint.pages[0]

    item_count = sum(
        len(region.items)
        for region in page.regions
    )

    assert item_count == 7


def test_customer_id_maps_to_number_field():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    customers_region = next(
        region
        for region in blueprint.pages[0].regions
        if region.source_block == "CUSTOMERS"
    )

    customer_id = next(
        item
        for item in customers_region.items
        if item.source_item == "CUSTOMER_ID"
    )

    assert (
        customer_id.component
        == "APEX_NUMBER_FIELD"
    )

    assert customer_id.database_item is True

    assert (
        customer_id.column_name
        == "CUSTOMER_ID"
    )

    assert customer_id.required is True


def test_status_maps_to_select_list_with_lov():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    customers_region = next(
        region
        for region in blueprint.pages[0].regions
        if region.source_block == "CUSTOMERS"
    )

    status = next(
        item
        for item in customers_region.items
        if item.source_item == "STATUS"
    )

    assert (
        status.component
        == "APEX_SELECT_LIST"
    )

    assert status.lov_name == "LOV_STATUS"


def test_save_button_maps_to_apex_button():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    control_region = next(
        region
        for region in blueprint.pages[0].regions
        if region.source_block == "CONTROL"
    )

    save_button = next(
        item
        for item in control_region.items
        if item.source_item == "BTN_SAVE"
    )

    assert (
        save_button.component
        == "APEX_BUTTON"
    )

    assert save_button.database_item is False
    assert save_button.required is False


def test_blueprint_json_contains_item_metadata():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    parsed = json.loads(
        render_apex_blueprint_json(
            blueprint
        )
    )

    assert (
        parsed["schema_version"]
        == "1.4"
    )

    customers_region = next(
        region
        for region
        in parsed["pages"][0]["regions"]
        if (
            region["source_block"]
            == "CUSTOMERS"
        )
    )

    customer_id = next(
        item
        for item
        in customers_region["items"]
        if (
            item["source_item"]
            == "CUSTOMER_ID"
        )
    )

    assert (
        customer_id["component"]
        == "APEX_NUMBER_FIELD"
    )

    assert (
        customer_id["database_item"]
        is True
    )

    assert customer_id["required"] is True

def test_customers_blueprint_contains_lov():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    assert len(blueprint.lovs) == 1

    lov = blueprint.lovs[0]

    assert lov.name == "LOV_STATUS"
    assert lov.lov_type == "STATIC"

    assert (
        lov.component
        == "APEX_STATIC_LOV"
    )


def test_status_lov_contains_values():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    lov = next(
        lov
        for lov in blueprint.lovs
        if lov.name == "LOV_STATUS"
    )

    assert len(lov.values) == 2

    return_values = {
        value.return_value
        for value in lov.values
    }

    assert return_values == {
        "ACTIVE",
        "INACTIVE",
    }


def test_status_lov_preserves_value_order():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    lov = next(
        lov
        for lov in blueprint.lovs
        if lov.name == "LOV_STATUS"
    )

    assert tuple(
        value.display_order
        for value in lov.values
    ) == (
        1,
        2,
    )


def test_item_lov_reference_matches_blueprint_lov():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    customers_region = next(
        region
        for region in blueprint.pages[0].regions
        if region.source_block == "CUSTOMERS"
    )

    status = next(
        item
        for item in customers_region.items
        if item.source_item == "STATUS"
    )

    lov_names = {
        lov.name
        for lov in blueprint.lovs
    }

    assert status.lov_name in lov_names


def test_blueprint_json_contains_lov_definition():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    parsed = json.loads(
        render_apex_blueprint_json(
            blueprint
        )
    )

    assert (
        parsed["schema_version"]
        == "1.4"
    )

    assert len(parsed["lovs"]) == 1

    lov = parsed["lovs"][0]

    assert lov["name"] == "LOV_STATUS"

    assert (
        lov["component"]
        == "APEX_STATIC_LOV"
    )

    assert len(lov["values"]) == 2

    assert (
        lov["values"][0]["return_value"]
        == "ACTIVE"
    )

    assert (
        lov["values"][1]["return_value"]
        == "INACTIVE"
    )

def test_customers_blueprint_has_no_relationship_definitions():
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    assert blueprint.relationships == ()


def test_orders_blueprint_contains_relationship_definition():
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    assert len(blueprint.relationships) == 1

    relationship = (
        blueprint.relationships[0]
    )

    assert (
        relationship.name
        == "ORDERS_ORDER_LINES"
    )

    assert (
        relationship.relation_type
        == "MASTER_DETAIL"
    )

    assert (
        relationship.component
        == "APEX_MASTER_DETAIL"
    )


def test_orders_relationship_preserves_blocks():
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    relationship = (
        blueprint.relationships[0]
    )

    assert (
        relationship.master_block
        == "ORDERS"
    )

    assert (
        relationship.detail_block
        == "ORDER_LINES"
    )


def test_orders_relationship_preserves_source_items():
    model = parse_form_xml(
        GOLDEN_002
    )

    source_relation = (
        model.relations[0]
    )

    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    relationship = (
        blueprint.relationships[0]
    )

    assert (
        relationship.master_item
        == source_relation.master_item
    )

    assert (
        relationship.detail_item
        == source_relation.detail_item
    )

    assert (
        relationship.synchronization
        == "DETAIL_REFRESH_ON_MASTER_CHANGE"
    )


def test_blueprint_json_contains_relationship_contract():
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    parsed = json.loads(
        render_apex_blueprint_json(
            blueprint
        )
    )

    assert (
        parsed["schema_version"]
        == "1.4"
    )

    assert (
        len(parsed["relationships"])
        == 1
    )

    relationship = (
        parsed["relationships"][0]
    )

    assert (
        relationship["name"]
        == "ORDERS_ORDER_LINES"
    )

    assert (
        relationship["component"]
        == "APEX_MASTER_DETAIL"
    )

    assert (
        relationship["synchronization"]
        == "DETAIL_REFRESH_ON_MASTER_CHANGE"
    )