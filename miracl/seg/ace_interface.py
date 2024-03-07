# from pathlib import Path
# import os
import torch
from pathlib import Path
from miracl.seg import ace_generate_patch, ace_deploy_model, ace_patch_stacking
import sys


def main(args):

    if torch.cuda.is_available():
        print("CUDA available!")

        input_folder_arg = args.single
        ace_flow_seg_output_folder = Path(args.sa_output_folder) / "seg_final"
        output_folder_arg = ace_flow_seg_output_folder if ace_flow_seg_output_folder.is_dir() else Path(args.sa_output_folder)
        model_type_arg = args.sa_model_type
        voxel_resolutions_arg = args.sa_resolution
        image_sizes_arg = args.sa_image_size
        number_workers_arg = args.sa_nr_workers
        cache_rate_arg = args.sa_cache_rate
        batch_size_arg = args.sa_batch_size
        visualize_results_arg = args.sa_visualize_results
        uncertainty_map_arg = args.sa_uncertainty_map
        forward_passes_arg = args.sa_monte_carlo

        print("The following parameters will be used:\n")
        print(f"  Input folder:      {input_folder_arg}")
        print(f"  Output folder:     {output_folder_arg}")
        print(f"  Model type:        {model_type_arg}")
        print(f"  Voxel resolutions: {voxel_resolutions_arg}")
        print(f"  Image sizes:       {image_sizes_arg}")
        print(f"  Number workers:    {number_workers_arg}")
        print(f"  Cache rate:        {cache_rate_arg}")
        print(f"  sw batch size:     {batch_size_arg}")
        print(f"  Visualize results: {visualize_results_arg}")
        print(f"  Uncertainty map:   {uncertainty_map_arg}\n")
        print(f"  Forward passes:    {forward_passes_arg}\n")

        # TODO: Add program logic here

        # tmp_in, tmp_out = ace_generate_patch.main(args.input_folder, args.output_folder)
        #
        # print(f"In: {tmp_in}")
        # print(f"Out: {tmp_out}")

        # INFO: ace_generate_patch.py

        patches_folder = ace_generate_patch.generate_patch_main(
            input_folder=input_folder_arg,
            output_folder=output_folder_arg
        )

        print(f"Patches folder path is: {patches_folder}")

        # INFO: ace_deploy_model.py
        # INFO: ace_prepare_model_transform.py is called from within ace_deploy_model.py

        ace_deploy_model.deploy_functions(
            chosen_model=model_type_arg,
            patch_dir_var=patches_folder,
            batch_size_var=batch_size_arg,
            cache_rate_var=cache_rate_arg,
            num_workers_var=number_workers_arg,
            forward_passes_var=forward_passes_arg,
        )

        # INFO: ace_patch_stacking.py

        ace_patch_stacking.run_stacking(
                patches_path=patches_folder,
                main_input_folder_path=input_folder_arg,
                output_folder_path=output_folder_arg,
                monte_carlo=True if forward_passes_arg > 0 else False,
                model_name_var=model_type_arg
                )

    else:
        raise ValueError("No GPU support detected in Docker container. \
Please install MIRACL with GPU passthrough as explained in our docs.")


if __name__ == "__main__":
    main(args)
