from __future__ import annotations

from dataclasses import dataclass


DEFAULT_APEX_VERSION = "24.2"


@dataclass(frozen=True)
class ApexVersionAdapter:
    version: str
    family: str

    export_format: str
    readable_export_format: str
    deployment_tool: str

    supports_json_readable_export: bool

    component_generation_strategy: str
    requires_reference_export: bool


_APEX_24_2 = ApexVersionAdapter(
    version="24.2",
    family="24.x",
    export_format="SQL",
    readable_export_format="YAML",
    deployment_tool="SQLcl",
    supports_json_readable_export=False,
    component_generation_strategy=(
        "REFERENCE_EXPORT_TEMPLATE"
    ),
    requires_reference_export=True,
)


_ADAPTERS = {
    "24.2": _APEX_24_2,
}


_VERSION_ALIASES = {
    "24.2": "24.2",
    "24_2": "24.2",
    "24-2": "24.2",
}


def normalize_apex_version(
    version: str,
) -> str:

    normalized = (
        version
        .strip()
        .lower()
    )

    if not normalized:
        raise ValueError(
            "APEX version cannot be empty."
        )

    try:
        return _VERSION_ALIASES[
            normalized
        ]

    except KeyError as exc:
        raise ValueError(
            "Unsupported APEX version: "
            f"{version}. "
            "Supported versions: "
            f"{', '.join(sorted(_ADAPTERS))}"
        ) from exc


def get_apex_version_adapter(
    version: str = DEFAULT_APEX_VERSION,
) -> ApexVersionAdapter:

    normalized = (
        normalize_apex_version(
            version
        )
    )

    return _ADAPTERS[
        normalized
    ]