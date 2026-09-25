from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET


from pathlib import Path
from typing import Sequence

from f2a.parser.xml_parser import parse_form_xml
from f2a.reporting.generator import generate_assessment_file
from importlib.metadata import (
    PackageNotFoundError,
    version,
)
from dataclasses import dataclass

from f2a.reporting.assessment import (
    AssessmentSummary,
    build_assessment_summary,
)

from f2a.reporting.portfolio import (
    generate_portfolio_file,
)

PACKAGE_NAME = "forms2apex-accelerator"


def get_version() -> str:
    try:
        return version(
            PACKAGE_NAME
        )
    except PackageNotFoundError:
        return "dev"
    
@dataclass(frozen=True)
class BatchAssessmentResult:
    total_files: int

    generated_files: tuple[
        Path, ...
    ]

    assessment_summaries: tuple[
        AssessmentSummary, ...
    ]

    failures: tuple[
        tuple[Path, str],
        ...
    ]

    @property
    def success_count(self) -> int:
        return len(
            self.generated_files
        )

    @property
    def failure_count(self) -> int:
        return len(
            self.failures
        )
    
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="f2a",
        description=(
            "Forms2APEX Accelerator - "
            "Oracle Forms to Oracle APEX migration tooling"
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=(
            f"%(prog)s {get_version()}"
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # ----------------------------------------------------------
    # assessment
    # ----------------------------------------------------------

    assessment_parser = subparsers.add_parser(
        "assessment",
        help="Generate a migration assessment from a Forms XML file.",
    )

    assessment_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=Path,
        help="Path to the Oracle Forms XML file.",
    )

    assessment_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("output"),
        help=(
            "Directory where the assessment will be generated. "
            "Default: output"
        ),
    )

    assessment_parser.add_argument(
        "--form-name",
        type=str,
        default=None,
        help=(
            "Optional form name override. "
            "By default the XML filename is used."
        ),
    )

    # ----------------------------------------------------------
    # assessment-batch
    # ----------------------------------------------------------

    batch_parser = subparsers.add_parser(
        "assessment-batch",
        help=(
            "Generate migration assessments "
            "for all Forms XML files in a directory."
        ),
    )

    batch_parser.add_argument(
        "--input-dir",
        "-i",
        required=True,
        type=Path,
        help=(
            "Directory containing Oracle Forms XML files."
        ),
    )

    batch_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("output"),
        help=(
            "Directory where assessments will be generated. "
            "Default: output"
        ),
    )

    return parser


def _validate_input_file(
    input_path: Path,
) -> Path:
    input_path = input_path.expanduser()

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file does not exist: {input_path}"
        )

    if not input_path.is_file():
        raise ValueError(
            f"Input path is not a file: {input_path}"
        )

    if input_path.suffix.lower() != ".xml":
        raise ValueError(
            "Input file must have .xml extension."
        )

    return input_path


def generate_assessment_command(
    *,
    input_path: Path,
    output_dir: Path,
    form_name: str | None = None,
) -> Path:

    input_path = _validate_input_file(
        input_path
    )

    try:
        model = parse_form_xml(
            input_path
        )
    except ET.ParseError as exc:
        raise ValueError(
            f"Invalid XML file: {input_path}. "
            f"XML parsing failed: {exc}"
        ) from exc

    if form_name is None:
        resolved_form_name = (
            input_path.stem.upper()
        )
    else:
        resolved_form_name = (
            form_name.strip().upper()
        )

        if not resolved_form_name:
            raise ValueError(
                "Form name cannot be empty."
            )

    return generate_assessment_file(
        model,
        form_name=resolved_form_name,
        output_dir=output_dir,
    )

def _validate_input_directory(
    input_dir: Path,
) -> Path:

    input_dir = input_dir.expanduser()

    if not input_dir.exists():
        raise FileNotFoundError(
            f"Input directory does not exist: {input_dir}"
        )

    if not input_dir.is_dir():
        raise ValueError(
            f"Input path is not a directory: {input_dir}"
        )

    return input_dir


def generate_assessment_batch(
    *,
    input_dir: Path,
    output_dir: Path,
) -> BatchAssessmentResult:

    input_dir = _validate_input_directory(
        input_dir
    )

    xml_files = tuple(
        sorted(
            input_dir.glob("*.xml"),
            key=lambda path: path.name.lower(),
        )
    )

    if not xml_files:
        raise ValueError(
            f"No XML files found in directory: {input_dir}"
        )

    generated_files: list[Path] = []

    assessment_summaries: list[
        AssessmentSummary
    ] = []

    failures: list[
        tuple[Path, str]
    ] = []

    for input_path in xml_files:

        try:
            output_path = generate_assessment_command(
                input_path=input_path,
                output_dir=output_dir,
            )

        except (
            FileNotFoundError,
            ValueError,
        ) as exc:

            failures.append(
                (
                    input_path,
                    str(exc),
                )
            )

            continue

        generated_files.append(
            output_path
        )

        model = parse_form_xml(
            input_path
        )

        summary = build_assessment_summary(
            model,
            form_name=input_path.stem.upper(),
        )

        assessment_summaries.append(
            summary
        )

    return BatchAssessmentResult(
        total_files=len(xml_files),
        generated_files=tuple(
            generated_files
        ),
        assessment_summaries=tuple(
            assessment_summaries
        ),
        failures=tuple(
            failures
        ),
    )

def main(
    argv: Sequence[str] | None = None,
) -> int:

    parser = build_parser()
    args = parser.parse_args(argv)

    try:

        if args.command == "assessment":

            print()
            print(
                "Forms2APEX Accelerator - Assessment"
            )
            print("=" * 60)

            print(
                f"Input  : {args.input}"
            )

            output_path = generate_assessment_command(
                input_path=args.input,
                output_dir=args.output,
                form_name=args.form_name,
            )

            print(
                f"Output : {output_path}"
            )

            print()
            print(
                "Assessment generation: OK"
            )

            return 0
    
        if args.command == "assessment-batch":

            print()
            print(
                "Forms2APEX Accelerator - Batch Assessment"
            )
            print("=" * 60)

            print(
                f"Input directory : {args.input_dir}"
            )

            print(
                f"Output directory: {args.output}"
            )

            result = generate_assessment_batch(
                input_dir=args.input_dir,
                output_dir=args.output,
            )

        portfolio_path = None

        if result.assessment_summaries:

            portfolio_path = generate_portfolio_file(
                    result.assessment_summaries,
                    total_files=result.total_files,
                    failed_forms=result.failure_count,
                    output_dir=args.output,
                )

            print()
            print("Results")
            print("-" * 60)

            for output_path in result.generated_files:

                print(
                    f"[OK]    {output_path}"
                )

            if portfolio_path is not None:

                print(
                    f"[PORTFOLIO] {portfolio_path}"
                )

            for input_path, error in result.failures:

                print(
                    f"[ERROR] {input_path}"
                )

                print(
                    f"        {error}"
                )

            print()
            print("Summary")
            print("-" * 60)

            print(
                f"Total     : {result.total_files}"
            )

            print(
                f"Generated : {result.success_count}"
            )

            print(
                f"Failed    : {result.failure_count}"
            )

            print()

            if result.failure_count:

                print(
                    "Batch assessment completed with errors."
                )

                return 1

            print(
                "Batch assessment: OK"
            )

            return 0

        parser.error(
            f"Unsupported command: {args.command}"
        )

    except (
        FileNotFoundError,
        ValueError,
    ) as exc:

        print()
        print(
            f"ERROR: {exc}"
        )

        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())