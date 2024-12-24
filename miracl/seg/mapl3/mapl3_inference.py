"""
This code is written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca
Modified for implementation into MIRACL by Jonas Osmann, j.osmann@alumni.utoronto.ca
this is the inference mode code when the model is trained and ready to use

Main Inputs:
    model, config, and transforms
    path to the generated patches
Outputs:
    a directory conatining: 
        probability maps
        binary outputs 

"""

# load libraries
import os
import argparse
from monai.inferers import sliding_window_inference
from monai.transforms import (
    AsDiscrete,
    Compose,
    ScaleIntensityd,
    EnsureTyped,
    EnsureType,
    AddChanneld,
    Transform,
)
import torch
import torch.nn as nn
from monai.networks.layers import Norm
from monai.data import CacheDataset, DataLoader, decollate_batch, Dataset
import numpy as np
import yaml
import tifffile
import yaml
import model_init
import json
import multiprocessing
import concurrent
import time
from miracl import miracl_logger

logger = miracl_logger.logger

# # Create the parser
# my_parser = argparse.ArgumentParser(description="Working directory")
#
# # Add the arguments
# my_parser.add_argument(
#     "-c",
#     "--config",
#     help="path of config file used during training to defien the model",
#     required=True,
# )
# my_parser.add_argument(
#     "-o",
#     "--output_path",
#     help="if passed it saves the results",
#     required=False,
#     default=False,
# )
# my_parser.add_argument(
#     "-m", "--model_path", help="path of trained model", required=True
# )
# my_parser.add_argument(
#     "-i",
#     "--input_dir",
#     help="path to input directory containing patches",
#     required=True,
# )
# my_parser.add_argument(
#     "-p",
#     "--tissue_precentage_threshold",
#     help="whether to use json file to filter empty patches if passsed must be threshold between 0 and 1",
#     required=False,
#     default=0,
#     type=float,
# )
# my_parser.add_argument(
#     "-g",
#     "--gpu_index",
#     help="gpu index to be used; if you wanna use all the available gpus pass all; default it uses index 0",
#     required=False,
#     default=0,
# )
# my_parser.add_argument(
#     "-t",
#     "--binarization_threshold",
#     help="threshold to binarize the model probabilty map; between 0-1",
#     required=False,
#     default=0.5,
#     type=float,
# )
# my_parser.add_argument(
#     "-s",
#     "--save_prob_map_flag",
#     help="a flag to whether save the prob map",
#     required=False,
#     default=False,
#     action="store_true",
# )


# create dataloader
def create_dataloader(cfg, data_dicts, gpu_id):
    # fdata axis should be H * W * D
    class MyLoadImage(Transform):
        def __call__(self, image_dict):
            # load the .tiff files they are HxWxD
            image_dict["img_path"] = image_dict["image"]
            image_dict["image"] = tifffile.imread(image_dict["image"])

            # change the order axis of the image from DHW to HWD
            image_dict["image"] = np.moveaxis(image_dict["image"], 0, 2)
            image_dict["image"] = np.moveaxis(image_dict["image"], 0, 1)

            return image_dict

    transforms = Compose(
        [
            MyLoadImage(),
            AddChanneld(keys=["image"]),
            ScaleIntensityd(keys=["image"]),
            EnsureTyped(keys=["image"]),
        ]
    )

    # Assign specific CPU cores to this DataLoader
    num_cores = multiprocessing.cpu_count() - 4  # I leave four cpus to avoid freezing
    cores_per_gpu = num_cores // torch.cuda.device_count()

    core_ids = list(
        range(int(gpu_id) * cores_per_gpu, (int(gpu_id) + 1) * cores_per_gpu)
    )

    # Set CPU core affinity for this DataLoader's process (Linux only)
    os.sched_setaffinity(0, core_ids)

    # cache_rate_val = cfg['general'].get('cache_rate_val', 0.01)
    cache_rate_val = 0
    ds = CacheDataset(
        data=data_dicts,
        transform=transforms,
        cache_rate=cache_rate_val,
        num_workers=cores_per_gpu,
    )

    data_loader = DataLoader(
        ds, batch_size=cfg["general"].get("batch_size", 8), num_workers=cores_per_gpu
    )  # Adjust workers per GPU

    return data_loader, core_ids


