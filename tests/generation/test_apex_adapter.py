import pytest

from f2a.generation.apex_adapter import (
    DEFAULT_APEX_VERSION,
    get_apex_version_adapter,
    normalize_apex_version,
)


def test_default_apex_adapter_is_24_2():
    adapter = get_apex_version_adapter()

    assert DEFAULT_APEX_VERSION == "24.2"
    assert adapter.version == "24.2"
    assert adapter.family == "24.x"


def test_apex_24_2_adapter_uses_current_export_strategy():
    adapter = get_apex_version_adapter(
        "24.2"
    )

    assert adapter.export_format == "SQL"

    assert (
        adapter.readable_export_format
        == "YAML"
    )

    assert (
        adapter.deployment_tool
        == "SQLcl"
    )

    assert (
        adapter.supports_json_readable_export
        is False
    )


def test_apex_version_aliases_are_normalized():
    assert (
        normalize_apex_version("24_2")
        == "24.2"
    )

    assert (
        normalize_apex_version("24-2")
        == "24.2"
    )


def test_unsupported_apex_version_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unsupported APEX version",
    ):
        get_apex_version_adapter(
            "20.1"
        )