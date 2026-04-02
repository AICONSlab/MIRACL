from pathlib import Path
import subprocess
import json

TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "cookiecutter" / "miracl-module"


def create_module() -> None:
    """Interactive CLI for creating a MIRACL module."""
    print("📦 MIRACL Module Generator\n")

    module_name = input("Module name: ").strip()
    description = input("Description: ").strip()

    def prompt_list(field_name: str) -> str:
        items = input(f"{field_name} (comma-separated, leave empty if none): ").strip()
        return json.dumps([item.strip() for item in items.split(",") if item.strip()])

    authors = prompt_list("Authors")
    maintainers = prompt_list("Maintainers")
    contributors = prompt_list("Contributors")
    version = input("Version (default 0.1.0): ").strip() or "0.1.0"

    command = [
        "cookiecutter",
        str(TEMPLATE_PATH),
        "--no-input",
        f"module_name={module_name}",
        f"description={description}",
        f"authors={authors}",
        f"maintainers={maintainers}",
        f"contributors={contributors}",
        f"version={version}",
    ]

    subprocess.run(command, check=True)
    print(f"\n✅ Module '{module_name}' created successfully in the current folder.")
