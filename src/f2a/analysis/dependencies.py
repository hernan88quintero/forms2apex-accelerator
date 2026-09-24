from __future__ import annotations

import re

from dataclasses import dataclass, field

from f2a.model import FormModel
from f2a.rules.builtins import BUILTIN_CATALOG


# ==============================================================
# Dependency graph model
# ==============================================================


@dataclass(frozen=True)
class DependencyNode:
    node_id: str
    node_type: str
    name: str
    scope: str | None = None
    parent: str | None = None


@dataclass(frozen=True)
class DependencyEdge:
    source: str
    target: str
    relation: str


@dataclass
class DependencyGraph:
    nodes: dict[str, DependencyNode] = field(
        default_factory=dict
    )

    edges: list[DependencyEdge] = field(
        default_factory=list
    )

    def add_node(
        self,
        node: DependencyNode,
    ) -> None:
        self.nodes[node.node_id] = node

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
    ) -> None:

        edge = DependencyEdge(
            source=source,
            target=target,
            relation=relation,
        )

        if edge not in self.edges:
            self.edges.append(edge)

    def get_node(
        self,
        node_id: str,
    ) -> DependencyNode | None:
        return self.nodes.get(node_id)

    def nodes_by_type(
        self,
        node_type: str,
    ) -> tuple[DependencyNode, ...]:

        return tuple(
            node
            for node in self.nodes.values()
            if node.node_type == node_type
        )

    def outgoing(
        self,
        node_id: str,
    ) -> tuple[DependencyEdge, ...]:

        return tuple(
            edge
            for edge in self.edges
            if edge.source == node_id
        )

    def incoming(
        self,
        node_id: str,
    ) -> tuple[DependencyEdge, ...]:

        return tuple(
            edge
            for edge in self.edges
            if edge.target == node_id
        )

    def has_edge(
        self,
        source: str,
        target: str,
        relation: str | None = None,
    ) -> bool:

        return any(
            edge.source == source
            and edge.target == target
            and (
                relation is None
                or edge.relation == relation
            )
            for edge in self.edges
        )
    
    def reachable_from(
        self,
        node_id: str,
    ) -> tuple[str, ...]:
        """
        Returns all nodes reachable from node_id
        following outgoing edges.
        """

        visited: set[str] = set()
        pending: list[str] = [node_id]

        while pending:

            current = pending.pop(0)

            for edge in self.outgoing(current):

                target = edge.target

                if target in visited:
                    continue

                visited.add(target)
                pending.append(target)

        return tuple(sorted(visited))

    def dependents_of(
        self,
        node_id: str,
    ) -> tuple[str, ...]:
        """
        Returns all nodes that depend directly or indirectly
        on node_id, following incoming edges.
        """

        visited: set[str] = set()
        pending: list[str] = [node_id]

        while pending:

            current = pending.pop(0)

            for edge in self.incoming(current):

                source = edge.source

                if source in visited:
                    continue

                visited.add(source)
                pending.append(source)

        return tuple(sorted(visited))

    def find_path(
        self,
        source: str,
        target: str,
    ) -> tuple[str, ...] | None:
        """
        Finds the shortest dependency path from source
        to target following outgoing edges.
        """

        if source == target:
            return (source,)

        pending: list[
            tuple[str, tuple[str, ...]]
        ] = [
            (
                source,
                (source,),
            )
        ]

        visited: set[str] = {
            source
        }

        while pending:

            current, path = pending.pop(0)

            for edge in self.outgoing(current):

                next_node = edge.target

                if next_node in visited:
                    continue

                next_path = (
                    *path,
                    next_node,
                )

                if next_node == target:
                    return next_path

                visited.add(next_node)

                pending.append(
                    (
                        next_node,
                        next_path,
                    )
                )

        return None

    def direct_dependencies_of(
        self,
        node_id: str,
    ) -> tuple[str, ...]:
        """
        Returns immediate dependencies of a node.
        """

        return tuple(
            sorted(
                edge.target
                for edge in self.outgoing(node_id)
            )
        )

    def direct_dependents_of(
        self,
        node_id: str,
    ) -> tuple[str, ...]:
        """
        Returns nodes that directly depend on node_id.
        """

        return tuple(
            sorted(
                edge.source
                for edge in self.incoming(node_id)
            )
        )


# ==============================================================
# Token detection
# ==============================================================


def _contains_token(
    source_code: str,
    token: str,
) -> bool:

    pattern = rf"\b{re.escape(token)}\b"

    return bool(
        re.search(
            pattern,
            source_code,
            flags=re.IGNORECASE,
        )
    )


def _detect_references(
    source_code: str,
    candidates: tuple[str, ...],
) -> tuple[str, ...]:

    return tuple(
        candidate
        for candidate in candidates
        if _contains_token(
            source_code,
            candidate,
        )
    )


# ==============================================================
# Node IDs
# ==============================================================


def _form_node_id(
    form_name: str,
) -> str:
    return f"FORM:{form_name.upper()}"


def _block_node_id(
    block_name: str,
) -> str:
    return f"BLOCK:{block_name.upper()}"


def _item_node_id(
    block_name: str,
    item_name: str,
) -> str:

    return (
        f"ITEM:"
        f"{block_name.upper()}."
        f"{item_name.upper()}"
    )


def _program_unit_node_id(
    unit_name: str,
) -> str:
    return f"PROGRAM_UNIT:{unit_name.upper()}"


def _builtin_node_id(
    builtin_name: str,
) -> str:
    return f"BUILTIN:{builtin_name.upper()}"


