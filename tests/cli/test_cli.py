from pathlib import Path

from f2a.cli import (
    build_parser,
    generate_assessment_batch,
    generate_assessment_command,
    main,
)


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)


def test_cli_parser_accepts_assessment_command():
    parser = build_parser()

    args = parser.parse_args(
        [
            "assessment",
            "--input",
            str(FIXTURE),
        ]
    )

    assert args.command == "assessment"
    assert args.input == FIXTURE
    assert args.output == Path("output")
    assert args.form_name is None


def test_cli_generates_assessment(
    tmp_path,
):
    output_path = generate_assessment_command(
        input_path=FIXTURE,
        output_dir=tmp_path,
    )

    assert output_path.exists()

    assert (
        output_path.name
        == "F2A_CUSTOMERS_FORM_assessment.md"
    )

    content = output_path.read_text(
        encoding="utf-8"
    )

    assert (
        "# Forms2APEX Migration Assessment"
        in content
    )

    assert (
        "F2A_CUSTOMERS_FORM"
        in content
    )


def test_cli_supports_custom_form_name(
    tmp_path,
):
    output_path = generate_assessment_command(
        input_path=FIXTURE,
        output_dir=tmp_path,
        form_name="customer_maintenance",
    )

    assert (
        output_path.name
        == "CUSTOMER_MAINTENANCE_assessment.md"
    )

    content = output_path.read_text(
        encoding="utf-8"
    )

    assert (
        "CUSTOMER_MAINTENANCE"
        in content
    )


def test_cli_rejects_missing_input(
    tmp_path,
):
    missing_file = (
        tmp_path
        / "missing_form.xml"
    )

    try:
        generate_assessment_command(
            input_path=missing_file,
            output_dir=tmp_path,
        )
    except FileNotFoundError as exc:

        assert (
            "Input file does not exist"
            in str(exc)
        )

    else:
        raise AssertionError(
            "Expected FileNotFoundError"
        )


