from miracl.system.registry.registry_loader import load_modules_from_yaml
from miracl.system.datamodels.to_argparse_class_test import MiraclCLIBuilder


def main():
    reg = load_modules_from_yaml("/code/miracl/system/registry/configs/modules.yaml")

    cli_builder = MiraclCLIBuilder(reg)
    parser = cli_builder.build_parser()
    args, parsed_objs = cli_builder.parse()

    reg.list_modules()

    # info = reg.list_modules(verbose=False)
    # print(info["preprocessing_parallel"]["script"])


if __name__ == "__main__":
    main()
