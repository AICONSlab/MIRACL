"""
This code is written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca
this code uses MONAI and PyTorch for neuron segmentation project
this is the inference mode code when the model is trained and ready to use

Inputs:
    model name
    model(s) and transforms
    path to the generated patches
Outputs:
    predictions (binary file of each model with MC_dropout)
    uncertainity
"""
# load libraries
import os
import sys
import pathlib
import argparse
import fnmatch
from monai.inferers import sliding_window_inference
from monai.transforms import (
    AsDiscrete,
    Compose,
    LoadImaged,
    RandCropByPosNegLabeld,
    ScaleIntensityd,
    EnsureTyped,
    EnsureType,
    AddChanneld,
    AsDiscreted,
    ScaleIntensityRangePercentilesd,
    Transform,
)
import torch
from monai.data import CacheDataset, DataLoader, decollate_batch

# from monai.handlers.utils import from_engine
import numpy as np
import yaml
import tifffile

# from prepare_model_transform import generate_model_transforms
from miracl.seg import ace_prepare_model_transform
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# def deploy_functions(chosen_model, patch_dir_var, monte_var):
#     # Define global vars
#     model_name = chosen_model
#     input_path = patch_dir_var
#     CFG_PATH = Path(os.environ["MIRACL_HOME"]) / "seg/config_unetr.yml"
#     MC_flag = monte_var
#
#     # Call generate_model_transforms fn for testing
#     ace_prepare_model_transform.generate_model_transforms(
#             chosen_model=model_name,
#             cfg_path_var=CFG_PATH
#             )
#
#     logging.debug("deploy_model called")


# -------------------------------------------------------
# save function
# -------------------------------------------------------
# this function reorders the order axis of the model output from HWD to DHW or ZYX which is readable by Fiji
# it recieves the subject ID, img, label, and model's output and save them as .tiff files
# this function reorders the order axis of the model output from HWD to DHW or ZYX which is readable by Fiji
# it recieves the subject ID, img, label, and model's output and save them as .tiff files
def save_tiff(img_list, output_path, path):
    # isExist = os.path.exists(output_path)
    # if not isExist:
    #     os.mkdir(output_path)

    img_filename = os.path.join(
        output_path, "img_" + os.path.split(path["image"])[1][:-4] + ".tiff"
    )
    out_filename = os.path.join(
        output_path, "out_" + os.path.split(path["image"])[1][:-4] + ".tiff"
    )

    img_type = ["float32", "uint8"]
    img_filename_list = [img_filename, out_filename]

    for idx, img in enumerate(img_list):
        img = np.array(img)
        img = np.moveaxis(img, 1, 0)
        img = np.moveaxis(img, 2, 0)
        tifffile.imwrite(
            img_filename_list[idx],
            img.astype(img_type[idx]),
            metadata={
                "DimensionOrder": "ZYX",
                "SizeC": 1,
                "SizeT": 1,
                "SizeX": img.shape[0],
                "SizeY": img.shape[1],
                "SizeZ": img.shape[2],
            },
        )


def save_tiff_MC_dropout(img_list, output_path, path):
    # isExist = os.path.exists(output_path)
    # if not isExist:
    #     os.mkdir(output_path)

    MC_filename = os.path.join(
        output_path, "MC_" + os.path.split(path["image"])[1][:-4] + ".tiff"
    )
    uncertainty_filename = os.path.join(
        output_path, "uncertainty_" + os.path.split(path["image"])[1][:-4] + ".tiff"
    )

    img_type = ["float32", "uint8"]
    img_filename_list = [uncertainty_filename, MC_filename]

    for idx, img in enumerate(img_list):
        img = np.array(img)
        img = np.moveaxis(img, 1, 0)
        img = np.moveaxis(img, 2, 0)
        tifffile.imwrite(
            img_filename_list[idx],
            img.astype(img_type[idx]),
            metadata={
                "DimensionOrder": "ZYX",
                "SizeC": 1,
                "SizeT": 1,
                "SizeX": img.shape[0],
                "SizeY": img.shape[1],
                "SizeZ": img.shape[2],
            },
        )


# -------------------------------------------------------
# functions for generating model output
# -------------------------------------------------------


