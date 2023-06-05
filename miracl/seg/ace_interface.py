from miracl.seg import ace_generate_patch


def main(args):
    # args_parser = aceParser()
    # args = args_parser.parse_args()
    print("  The following parameters will be used:\n")
    print(f"  Input file:       {args.input_folder}")
    print(f"  Output file:      {args.output_folder}")
    print(f"  Model type:       {args.model_type}")
    print(f"  Voxel dimensions: {args.voxel_size}")
    print(f"  Visulize results: {args.visualize_results}")
    print(f"  Uncertainty map:  {args.uncertainty_map}\n")

    # TODO: Add program logic here

    # tmp_in, tmp_out = ace_generate_patch.main(args.input_folder, args.output_folder)
    #
    # print(f"In: {tmp_in}")
    # print(f"Out: {tmp_out}")

    # Pass input and output directory args to ace_generate_patch.py
    ace_generate_patch.generate_patch_main(args.input_folder, args.output_folder)


if __name__ == "__main__":
    main(args)
