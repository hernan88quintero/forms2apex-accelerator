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
from f2a.generation.artifacts import (
    ARTIFACT_SCHEMA_VERSION,
    generate_apex_artifact_bundle,
)
from f2a.generation.blueprint import (
    build_apex_blueprint,
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


def test_artifact_bundle_creates_manifest(
    tmp_path,
):
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    result = generate_apex_artifact_bundle(
        blueprint,
        output_dir=tmp_path,
    )

    assert result.root_dir.exists()
    assert result.manifest_path.exists()

    manifest = json.loads(
        result.manifest_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        manifest["artifact_schema_version"]
        == ARTIFACT_SCHEMA_VERSION
    )

    assert (
        manifest["form_name"]
        == "F2A_CUSTOMERS_FORM"
    )

    assert manifest["page_count"] == 1


def test_artifact_bundle_creates_page_spec(
    tmp_path,
):
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    result = generate_apex_artifact_bundle(
        blueprint,
        output_dir=tmp_path,
    )

    assert len(result.page_paths) == 1

    page = json.loads(
        result.page_paths[0].read_text(
            encoding="utf-8"
        )
    )

    assert (
        page["name"]
        == "F2A_CUSTOMERS_FORM"
    )

    assert len(page["regions"]) == 2

    item_count = sum(
        len(region["items"])
        for region in page["regions"]
    )

    assert item_count == 7


def test_artifact_bundle_creates_lovs(
    tmp_path,
):
    blueprint = _build_blueprint(
        GOLDEN_001,
        "F2A_CUSTOMERS_FORM",
    )

    result = generate_apex_artifact_bundle(
        blueprint,
        output_dir=tmp_path,
    )

    assert result.lovs_path is not None
    assert result.lovs_path.exists()

    content = json.loads(
        result.lovs_path.read_text(
            encoding="utf-8"
        )
    )

    assert len(content["lovs"]) == 1

    assert (
        content["lovs"][0]["name"]
        == "LOV_STATUS"
    )


def test_artifact_bundle_creates_relationships(
    tmp_path,
):
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    result = generate_apex_artifact_bundle(
        blueprint,
        output_dir=tmp_path,
    )

    assert (
        result.relationships_path
        is not None
    )

    content = json.loads(
        result.relationships_path.read_text(
            encoding="utf-8"
        )
    )

    relationship = (
        content["relationships"][0]
    )

    assert (
        relationship["name"]
        == "ORDERS_ORDER_LINES"
    )

    assert (
        relationship["component"]
        == "APEX_MASTER_DETAIL"
    )


def test_artifact_manifest_lists_generated_files(
    tmp_path,
):
    blueprint = _build_blueprint(
        GOLDEN_002,
        "F2A_ORDERS_FORM",
    )

    result = generate_apex_artifact_bundle(
        blueprint,
        output_dir=tmp_path,
    )

    manifest = json.loads(
        result.manifest_path.read_text(
            encoding="utf-8"
        )
    )

    generated_files = set(
        manifest["generated_files"]
    )

    assert (
        "pages/F2A_ORDERS_FORM.json"
        in generated_files
    )

    assert (
        "migration_plan.json"
        in generated_files
    )

    assert (
        "relationships.json"
        in generated_files
    )