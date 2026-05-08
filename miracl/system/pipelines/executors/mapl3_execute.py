# Safely handle the environment (must always be at the top!!!)
from miracl.system.runtime.bootstrap import configure_runtime

configure_runtime()

# Import the runtime framework
from miracl.system.runtime.runtime import MiraclRuntime

if __name__ == "__main__":
    runtime = MiraclRuntime(
        registry_config="/code/miracl/system/pipelines/configs/registries/mapl3_module_config.yaml",
        workflow_config="/code/miracl/system/pipelines/configs/workflows/mapl3_workflow_config.yaml",
    )

    # Send it!!!
    results = runtime.run()