def test_cli_rejects_non_xml_input(
    tmp_path,
):
    source = (
        tmp_path
        / "form.txt"
    )

    source.write_text(
        "not xml",
        encoding="utf-8",
    )

    try:
        generate_assessment_command(
            input_path=source,
            output_dir=tmp_path,
        )
    except ValueError as exc:

        assert (
            ".xml extension"
            in str(exc)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_cli_main_returns_zero(
    tmp_path,
):
    exit_code = main(
        [
            "assessment",
            "--input",
            str(FIXTURE),
            "--output",
            str(tmp_path),
        ]
    )

    assert exit_code == 0


def test_cli_main_returns_error_for_missing_file(
    tmp_path,
):
    missing_file = (
        tmp_path
        / "missing.xml"
    )

    exit_code = main(
        [
            "assessment",
            "--input",
            str(missing_file),
            "--output",
            str(tmp_path),
        ]
    )

    assert exit_code == 2

def test_cli_rejects_invalid_xml(
    tmp_path,
):
    invalid_xml = (
        tmp_path
        / "broken_form.xml"
    )

    invalid_xml.write_text(
        "<Form><Block></Form>",
        encoding="utf-8",
    )

    try:
        generate_assessment_command(
            input_path=invalid_xml,
            output_dir=tmp_path,
        )
    except ValueError as exc:

        assert (
            "Invalid XML file"
            in str(exc)
        )

        assert (
            "XML parsing failed"
            in str(exc)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_cli_rejects_blank_form_name(
    tmp_path,
):
    try:
        generate_assessment_command(
            input_path=FIXTURE,
            output_dir=tmp_path,
            form_name="   ",
        )
    except ValueError as exc:

        assert (
            "Form name cannot be empty"
            in str(exc)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_cli_main_handles_invalid_xml(
    tmp_path,
):
    invalid_xml = (
        tmp_path
        / "broken.xml"
    )

    invalid_xml.write_text(
        "<Forms><Broken>",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "assessment",
            "--input",
            str(invalid_xml),
            "--output",
            str(tmp_path),
        ]
    )

    assert exit_code == 2

def test_cli_parser_accepts_batch_command():
    parser = build_parser()

    args = parser.parse_args(
        [
            "assessment-batch",
            "--input-dir",
            "forms",
            "--output",
            "reports",
        ]
    )

    assert args.command == "assessment-batch"
    assert args.input_dir == Path("forms")
    assert args.output == Path("reports")


def test_batch_generates_multiple_assessments(
    tmp_path,
):
    import shutil

    input_dir = tmp_path / "forms"
    output_dir = tmp_path / "output"

    input_dir.mkdir()

    shutil.copyfile(
        FIXTURE,
        input_dir / "customers.xml",
    )

    shutil.copyfile(
        FIXTURE,
        input_dir / "orders.xml",
    )

    result = generate_assessment_batch(
        input_dir=input_dir,
        output_dir=output_dir,
    )

    assert result.total_files == 2
    assert result.success_count == 2
    assert result.failure_count == 0

    assert (
        output_dir
        / "CUSTOMERS_assessment.md"
    ).exists()

    assert (
        output_dir
        / "ORDERS_assessment.md"
    ).exists()


def test_batch_rejects_missing_directory(
    tmp_path,
):
    missing_dir = (
        tmp_path
        / "missing"
    )

    try:
        generate_assessment_batch(
            input_dir=missing_dir,
            output_dir=tmp_path / "output",
        )

    except FileNotFoundError as exc:

        assert (
            "Input directory does not exist"
            in str(exc)
        )

    else:
        raise AssertionError(
            "Expected FileNotFoundError"
        )


def test_batch_rejects_empty_directory(
    tmp_path,
):
    input_dir = (
        tmp_path
        / "empty"
    )

    input_dir.mkdir()

    try:
        generate_assessment_batch(
            input_dir=input_dir,
            output_dir=tmp_path / "output",
        )

    except ValueError as exc:

        assert (
            "No XML files found"
            in str(exc)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_batch_continues_when_one_xml_is_invalid(
    tmp_path,
):
    import shutil

    input_dir = tmp_path / "forms"
    output_dir = tmp_path / "output"

    input_dir.mkdir()

    shutil.copyfile(
        FIXTURE,
        input_dir / "valid_form.xml",
    )

    invalid_file = (
        input_dir
        / "broken_form.xml"
    )

    invalid_file.write_text(
        "<Form><Broken></Form>",
        encoding="utf-8",
    )

    result = generate_assessment_batch(
        input_dir=input_dir,
        output_dir=output_dir,
    )

    assert result.total_files == 2
    assert result.success_count == 1
    assert result.failure_count == 1

    assert (
        output_dir
        / "VALID_FORM_assessment.md"
    ).exists()

    failed_path, error = (
        result.failures[0]
    )

    assert failed_path == invalid_file

    assert (
        "Invalid XML file"
        in error
    )


def test_cli_batch_main_returns_zero(
    tmp_path,
):
    import shutil

    input_dir = tmp_path / "forms"
    output_dir = tmp_path / "output"

    input_dir.mkdir()

    shutil.copyfile(
        FIXTURE,
        input_dir / "customers.xml",
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

def test_batch_collects_assessment_summaries(
    tmp_path,
):
    import shutil

    input_dir = tmp_path / "forms"
    output_dir = tmp_path / "output"

    input_dir.mkdir()

    shutil.copyfile(
        FIXTURE,
        input_dir / "customers.xml",
    )

    shutil.copyfile(
        FIXTURE,
        input_dir / "orders.xml",
    )

    result = generate_assessment_batch(
        input_dir=input_dir,
        output_dir=output_dir,
    )

    assert (
        len(result.assessment_summaries)
        == 2
    )

    form_names = {
        summary.form_name
        for summary
        in result.assessment_summaries
    }

    assert form_names == {
        "CUSTOMERS",
        "ORDERS",
    }

def test_cli_batch_generates_portfolio(
    tmp_path,
):
    import shutil

    input_dir = tmp_path / "forms"
    output_dir = tmp_path / "output"

    input_dir.mkdir()

    shutil.copyfile(
        FIXTURE,
        input_dir / "customers.xml",
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

    assert (
        output_dir
        / "F2A_PORTFOLIO_SUMMARY.md"
    ).exists()