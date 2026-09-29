from pathlib import Path
import shutil

from f2a.cli import (
    generate_assessment_batch,
    main,
)


GOLDEN_001 = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)

GOLDEN_002 = Path(
    "samples/golden_002/fixtures/f2a_orders_form.xml"
)


def _prepare_portfolio(
    tmp_path,
):
    input_dir = (
        tmp_path
        / "forms"
    )

    output_dir = (
        tmp_path
        / "output"
    )

    input_dir.mkdir()

    shutil.copyfile(
        GOLDEN_001,
        input_dir
        / "f2a_customers_form.xml",
    )

    shutil.copyfile(
        GOLDEN_002,
        input_dir
        / "f2a_orders_form.xml",
    )

    return (
        input_dir,
        output_dir,
    )


def test_multiple_golden_samples_batch_successfully(
    tmp_path,
):
    input_dir, output_dir = (
        _prepare_portfolio(
            tmp_path
        )
    )

    result = generate_assessment_batch(
        input_dir=input_dir,
        output_dir=output_dir,
    )

    assert result.total_files == 2
    assert result.success_count == 2
    assert result.failure_count == 0

    assert (
        len(result.assessment_summaries)
        == 2
    )


def test_multiple_golden_samples_generate_assessments(
    tmp_path,
):
    input_dir, output_dir = (
        _prepare_portfolio(
            tmp_path
        )
    )

    result = generate_assessment_batch(
        input_dir=input_dir,
        output_dir=output_dir,
    )

    assert result.success_count == 2

    customers_report = (
        output_dir
        / "F2A_CUSTOMERS_FORM_assessment.md"
    )

    orders_report = (
        output_dir
        / "F2A_ORDERS_FORM_assessment.md"
    )

    assert customers_report.exists()
    assert orders_report.exists()

    customers_content = (
        customers_report.read_text(
            encoding="utf-8"
        )
    )

    orders_content = (
        orders_report.read_text(
            encoding="utf-8"
        )
    )

    assert (
        "F2A_CUSTOMERS_FORM"
        in customers_content
    )

    assert (
        "F2A_ORDERS_FORM"
        in orders_content
    )

    assert (
        "ORDER_LINES"
        in orders_content
    )


def test_multiple_golden_samples_have_distinct_inventory(
    tmp_path,
):
    input_dir, output_dir = (
        _prepare_portfolio(
            tmp_path
        )
    )

    result = generate_assessment_batch(
        input_dir=input_dir,
        output_dir=output_dir,
    )

    summaries = {
        summary.form_name: summary
        for summary
        in result.assessment_summaries
    }

    customers = summaries[
        "F2A_CUSTOMERS_FORM"
    ]

    orders = summaries[
        "F2A_ORDERS_FORM"
    ]

    assert (
        orders.block_count
        > customers.block_count
    )

    assert (
        orders.item_count
        > customers.item_count
    )

    assert (
        orders.lov_count
        > customers.lov_count
    )


def test_multiple_golden_samples_generate_portfolio(
    tmp_path,
):
    input_dir, output_dir = (
        _prepare_portfolio(
            tmp_path
        )
    )

    exit_code = main(
        [
            "assessment-batch",
            "--input-dir",
            str(input_dir),
            "--output",
            str(output_dir),
        ]
    )

    assert exit_code == 0

    portfolio_path = (
        output_dir
        / "F2A_PORTFOLIO_SUMMARY.md"
    )

    assert portfolio_path.exists()

    portfolio = portfolio_path.read_text(
        encoding="utf-8"
    )

    assert (
        "| XML Files Discovered | 2 |"
        in portfolio
    )

    assert (
        "| Forms Assessed | 2 |"
        in portfolio
    )

    assert (
        "| Forms Failed | 0 |"
        in portfolio
    )

    assert (
        "F2A_CUSTOMERS_FORM"
        in portfolio
    )

    assert (
        "F2A_ORDERS_FORM"
        in portfolio
    )


def test_multiple_golden_samples_produce_different_assessments(
    tmp_path,
):
    input_dir, output_dir = (
        _prepare_portfolio(
            tmp_path
        )
    )

    generate_assessment_batch(
        input_dir=input_dir,
        output_dir=output_dir,
    )

    customers_report = (
        output_dir
        / "F2A_CUSTOMERS_FORM_assessment.md"
    ).read_text(
        encoding="utf-8"
    )

    orders_report = (
        output_dir
        / "F2A_ORDERS_FORM_assessment.md"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        customers_report
        != orders_report
    )

    assert (
        "ORDER_LINES"
        not in customers_report
    )

    assert (
        "ORDER_LINES"
        in orders_report
    )