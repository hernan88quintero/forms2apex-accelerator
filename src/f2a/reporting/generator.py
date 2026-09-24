from __future__ import annotations

from pathlib import Path

from f2a.model import FormModel
from f2a.reporting.assessment import (
    render_assessment_markdown,
)


def generate_assessment_file(
    model: FormModel,
    *,
    form_name: str,
    output_dir: Path,
) -> Path:

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        f"{form_name.upper()}_assessment.md"
    )

    output_path = (
        output_dir / filename
    )

    report = render_assessment_markdown(
        model,
        form_name=form_name.upper(),
    )

    output_path.write_text(
        report,
        encoding="utf-8",
    )

    return output_path