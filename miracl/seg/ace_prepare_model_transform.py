"""
This code is written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca
this code uses MONAI and PyTorch for neuron segmentation project
this the inference mode code when the model is trained and ready to use

Inputs:
    Model name; it can be unet, unetr, or ensemble
    a config file which is not defined by user
Outputs:
    Pre-trained model(s)
    Validation transforms


"""
# load libraries
from monai.networks.nets import UNet, UNETR
from monai.transforms import (
    Compose,
    EnsureTyped,
    AddChanneld,
    ScaleIntensityRangePercentilesd,
    Transform,
)
import torch
from monai.networks.layers import Norm
import numpy as np
import yaml
import tifffile
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# -------------------------------------------------------
# load the config file
# -------------------------------------------------------


def generate_model_transforms(chosen_model, cfg_path_var):

    model_name = chosen_model
    CFG_PATH = cfg_path_var

    # -------------------------------------------------------
    # load the config file
    # -------------------------------------------------------

    with open(CFG_PATH, "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # define the model
    def unet_creater(cfg):
        n_layers = cfg["unet"].get("n_encoder_layers", 5)
        initial_channel = cfg["unet"].get("channels_initial", 16)
        model_unet = UNet(
            spatial_dims=3,
            in_channels=1,
            out_channels=2,
            channels=tuple([initial_channel * (2**j) for j in range(n_layers)]),
            strides=tuple([2] * (n_layers - 1)),
            num_res_units=cfg["unet"].get("num_res_unit", 2),
            dropout=cfg["unet"].get("dropout", 0.2),
            norm=Norm.BATCH,
        )
        return model_unet

    def unetr_creater(cfg):
        crop_size = (96, 96, 96)
        model_unetr = UNETR(
            spatial_dims=3,
            in_channels=1,
            out_channels=2,
            img_size=crop_size,
            feature_size=cfg["unetr"].get("feature_size", 16),
            hidden_size=cfg["unetr"].get("hidden_size", 768),
            mlp_dim=cfg["unetr"].get("mlp_dim", 3072),
            num_heads=cfg["unetr"].get("num_heads", 12),
            dropout_rate=cfg["unetr"].get("dropout", 0.2),
            res_block=cfg["unetr"].get("res_block", True),
            norm_name="batch",
        )
        return model_unetr

    if model_name == "unet":
        model_unet = unet_creater(cfg)
    if model_name == "unetr":
        model_unetr = unetr_creater(cfg)
    if model_name == "ensemble":
        model_unet = unet_creater(cfg)
        model_unetr = unetr_creater(cfg)

    print("model(s) are initialized!")
    # -------------------------------------------------------
    # load the model's weights
    # -------------------------------------------------------

    if model_name == "unet":
        model_out = model_unet

    elif model_name == "unetr":
        model_out = model_unetr

    elif model_name == "ensemble":
        model_out = [model_unet, model_unetr]

    # -------------------------------------------------------
    # define transforms
    # -------------------------------------------------------

    # return image_dict
    class MyLoadImage(Transform):
        def __call__(self, image_dict):
            # load the .tiff files they are HxWxD
            # img_path = image_dict['image']
            image_dict["image"] = tifffile.imread(image_dict["image"])
            # print('img_path: ', img_path)
            # change the order axis of the image from DHW to HWD
            image_dict["image"] = np.moveaxis(image_dict["image"], 0, 2)
            image_dict["image"] = np.moveaxis(image_dict["image"], 0, 1)
            return image_dict

    test_transforms = Compose(
        [
            MyLoadImage(),
            AddChanneld(keys=["image"]),
            # ScaleIntensityRangePercentilesd(keys=["image"], lower=0.001, upper=99.99, b_min=0, b_max=1, clip=True, relative=False),
            ScaleIntensityRangePercentilesd(
                keys=["image"],
                lower=0.05,
                upper=99.95,
                b_min=0,
                b_max=1,
                clip=True,
                relative=False,
            ),
            EnsureTyped(keys=["image"]),
        ]
    )

    logging.debug("prepare_model_transform called")

    return model_out, test_transforms
