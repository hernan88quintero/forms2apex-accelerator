import shutil
import subprocess
import sys

from f2a.cli import get_version


def test_package_version():
    assert get_version() == "0.1.0"


def test_module_cli_version():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "f2a.cli",
            "--version",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0

    assert (
        result.stdout.strip()
        == "f2a 0.1.0"
    )


def test_installed_f2a_command_exists():
    executable = shutil.which(
        "f2a"
    )

    assert executable is not None


def test_installed_f2a_command_version():
    executable = shutil.which(
        "f2a"
    )

    assert executable is not None

    result = subprocess.run(
        [
            executable,
            "--version",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0

    assert (
        result.stdout.strip()
        == "f2a 0.1.0"
    )