# this function generates outputs using the trained model
def generate_output_single(model_name, model_out):
    def model_loader(model, trained_model_path):
        # move the models to gpu
        model.to(device)
        # load trained model
        model.load_state_dict(torch.load(trained_model_path))
        # set model to eval mode
        model.eval()

    if model_name == "unet":
        # definde crop size / what is used during training
        roi_size = (128, 128, 128)
        sw_batch_size = 4
        model_loader(model_out, cfg["general"].get("model_unet_trained_path"))
    if model_name == "unetr":
        # definde crop size / what is used during training
        roi_size = (96, 96, 96)
        sw_batch_size = 4
        model_loader(model_out, cfg["general"].get("model_unetr_trained_path"))

    with torch.no_grad():
        RI_subj_id = 1

        for i, val_data in enumerate(val_loader):
            print("Data #", RI_subj_id, ", ", data_dicts_test[RI_subj_id - 1])
            val_inputs = val_data["image"].to(device)

            val_outputs = sliding_window_inference(
                val_inputs, roi_size, sw_batch_size, model_out
            )

            val_outputs = [post_pred(i) for i in decollate_batch(val_outputs)]

            # save the images as .tiff file readable by Fiji
            img_list = [
                val_data["image"][0, 0, :, :, :],
                val_outputs[0][1, :, :, :].detach().cpu(),
            ]

            save_tiff(img_list, input_path, data_dicts_test[RI_subj_id - 1])
            RI_subj_id += 1


# this function generates outputs using the trained model and MC dropout techniques
def generate_output_MC(model_name, model_out):
    # number of forward pass
    forward_passes = 50

    # this function only sets the model dropout layesrs to train
    def enable_dropout(model):
        """Function to enable the dropout layers during test-time"""
        for m in model.modules():
            if m.__class__.__name__.startswith("Dropout"):
                m.train()

    def model_loader(model, trained_model_path):
        # move the models to gpu
        model.to(device)
        # load trained model
        model.load_state_dict(torch.load(trained_model_path))
        # set up the model
        model.eval()
        enable_dropout(model)

    if model_name == "unet":
        # definde crop size / what is used during training
        roi_size = (128, 128, 128)
        sw_batch_size = 4
        model_loader(model_out, cfg["general"].get("model_unet_trained_path"))
    if model_name == "unetr":
        # definde crop size / what is used during training
        roi_size = (96, 96, 96)
        sw_batch_size = 4
        model_loader(model_out, cfg["general"].get("model_unetr_trained_path"))

    with torch.no_grad():
        RI_subj_id = 1

        for i, val_data in enumerate(val_loader):
            print("Data #", RI_subj_id, ", ", data_dicts_test[RI_subj_id - 1])
            val_outputs_list = []
            for f in range(forward_passes):
                val_inputs = val_data["image"].to(device)

                val_outputs = sliding_window_inference(
                    val_inputs, roi_size, sw_batch_size, model_out, 0.0
                )

                val_outputs_list.append(val_outputs[0].detach().cpu())

            # stack all the forward passes together
            # use compute_variance function to calculate the uncertainty
            # the should be [N, C, H, W, D] or [N, C, H, W] or [N, C, H] where N is repeats,
            # C is channels and H, W, D stand for Height, Width & Depth

            val_outputs_stack = np.stack(val_outputs_list, axis=0)

            # clear val_output_list for memory efficiency
            del val_outputs_list

            # calculate the uncertainty; channel 0 is background so, we don't want it
            uncertainty = np.var(val_outputs_stack, axis=0)[1, :, :, :]

            # get the average of MC_dropout and send it to GPU for calculating the new dice score
            MC_outputs = torch.Tensor(np.mean(val_outputs_stack, axis=0)).to(device)

            # clear val_outputs_stack for memory efficiency
            del val_outputs_stack

            # prepare the MC outputs for calculating the metrics
            MC_outputs = [
                post_pred(i) for i in decollate_batch(MC_outputs.unsqueeze(0))
            ]

            # save the images as .tiff file readable by Fiji
            img_list = [uncertainty, MC_outputs[0][1, :, :, :].detach().cpu()]

            save_tiff_MC_dropout(img_list, input_path, data_dicts_test[RI_subj_id - 1])

            RI_subj_id += 1


