from pathlib import Path
import tomllib


PYPROJECT = Path("pyproject.toml")


def get_pyproject():
    with PYPROJECT.open("rb") as file:
        return tomllib.load(file)


def test_cli_console_script_is_registered():
    config = get_pyproject()

    assert "project" in config
    assert "scripts" in config["project"]

    assert (
        config["project"]["scripts"]["f2a"]
        == "f2a.cli:main"
    )


def test_project_package_name():
    config = get_pyproject()

    assert (
        config["project"]["name"]
        == "forms2apex-accelerator"
    )