# create model
def create_model(cfg):

    print("creating the model ...")

    # load the config
    temp_value = cfg["general"].get("network_patch_size", 128)
    network_patch_size = (
        temp_value,
        temp_value,
        temp_value,
    )  # the network image patch size

    N_crops = cfg["general"].get("crop_number", 1)

    temp_value = cfg["general"].get("main_input_img_size", None)
    main_input_img_size = (
        temp_value,
        temp_value,
        temp_value,
    )  # the main input to the model
    in_channels = cfg["model"].get("in_channels")
    out_channels = cfg["model"].get("out_channels")
    final_sigmoid = cfg["model"].get("final_sigmoid")
    if final_sigmoid == "None":
        final_sigmoid = None
    encoder_depth = int(cfg["model"].get("encoder_depth", 5))
    f_maps = cfg["model"].get("f_maps")
    f_maps = tuple([f_maps * (2**j) for j in range(encoder_depth)])
    layer_order = cfg["model"].get("layer_order")
    num_groups = cfg["model"].get("num_groups")
    is_segmentation = cfg["model"].get("is_segmentation")
    conv_kernel_size = cfg["model"].get("conv_kernel_size")
    pool_kernel_size = cfg["model"].get("pool_kernel_size")
    conv_padding = cfg["model"].get("conv_padding")
    is3d = cfg["model"].get("is3d")
    drop_path = cfg["model"].get("drop_path")
    dropout_prob = cfg["model"].get("dropout_prob")
    attention_sum = cfg["model"].get("attention_sum")
    attention_weights = cfg["model"].get("attention_weights")
    # voxel wise attention params
    voxel_wise_attn = cfg["attention_voxel_wise"].get("flag")
    atten_depth_voxel = cfg["attention_voxel_wise"].get("atten_depth")
    num_heads_voxel = cfg["attention_voxel_wise"].get("num_heads")
    mlp_ratio_voxel = cfg["attention_voxel_wise"].get("mlp_ratio")
    qkv_bias_voxel = cfg["attention_voxel_wise"].get("qkv_bias")
    qk_scale_voxel = cfg["attention_voxel_wise"].get("qk_scale")
    if qk_scale_voxel == "None":
        qk_scale_voxel = None
    drop_rate_voxel = cfg["attention_voxel_wise"].get("drop")
    attn_drop_rate_voxel = cfg["attention_voxel_wise"].get("atten_drop")
    attn_drop_path_voxel = cfg["attention_voxel_wise"].get("drop_path")
    encoder_depth_voxel = int(cfg["attention_voxel_wise"].get("encoder_depth_voxel"))
    atten_dim_voxel = int(f_maps[encoder_depth_voxel - 1])
    if voxel_wise_attn:
        print(
            "Attention dimension / embedding size for voxel wise attention is: ",
            atten_dim_voxel,
        )

    # patch wise attention params
    patch_wise_attn = cfg["attention_patch_wise"].get("flag")
    patch_wise_attn_down = cfg["attention_patch_wise"].get("down_flag")
    patch_wise_attn_down_factor = cfg["attention_patch_wise"].get("down_factor")
    patch_wise_adaptive_thr = cfg["attention_patch_wise"].get("adaptive_thr")
    patch_wise_PE_3D = cfg["attention_patch_wise"].get("patch_wise_PE_3D")
    atten_depth_patch = cfg["attention_patch_wise"].get("atten_depth")
    num_heads_patch = cfg["attention_patch_wise"].get("num_heads")
    mlp_ratio_patch = cfg["attention_patch_wise"].get("mlp_ratio")
    qkv_bias_patch = cfg["attention_patch_wise"].get("qkv_bias")
    qk_scale_patch = cfg["attention_patch_wise"].get("qk_scale")
    if qk_scale_patch == "None":
        qk_scale_patch = None
    drop_rate_patch = cfg["attention_patch_wise"].get("drop")
    attn_drop_rate_patch = cfg["attention_patch_wise"].get("atten_drop")
    attn_drop_path_patch = cfg["attention_patch_wise"].get("drop_path")
    encoder_depth_patch = int(cfg["attention_patch_wise"].get("encoder_depth_patch"))
    atten_dim_patch = int(
        f_maps[encoder_depth_patch - 1]
        * ((network_patch_size[0] / (2 ** (encoder_depth_patch - 1))) ** 3)
    )
    if patch_wise_attn:
        if patch_wise_attn_down:
            atten_dim_patch = int(atten_dim_patch / patch_wise_attn_down_factor)
        print(
            "Attention dimenstion / embedding size for pacth wise attention is: ",
            atten_dim_patch,
        )

    deep_supervision = cfg["loss"].get("deep_supervision_level")
    deep_supervision = np.clip(deep_supervision, 0, encoder_depth)

    model_name = cfg["general"].get("model_name")
    if model_name == "unetr":
        # model = UNETR(
        #     spatial_dims=3,
        #     in_channels=1,
        #     out_channels=2,
        #     img_size=main_input_img_size,
        #     feature_size=cfg['unetr'].get('feature_size', 16),
        #     hidden_size=cfg['unetr'].get('hidden_size', 768),
        #     mlp_dim=cfg['unetr'].get('mlp_dim', 3072),
        #     num_heads=cfg['unetr'].get('num_heads', 12),
        #     dropout_rate=cfg['unetr'].get('dropout', 0.2),
        #     res_block=cfg['unetr'].get('res_block', True),
        #     norm_name='batch'
        #     )
        print("!!!")

    else:
        # load the model
        model = model_init.ResidualUNet3D(
            in_channels=in_channels,
            out_channels=out_channels,
            final_sigmoid=final_sigmoid,
            conv_kernel_size=conv_kernel_size,
            pool_kernel_size=pool_kernel_size,
            is3d=is3d,
            img_size=main_input_img_size,
            crop_size=network_patch_size,
            f_maps=f_maps,
            layer_order=layer_order,
            num_groups=num_groups,
            num_levels=encoder_depth,
            is_segmentation=is_segmentation,
            attention_sum=attention_sum,
            conv_padding=conv_padding,
            drop_path=drop_path,
            dropout_prob=dropout_prob,
            attention_weights=attention_weights,
            patch_wise_attn=patch_wise_attn,
            patch_wise_attn_down=patch_wise_attn_down,
            patch_wise_attn_down_factor=patch_wise_attn_down_factor,
            patch_wise_adaptive_thr=patch_wise_adaptive_thr,
            patch_wise_PE_3D=patch_wise_PE_3D,
            encoder_depth_patch=encoder_depth_patch,
            atten_dim_patch=atten_dim_patch,
            atten_depth_patch=atten_depth_patch,
            num_heads_patch=num_heads_patch,
            mlp_ratio_patch=mlp_ratio_patch,
            qkv_bias_patch=qkv_bias_patch,
            qk_scale_patch=qk_scale_patch,
            drop_rate_patch=drop_rate_patch,
            attn_drop_rate_patch=attn_drop_rate_patch,
            attn_drop_path_patch=attn_drop_path_patch,
            norm_layer_patch=nn.LayerNorm,
            voxel_wise_attn=voxel_wise_attn,
            encoder_depth_voxel=encoder_depth_voxel,
            atten_dim_voxel=atten_dim_voxel,
            atten_depth_voxel=atten_depth_voxel,
            num_heads_voxel=num_heads_voxel,
            mlp_ratio_voxel=mlp_ratio_voxel,
            qkv_bias_voxel=qkv_bias_voxel,
            qk_scale_voxel=qk_scale_voxel,
            drop_rate_voxel=drop_rate_voxel,
            attn_drop_rate_voxel=attn_drop_rate_voxel,
            attn_drop_path_voxel=attn_drop_path_voxel,
            norm_layer_voxel=nn.LayerNorm,
            deep_supervision=deep_supervision,
        )

    return model