# this function generates outputs using ensemble two models
def generate_output_ensemble(model_out):
    sw_batch_size = 4

    def model_loader(model, trained_model_path):
        # move the models to gpu
        model.to(device)
        # load trained model
        model.load_state_dict(torch.load(trained_model_path))
        # set up the model
        model.eval()

    # model 1
    roi_size_unet = (128, 128, 128)
    model_unet = model_out[0]
    model_loader(model_unet, cfg["general"].get("model_unet_trained_path"))

    # model 2
    roi_size_unetr = (96, 96, 96)
    model_unetr = model_out[1]
    model_loader(model_unetr, cfg["general"].get("model_unetr_trained_path"))

    with torch.no_grad():
        RI_subj_id = 1
        for i, val_data in enumerate(val_loader):
            print("Data #", RI_subj_id, ", ", data_dicts_test[RI_subj_id - 1])

            val_inputs = val_data["image"].to(device)

            val_outputs1 = sliding_window_inference(
                val_inputs, roi_size_unet, sw_batch_size, model_unet, 0.0
            )

            val_outputs2 = sliding_window_inference(
                val_inputs, roi_size_unetr, sw_batch_size, model_unetr, 0.0
            )

            # change the shape of val_outputs from (1, 2, 512, 512, 512) to (2, 512, 512, 512)
            # also move it to cpu
            val_outputs1 = val_outputs1.squeeze(0).detach().cpu()
            val_outputs2 = val_outputs2.squeeze(0).detach().cpu()

            # stack them together --> (2, 2, 512, 512, 512)
            val_outputs = np.stack([val_outputs1, val_outputs2], axis=0)

            # average them together ---> (2, 512, 512, 512)
            # add one channel and change it to tensor ---> (1, 2, 512, 512, 512)
            val_outputs = (
                torch.Tensor(np.mean(val_outputs, axis=0)).unsqueeze(0).to(device)
            )

            val_outputs = [post_pred(i) for i in decollate_batch(val_outputs)]

            # save the images as .tiff file readable by Fiji
            img_list = [
                val_data["image"][0, 0, :, :, :],
                val_outputs[0].detach().cpu()[1, :, :, :],
            ]
            save_tiff(img_list, input_path, data_dicts_test[RI_subj_id - 1])

            RI_subj_id += 1


# this function generates outputs using ensemble of ensembles (averaging two models + MC) technique
def generate_output_ensemble_of_ensembles(model_out):
    # number of forward pass
    forward_passes = 50

    sw_batch_size = 4

    # this function only sets the model dropout layesrs to train
    def enable_dropout(model):
        """Function to enable the dropout layers during test-time"""
        for m in model.modules():
            if m.__class__.__name__.startswith("Dropout"):
                m.train()

    def model_loader(model, trained_model_path):
        # move the models to gpu
        model.to(device)
        # load trained model
        model.load_state_dict(torch.load(trained_model_path))
        # set up the model
        model.eval()
        enable_dropout(model)

    # model 1
    roi_size_unet = (128, 128, 128)
    model_unet = model_out[0]
    model_loader(model_unet, cfg["general"].get("model_unet_trained_path"))

    # model 2
    roi_size_unetr = (96, 96, 96)
    model_unetr = model_out[1]
    model_loader(model_unetr, cfg["general"].get("model_unetr_trained_path"))

    with torch.no_grad():
        RI_subj_id = 1
        for i, val_data in enumerate(val_loader):
            print("Data #", RI_subj_id, ", ", data_dicts_test[RI_subj_id - 1])
            val_outputs_list1 = []
            val_outputs_list2 = []
            for f in range(forward_passes):
                val_inputs = val_data["image"].to(device)

                val_outputs1 = sliding_window_inference(
                    val_inputs, roi_size_unet, sw_batch_size, model_unet, 0.0
                )

                val_outputs2 = sliding_window_inference(
                    val_inputs, roi_size_unetr, sw_batch_size, model_unetr, 0.0
                )

                val_outputs_list1.append(val_outputs1[0].detach().cpu())
                val_outputs_list2.append(val_outputs2[0].detach().cpu())

            val_outputs_stack1 = np.stack(val_outputs_list1, axis=0)
            val_outputs_stack2 = np.stack(val_outputs_list2, axis=0)

            # clear val_output_list for memory efficiency
            del val_outputs_list1
            del val_outputs_list2

            # calculate the uncertainity of model1 and model2
            # then I get the mean of two uncertainty for the final uncertainty
            # calculate the uncertainty; channel 0 is background so, we don't want it
            uncertainty1 = np.var(val_outputs_stack1, axis=0)[1, :, :, :]
            uncertainty2 = np.var(val_outputs_stack2, axis=0)[1, :, :, :]

            uncertainty_stack = np.stack([uncertainty1, uncertainty2], axis=0)
            uncertainty = np.mean(uncertainty_stack, axis=0)

            # clear uncertainty_stack for memory efficiency
            del uncertainty_stack

            MC_outputs1 = np.mean(val_outputs_stack1, axis=0)
            MC_outputs2 = np.mean(val_outputs_stack2, axis=0)

            # clear val_outputs_stack for memory efficiency
            del val_outputs_stack1
            del val_outputs_stack2

            # combine the MC_outputs together to get the average of the two models
            val_outputs_stack = np.stack([MC_outputs1, MC_outputs2], axis=0)

            val_outputs = torch.Tensor(np.mean(val_outputs_stack, axis=0)).to(device)

            # clear val_outputs_stack for memory efficiency
            del val_outputs_stack

            # prepare the MC outputs for calculating the metrics
            val_outputs = [
                post_pred(i) for i in decollate_batch(val_outputs.unsqueeze(0))
            ]

            # save the images as .tiff file readable by Fiji
            img_list = [uncertainty, val_outputs[0][1, :, :, :].detach().cpu()]

            save_tiff_MC_dropout(img_list, input_path, data_dicts_test[RI_subj_id - 1])

            RI_subj_id += 1


