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
    EnsureType,
    AddChannel,
    ScaleIntensityRangePercentiles,
    Transform
)
import torch
from monai.networks.layers import Norm
import numpy as np
import yaml
import tifffile 

# -------------------------------------------------------
# inputs
# -------------------------------------------------------

model_name = ...
cfg_path = ...
    
   
# -------------------------------------------------------
# load the config file
# -------------------------------------------------------

def generate_model_transforms():
    
    # -------------------------------------------------------
    # load the config file
    # -------------------------------------------------------

    with open(cfg_path, "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    
    # define the model
    if model_name == 'unet':
        crop_size = (128, 128, 128)
        n_layers = cfg['unet'].get('n_encoder_layers', 5)
        initial_channel = cfg['unet'].get('channels_initial', 16)
        model_unet = UNet(
            spatial_dims=3,
            in_channels=1,
            out_channels=2,
            channels=tuple([initial_channel * (2**j) for j in range(n_layers)]),
            strides=tuple([2] * (n_layers - 1)),
            num_res_units=cfg['unet'].get('num_res_unit', 2),
            dropout = cfg['unet'].get('dropout', 0.2),
            norm = Norm.BATCH
        )
    elif model_name == 'unetr':
        crop_size = (96, 96, 96)
        model_unetr = UNETR(
            spatial_dims=3,
            in_channels=1,
            out_channels=2,
            img_size=crop_size,
            feature_size=cfg['unetr'].get('feature_size', 16),
            hidden_size=cfg['unetr'].get('hidden_size', 768),
            mlp_dim=cfg['unetr'].get('mlp_dim', 3072),
            num_heads=cfg['unetr'].get('num_heads', 12),
            dropout_rate=cfg['unetr'].get('dropout', 0.2),
            res_block=cfg['unetr'].get('res_block', True),
            norm_name='batch'             
            )
    elif model_name == 'ensemble':     
        # U-Net
        crop_size = (128, 128, 128)
        n_layers = cfg['unet'].get('n_encoder_layers', 5)
        initial_channel = cfg['unet'].get('channels_initial', 16)
        model_unet = UNet(
            spatial_dims=3,
            in_channels=1,
            out_channels=2,
            channels=tuple([initial_channel * (2**j) for j in range(n_layers)]),
            strides=tuple([2] * (n_layers - 1)),
            num_res_units=cfg['unet'].get('num_res_unit', 2),
            dropout = cfg['unet'].get('dropout', 0.2),
            norm = Norm.BATCH
        )
        
        # UNETR
        crop_size = (96, 96, 96)
        model_unetr = UNETR(
            spatial_dims=3,
            in_channels=1,
            out_channels=2,
            img_size=crop_size,
            feature_size=cfg['unetr'].get('feature_size', 16),
            hidden_size=cfg['unetr'].get('hidden_size', 768),
            mlp_dim=cfg['unetr'].get('mlp_dim', 3072),
            num_heads=cfg['unetr'].get('num_heads', 12),
            dropout_rate=cfg['unetr'].get('dropout', 0.2),
            res_block=cfg['unetr'].get('res_block', True),
            norm_name='batch'             
            )
        
    print("model(s) are initialized!")   
    # -------------------------------------------------------
    # load the model's weights
    # -------------------------------------------------------
    model_path_unet = cfg['general'].get('model_unet_trained_path')
    model_path_unetr = cfg['general'].get('model_unetr_trained_path')
    
    if model_name == 'unet':
        model_unet.load_state_dict(torch.load(model_path_unet))
        model_out = model_unet
        
    elif model_name == 'unetr':
        model_unetr.load_state_dict(torch.load(model_path_unetr))
        model_out = model_unetr
        
    elif model_name == 'ensemble':
        model_unet.load_state_dict(torch.load(model_path_unet))
        model_unetr.load_state_dict(torch.load(model_path_unetr))
        model_out = [model_unet, model_unetr]
    
    print("Trained model(s) are loaded!")   
    # -------------------------------------------------------
    # define transforms
    # -------------------------------------------------------
    
    # return image_dict
    class MyLoadImage(Transform):
        def __call__(self, img_path):
            # load the .tiff files they are HxWxD
            image = tifffile.imread(img_path)
            # change the order axis of the image from DHW to HWD
            image = np.moveaxis(image, 0, 2)
            image = np.moveaxis(image, 0, 1)
            
            
            return image
    
    val_transforms = Compose(
        [
            MyLoadImage(),
            AddChannel(),
            ScaleIntensityRangePercentiles(keys=["image"], lower=0.05, upper=99.95, b_min=0, b_max=1, clip=True, relative=False),
            EnsureType(),
        ]
    )
    
    
    return model_out, val_transforms
    



    
