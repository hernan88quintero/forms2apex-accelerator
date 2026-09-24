from dataclasses import dataclass


@dataclass(frozen=True)
class BuiltinFinding:
    name: str
    category: str
    apex_strategy: str
    risk: str


@dataclass(frozen=True)
class MigrationFinding:
    scope: str
    object_name: str
    trigger_name: str
    apex_pattern: str

    complexity: str
    risk: str
    effort: int
    confidence: str
    automation_level: str
    recommendation: str

    builtins: tuple[str, ...] = ()
    builtin_details: tuple[BuiltinFinding, ...] = ()
    referenced_program_units: tuple[str, ...] = ()