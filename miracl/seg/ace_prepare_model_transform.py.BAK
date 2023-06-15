"""
This code is written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca
It uses MONAI and PyTorch for neuron segmentation project. The code inferences
when the model is trained and ready to use.

Inputs:
    Model name: {unet, unetr, ensemble}
    A config file not defined by the user at a static path
Outputs:
    tuple(Pre-trained model(s), Validation transforms)
"""
# load libraries
from monai.networks.nets import UNet, UNETR
from monai.transforms import (
    Compose,
    EnsureTyped,
    AddChanneld,
    ScaleIntensityRangePercentilesd,
    Transform
)
import torch
from monai.networks.layers import Norm
import numpy as np
import yaml
import tifffile
import os
from pathlib import Path


def generate_model_transforms(chosen_model, cfg_path_var):
    model_name = chosen_model
    CFG_PATH = cfg_path_var

    print("prepare_model_transforms called")

# def generate_model_transforms(chosen_model, cfg_path_var):
#     # -------------------------------------------------------
#     # inputs
#     # -------------------------------------------------------
#
#     # model_name = chosen_model
#     model_name = chosen_model
#     # print(os.getcwd())
#     # print(model_name)
#     CFG_PATH = cfg_path_var
#     # print(f"cfg file path: {cfg_path}")
#
#     # -------------------------------------------------------
#     # load the config file
#     # -------------------------------------------------------
#
#     with open(CFG_PATH, "r") as ymlfile:
#         cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
#
#     # print(cfg)
#
#     # n_layers = cfg["unet"].get("n_encoder_layers", 5)
#     model_path_unet = cfg["general"].get("model_unet_trained_path")
#     model_path_unetr = cfg["general"].get("model_unetr_trained_path")
#
#     # print(f"# layers: {n_layers}")
#     # print(f"unet: {model_path_unet}")
#     # print(f"unetr: {model_path_unetr}")
#
#     if torch.cuda.is_available():
#         print("INFO: CUDA is available! Torch device will be set to `GPU`.\n")
#     else:
#         print("WARNING: CUDA is not available! Torch device will be set to \
# 'CPU'.\n")
#
#     # define the model
#     def unet_creator(cfg):
#         n_layers = cfg["unet"].get("n_encoder_layers", 5)
#         initial_channel = cfg["unet"].get("channels_initial", 16)
#         model_unet = UNet(
#             spatial_dims=3,
#             in_channels=1,
#             out_channels=2,
#             channels=tuple([initial_channel * (2**j) for j in range(n_layers)]),
#             strides=tuple([2] * (n_layers - 1)),
#             num_res_units=cfg["unet"].get("num_res_unit", 2),
#             dropout=cfg["unet"].get("dropout", 0.2),
#             norm=Norm.BATCH,
#         )
#         return model_unet
#
#     def unetr_creator(cfg):
#         crop_size = (96, 96, 96)
#         model_unetr = UNETR(
#             spatial_dims=3,
#             in_channels=1,
#             out_channels=2,
#             img_size=crop_size,
#             feature_size=cfg["unetr"].get("feature_size", 16),
#             hidden_size=cfg["unetr"].get("hidden_size", 768),
#             mlp_dim=cfg["unetr"].get("mlp_dim", 3072),
#             num_heads=cfg["unetr"].get("num_heads", 12),
#             dropout_rate=cfg["unetr"].get("dropout", 0.2),
#             res_block=cfg["unetr"].get("res_block", True),
#             norm_name="batch",
#         )
#         return model_unetr
#
#     model_path_unet = cfg["general"].get("model_unet_trained_path")
#     model_path_unetr = cfg["general"].get("model_unetr_trained_path")
#
#     if model_name == "unet":
#         model_unet = unet_creator(cfg)
#         if torch.cuda.is_available():
#             model_unet.load_state_dict(torch.load(model_path_unet))
#         else:
#             model_unet.load_state_dict(torch.load(model_path_unet, map_location="cpu"))
#         model_out = model_unet
#         print(f"Trained {model_name} model is initialized and loaded!\n")
#
#     elif model_name == "unetr":
#         model_unetr = unetr_creator(cfg)
#         if torch.cuda.is_available():
#             model_unetr.load_state_dict(torch.load(model_path_unetr))
#         else:
#             state_dict = torch.load(model_path_unet, map_location="cpu")
#             # expected_keys = model_unetr.state_dict().keys()
#             # print(f"State dict: {state_dict.items()}")
#             # print(f"State dict: {state_dict.keys()}")
#             # print(f"Expected UNETR keys: {expected_keys}")
#             # # state_dict = {k: v for k, v in state_dict.keys() if k in expected_keys}
#             # state_dict = {key: state_dict[key] for key in state_dict if key in expected_keys}
#             # print("Loading state dict")
#             model_unetr.load_state_dict(state_dict, strict=False)
#         model_out = model_unetr
#         print(f"Trained {model_name} model is initialized and loaded!\n")
#
#     else:
#         model_unet, model_unetr = unet_creator(cfg), unetr_creator(cfg)
#         if torch.cuda.is_available():
#             model_unet.load_state_dict(torch.load(model_path_unet))
#             model_unetr.load_state_dict(torch.load(model_path_unetr))
#         else:
#             model_unet.load_state_dict(torch.load(model_path_unet, map_location="cpu"))
#             model_unetr.load_state_dict(
#                 torch.load(model_path_unetr, map_location="cpu")
#             )
#         # FIX: This cannot be returned as a list. Most likely it will have
#         # to be unpacked as a tuple?
#         model_out = [model_unet, model_unetr]
#         print("unet and unetr models are initialized and loaded!\n")
#
#     # print("Trained model(s) are initialized and loaded!")
#     # -------------------------------------------------------
#     # load the model's weights
#     # -------------------------------------------------------
#     # model_path_unet = cfg["general"].get("model_unet_trained_path")
#     # model_path_unetr = cfg["general"].get("model_unetr_trained_path")
#
#     # if model_name == "unet":
#     #     model_unet.load_state_dict(torch.load(model_path_unet))
#     #     model_out = model_unet
#     #
#     # elif model_name == "unetr":
#     #     model_unetr.load_state_dict(torch.load(model_path_unetr))
#     #     model_out = model_unetr
#     #
#     # elif model_name == "ensemble":
#     #     model_unet.load_state_dict(torch.load(model_path_unet))
#     #     model_unetr.load_state_dict(torch.load(model_path_unetr))
#     #     model_out = [model_unet, model_unetr]
#
#     # print("Trained model(s) are loaded!")
#
#     # -------------------------------------------------------
#     # define transforms
#     # -------------------------------------------------------
#
#     # return image_dict
#     class MyLoadImage(Transform):
#         def __call__(self, image_dict):
#             # load the .tiff files they are HxWxD
#             # img_path = image_dict['image']
#             image_dict["image"] = tifffile.imread(image_dict["image"])
#             # print('img_path: ', img_path)
#             # change the order axis of the image from DHW to HWD
#             image_dict["image"] = np.moveaxis(image_dict["image"], 0, 2)
#             image_dict["image"] = np.moveaxis(image_dict["image"], 0, 1)
#             return image_dict
#
#     test_transforms = Compose(
#         [
#             MyLoadImage(),
#             AddChanneld(keys=["image"]),
#             # ScaleIntensityRangePercentilesd(keys=["image"], lower=0.001, upper=99.99, b_min=0, b_max=1, clip=True, relative=False),
#             ScaleIntensityRangePercentilesd(
#                 keys=["image"],
#                 lower=0.05,
#                 upper=99.95,
#                 b_min=0,
#                 b_max=1,
#                 clip=True,
#                 relative=False,
#             ),
#             EnsureTyped(keys=["image"]),
#         ]
#     )
#
#     return model_out, test_transforms
#
#     # -------------------------------------------------------
#     # define transforms
#     # -------------------------------------------------------
#
#     # # return image_dict
#     # class MyLoadImage(Transform):
#     #     def __call__(self, img_path):
#     #         # load the .tiff files they are HxWxD
#     #         image = tifffile.imread(img_path)
#     #         # change the order axis of the image from DHW to HWD
#     #         image = np.moveaxis(image, 0, 2)
#     #         image = np.moveaxis(image, 0, 1)
#     #         return image
#     #
#     # val_transforms = Compose(
#     #     [
#     #         MyLoadImage(),
#     #         AddChannel(),
#     #         ScaleIntensityRangePercentiles(
#     #             keys=["image"],
#     #             lower=0.05,
#     #             upper=99.95,
#     #             b_min=0,
#     #             b_max=1,
#     #             clip=True,
#     #             relative=False,
#     #         ),
#     #         EnsureType(),
#     #     ]
#     # )
#     #
#     # return model_out, val_transforms
#     # return model_out