# This will take image, prediction, labels, and save them in the root dir
def image_saver(root_dir, name, outputs=None, thr=0.5, save_prob=False):
    name_parts = name.split("/")
    name = name_parts[-4] + "_" + name_parts[-1]

    post_pred = Compose(
        [EnsureType(), AsDiscrete(threshold=thr), AsDiscrete(to_onehot=2)]
    )

    outputs = torch.nn.functional.softmax(outputs, dim=1)[:, 1:, ...]

    if save_prob:

        out = outputs.cpu().detach().numpy()[0, 0, ...]
        out = np.moveaxis(out, 1, 0)
        out = np.moveaxis(out, 2, 0)
        tifffile.imwrite(
            os.path.join(root_dir, f"out_prob_{name}"),
            out,
            metadata={
                "DimensionOrder": "ZYX",
                "SizeC": 1,
                "SizeT": 1,
                "SizeX": out.shape[0],
                "SizeY": out.shape[1],
                "SizeZ": out.shape[2],
            },
        )

        outputs = [post_pred(i) for i in decollate_batch(outputs)]

        out = outputs[0].cpu().detach().numpy()[1, ...]
        out = np.moveaxis(out, 1, 0)
        out = np.moveaxis(out, 2, 0)

        tifffile.imwrite(
            os.path.join(root_dir, f"out_{name}"),
            out.astype(np.bool_),
            metadata={
                "DimensionOrder": "ZYX",
                "SizeC": 1,
                "SizeT": 1,
                "SizeX": out.shape[0],
                "SizeY": out.shape[1],
                "SizeZ": out.shape[2],
            },
        )


