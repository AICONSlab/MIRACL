"""
This code is written and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca).

Workflow DAG using networkX for dependency validation, execution ordering, parallel
stage detection, failure cascading, and status tracking.

Builds a directed graph from a WorkFlowConfig where:
  - Nodes = module instance names (e.g. 'conv', 'reg', 'inf')
  - Edges = dependency relationships (A -> B means A must finish before B starts)

Edge sources:
  - data_flow input: entries  (module B's input references a var produced by module A)
  - data_flow output: entries (used to build the var->producer map; not edges themselves)
  - hooks              (pre_run, post_run, on_failure, on_success expressions)
  - vars               (transitively expanded through var-to-var and var-to-module refs)

Two kinds of dependency are both captured and both required:
  - Path-construction deps: module A's name appears inside a var's DSL expression
    (e.g. "ref:conv.out_dir" inside a pattern:, conv must run first to provide the
    value that builds the path string).
  - Data-production deps: module A's output block names the var that module B's input
    block consumes (e.g. gen_patch declares output generated_patches, and preproc_para
    declares input generated_patches, so gen_patch must run first to write the data on
    disk).
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set

import networkx as nx

from miracl.system.workflow.workflow_dsl import parse_expression
from miracl.system.logger import get_logger

logger = get_logger(__name__)


#######################################################################################
# NODE STATUS
#######################################################################################


class NodeStatus(Enum):
    """Runtime status of a single module instance node."""

    PENDING = auto()
    RUNNING = auto()
    DONE = auto()
    FAILED = auto()
    SKIPPED = auto()


_DOT_STATUS_ATTRS: dict[NodeStatus, dict[str, str]] = {
    NodeStatus.PENDING: {"fillcolor": "lightgray", "style": "filled"},
    NodeStatus.RUNNING: {"fillcolor": "gold", "style": "filled,bold"},
    NodeStatus.DONE: {"fillcolor": "green", "style": "filled"},
    NodeStatus.FAILED: {"fillcolor": "salmon", "style": "filled,bold"},
    NodeStatus.SKIPPED: {"fillcolor": "lightblue", "style": "filled,dashed"},
}


#######################################################################################
# EXCEPTIONS
#######################################################################################


class WorkflowGraphError(Exception):
    """Base exception for all workflow graph errors."""


class CircularDependencyError(WorkflowGraphError):
    """
    Raised when the workflow module graph contains a cycle.

    A cycle means module A depends on B which depends on A (directly or transitively).
    This would deadlock at runtime, so it is caught during graph validation, before any
    user input is gathered.
    """


class CircularVarDependencyError(WorkflowGraphError):
    """
    Raised when the vars block contains a cycle.

    E.g. vars.a = ref:vars.b and vars.b = ref:vars.a. Kept separate from
    CircularDependencyError so the error message can identify whether the cycle is in
    the module graph or the vars subgraph.
    """


#######################################################################################
# WORKFLOW GRAPH
#######################################################################################


class WorkflowGraph:
    """
    Directed graph of module instance dependencies for a single workflow.

    Constructed from a WorkFlowConfig object. Validates the graph for cycles, tracks
    execution status per node, and provides query methods for parallel execution,
    failure cascading, and status reporting.

    Build pipeline (runs in __init__):
        1. _add_nodes()             —> one node per module instance
        2. _resolve_vars()          —> two-phase var resolution (cycle detect + expand)
        3. _build_var_producer_map() —> map var_key -> producing module from output: blocks
        4. _add_data_flow_edges()   —> edges from data_flow input: DSL expressions
        5. _add_hook_edges()        —> edges from hook DSL expressions

    Usage:
        graph = WorkflowGraph(workflow_config)
        graph.validate()
        stages = graph.parallel_stages()
        graph.set_status("conv", NodeStatus.RUNNING)
        graph.mark_failed("preprocess", cascade=True)
    """

    def __init__(self, workflow_config: Any) -> None:
        """
        Build the DAG from a workflow configuration in five phases.

        Args:
            workflow_config: A WorkFlowConfig instance. Expected attributes:
                .modules         — Dict[str, ModuleInstanceConfig]
                .data_flow       — Dict[str, ModuleDataFlow]
                .vars            — Dict[str, Any]
                .execution_order — List[str]

        Raises:
            CircularVarDependencyError: If the vars block has a cycle.
            WorkflowGraphError:         If two modules declare the same var
                                        as an output (duplicate producers).
        """
        self._graph: nx.DiGraph = nx.DiGraph()
        self._config = workflow_config

        self._var_graph: nx.DiGraph = nx.DiGraph()
        self._var_module_deps: Dict[str, List[str]] = {}
        self._var_producer_map: Dict[str, str] = {}
        self._status: Dict[str, NodeStatus] = {}
        self._execution_order: List[str] = list(
            getattr(workflow_config, "execution_order", [])
        )

        self._add_nodes(workflow_config)

        if getattr(workflow_config, "vars", None):
            self._resolve_vars(workflow_config)

        self._build_var_producer_map(workflow_config)  # Phase 3 — before edges
        self._add_data_flow_edges(workflow_config)
        self._add_hook_edges(workflow_config)

        logger.debug(
            "WorkflowGraph built | nodes=%d | edges=%d | var_edges=%d | producers=%d",
            self._graph.number_of_nodes(),
            self._graph.number_of_edges(),
            self._var_graph.number_of_edges(),
            len(self._var_producer_map),
        )

    ###################################################################################
    # NODES
    ###################################################################################

    def _add_nodes(self, config: Any) -> None:
        """
        Phase 1: Create one graph node per module instance in the config.
        """
        for instance_name in config.modules:
            self._graph.add_node(instance_name)
            self._status[instance_name] = NodeStatus.PENDING

        logger.debug("Nodes added | count=%d", len(config.modules))

    ###################################################################################
    # VAR RESOLUTION
    ###################################################################################

    def _resolve_vars(self, config: Any) -> None:
        """
        Phase 2: Resolve workflow-level variables in two phases.
        """
        direct: Dict[str, List[str]] = {}
        var_to_var: Dict[str, List[str]] = {}

        _DSL_PREFIXES = ("ref:", "pattern:", "fn:", "literal:")

        for var_key, expr_val in (config.vars or {}).items():
            if not isinstance(expr_val, str) or not any(
                expr_val.startswith(p) for p in _DSL_PREFIXES
            ):
                logger.debug(
                    "Var '%s' is a constant (non-DSL value) — no deps to resolve",
                    var_key,
                )
                direct[var_key] = []
                var_to_var[var_key] = []
                continue

            expr = parse_expression(expr_val)
            direct[var_key] = expr.get_dependencies()
            var_to_var[var_key] = [v for v in expr.get_var_refs() if v != var_key]

            for ref in var_to_var[var_key]:
                self._var_graph.add_edge(var_key, ref)

        if not nx.is_directed_acyclic_graph(self._var_graph):
            cycle = nx.find_cycle(self._var_graph)
            cycle_str = " -> ".join(f"vars.{v}" for v, _ in cycle)
            raise CircularVarDependencyError(
                f"Circular dependency detected in workflow vars: {cycle_str}"
            )

        for var_key in direct:
            self._var_module_deps[var_key] = list(direct[var_key])

        # ── PHASE B ──────────────────────────────────────────────────────
        if self._var_graph.number_of_nodes() > 0:
            for var_key in nx.topological_sort(self._var_graph):
                for referenced_var in var_to_var.get(var_key, []):
                    for dep in self._var_module_deps.get(referenced_var, []):
                        if dep not in self._var_module_deps[var_key]:
                            self._var_module_deps[var_key].append(dep)

        logger.debug(
            "Vars resolved | total=%d | var_graph_edges=%d | module_deps=%s",
            len(config.vars or {}),
            self._var_graph.number_of_edges(),
            {k: v for k, v in self._var_module_deps.items() if v},
        )

    ###################################################################################
    # VAR PRODUCER MAP
    ###################################################################################

    def _build_var_producer_map(self, config: Any) -> None:
        """
        Build a map from var key -> the module instance that produces it.

        Scans every output: block across all data_flow entries. Because
        ModuleDataFlow.output_values_must_be_var_refs() enforces that output values
        are ref:vars.<key> expressions, the var key is extracted by a simple string
        strip, no DSL parsing required.

        This map is the foundation of data-production dependency resolution.

        Args:
            config: WorkFlowConfig instance.

        Raises:
            WorkflowGraphError: If two modules declare the same var as output.
                                One var, one producer — ambiguity is an error.
        """
        for instance_name, flow in (config.data_flow or {}).items():
            output_block: Dict[str, str] = getattr(flow, "output", {}) or {}
            for _param, expr_str in output_block.items():
                var_key = expr_str[len("ref:vars.") :]
                if var_key in self._var_producer_map:
                    existing = self._var_producer_map[var_key]
                    raise WorkflowGraphError(
                        f"Multiple producers declared for var '{var_key}': "
                        f"'{existing}' and '{instance_name}' both list it as output. "
                        f"Each workflow var may have at most one producing module."
                    )
                self._var_producer_map[var_key] = instance_name

        logger.debug(
            "Var producer map built | entries=%d | map=%s",
            len(self._var_producer_map),
            self._var_producer_map,
        )

    ###################################################################################
    # SHARED DEPENDENCY RESOLVER
    ###################################################################################

    def _get_transitive_producers(self, var_key: str) -> List[str]:
        """
        Return all module producers reachable from var_key through var-to-var deps.

        Args:
            var_key: Starting var key (without the vars. namespace prefix).

        Returns:
            Deduplicated list of module instance names that are transitive
            producers for this var.  Empty if none.
        """
        producers: Dict[str, None] = {}  # insertion-ordered deduplication for aliases
        visited: Set[str] = set()
        queue = [var_key]

        while queue:
            vk = queue.pop(0)
            if vk in visited:
                continue
            visited.add(vk)

            if vk in self._var_producer_map:
                producers[self._var_producer_map[vk]] = None

            if vk in self._var_graph:
                for dep_var in self._var_graph.successors(vk):
                    if dep_var not in visited:
                        queue.append(dep_var)

        return list(producers)

    def _resolve_expr_deps(self, expr_str: str) -> List[str]:
        """
        Parse a DSL expression string and resolve ALL module dependencies,
        including both path-construction and data-production deps.

        Three-step resolution (all deduplicated via insertion-ordered dict):

          1. get_dependencies()        — direct module instance refs in the expr
          2. _var_module_deps lookup   — path-construction deps via var expansion
          3. _get_transitive_producers — data-production deps via producer map

        Args:
            expr_str: A DSL expression string (ref:, pattern:, fn:, literal:).

        Returns:
            Deduplicated list of module instance names this expression depends
            on (all kinds combined). Empty list if none.
        """
        expr = parse_expression(expr_str)

        deps: Dict[str, None] = {}

        for dep in expr.get_dependencies():
            deps[dep] = None

        for var_key in expr.get_var_refs():
            for dep in self._var_module_deps.get(var_key, []):
                deps[dep] = None

            for producer in self._get_transitive_producers(var_key):
                deps[producer] = None

        return list(deps)

    ###################################################################################
    # BUILD PHASE 4 — DATA FLOW EDGES
    ###################################################################################

    def _add_data_flow_edges(self, config: Any) -> None:
        """
        Add edges derived from data_flow input: DSL expressions.
        """
        for target_instance, flow in (config.data_flow or {}).items():
            input_block: Dict[str, str] = getattr(flow, "input", {}) or {}
            for param_name, expr_str in input_block.items():
                deps = self._resolve_expr_deps(expr_str)
                for dep in deps:
                    if dep in self._graph and dep != target_instance:
                        data = self._graph.get_edge_data(
                            dep, target_instance, default={}
                        )
                        edge_types = set(data.get("edge_types", []))
                        edge_types.add("data_flow")

                        params = set(data.get("params", []))
                        params.add(param_name)

                        self._graph.add_edge(
                            dep,
                            target_instance,
                            edge_types=list(edge_types),
                            params=list(params),
                        )
                        logger.debug(
                            "Data flow edge | %s -> %s | param=%s",
                            dep,
                            target_instance,
                            param_name,
                        )

    ###################################################################################
    # BUILD PHASE 5 — HOOK EDGES
    ###################################################################################

    def _add_hook_edges(self, config: Any) -> None:
        """
        Add edges derived from hook DSL expressions.

        Non-existent dependency names are silently skipped.
        """
        HOOK_TYPES = ("pre_run", "post_run", "on_failure", "on_success")

        for instance_name, mod_cfg in config.modules.items():
            hooks_obj = getattr(mod_cfg, "hooks", None)
            if hooks_obj is None:
                continue

            for hook_type in HOOK_TYPES:
                hook_list: List[str] = getattr(hooks_obj, hook_type, [])
                for expr_str in hook_list:
                    deps = self._resolve_expr_deps(expr_str)
                    for dep in deps:
                        if dep in self._graph and dep != instance_name:
                            data = self._graph.get_edge_data(
                                dep, instance_name, default={}
                            )
                            edge_types = set(data.get("edge_types", []))
                            edge_types.add("hook")

                            hook_types = set(data.get("hook_types", []))
                            hook_types.add(hook_type)

                            self._graph.add_edge(
                                dep,
                                instance_name,
                                edge_types=list(edge_types),
                                hook_types=list(hook_types),
                            )
                            logger.debug(
                                "Hook edge | %s -> %s | hook_type=%s",
                                dep,
                                instance_name,
                                hook_type,
                            )

    ###################################################################################
    # VALIDATION
    ###################################################################################

    def validate(self) -> None:
        """
        Validate the module graph for acyclicity.

        Var cycles are already detected (and raised) during _resolve_vars() at
        construction time, so this method only checks the module graph.

        Raises:
            CircularDependencyError: If the module graph contains a cycle.
        """
        if not nx.is_directed_acyclic_graph(self._graph):
            cycle = nx.find_cycle(self._graph)
            cycle_str = " -> ".join(f"'{u}'" for u, _ in cycle)
            raise CircularDependencyError(
                f"Circular dependency detected in workflow graph: {cycle_str}"
            )

        logger.info(
            "Workflow DAG validated | nodes=%d | edges=%d | acyclic=True",
            self._graph.number_of_nodes(),
            self._graph.number_of_edges(),
        )

    ###################################################################################
    # STATUS TRACKING
    ###################################################################################

    def set_status(self, instance_name: str, status: NodeStatus) -> None:
        """
        Update the runtime status of a module instance node.

        Raises:
            KeyError: If instance_name is not a registered node.
        """
        if instance_name not in self._status:
            raise KeyError(
                f"Unknown module instance '{instance_name}'. "
                f"Known instances: {sorted(self._status)}"
            )
        self._status[instance_name] = status

    def mark_failed(self, instance_name: str, cascade: bool = True) -> None:
        """
        Mark a module instance as FAILED and optionally cascade to descendants.

        When cascade=True, every DONE descendant is reset to PENDING so
        downstream modules are re-executed on the next retry.
        """
        self._status[instance_name] = NodeStatus.FAILED
        logger.debug("Node marked FAILED | instance=%s", instance_name)

        if cascade:
            for descendant in nx.descendants(self._graph, instance_name):
                if self._status.get(descendant) == NodeStatus.DONE:
                    self._status[descendant] = NodeStatus.PENDING
                    logger.debug(
                        "Cascade reset to PENDING | instance=%s | due_to=%s",
                        descendant,
                        instance_name,
                    )

    def status_summary(self) -> Dict[str, str]:
        """
        Return a snapshot of all node statuses as {instance_name: status_name}.
        """
        return {name: status.name for name, status in self._status.items()}

    ###################################################################################
    # QUERY METHODS
    ###################################################################################

    def parallel_stages(self) -> List[List[str]]:
        """
        Group nodes into stages that can execute in parallel.

        Each stage is a list of module instances with no interdependencies. Stages are
        ordered: every node in stage n must complete before any node in stage n+1 can
        start.
        """
        order_index: Dict[str, int] = {
            name: i for i, name in enumerate(self._execution_order)
        }
        return [
            sorted(stage, key=lambda n: order_index.get(n, 999))
            for stage in nx.topological_generations(self._graph)
        ]

    def ready_to_run(self) -> List[str]:
        """
        Return all PENDING module instances whose dependencies are satisfied.

        A node is ready when its status is PENDING and all predecessors are DONE.
        """
        ready: List[str] = []
        for node in nx.topological_sort(self._graph):
            if self._status.get(node) != NodeStatus.PENDING:
                continue
            predecessors = list(self._graph.predecessors(node))
            if all(self._status.get(p) == NodeStatus.DONE for p in predecessors):
                ready.append(node)
        return ready

    ###################################################################################
    # DOT EXPORT
    ###################################################################################

    def to_dot(
        self,
        path: Optional[str] = None,
        *,
        show_status: bool = True,
        show_vars: bool = False,
        show_stages: bool = True,
        show_legend: bool = True,
        title: str | None = None,
    ) -> str:
        """
        Return a Graphviz DOT string for the workflow graph.
        """

        def _attr(**kw: Any) -> str:
            return " ".join(f'{k}="{v}"' for k, v in kw.items() if v is not None)

        graph_label = (
            title if title is not None else getattr(self._config, "name", "workflow")
        )

        lines: list[str] = [
            "digraph workflow {",
            f"    graph [{_attr(label=graph_label, labelloc='t', fontname='Helvetica', fontsize='14', rankdir='LR')}];",
            f"    node  [{_attr(shape='box', fontname='Helvetica', fontsize='11')}];",
            f"    edge  [{_attr(fontname='Helvetica', fontsize='9')}];",
            "",
        ]

        if show_stages:
            for i, stage in enumerate(self.parallel_stages()):
                lines.append(f"    subgraph cluster_stage_{i} {{")
                lines.append('        graph [style="invis"];')
                lines.append("        rank=same;")
                for node in stage:
                    lines.append(f'        "{node}";')
                lines.append("    }\n")

        for name in self._graph.nodes():
            node_attrs: dict[str, str] = {"label": name, "style": "filled,rounded"}
            if show_status:
                status = self._status.get(name, NodeStatus.PENDING)
                node_attrs.update(_DOT_STATUS_ATTRS.get(status, {}))
                node_attrs["tooltip"] = status.name
            lines.append(f'    "{name}" [{_attr(**node_attrs)}];')

        lines.append("")

        for src, dst, data in self._graph.edges(data=True):
            edge_attrs: dict[str, str] = {}
            types = data.get("edge_types", [])
            if "hook" in types and "data_flow" not in types:
                edge_attrs.update({"style": "dashed", "color": "gray"})
            lines.append(f'    "{src}" -> "{dst}" [{_attr(**edge_attrs)}];')

        if show_vars and hasattr(self, "_var_module_deps") and self._var_module_deps:
            lines.append("\n    subgraph cluster_vars {")
            lines.append(
                f"        graph [{_attr(label='vars', style='dashed', color='gray')}];"
            )
            lines.append(
                f"        node  [{_attr(shape='ellipse', fillcolor='lightyellow', style='filled', fontname='Helvetica', fontsize='9')}];"
            )
            for var_key in self._var_module_deps:
                lines.append(f'        "vars.{var_key}";')
            lines.append("    }\n")
            for var_key, module_deps in self._var_module_deps.items():
                for dep in module_deps:
                    lines.append(
                        f'    "{dep}" -> "vars.{var_key}" [{_attr(style="dashed", color="gray")}];'
                    )

        if show_legend and show_status:
            lines.append("\n    subgraph cluster_legend {")
            lines.append(
                '        graph [label="Legend", fontsize="10", color="gray70"];'
            )
            for status, attrs in _DOT_STATUS_ATTRS.items():
                lines.append(
                    f'        "legend_{status.name}" [{_attr(label=status.name, **attrs)}];'
                )
            lines.append("    }")

        lines.append("}")
        dot_src = "\n".join(lines)

        if path:
            with open(path, "w") as f:
                f.write(dot_src)

        return dot_src

    ###################################################################################
    # PRIVATE HELPERS & PROPERTIES
    ###################################################################################

    def _has_node(self, name: str) -> bool:
        """
        Return True if name is a registered module instance node.
        """
        return name in self._graph

    @property
    def nodes(self) -> List[str]:
        """
        All module instance names in the graph.
        """
        return list(self._graph.nodes())

    @property
    def edges(self) -> List[tuple]:
        """
        All dependency edges as (source, target) tuples.
        """
        return list(self._graph.edges())
