from pathlib import Path

from f2a.parser.xml_parser import parse_form_xml


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)


def test_golden_sample_counts():
    model = parse_form_xml(FIXTURE)

    assert len(model.blocks) == 2
    assert model.item_count == 7
    assert model.trigger_count == 5
    assert len(model.program_units) == 2
    assert len(model.lovs) == 1


def test_expected_results_match_parser():
    model = parse_form_xml(FIXTURE)

    actual = {
        "forms": 1,
        "blocks": len(model.blocks),
        "items": model.item_count,
        "triggers": model.trigger_count,
        "program-units": len(model.program_units),
        "lovs": len(model.lovs),
    }

    assert actual == model.expected_results


def test_block_structure():
    model = parse_form_xml(FIXTURE)

    assert len(model.blocks) == 2

    customers = next(
        block
        for block in model.blocks
        if block.name == "CUSTOMERS"
    )

    control = next(
        block
        for block in model.blocks
        if block.name == "CONTROL"
    )

    assert customers.block_type == "DATABASE"
    assert customers.database_block == "Y"
    assert customers.data_source == "CUSTOMERS"
    assert customers.records_displayed == 1
    assert len(customers.items) == 5

    assert control.block_type == "CONTROL"
    assert control.database_block == "N"
    assert control.records_displayed == 1
    assert len(control.items) == 2


def test_item_required_defaults():
    model = parse_form_xml(FIXTURE)

    items = {
        item.name: item
        for block in model.blocks
        for item in block.items
    }

    assert items["CUSTOMER_ID"].required == "Y"
    assert items["FIRST_NAME"].required == "Y"
    assert items["LAST_NAME"].required == "Y"
    assert items["EMAIL"].required == "Y"
    assert items["STATUS"].required == "Y"

    assert items["BTN_SAVE"].required == "N"
    assert items["BTN_CANCEL"].required == "N"


def test_program_units():
    model = parse_form_xml(FIXTURE)

    units = {
        unit.name: unit
        for unit in model.program_units
    }

    assert set(units) == {
        "VALIDATE_EMAIL",
        "SAVE_CUSTOMER",
    }

    assert units["VALIDATE_EMAIL"].unit_type == "PROCEDURE"
    assert units["SAVE_CUSTOMER"].unit_type == "PROCEDURE"

    assert len(units["VALIDATE_EMAIL"].source_code) > 0
    assert len(units["SAVE_CUSTOMER"].source_code) > 0


def test_lov_status():
    model = parse_form_xml(FIXTURE)

    assert len(model.lovs) == 1

    lov = model.lovs[0]

    assert lov.name == "LOV_STATUS"
    assert lov.lov_type == "STATIC"
    assert len(lov.values) == 2

    assert lov.values[0].return_value == "ACTIVE"
    assert lov.values[0].display_value == "Active"
    assert lov.values[0].display_order == 1

    assert lov.values[1].return_value == "INACTIVE"
    assert lov.values[1].display_value == "Inactive"
    assert lov.values[1].display_order == 2

def test_trigger_structure():
    model = parse_form_xml(FIXTURE)

    customers = next(
        block
        for block in model.blocks
        if block.name == "CUSTOMERS"
    )

    control = next(
        block
        for block in model.blocks
        if block.name == "CONTROL"
    )

    email_item = next(
        item
        for item in customers.items
        if item.name == "EMAIL"
    )

    save_button = next(
        item
        for item in control.items
        if item.name == "BTN_SAVE"
    )

    # ITEM trigger: EMAIL
    assert len(email_item.triggers) == 1

    email_trigger = email_item.triggers[0]

    assert email_trigger.name == "WHEN-VALIDATE-ITEM"
    assert email_trigger.level == "ITEM"

    # ITEM trigger: BTN_SAVE
    assert len(save_button.triggers) == 1

    save_trigger = save_button.triggers[0]

    assert save_trigger.name == "WHEN-BUTTON-PRESSED"
    assert save_trigger.level == "ITEM"

    # BLOCK triggers: CUSTOMERS
    assert len(customers.triggers) == 2

    customer_trigger_names = {
        trigger.name
        for trigger in customers.triggers
    }

    assert customer_trigger_names == {
        "PRE-INSERT",
        "POST-QUERY",
    }

    for trigger in customers.triggers:
        assert trigger.level == "BLOCK"

    # CONTROL has no block-level triggers
    assert len(control.triggers) == 0

    # FORM trigger
    assert len(model.form_triggers) == 1

    form_trigger = model.form_triggers[0]

    assert form_trigger.name == "WHEN-NEW-FORM-INSTANCE"
    assert form_trigger.level == "FORM"


def test_trigger_source_code_is_preserved():
    model = parse_form_xml(FIXTURE)

    customers = next(
        block
        for block in model.blocks
        if block.name == "CUSTOMERS"
    )

    control = next(
        block
        for block in model.blocks
        if block.name == "CONTROL"
    )

    email_item = next(
        item
        for item in customers.items
        if item.name == "EMAIL"
    )

    save_button = next(
        item
        for item in control.items
        if item.name == "BTN_SAVE"
    )

    email_source = email_item.triggers[0].source_code.upper()
    save_source = save_button.triggers[0].source_code.upper()

    pre_insert = next(
        trigger
        for trigger in customers.triggers
        if trigger.name == "PRE-INSERT"
    )

    post_query = next(
        trigger
        for trigger in customers.triggers
        if trigger.name == "POST-QUERY"
    )

    form_trigger = model.form_triggers[0]

    assert "VALIDATE_EMAIL" in email_source
    assert ":CUSTOMERS.EMAIL" in email_source

    assert "SAVE_CUSTOMER" in save_source

    assert "CUSTOMERS_SEQ.NEXTVAL" in pre_insert.source_code.upper()
    assert ":CUSTOMERS.CUSTOMER_ID" in pre_insert.source_code.upper()

    assert len(post_query.source_code.strip()) > 0

    assert "GO_BLOCK('CUSTOMERS')" in form_trigger.source_code.upper()
    assert "EXECUTE_QUERY" in form_trigger.source_code.upper()