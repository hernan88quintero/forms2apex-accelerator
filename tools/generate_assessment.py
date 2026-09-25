from pathlib import Path

from f2a.cli import main as cli_main


FIXTURE = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)


def main() -> int:
    """
    Development shortcut for the Golden Sample.

    Production usage should use:
        f2a assessment --input <form.xml>
    """

    return cli_main(
        [
            "assessment",
            "--input",
            str(FIXTURE),
            "--output",
            "output",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())