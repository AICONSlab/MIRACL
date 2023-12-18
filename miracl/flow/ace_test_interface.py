# from pathlib import Path
# import os
import torch
import sys
from miracl.seg import ace_generate_patch, ace_deploy_model, ace_patch_stacking


def main(args, flow=False):
    input_file_arg = args.sa_input_folder if flow else args.input_folder
    output_file_arg = args.sa_output_folder if flow else args.output_folder
    model_type_arg = args.sa_model_type if flow else args.model_type
    voxel_resolutions_arg = args.sa_resolution if flow else args.resolution
    image_sizes_arg = args.sa_image_size if flow else args.image_size
    number_workers_arg = args.sa_nr_workers if flow else args.nr_workers
    cache_rate_arg = args.sa_cache_rate if flow else args.cache_rate
    sw_batch_size_arg = args.sa_sw_batch_size if flow else args.sw_batch_size
    monte_dropout_arg = args.sa_monte_dropout if flow else args.monte_dropout
    visualize_results_arg = args.sa_visualize_results if flow else args.visualize_results
    uncertainty_map_arg = args.sa_uncertainty_map if flow else args.uncertainty_map

    if torch.cuda.is_available():
        print("CUDA available!")

        # args_parser = aceParser()
        # args = args_parser.parse_args()
        print("The following parameters will be used:\n")
        print(f"  Input file:        {input_file_arg}")
        print(f"  Output file:       {output_file_arg}")
        print(f"  Model type:        {model_type_arg}")
        print(f"  Voxel resolutions: {voxel_resolutions_arg}")
        print(f"  Image sizes:       {image_sizes_arg}")
        print(f"  Number workers:    {number_workers_arg}")
        print(f"  Cache rate:        {cache_rate_arg}")
        print(f"  sw batch size:     {sw_batch_size_arg}")
        print(f"  Monte dropout:     {monte_dropout_arg}")
        print(f"  Visualize results: {visualize_results_arg}")
        print(f"  Uncertainty map:   {uncertainty_map_arg}\n")

        return output_file_arg
        # sys.exit()

        # TODO: Add program logic here

        # tmp_in, tmp_out = ace_generate_patch.main(args.input_folder, args.output_folder)
        #
        # print(f"In: {tmp_in}")
        # print(f"Out: {tmp_out}")

        # INFO: ace_generate_patch.py

        patches_folder = ace_generate_patch.generate_patch_main(
            input_folder=args.input_folder, output_folder=args.output_folder
        )

        print(f"Patches folder path is: {patches_folder}")

        # INFO: ace_deploy_model.py
        # INFO: ace_prepare_model_transform.py is called from within ace_deploy_model.py

        ace_deploy_model.deploy_functions(
            chosen_model=args.model_type,
            patch_dir_var=patches_folder,
            sw_batch_size_var=args.sw_batch_size,
            monte_var=args.monte_dropout,
            cache_rate_var=args.cache_rate,
            num_workers_var=args.nr_workers,
        )

        # INFO: ace_patch_stacking.py

        ace_patch_stacking.run_stacking(
            patches_path=patches_folder,
            main_input_folder_path=args.input_folder,
            output_folder_path=args.output_folder,
            monte_carlo=args.monte_dropout,
            model_name_var=args.model_type,
        )

    else:
        raise ValueError(
            "No GPU support detected in Docker container. \
Please install MIRACL with GPU passthrough as explained in our docs."
        )


if __name__ == "__main__":
    main(args)