# Parallel Inference function
def run_inference_on_gpu(
    cfg,
    bin_thr,
    save_prob_map_flag,
    output_dir,
    model,
    dataloader,
    device,
    gpu_id,
    core_ids,
):

    print(f"Starting inference on GPU {gpu_id} ...")
    # Set CPU core affinity for this DataLoader's process (Linux only)
    os.sched_setaffinity(0, core_ids)
    print(f"Current CPU affinity for GPU {gpu_id}: {os.sched_getaffinity(0)}")

    model.eval()
    roi_size = tuple([cfg["general"].get("main_input_img_size", None)] * 3)
    sw_batch_size = 1

    with torch.no_grad():

        for i, data in enumerate(dataloader):

            inputs = data["image"].to(device)
            print(f"Processing {data['img_path'][0]} on {device}")

            outputs = sliding_window_inference(inputs, roi_size, sw_batch_size, model)

            # save the images as .tiff file readable by Fiji
            image_saver(
                root_dir=output_dir,
                name=data["img_path"][0],
                outputs=outputs,
                thr=bin_thr,
                save_prob=save_prob_map_flag,
            )

    print(f"Inference on GPU {device} complete!")
    return True


# main function
def main(
    generate_patch_output_folder,
    inference_output_folder,
    inference_config,
    inference_model_path,
    inference_tissue_percentage_threshold,
    inference_gpu_index,
    inference_binarization_threshold,
):
    # -------------------------------------------------------
    # get the args
    # -------------------------------------------------------
    config_path = inference_config.filepath
    with open(config_path, "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    print("config file is loaded ...")

    output_dir = args["output_path"]
    isExist = os.path.exists(output_dir)
    if not isExist:
        os.mkdir(output_dir)

    input_path = generate_patch_output_folder.dirpath
    percentage_brain_patch_skip = inference_tissue_percentage_threshold.content
    model_path = inference_model_path.filepath
    gpu_index = inference_gpu_index.content
    binarization_threshold = inference_binarization_threshold.content
    save_prob_map_flag = args["save_prob_map_flag"]
    # -------------------------------------------------------
    # Read generate_patch directory / created by generate_patch.py
    # -------------------------------------------------------
    print("preparing dataset ...")

    images_val = []

    with os.scandir(input_path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.lower().endswith((".tif", ".tiff")):
                images_val.append(os.path.join(input_path, entry.name))

    if percentage_brain_patch_skip > 0:
        # load in percentage_brain_patch.json
        with open(os.path.join(input_path, "percentage_brain_patch.json")) as f:
            percentage_brain_patch = json.load(f)

        # filter through images val based on percentage threshold
        images_val_non_empty = [
            os.path.join(input_path, image)
            for image in images_val
            if percentage_brain_patch[image] > percentage_brain_patch_skip
        ]
        images_val_non_empty.sort()

        images_val_empty = [
            os.path.join(input_path, image)
            for image in images_val
            if percentage_brain_patch[image] <= percentage_brain_patch_skip
        ]
        images_val_empty.sort()

        images_val = images_val_non_empty

    data_dicts = [{"image": image_name} for image_name in images_val]
    print("Data dicts are ready!")
    print(f"Some samples from data dicts: {data_dicts[:3]}")
    print(
        f"In total we have {len(data_dicts)} data dicts that the model will be deployed on"
    )

    # -------------------------------------------------------
    # GPU selection and split the data
    # -------------------------------------------------------
    models = []
    devices = []
    data_loaders = []
    core_ids = []
    if gpu_index != "all":

        # define the data loader
        d, ids = create_dataloader(cfg, data_dicts, gpu_index)
        core_ids.append(ids)
        data_loaders.append(d)
        # create model
        models.append(create_model(cfg))

        # put the model on gpu
        # os.environ["CUDA_VISIBLE_DEVICES"] = gpu_index
        devices.append(torch.device(f"cuda:{gpu_index}"))

        models[0].to(devices[0])

        print(
            f"Model is loaded to the device (gpu_index is {devices[0]}) succesfully, core_ids are set to {core_ids[0]}"
        )

    else:

        device_count = torch.cuda.device_count()

        # split the data
        # data_dicts = (torch.chunk(torch.tensor(data_dicts), device_count)).tolist()
        data_dicts = [data_dicts[i::device_count] for i in range(device_count)]
        for i in range(device_count):

            d, ids = create_dataloader(cfg, data_dicts[i], i)
            core_ids.append(ids)
            data_loaders.append(d)
            models.append(create_model(cfg))
            devices.append(torch.device(f"cuda:{i}"))
            models[i].to(devices[i])

            print(
                f"Model is loaded to the device (gpu_index is {devices[i]}) succesfully, core_ids are set to {core_ids[i]}"
            )

    # -------------------------------------------------------
    # Load the trained model
    # -------------------------------------------------------
    for i in range(len(models)):

        models[i].load_state_dict(torch.load(model_path))

    print("Trained model(s) loaded!")
    # -------------------------------------------------------
    # Run inference on GPU(s)
    # -------------------------------------------------------
    if gpu_index != "all":

        start_time = time.time()
        run_inference_on_gpu(
            cfg,
            binarization_threshold,
            save_prob_map_flag,
            output_dir,
            models[0],
            data_loaders[0],
            devices[0],
            gpu_index,
            core_ids[0],
        )
        end_time = time.time()
        execution_time_minutes = (
            end_time - start_time
        ) / 60  # Convert seconds to minutes
        print(f"Execution time on GPU: {execution_time_minutes:.6f} minutes")

    else:

        import time

        print("Starting parallel inference ...")
        start_time = time.time()
        # Use ThreadPoolExecutor for parallel execution
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=device_count
        ) as executor:
            # Submit tasks for each GPU
            futures = [
                executor.submit(
                    run_inference_on_gpu,
                    cfg,
                    binarization_threshold,
                    save_prob_map_flag,
                    output_dir,
                    models[i],
                    data_loaders[i],
                    devices[i],
                    i,
                    core_ids[i],
                )
                for i in range(device_count)
            ]
            # # Collect results (if needed)
            # results = [future.result() for future in concurrent.futures.as_completed(futures)]
        end_time = time.time()
        execution_time_minutes = (
            end_time - start_time
        ) / 60  # Convert seconds to minutes
        print(f"Execution time on GPU: {execution_time_minutes:.6f} minutes")
    print("Inference complete!")

