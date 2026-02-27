from typing import Any, Optional, Iterable
from models import ExecutionContext, ResolvedObject, CommandPlan


def _flatten_list(values: Iterable[Any]) -> list[str]:
    """Flattens and stringifies values for CLI."""
    flat = []
    for v in values:
        if isinstance(v, (list, tuple)):
            flat.extend(_flatten_list(v))
        else:
            flat.append(str(v))
    return flat


class CLISerializer:
    @staticmethod
    def create_plan(
        ctx: ExecutionContext,
        objects: dict[str, ResolvedObject],
        overrides: Optional[dict[str, Any]] = None,
    ) -> CommandPlan:
        # 1. Apply Overrides
        if overrides:
            for name, val in overrides.items():
                if name in objects:
                    objects[name].content = val

        # 2. Validation
        for name, meta in ctx.arg_metadata.items():
            if meta.cli_required and not meta.gui_hidden:
                obj = objects.get(name)
                if obj is None or obj.content is None:
                    raise ValueError(f"Required argument '{name}' is missing.")

        # 3. Construction of Shell Tokens
        tokens = [ctx.script]
        for name, obj in objects.items():
            if obj.content is None:
                continue

            meta = ctx.arg_metadata[name]
            flag = ctx.flag_map.get(f"--{meta.cli_l_flag}", f"--{meta.cli_l_flag}")

            if isinstance(obj.content, (list, tuple)):
                tokens.append(flag)
                tokens.extend(_flatten_list(obj.content))
            elif isinstance(obj.content, bool):
                if obj.content is True:
                    tokens.append(flag)
            else:
                tokens.extend([flag, str(obj.content)])

        return CommandPlan(tokens=tokens, runner=ctx.runner)
