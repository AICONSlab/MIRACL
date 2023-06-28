# from pathlib import Path
# import os
import torch
from miracl.seg import ace_generate_patch, ace_deploy_model, ace_patch_stacking


def main(args):

    if torch.cuda.is_available():
        print("CUDA available!")

        # args_parser = aceParser()
        # args = args_parser.parse_args()
        print("The following parameters will be used:\n")
        print(f"  Input file:        {args.input_folder}")
        print(f"  Output file:       {args.output_folder}")
        print(f"  Model type:        {args.model_type}")
        print(f"  Voxel resolutions: {args.voxel_res}")
        print(f"  Image sizes:       {args.image_size}")
        print(f"  Number workers:    {args.nr_workers}")
        print(f"  Cache rate:        {args.cache_rate}")
        print(f"  sw batch size:     {args.sw_batch_size}")
        print(f"  Monte dropout:     {args.monte_dropout}")
        print(f"  Visulize results:  {args.visualize_results}")
        print(f"  Uncertainty map:   {args.uncertainty_map}\n")

        # TODO: Add program logic here

        # tmp_in, tmp_out = ace_generate_patch.main(args.input_folder, args.output_folder)
        #
        # print(f"In: {tmp_in}")
        # print(f"Out: {tmp_out}")

        # INFO: ace_generate_patch.py

        patches_folder = ace_generate_patch.generate_patch_main(
            input_folder=args.input_folder,
            output_folder=args.output_folder
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
            num_workers_var=args.nr_workers
        )

        # INFO: ace_patch_stacking.py

        ace_patch_stacking.run_stacking(
                patches_path=patches_folder,
                main_input_folder_path=args.input_folder,
                output_folder_path=args.output_folder,
                monte_carlo=args.monte_dropout,
                h=args.image_size[0],
                w=args.image_size[1],
                z=args.image_size[2]
                )

    else:
        raise ValueError("No GPU support detected in Docker container. \
Please install MIRACL with GPU passthrough as explained in our docs.")


if __name__ == "__main__":
    main(args)
