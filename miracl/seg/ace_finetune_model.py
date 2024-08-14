"""
This code is written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca
this code uses MONAI and PyTorch for ACE project
In this code we load the trained model and fine tuned it.


"""

# -------------------------------------------------------
# load libraries
# -------------------------------------------------------

import os
import numpy as np
from monai.utils import set_determinism
from monai.data import CacheDataset, DataLoader, decollate_batch, Dataset
from monai.losses import DiceLoss, DiceCELoss, DiceFocalLoss, TverskyLoss
from monai.networks.nets import UNet, DynUNet, UNETR
from monai.transforms import (
    AsDiscrete,
    AsDiscreted,
    Compose,
    LoadImaged,
    RandCropByPosNegLabeld,
    ScaleIntensityd,
    EnsureTyped,
    EnsureType,
    AddChanneld,
    RandAffined,
    Rand3DElasticd,
    RandZoomd,
    RandAdjustContrastd,
    ScaleIntensityRangePercentilesd,
    OneOf,
    RandGaussianSharpend,
    RandGaussianSmoothd,
    RandGaussianNoised,
    RandCoarseDropoutd,
    ToTensord,
    RandFlipd,
    RandShiftIntensityd,
    RandHistogramShiftd,
    RandAxisFlipd,
    Transform
    
)
#from monai.utils import first
from monai.networks.layers import Norm
from monai.metrics import DiceMetric, ConfusionMatrixMetric, HausdorffDistanceMetric
from monai.inferers import sliding_window_inference
import torch
import argparse
from datetime import datetime
import fnmatch
import pickle
from torchio.transforms import RandomAffine
from skimage.util import random_noise
import shutil
import yaml
import tifffile

# -------------------------------------------------------
# create parser
# -------------------------------------------------------
# Add the arguments
# Create the parser
my_parser = argparse.ArgumentParser(description='Working directory')
my_parser.add_argument('-o','--output', help='output directory', required=True)
my_parser.add_argument('-c','--config', help='path of config file', required=True)
my_parser.add_argument('-t','--train', help='train imgs directory should contain .tif or .tiff raw images', required=True)
my_parser.add_argument('-tl','--train_label', help='train ground truth imgs directory should contain .tif or .tiff raw images', required=True)
my_parser.add_argument('-v','--validation', help='validation imgs directory should contain .tif or .tiff raw images', required=True)
my_parser.add_argument('-vl','--validation_label', help='validation ground truth imgs directory should contain .tif or .tiff raw images', required=True)


