def main(args):
    # TODO: Add program logic here
    print(f"Input file: {args.input_folder}")
    print(f"Output file: {args.output_folder}")
    print(f"Model type: {args.model_type}")
    print(f"Voxel dimensions: {args.voxel_size}")
    print(f"Visulize results: {args.visualize_results}")
    print(f"Uncertainty map: {args.uncertainty_map}")
    # if args.visualize_results:
    #     print("Visualization enabled")
    # if args.uncertainty_map:
    #     print("Map enabled")


if __name__ == "__main__":
    main(args)
