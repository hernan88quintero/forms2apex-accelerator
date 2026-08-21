from dataclasses import dataclass, field


@dataclass
class Trigger:
    name: str
    level: str
    source_code: str


@dataclass
class Item:
    name: str
    item_type: str | None = None
    data_type: str | None = None
    database_item: str | None = None
    column_name: str | None = None
    required: str = "N"
    lov_name: str | None = None
    triggers: list[Trigger] = field(default_factory=list)


@dataclass
class Block:
    name: str
    block_type: str | None = None
    database_block: str | None = None
    data_source: str | None = None
    records_displayed: int | None = None

    items: list[Item] = field(default_factory=list)
    triggers: list[Trigger] = field(default_factory=list)


@dataclass
class ProgramUnit:
    name: str
    unit_type: str
    source_code: str


@dataclass
class LovValue:
    return_value: str
    display_value: str
    display_order: int

@dataclass
class Lov:
    name: str
    lov_type: str = "STATIC"
    query_text: str | None = None
    values: list[LovValue] = field(default_factory=list)


@dataclass
class FormModel:
    blocks: list[Block] = field(default_factory=list)
    form_triggers: list[Trigger] = field(default_factory=list)
    program_units: list[ProgramUnit] = field(default_factory=list)
    lovs: list[Lov] = field(default_factory=list)

    expected_results: dict[str, int] = field(default_factory=dict)

    @property
    def item_count(self) -> int:
        return sum(len(block.items) for block in self.blocks)

    @property
    def trigger_count(self) -> int:
        block_triggers = sum(
            len(block.triggers)
            for block in self.blocks
        )

        item_triggers = sum(
            len(item.triggers)
            for block in self.blocks
            for item in block.items
        )

        return (
            len(self.form_triggers)
            + block_triggers
            + item_triggers
        )