def main(args):
    
    # -------------------------------------------------------
    # get args parameters and files
    # -------------------------------------------------------

     # Execute the parse_args() method
    args = vars(my_parser.parse_args())

    # root_dir is where results will be stored
    root_dir = args['output']
    isExist = os.path.exists(root_dir)
    if not isExist: os.mkdir(root_dir)

    # load config file
    config_path = args['config'] 
    with open(config_path, "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    print('config: ', cfg)

    # load data
    print('reading images ...')

    # images train
    images_train_path = args['train']
    file_names = os.listdir(images_train_path)
    images_train = [os.path.join(images_train_path, file) for file in file_names if file.endswith('.tiff') or file.endswith('.tif')]

    # segs/labels train
    images_segs_train_path = args['train_label']
    file_names = os.listdir(images_segs_train_path)
    segs_train = [os.path.join(images_segs_train_path, file) for file in file_names if file.endswith('.tiff') or file.endswith('.tif')]

    # images val
    images_val_path = args['validation']
    file_names = os.listdir(images_val_path)
    images_val = [os.path.join(images_val_path, file) for file in file_names if file.endswith('.tiff') or file.endswith('.tif')]

    # segs/labels val
    images_segs_val_path = args['validation_label']
    file_names = os.listdir(images_segs_val_path)
    segs_val = [os.path.join(images_segs_val_path, file) for file in file_names if file.endswith('.tiff') or file.endswith('.tif')]

    # -------------------------------------------------------
    # Set deterministic training for reproducibility
    # -------------------------------------------------------

    set_determinism(seed=0)

    # -------------------------------------------------------
    # creating dictionary for images ('images', 'labels')
    # -------------------------------------------------------

    data_dicts_train = [
        {"image": image_name, "label": label_name}
        for image_name, label_name in zip(images_train, segs_train)
    ]
    data_dicts_val = [
        {"image": image_name, "label": label_name}
        for image_name, label_name in zip(images_val, segs_val)
    ] 
    print("train data: ", data_dicts_train)
    print("val data: ", data_dicts_val)

    # -------------------------------------------------------
    # creating dictionary for images ('images', 'labels')
    # -------------------------------------------------------

    # saving data_dicts for inference code
    with open(os.path.join(root_dir, "data_dicts.pickle"), 'wb') as f:
        pickle.dump([data_dicts_train, data_dicts_val], f)  
            
    print('selecting ', len(data_dicts_train), ' images as train dataset ...')
    print('selecting ', len(data_dicts_val), ' images as validation dataset ...')

    # -------------------------------------------------------
    # Define transforms for image and segmentation
    # -------------------------------------------------------

    class random_salt_pepper(Transform):
        def __call__(self, image_dict):
            # randomly apply salt and pepper noise on 1 percent of the data
            image_dict["image"] = torch.tensor(random_noise(image_dict["image"], mode='s&p', amount=0.001, clip=True))
            return image_dict

    # return image_dict
    class MyLoadImage(Transform):
        def __call__(self, image_dict):
            # load the .tiff files they are HxWxD
            # img_path = image_dict['image']
            image_dict['image'] = tifffile.imread(image_dict['image'])
            # print(f"image max: {image_dict['image'].max()}, image shape: {image_dict['image'].shape}")
            # print('img_path: ', img_path)
            # change the order axis of the image from DHW to HWD
            image_dict['image'] = np.moveaxis(image_dict['image'], 0, 2)
            image_dict['image'] = np.moveaxis(image_dict['image'], 0, 1)

            # img_path = image_dict['image']
            if ("vessel" in image_dict['label']) or ("vent" in image_dict['label']):
                image_dict['label'] = np.zeros((image_dict["image"].shape)).astype(np.uint8)
                
            else:

                image_dict['label'] = tifffile.imread(image_dict['label'])[201:]
                image_dict['label'] = (image_dict['label'] > 0.65).astype(np.uint8)
                # print('img_path: ', img_path)
                # change the order axis of the image from DHW to HWD
                image_dict['label'] = np.moveaxis(image_dict['label'], 0, 2)
                image_dict['label'] = np.moveaxis(image_dict['label'], 0, 1)


            # image_dict['label'][100, 100, 100] = 1

            # print(f"label max: {image_dict['label'].max()}, label shape: {image_dict['label'].shape}")
            return image_dict    

    class fix_all_zero_label_issue(Transform):

        def __call__(self, image_dict):

            if torch.sum(image_dict["label"]) < 1:

                image_dict['label'][0, 100, 100, 100] = 1

            return image_dict

    # fdata axis should be H * W * D
    temp_value= cfg['general'].get('crop_size', 128)
    crop_size = (temp_value, temp_value, temp_value)
    N_crops = cfg['general'].get('crop_number', 3)
    data_aug_prob = cfg['general'].get('data_aug_prob', 0.1)
    train_transforms = Compose(
        [
            MyLoadImage(),
            AddChanneld(keys=["image", "label"]),
            ScaleIntensityRangePercentilesd(keys=["image"], lower=0.05, upper=99.95, b_min=0, b_max=1, clip=True, relative=False),
            # changing 255 index to 1, making sure that the label values are between 0 and 1
            ScaleIntensityd(keys=["label"]),
            OneOf(transforms=[
                RandomAffine(include=["image", "label"], p=data_aug_prob, degrees=(30,30,30),
                            scales=(0.5, 2), translation=(0.1,0.1,0.1),
                            default_pad_value='mean', label_keys='label'),
                random_salt_pepper(),
                RandAdjustContrastd(keys=["image"], prob=data_aug_prob, gamma=(0.5, 4)),
                RandGaussianSharpend(keys=["image"], prob=data_aug_prob),
                RandGaussianSmoothd(keys=["image"], prob=data_aug_prob),
                RandGaussianNoised(keys=["image"], prob=data_aug_prob, std=0.02),
                RandHistogramShiftd(keys=["image"], num_control_points=10, prob=data_aug_prob),
            ]),
            ToTensord(keys=["image", "label"]),    
            RandAxisFlipd(keys=["image", "label"], prob=data_aug_prob),
            fix_all_zero_label_issue(),
            RandCropByPosNegLabeld(
                keys=["image", "label"], label_key="label",
                spatial_size=crop_size, pos=1, neg=1,
                num_samples=N_crops, image_key="image", image_threshold=0,
            ),
            EnsureTyped(keys=["image", "label"]),
        ]
    )

    val_transforms = Compose(
        [
            MyLoadImage(),
            AddChanneld(keys=["image", "label"]),
            ScaleIntensityRangePercentilesd(keys=["image"], lower=0.05, upper=99.95, b_min=0, b_max=1, clip=True, relative=False),
            ScaleIntensityd(keys=["label"]),
            EnsureTyped(keys=["image", "label"]),
        ]
    )

    # -------------------------------------------------------
    # Define CacheDataset and DataLoader for training and validation¶
    # -------------------------------------------------------

    cache_rate_train = cfg['general'].get('cache_rate_train', 0.05)
    train_ds = CacheDataset(data=data_dicts_train, transform=train_transforms, cache_rate=cache_rate_train, num_workers=2)
    #train_ds = Dataset(data=data_dicts_train, transform=train_transforms)
    train_loader = DataLoader(train_ds, batch_size=cfg['general'].get('batch_size', 8), shuffle=True, num_workers=4)

    cache_rate_val = cfg['general'].get('cache_rate_val', 0.01)
    val_ds = CacheDataset(data=data_dicts_val, transform=val_transforms, cache_rate=cache_rate_val, num_workers=2)
    #val_ds = Dataset(data=data_dicts_val, transform=val_transforms)
    val_loader = DataLoader(val_ds, batch_size=1, num_workers=4)

    # -------------------------------------------------------
    # Create Model, Loss, Optimizer
    # -------------------------------------------------------

    print('creating the model ...')

    # Create UNet, DiceLoss and Adam optimizer
    model_name = cfg['general'].get('model_name', 'unet')
    if model_name == 'unet':
        n_layers = cfg['unet'].get('n_encoder_layers', 5)
        initial_channel = cfg['unet'].get('channels_initial', 16)
        model = UNet(
            spatial_dims=3,
            in_channels=1,
            out_channels=2,
            channels=tuple([initial_channel * (2**j) for j in range(n_layers)]),
            strides=tuple([2] * (n_layers - 1)),
            num_res_units=cfg['unet'].get('num_res_unit', 2),
            dropout = cfg['unet'].get('dropout', 0.2),
            norm = Norm.BATCH
        )
    elif model_name == 'dynunet':
        n_layers = cfg['dynunet'].get('n_layers', 5)
        initial_filter = cfg['dynunet'].get('filters_initial', 16)
        # e.g. creating [[3, 3, 3], [3, 3, 3], [3, 3, 3], [3, 3, 3], [3, 3, 3]] if n_layers=5
        kernel_sizes = [[3, 3, 3] for j in range(n_layers)]
        # e.g. creating [[1, 1, 1], [2, 2, 2], [2, 2, 2], [2, 2, 2], [2, 2, 2]] if n_layers=5
        strides = [[2, 2, 2] for j in range(n_layers-1)]
        strides.insert(0, [1, 1, 1])
        filters = [initial_filter * (2**j) for j in range(n_layers)]
        model = DynUNet(
            spatial_dims=3,
            in_channels=1,
            out_channels=2,
            kernel_size=kernel_sizes,
            strides=strides,
            filters=filters,
            upsample_kernel_size=strides[1:],
            res_block=cfg['dynunet'].get('res_block', True),
            deep_supervision=True,
            deep_supr_num=2,
            dropout=cfg['dynunet'].get('dropout', 0.2),
            norm_name = Norm.BATCH
        )
    elif model_name == 'unetr':
        model = UNETR(
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
    print('model: ', model)

    # -------------------------------------------------------
    # GPU selection
    # -------------------------------------------------------

    gpu_opt = cfg['general'].get('GPU', 'single')
    if gpu_opt == 'single':
        device = torch.device("cuda:0")
        model.to(device)
    else:
        print('number of available gpus: ', torch.cuda.device_count())
        device = torch.device("cuda:0")
        model = torch.nn.DataParallel(model)
        model.to(device)

        
    # -------------------------------------------------------
    # check if the model is trained ; just load the model
    # -------------------------------------------------------
    model_state = cfg['general'].get('model_state', 'untrained')
    model_path = cfg['general'].get('model_trained_path')
    if model_state == 'trained':
        model.load_state_dict(torch.load(model_path))
        print('trained model loaded!')
    # -------------------------------------------------------   
    # define loss function
    # -------------------------------------------------------

    loss_name = cfg['loss'].get('name')
    if (loss_name == 'dicece'):
        lambda_dice = cfg['loss'].get('dicece_lambda_dice', 1.0)
        lambda_ce = cfg['loss'].get('dicece_lambda_ce', 1.0)
        weight = torch.tensor([1/(cfg['loss'].get('dicece_weights', 1)), 1], dtype=torch.float, device=device)
        loss_function = DiceCELoss(to_onehot_y=True, softmax=True, ce_weight=weight, lambda_dice=lambda_dice, lambda_ce=lambda_ce)
        # CE_loss = torch.nn.CrossEntropyLoss(weight=torch.tensor([5., 1.]).to(device), size_average=None, ignore_index=-100, reduce=None, reduction='mean', label_smoothing=0.0)
        # DICE_loss = DiceLoss(to_onehot_y=True, softmax=True)
        # loss_function = lambda x, y: CE_loss(x, y[:,0,...].long()) + DICE_loss(x, y)
    elif (loss_name == 'dice'):
        loss_function = DiceLoss(to_onehot_y=True, softmax=True)
    elif (loss_name == 'focaldice'):
        loss_function = DiceFocalLoss(to_onehot_y=True, softmax=True)
    elif (loss_name == 'tversky'):
        tversky_alpha = cfg['loss'].get('tversky_alpha', 0.5) # weight of FP
        tversky_beta = cfg['loss'].get('tversky_beta', 0.5) # weight of FN
        loss_function = TverskyLoss(to_onehot_y=True, softmax=True, alpha=tversky_alpha, beta=tversky_beta)

    learning_rate = cfg['optimizer'].get('learning_rate', 1e-4)
    weight_decay = cfg['optimizer'].get('weight_decay', 0.0)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)

    # -------------------------------------------------------
    # dice and ConfusionMatrix from MONAI
    # -------------------------------------------------------

    dice_metric = DiceMetric(include_background=False, reduction="mean")
    metrics = ConfusionMatrixMetric(include_background=False,
                                    metric_name = ["sensitivity", 
                                                "precision", 
                                                "f1 score"])
    hausdorff_metric = HausdorffDistanceMetric(include_background=False, percentile=95)

    # -------------------------------------------------------
    # Execute a typical PyTorch training process
    # -------------------------------------------------------

    max_epochs = cfg['general'].get('max_epochs', 200)
    val_interval = cfg['general'].get('validation_interval', 2)
    save_result_interval = cfg['general'].get('checkpoint_period', 10)
    early_stop_patience_cnt = 0
    best_metric = -1
    best_metric_epoch = -1
    epoch_loss_values = []
    dice_metric_values = []
    hd_metric_values = []
    metrics_values = []
    post_pred = Compose([EnsureType(), AsDiscrete(argmax=True, to_onehot=2)])
    post_label = Compose([EnsureType(), AsDiscrete(to_onehot=2)])
    scaler = torch.cuda.amp.GradScaler()
    for epoch in range(max_epochs):
        print("-" * 10)
        print(f"epoch {epoch + 1}/{max_epochs}")
        model.train()
        epoch_loss = 0
        step = 0
        for batch_data in train_loader:
            step += 1
            inputs, labels = (
                batch_data["image"].to(device),
                batch_data["label"].to(device),
            )
            # print(inputs.shape)
            # print(labels.shape)
            optimizer.zero_grad()
            with torch.cuda.amp.autocast():
                outputs = model(inputs)
                if model_name == 'dynunet':
                    loss = compute_train_loss(outputs, labels)
                else:
                    loss = loss_function(outputs, labels)
        
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            epoch_loss += loss.item()
            print(
                f"{step}/{len(train_ds) // train_loader.batch_size}, "
                f"train_loss: {loss.item():.4f}")
            
        epoch_loss /= step
        epoch_loss_values.append(epoch_loss)
        print(f"epoch {epoch + 1} average loss: {epoch_loss:.4f}")
        

        if (epoch + 1) % val_interval == 0:
            model.eval()
            with torch.no_grad():
                RI_subj_id = 1
                for val_data in val_loader:
                    val_inputs, val_labels = (
                        val_data["image"].to(device),
                        val_data["label"].to(device),
                    )
                    # print(val_inputs.shape)
                    # print(val_labels.shape)
                    roi_size = crop_size
                    sw_batch_size = 4
                    with torch.cuda.amp.autocast():
                        val_outputs = sliding_window_inference(
                            val_inputs, roi_size, sw_batch_size, model)
                    val_outputs = [post_pred(i) for i in decollate_batch(val_outputs)]
                    val_labels = [post_label(i) for i in decollate_batch(val_labels)]
                    # compute metric for current iteration
                    dice_metric(y_pred=val_outputs, y=val_labels)
                    metrics(y_pred=val_outputs, y=val_labels)
                    hausdorff_metric(y_pred=val_outputs, y=val_labels)
                    RI_subj_id += 1
                
                # aggregate the final mean dice result
                metric = dice_metric.aggregate().item()
                hd = hausdorff_metric.aggregate().item()
                metrics_list = metrics.aggregate()
                metrics_list_cpu = []
                for value in metrics_list:
                    metrics_list_cpu.append(value.cpu().numpy())
                    

                # reset the status for next validation round
                dice_metric.reset()
                metrics.reset()
                hausdorff_metric.reset()

                dice_metric_values.append(metric)
                hd_metric_values.append(hd)
                metrics_values.append(metrics_list_cpu)
                
                sen = metrics_list_cpu[0]
                prec = metrics_list_cpu[1]
                f1 = metrics_list_cpu[2]
                
                if metric > best_metric:
                    best_metric = metric
                    best_metric_epoch = epoch + 1
                    early_stop_patience_cnt = 0
                    torch.save(model.state_dict(), os.path.join(
                        root_dir, "best_metric_model.pth"))
                    print("saved new best metric model")
                else:
                    early_stop_patience_cnt += 1
                    
                if early_stop_patience_cnt >= cfg['general'].get('early_stop_patience', 10):
                    break
                
                print(
                    f"current epoch: {epoch + 1} current mean dice: {metric:.4f}"
                    f"\ncurrent epoch: {epoch + 1} current mean hd: {hd:.4f}"
                    f"\nbest mean dice: {best_metric:.4f}"
                    f" at epoch: {best_metric_epoch}"
                    f"\ncurrent sen: {sen[0]:.4f}"
                    f"\ncurrent prec: {prec[0]:.4f}"
                    f"\ncurrent f1: {f1[0]:.4f}"
                )
                
        if (epoch + 1) % save_result_interval == 0:
            
            with open(os.path.join(root_dir, "results.pickle"), 'wb') as f:
                pickle.dump([epoch_loss_values, dice_metric_values, hd_metric_values, metrics_values], f)
            
            torch.save(model.state_dict(), os.path.join(root_dir, "last_trained_model.pth"))
            


    print(
        f"train completed, best_metric: {best_metric:.4f} "
        f"at epoch: {best_metric_epoch}")

    # -------------------------------------------------------
    # saving epoch_loss_values and metric_values and last trained model
    # -------------------------------------------------------

    with open(os.path.join(root_dir, "results.pickle"), 'wb') as f:
        pickle.dump([epoch_loss_values, dice_metric_values, hd_metric_values, metrics_values], f)

    torch.save(model.state_dict(), os.path.join(
        root_dir, "last_trained_model.pth"))
    print("saved last trained model")


if __name__ == '__main__':
    # Execute the parse_args() method
    args = vars(my_parser.parse_args())
    main(args)