def _trigger_node_id(
    *,
    scope: str,
    object_name: str,
    trigger_name: str,
) -> str:

    return (
        f"TRIGGER:"
        f"{scope.upper()}:"
        f"{object_name.upper()}:"
        f"{trigger_name.upper()}"
    )


# ==============================================================
# Graph builder
# ==============================================================


def build_dependency_graph(
    model: FormModel,
    *,
    form_name: str = "FORM",
) -> DependencyGraph:

    graph = DependencyGraph()

    form_name = form_name.upper()

    form_id = _form_node_id(
        form_name
    )

    graph.add_node(
        DependencyNode(
            node_id=form_id,
            node_type="FORM",
            name=form_name,
        )
    )

    # ----------------------------------------------------------
    # Known names
    # ----------------------------------------------------------

    program_units_by_name = {
        unit.name.upper(): unit
        for unit in model.program_units
    }

    program_unit_names = tuple(
        program_units_by_name.keys()
    )

    builtin_names = tuple(
        BUILTIN_CATALOG.keys()
    )

    # ----------------------------------------------------------
    # Program Units
    # ----------------------------------------------------------

    for unit_name, unit in program_units_by_name.items():

        unit_id = _program_unit_node_id(
            unit_name
        )

        graph.add_node(
            DependencyNode(
                node_id=unit_id,
                node_type="PROGRAM_UNIT",
                name=unit_name,
            )
        )

        source_code = unit.source_code or ""

        # Program Unit -> Program Unit
        referenced_units = _detect_references(
            source_code,
            program_unit_names,
        )

        for referenced_name in referenced_units:

            if referenced_name == unit_name:
                continue

            referenced_id = _program_unit_node_id(
                referenced_name
            )

            graph.add_edge(
                unit_id,
                referenced_id,
                "CALLS_PROGRAM_UNIT",
            )

        # Program Unit -> Built-in
        referenced_builtins = _detect_references(
            source_code,
            builtin_names,
        )

        for builtin_name in referenced_builtins:

            builtin_id = _builtin_node_id(
                builtin_name
            )

            graph.add_node(
                DependencyNode(
                    node_id=builtin_id,
                    node_type="BUILTIN",
                    name=builtin_name,
                )
            )

            graph.add_edge(
                unit_id,
                builtin_id,
                "USES_BUILTIN",
            )

    # ----------------------------------------------------------
    # Helper for triggers
    # ----------------------------------------------------------

    def add_trigger(
        *,
        trigger,
        scope: str,
        object_name: str,
        owner_node_id: str,
    ) -> None:

        trigger_id = _trigger_node_id(
            scope=scope,
            object_name=object_name,
            trigger_name=trigger.name,
        )

        graph.add_node(
            DependencyNode(
                node_id=trigger_id,
                node_type="TRIGGER",
                name=trigger.name,
                scope=scope,
                parent=object_name,
            )
        )

        graph.add_edge(
            owner_node_id,
            trigger_id,
            "HAS_TRIGGER",
        )

        source_code = trigger.source_code or ""

        # Trigger -> Program Unit
        referenced_units = _detect_references(
            source_code,
            program_unit_names,
        )

        for unit_name in referenced_units:

            unit_id = _program_unit_node_id(
                unit_name
            )

            graph.add_edge(
                trigger_id,
                unit_id,
                "CALLS_PROGRAM_UNIT",
            )

        # Trigger -> Built-in
        referenced_builtins = _detect_references(
            source_code,
            builtin_names,
        )

        for builtin_name in referenced_builtins:

            builtin_id = _builtin_node_id(
                builtin_name
            )

            graph.add_node(
                DependencyNode(
                    node_id=builtin_id,
                    node_type="BUILTIN",
                    name=builtin_name,
                )
            )

            graph.add_edge(
                trigger_id,
                builtin_id,
                "USES_BUILTIN",
            )

    # ----------------------------------------------------------
    # Blocks / Items / Triggers
    # ----------------------------------------------------------

    for block in model.blocks:

        block_id = _block_node_id(
            block.name
        )

        graph.add_node(
            DependencyNode(
                node_id=block_id,
                node_type="BLOCK",
                name=block.name,
                parent=form_name,
            )
        )

        graph.add_edge(
            form_id,
            block_id,
            "CONTAINS",
        )

        # ------------------------------------------------------
        # Items
        # ------------------------------------------------------

        for item in block.items:

            object_name = (
                f"{block.name}.{item.name}"
            )

            item_id = _item_node_id(
                block.name,
                item.name,
            )

            graph.add_node(
                DependencyNode(
                    node_id=item_id,
                    node_type="ITEM",
                    name=item.name,
                    scope=object_name,
                    parent=block.name,
                )
            )

            graph.add_edge(
                block_id,
                item_id,
                "CONTAINS",
            )

            # Item triggers
            for trigger in item.triggers:

                add_trigger(
                    trigger=trigger,
                    scope="ITEM",
                    object_name=object_name,
                    owner_node_id=item_id,
                )

        # ------------------------------------------------------
        # Block triggers
        # ------------------------------------------------------

        for trigger in block.triggers:

            add_trigger(
                trigger=trigger,
                scope="BLOCK",
                object_name=block.name,
                owner_node_id=block_id,
            )

    # ----------------------------------------------------------
    # Form triggers
    # ----------------------------------------------------------

    for trigger in model.form_triggers:

        add_trigger(
            trigger=trigger,
            scope="FORM",
            object_name=form_name,
            owner_node_id=form_id,
        )

    return graph