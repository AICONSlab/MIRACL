#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys
import libcst as cst
from libcst import matchers as m


# ============================================================
# Transformer
# ============================================================


class MiraclObjTransformer(cst.CSTTransformer):
    def leave_Call(self, original_node, updated_node):
        if not m.matches(original_node.func, m.Name("MiraclObj")):
            return updated_node

        return self._rewrite_miracl_obj(original_node)

    # --------------------------------------------------------

    def _rewrite_miracl_obj(self, node: cst.Call) -> cst.Call:
        cli_args = []
        gui_args = []
        other_args = []
        flow_arg = None

        for arg in node.args:
            if arg.keyword is None:
                other_args.append(arg)
                continue

            key = arg.keyword.value

            if key.startswith("cli_"):
                cli_args.append((key.replace("cli_", ""), arg.value))

            elif key.startswith("gui_"):
                gui_args.append((key.replace("gui_", ""), arg.value))

            elif key == "flow":
                flow_arg = arg

            else:
                other_args.append(arg)

        new_args = list(other_args)

        cli_spec = self._build_cli_spec(cli_args)
        if cli_spec:
            new_args.append(cli_spec)

        gui_spec = self._build_gui_namespace(gui_args)
        if gui_spec:
            new_args.append(gui_spec)

        flow_spec = self._rewrite_flow(flow_arg)
        if flow_spec:
            new_args.append(flow_spec)

        return node.with_changes(args=new_args)

    # --------------------------------------------------------

    def _build_cli_spec(self, cli_args):
        if not cli_args:
            return None

        return cst.Arg(
            keyword=cst.Name("cli"),
            value=cst.Call(
                func=cst.Name("CLISpec"),
                args=[
                    cst.Arg(keyword=cst.Name(name), value=value)
                    for name, value in cli_args
                ],
            ),
        )

    # --------------------------------------------------------

    def _build_gui_namespace(self, gui_args):
        if not gui_args:
            return None

        return cst.Arg(
            keyword=cst.Name("gui"),
            value=cst.Call(
                func=cst.Name("GuiNamespace"),
                args=[
                    cst.Arg(keyword=cst.Name(name), value=value)
                    for name, value in gui_args
                ],
            ),
        )

    # --------------------------------------------------------

    def _rewrite_flow(self, flow_arg):
        if flow_arg is None:
            return None

        if not isinstance(flow_arg.value, cst.Dict):
            return flow_arg

        new_elements = []

        for element in flow_arg.value.elements:
            if element is None:
                continue

            key = element.key
            value = element.value

            if not isinstance(value, cst.Dict):
                new_elements.append(element)
                continue

            cli_delta_args = []

            for sub in value.elements:
                if sub is None:
                    continue

                if not isinstance(sub.key, cst.SimpleString):
                    continue

                sub_key = sub.key.value.strip('"').strip("'")

                if sub_key.startswith("cli_"):
                    new_key = sub_key.replace("cli_", "")
                    cli_delta_args.append(
                        cst.Arg(
                            keyword=cst.Name(new_key),
                            value=sub.value,
                        )
                    )

            flow_override = cst.Call(
                func=cst.Name("FlowOverride"),
                args=[
                    cst.Arg(
                        keyword=cst.Name("cli"),
                        value=cst.Call(
                            func=cst.Name("CLIDelta"),
                            args=cli_delta_args,
                        ),
                    )
                ],
            )

            new_elements.append(
                cst.DictElement(
                    key=key,
                    value=flow_override,
                )
            )

        return cst.Arg(
            keyword=cst.Name("flow"),
            value=cst.Dict(new_elements),
        )


# ============================================================
# File Processing
# ============================================================


def process_file(path: Path, dry_run: bool):
    source = path.read_text()

    try:
        module = cst.parse_module(source)
    except Exception as e:
        print(f"❌ Failed to parse {path}: {e}")
        return

    transformer = MiraclObjTransformer()
    modified = module.visit(transformer)

    if modified.code != source:
        print(f"✔ Migrated: {path}")

        if not dry_run:
            path.write_text(modified.code)
    else:
        print(f"– No changes: {path}")


def process_path(target: Path, dry_run: bool):
    if target.is_file() and target.suffix == ".py":
        process_file(target, dry_run)
        return

    if target.is_dir():
        for py_file in target.rglob("*.py"):
            process_file(py_file, dry_run)
        return

    print(f"Invalid target: {target}")


# ============================================================
# CLI
# ============================================================


def main():
    parser = argparse.ArgumentParser(
        description="Migrate MiraclObj flat fields to structured API."
    )
    parser.add_argument("path", help="File or directory to migrate")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )

    args = parser.parse_args()

    target = Path(args.path)

    if not target.exists():
        print("Path does not exist.")
        sys.exit(1)

    process_path(target, args.dry_run)


if __name__ == "__main__":
    main()