# -------------------------------------------------------
# deployment of functions
# -------------------------------------------------------
def deploy_functions(chosen_model, patch_dir_var, monte_var, cache_rate_var, num_workers_var):
    # Define global vars
    model_name = chosen_model
    input_path = patch_dir_var
    CFG_PATH = Path(os.environ["MIRACL_HOME"]) / "seg/config_unetr.yml"
    MC_flag = monte_var

    # -------------------------------------------------------
    # Read generate_patch directory / created by generate_patch.py
    # -------------------------------------------------------
    print("preparing dataset!")

    images_val = []

    with os.scandir(input_path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.lower().endswith((".tif", ".tiff")):
                images_val.append(entry.name)

    images_val.sort()
    images_val = [os.path.join(input_path, image) for image in images_val]
    data_dicts_test = [{"image": image_name} for image_name in images_val]
    print("data dicts are ready!")
    print(f"some samples from data dicts: {data_dicts_test[:3]}")
    print(f"in total we have {len(data_dicts_test)} data dicts")

    # -------------------------------------------------------
    # prepare models, transforms, and data loader
    # -------------------------------------------------------
    model_out, test_transforms = ace_prepare_model_transform.generate_model_transforms(
        model_name, CFG_PATH
    )
    post_pred = Compose([EnsureType(), AsDiscrete(argmax=True, to_onehot=2)])
    post_label = Compose([EnsureType(), AsDiscrete(to_onehot=2)])

    with open(CFG_PATH, "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # GPU selection
    print(f"number of available gpus: {torch.cuda.device_count()}")
    gpu_opt = cfg["general"].get("GPU", "single")
    if gpu_opt == "single":
        device = torch.device("cuda:0")
    else:
        device = torch.device("cuda:0")
        # model = torch.nn.DataParallel(model)
        # model.to(device)

    # define dataloader
    val_ds = CacheDataset(
        data=data_dicts_test,
        transform=test_transforms,
        cache_rate=cache_rate_var,
        num_workers=num_workers_var
    )
    # val_ds = Dataset(data=data_dicts_val, transform=val_transforms)
    val_loader = DataLoader(val_ds, batch_size=1, num_workers=4)

    # # unet alone
    # if model_name == "unet" and not MC_flag:
    #     generate_output_single(model_name, model_out)
    # # unetr alone
    # elif model_name == "unetr" and not MC_flag:
    #     generate_output_single(model_name, model_out)
    # # unet alone + MC dropout
    # elif model_name == "unet" and MC_flag:
    #     generate_output_MC(model_name, model_out)
    # # unetr alone + MC dropout
    # elif model_name == "unetr" and MC_flag:
    #     generate_output_MC(model_name, model_out)
    # # unet + unetr
    # elif model_name == "ensemble" and not MC_flag:
    #     generate_output_ensemble(model_out)
    # # unet + unetr + MC dropout
    # elif model_name == "ensemble" and MC_flag:
    #     generate_output_ensemble_of_ensembles(model_out)
    # else:
    #     raise ValueError("Selected model is invalid")

    logging.debug("deploy_model called")
