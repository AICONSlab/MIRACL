# This is the code for creating the ACE architecture: consisting UNet + transformer layer.
# written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca, Grace Yu gracefengqing.yu@mail.utoronto.ca

# 3D Unet code modified from
# @article {10.7554/eLife.57613,
# article_type = {journal},
# title = {Accurate and versatile 3D segmentation of plant tissues at cellular resolution},
# author = {Wolny, Adrian and Cerrone, Lorenzo and Vijayan, Athul and Tofanelli, Rachele and Barro, Amaya Vilches and Louveaux, Marion and Wenzl, Christian and Strauss, Sören and Wilson-Sánchez, David and Lymbouridou, Rena and Steigleder, Susanne S and Pape, Constantin and Bailoni, Alberto and Duran-Nebreda, Salva and Bassel, George W and Lohmann, Jan U and Tsiantis, Miltos and Hamprecht, Fred A and Schneitz, Kay and Maizel, Alexis and Kreshuk, Anna},
# editor = {Hardtke, Christian S and Bergmann, Dominique C and Bergmann, Dominique C and Graeff, Moritz},
# volume = 9,
# year = 2020,
# month = {jul},
# pub_date = {2020-07-29},
# pages = {e57613},
# citation = {eLife 2020;9:e57613},
# doi = {10.7554/eLife.57613},
# url = {https://doi.org/10.7554/eLife.57613},
# keywords = {instance segmentation, cell segmentation, deep learning, image analysis},
# journal = {eLife},
# issn = {2050-084X},
# publisher = {eLife Sciences Publications, Ltd},
# }
# residual UNet is originally from this paper https://arxiv.org/pdf/1706.00120.pdf

# Transformer code modified from
# @misc{oquab2023dinov2,
#   title={DINOv2: Learning Robust Visual Features without Supervision},
#   author={Oquab, Maxime and Darcet, Timothée and Moutakanni, Theo and Vo, Huy V. and Szafraniec, Marc and Khalidov, Vasil and Fernandez, Pierre and Haziza, Daniel and Massa, Francisco and El-Nouby, Alaaeldin and Howes, Russell and Huang, Po-Yao and Xu, Hu and Sharma, Vasu and Li, Shang-Wen and Galuba, Wojciech and Rabbat, Mike and Assran, Mido and Ballas, Nicolas and Synnaeve, Gabriel and Misra, Ishan and Jegou, Herve and Mairal, Julien and Labatut, Patrick and Joulin, Armand and Bojanowski, Piotr},
#   journal={arXiv:2304.07193},
#   year={2023}
# }


from mapl3_inference_building_blocks import (
    DoubleConv,
    ResNetBlock,
    create_decoders,
    create_encoders,
)
from mapl3_inference_transformer_block import Block, Mlp
import torch.nn as nn
import torch
from torch.nn.functional import interpolate
import einops


# ------------------
# reshaping the inputs to apply attention
# ------------------
class ImageToPatch(nn.Module):
    """Image to Patch without creating Embedding"""

    # Example: img_size: 32*32*32, patch size: 8*8*8, num patches: 64
    def __init__(self, img_size=(512, 512, 512), patch_size=(64, 64, 64)):
        super().__init__()
        num_patches = (img_size[0] // patch_size[0]) ** 3
        self.img_size = img_size
        self.patch_size = patch_size
        self.num_patches = num_patches
        self.is3d = True
        if len(img_size) == 2:
            self.is3d = False

        self.topatch = nn.Unfold(kernel_size=patch_size, stride=patch_size)

    def forward(self, x):
        if not self.is3d:
            x = self.topatch(x)  # will have shape N,C×product of (kernel_size),L
            # we want num_patch (batch) x C x 128 x 128 x 128
            x = torch.squeeze(x)  # C×product of (kernel_size),L
            x = torch.transpose(x, 0, 1)  # L, C×product of (kernel_size)
            x = torch.unflatten(
                x, 1, (-1, self.patch_size[0], self.patch_size[1], self.patch_size[2])
            )
            return x
        else:
            patch_size = self.patch_size
            img_size = self.img_size
            temp1, temp2, temp3 = (
                img_size[0] // patch_size[0],
                img_size[1] // patch_size[1],
                img_size[2] // patch_size[2],
            )
            x = einops.rearrange(
                x,
                "1 c (b1 h) (b2 w) (b3 d) -> (b1 b2 b3) c h w d",
                b1=temp1,
                b2=temp2,
                b3=temp3,
            )
            return x


class PatchToImage(nn.Module):
    """Patch concatenate to image"""

    # Example: img_size: 32*32*32, patch size: 8*8*8, num patches: 64
    def __init__(self, img_size=(512, 512, 512), patch_size=(64, 64, 64)):
        super().__init__()
        num_patches = (img_size[0] // patch_size[0]) ** 3
        self.img_size = img_size
        self.patch_size = patch_size
        self.num_patches = num_patches

    def forward(self, x):
        N, C, H, W, D = x.shape
        assert (
            H == self.patch_size[0]
            and W == self.patch_size[1]
            and D == self.patch_size[2]
        )
        patch_size = self.patch_size
        img_size = self.img_size
        temp1, temp2, temp3 = (
            img_size[0] // patch_size[0],
            img_size[1] // patch_size[1],
            img_size[2] // patch_size[2],
        )

        x = einops.rearrange(
            x,
            " (b1 b2 b3) c h w d -> 1 c (b1 h) (b2 w) (b3 d)",
            b1=temp1,
            b2=temp2,
            b3=temp3,
        )
        return x


# ------------------
# model
# ------------------
# Mechanism: in the Encoder, select the basic module (DoubleConv or ResNetBlock or SingleConv?)
# the Encoder function only creates one encoder block
# use conv_layer_order to select order of things:
# 'cr' -> conv + ReLU
# 'gcr' -> groupnorm + conv + ReLU
# 'cl' -> conv + LeakyReLU
# 'ce' -> conv + ELU
# 'bcr' -> batchnorm + conv + ReLU

# to create the entire encoder, use create_encoders that contains all of the encoder modules
# depth of encoders = `len(f_maps)`
# f_map: channels in monai Unet, correspond to number of kernels in each layer, eg. [4,8,16,32,64]
# len(f_map) is the depth of the encoder


def number_of_features_per_level(init_channel_number, num_levels):
    return [init_channel_number * 2**k for k in range(num_levels)]


class AbstractUNet(nn.Module):
    """
    Base class for standard and residual UNet.

    Args:
        in_channels (int): number of input channels
        out_channels (int): number of output segmentation masks;
            Note that the of out_channels might correspond to either
            different semantic classes or to different binary segmentation mask.
            It's up to the user of the class to interpret the out_channels and
            use the proper loss criterion during training (i.e. CrossEntropyLoss (multi-class)
            or BCEWithLogitsLoss (two-class) respectively)
        f_maps (int, tuple): number of feature maps at each level of the encoder; if it's an integer the number
            of feature maps is given by the geometric progression: f_maps ^ k, k=1,2,3,4
        final_sigmoid (bool): if True apply element-wise nn.Sigmoid after the final 1x1 convolution,
            otherwise apply nn.Softmax. In effect only if `self.training == False`, i.e. during validation/testing
        basic_module: basic model for the encoder/decoder (DoubleConv, ResNetBlock, ....)
        layer_order (string): determines the order of layers in `SingleConv` module.
            E.g. 'crg' stands for GroupNorm3d+Conv3d+ReLU. See `SingleConv` for more info
        num_groups (int): number of groups for the GroupNorm
        num_levels (int): number of levels in the encoder/decoder path (applied only if f_maps is an int)
            default: 4
        is_segmentation (bool): if True and the model is in eval mode, Sigmoid/Softmax normalization is applied
            after the final convolution; if False (regression problem) the normalization layer is skipped
        conv_kernel_size (int or tuple): size of the convolving kernel in the basic_module
        pool_kernel_size (int or tuple): the size of the window
        conv_padding (int or tuple): add zero-padding added to all three sides of the input
        is3d (bool): if True the model is 3D, otherwise 2D, default: True
    """

    def __init__(
        self,
        in_channels,
        out_channels,
        final_sigmoid,
        basic_module,
        f_maps=64,
        layer_order="gcr",
        img_size=(512, 512, 512),
        crop_size=(128, 128, 128),
        dropout_prob=0.2,
        num_groups=8,
        num_levels=4,
        is_segmentation=True,
        conv_kernel_size=3,
        pool_kernel_size=2,
        conv_padding=1,
        is3d=True,
        drop_path=0.1,
        attention_sum=True,
        attention_weights=True,
        patch_wise_attn=True,
        patch_wise_attn_down=True,
        patch_wise_attn_down_factor=2,
        patch_wise_adaptive_thr=True,
        patch_wise_PE_3D=True,
        encoder_depth_patch=5,
        atten_dim_patch=512,
        atten_depth_patch=8,
        num_heads_patch=8,
        mlp_ratio_patch=1.0,
        qkv_bias_patch=True,
        qk_scale_patch=1,
        drop_rate_patch=0.0,
        attn_drop_rate_patch=0.0,
        attn_drop_path_patch=0.1,
        norm_layer_patch=nn.LayerNorm,
        voxel_wise_attn=True,
        encoder_depth_voxel=5,
        atten_dim_voxel=512,
        atten_depth_voxel=8,
        num_heads_voxel=8,
        mlp_ratio_voxel=1.0,
        qkv_bias_voxel=True,
        qk_scale_voxel=1,
        drop_rate_voxel=0.0,
        attn_drop_rate_voxel=0.0,
        attn_drop_path_voxel=0.1,
        norm_layer_voxel=nn.LayerNorm,
        deep_supervision=0,
    ):
        super(AbstractUNet, self).__init__()

        if isinstance(f_maps, int):
            f_maps = number_of_features_per_level(f_maps, num_levels=num_levels)
        self.f_maps = f_maps

        assert isinstance(f_maps, list) or isinstance(f_maps, tuple)
        assert len(f_maps) > 1, "Required at least 2 levels in the U-Net"
        if "g" in layer_order:
            assert (
                num_groups is not None
            ), "num_groups must be specified if GroupNorm is used"

        # create encoder path
        self.encoders = create_encoders(
            in_channels,
            f_maps,
            basic_module,
            conv_kernel_size,
            conv_padding,
            layer_order,
            num_groups,
            pool_kernel_size,
            is3d,
            dropout_prob,
            drop_path,
        )

        # create decoder path
        self.decoders = create_decoders(
            f_maps,
            basic_module,
            conv_kernel_size,
            conv_padding,
            layer_order,
            num_groups,
            is3d,
            dropout_prob,
            drop_path,
        )

        # reshape the input
        self.image_to_patch = ImageToPatch(img_size=img_size, patch_size=crop_size)
        self.patch_to_image = PatchToImage(img_size=img_size, patch_size=crop_size)

        # in the last layer a 1×1 convolution reduces the number of output channels to the number of labels
        if is3d:
            self.final_conv = nn.Conv3d(f_maps[0], out_channels, 1)
        else:
            self.final_conv = nn.Conv2d(f_maps[0], out_channels, 1)

        if is_segmentation:
            # semantic segmentation problem
            if final_sigmoid:
                self.final_activation = nn.Sigmoid()
            else:
                self.final_activation = nn.Softmax(dim=1)
        else:
            # regression problem
            self.final_activation = None

        # define attention block for voxel wise attn
        self.voxel_wise_attn = voxel_wise_attn
        self.encoder_depth_voxel = encoder_depth_voxel
        if voxel_wise_attn:
            self.attention_blocks_voxel = nn.ModuleList(
                [
                    Block(
                        dim=atten_dim_voxel,
                        num_heads=num_heads_voxel,
                        mlp_ratio=mlp_ratio_voxel,
                        qkv_bias=qkv_bias_voxel,
                        qk_scale=qk_scale_voxel,
                        drop=drop_rate_voxel,
                        attn_drop=attn_drop_rate_voxel,
                        drop_path=attn_drop_path_voxel,
                        norm_layer=norm_layer_voxel,
                    )
                    for i in range(atten_depth_voxel)
                ]
            )

            # positonal encoding
            n_seq_length = int((crop_size[0] / (2 ** (encoder_depth_voxel - 1))) ** 3)
            c_channel_size = f_maps[encoder_depth_voxel - 1]
            self.pos_embed_voxel = nn.Parameter(
                torch.zeros(1, n_seq_length, c_channel_size)
            )
            self.pos_drop_voxel = nn.Dropout(p=drop_rate_voxel)

        # define attention block for patch wise attn
        self.patch_wise_attn = patch_wise_attn
        self.patch_wise_attn_down = patch_wise_attn_down
        self.patch_wise_adaptive_thr = patch_wise_adaptive_thr
        self.patch_wise_PE_3D = patch_wise_PE_3D
        self.encoder_depth_patch = encoder_depth_patch
        if patch_wise_attn:
            self.attention_blocks_patch = nn.ModuleList(
                [
                    Block(
                        dim=atten_dim_patch,
                        num_heads=num_heads_patch,
                        mlp_ratio=mlp_ratio_patch,
                        qkv_bias=qkv_bias_patch,
                        qk_scale=qk_scale_patch,
                        drop=drop_rate_patch,
                        attn_drop=attn_drop_rate_patch,
                        drop_path=attn_drop_path_patch,
                        norm_layer=norm_layer_patch,
                    )
                    for i in range(atten_depth_patch)
                ]
            )

            # positonal encoding

            num_patches = (img_size[0] // crop_size[0]) ** 3
            if patch_wise_PE_3D:
                patch_per_dim = round(num_patches ** (1 / 3))
                self.patch_wise_PE_inds = torch.zeros(
                    patch_per_dim, patch_per_dim, patch_per_dim, 3
                ).long()
                # matrix of indices for each dimenstion
                for i in range(patch_per_dim):
                    self.patch_wise_PE_inds[i, :, :, 0] = i
                    self.patch_wise_PE_inds[:, i, :, 1] = i
                    self.patch_wise_PE_inds[:, :, i, 2] = i

                pos_embed_dim = atten_dim_patch // 3  # per dimension
                self.patch_wise_PE_x_params = nn.Parameter(
                    torch.randn(patch_per_dim, pos_embed_dim)
                )
                nn.init.trunc_normal_(self.patch_wise_PE_x_params)
                self.patch_wise_PE_y_params = nn.Parameter(
                    torch.randn(patch_per_dim, pos_embed_dim)
                )
                nn.init.trunc_normal_(self.patch_wise_PE_y_params)
                self.patch_wise_PE_z_params = nn.Parameter(
                    torch.randn(patch_per_dim, atten_dim_patch - 2 * pos_embed_dim)
                )
                nn.init.trunc_normal_(self.patch_wise_PE_z_params)
            else:
                self.pos_embed_patch = nn.Parameter(
                    torch.zeros(1, num_patches, atten_dim_patch)
                )

            self.pos_drop_patch = nn.Dropout(p=drop_rate_patch)

            if patch_wise_attn_down:
                self.patch_wise_attn_down_conv = nn.Conv3d(
                    f_maps[encoder_depth_patch - 1],
                    int(f_maps[encoder_depth_patch - 1] / patch_wise_attn_down_factor),
                    1,
                )
                self.patch_wise_attn_up_conv = nn.Conv3d(
                    int(f_maps[encoder_depth_patch - 1] / patch_wise_attn_down_factor),
                    f_maps[encoder_depth_patch - 1],
                    1,
                )

            if patch_wise_adaptive_thr:

                self.Mlp = Mlp(
                    in_features=atten_dim_patch,
                    out_features=2,
                    hidden_features=int(atten_dim_patch / 4),
                    act_layer=nn.GELU,
                    drop=0.0,
                )

        # defines weights for voxel wise and patch wise
        self.attention_sum = attention_sum
        self.attention_weights = attention_weights
        if attention_weights:
            self.w_patch_transformer = nn.Parameter(torch.zeros(1, 1, 1, 1, 1))

            self.w_voxel_transformer = nn.Parameter(torch.zeros(1, 1, 1, 1, 1))

        self.deep_supervision_module = []
        self.deep_supervision_num = deep_supervision
        # deep supervision convolution
        for i in range(deep_supervision):
            self.deep_supervision_module.append(
                nn.Conv3d(f_maps[i + 1], out_channels, 1)
            )

        self.deep_supervision_module = nn.ModuleList(self.deep_supervision_module)

    # def interpolate_pos_encoding(self, x, w, h, d):
    #     npatch = x.shape[1]
    #     N = self.pos_embed.shape[1]
    #     if npatch == N and w == h and h==d:
    #         return self.pos_embed
    #     else:
    #         print('should not reach here -> view interpolation pos encoding please')

    def compute_deep_supervision_output(self, decoder_output):
        """Will change the channel of decoder output to be the same as the # of channel for the final output by
        using a 1x1 convolution.
        Also up sample the decoder output using interpolation.
        """
        decoder_output_transformed = []
        out = decoder_output.pop()
        decoder_output_transformed.append(out)

        for i in range(self.deep_supervision_num):
            output = self.deep_supervision_module[i](decoder_output[-i - 1])
            output = interpolate(output, out.shape[2:])
            decoder_output_transformed.append(output)
        return decoder_output_transformed

    def voxel_wise_transformer(self, x):
        """applies a voxel wise transformer blocks
        step 1: flatten the input
        given patch size of 64^3 and main image of 256^3 and f_maps initlized by 8
        last_encoder_output_shape is [64, 128, 4, 4, 4].
        we flatten the last three dimension -- > [64, 128, 64]
        then in mapl3_inference_transformer_block.py it needs batch size, sequence length, embed dimension,
        so to apply voxel wise we need to swapaxis --- > [64, 64, 128]
        the output of transformer's axis will be permuted again and reshape to have the size of [64, 128, 4, 4, 4]
        """
        if self.voxel_wise_attn:

            output_shape = x.shape
            x = torch.flatten(x, start_dim=2)
            x = torch.permute(x, (0, 2, 1))

            # step 2: use attention block / ViT
            # first encode position
            # x = x + self.interpolate_pos_encoding(x, w, h, d)
            # we don't need interpolate
            x = x + self.pos_embed_voxel
            x = self.pos_drop_voxel(x)
            # then attention
            for blk in self.attention_blocks_voxel:
                x = blk(x)
            # step 3: unflatten the input
            x = torch.permute(
                x, (0, 2, 1)
            )  # now should be B x sequence length x embed dim
            x = x.view(
                output_shape[0],
                output_shape[1],
                output_shape[2],
                output_shape[3],
                output_shape[4],
            )

        return x

    def patch_wise_transformer(self, x):
        """applies patch_wise transformer blocks
        given patch size of 64^3 and main image of 256^3 and f_maps initlized by 8
        last_encoder_output_shape is [64, 128, 4, 4, 4].
        we flatten the last four dimension -- > [64, 8192]
        we unsqueeze to add a batch as the first 64 above is the number of patches we want to attend -- > [1, 64, 8192]
        then in mapl3_inference_transformer_block.py it needs batch size, sequence length, embed dimension,
        if patch_wise_attn_down is true and down_factor is 2, we first downsample the number of channe;
        [64, 128, 4, 4, 4] ---> [64, 64, 4, 4, 4] ---> apply transformer
        then using another conv we restore to [64, 128, 4, 4, 4] after transformer
        if adaptive thr is true we pass the output of transformer before the last conv to a MLP and add that to the foreground
        """
        if self.patch_wise_attn:
            output_shape = x.shape

            if self.patch_wise_attn_down:
                x = self.patch_wise_attn_down_conv(x)
                output_shape = x.shape

            x = torch.flatten(x, start_dim=1)
            x = torch.unsqueeze(
                x, 0
            )  # should be (Batch, sequence length, patch embeb dimension)

            # step 2: use attention block / ViT
            # first encode position
            # x = x + self.interpolate_pos_encoding(x, w, h, d)
            # we don't need interpolate
            if self.patch_wise_PE_3D:
                # flatten indices to match with the size of data ---> 1, num_patch, attn_dim
                flattened_inds = self.patch_wise_PE_inds.reshape(-1, 3).to(
                    self.patch_wise_PE_x_params.device
                )
                x_vecs = torch.index_select(
                    self.patch_wise_PE_x_params, dim=0, index=flattened_inds[:, 0]
                )
                y_vecs = torch.index_select(
                    self.patch_wise_PE_y_params, dim=0, index=flattened_inds[:, 1]
                )
                z_vecs = torch.index_select(
                    self.patch_wise_PE_z_params, dim=0, index=flattened_inds[:, 2]
                )
                patch_wise_PE = torch.unsqueeze(
                    torch.cat([x_vecs, y_vecs, z_vecs], dim=1), 0
                )
            else:
                patch_wise_PE = self.pos_embed_patch

            x = x + patch_wise_PE
            x = self.pos_drop_patch(x)
            # then attention
            for blk in self.attention_blocks_patch:
                x = blk(x)

            # step 3: unflatten the input # now should be B x NC x sequence length x embed dim
            x = torch.squeeze(x)  # now should be sequence length x embed dim

            if self.patch_wise_adaptive_thr:
                # adaptive_thr_bias = self.Mlp(x) # should be 64, 2

                # detch x to decouple bias estimation from backbone train
                adaptive_thr_bias = self.Mlp(x.detach())

            # reshape to BxCxHxDxW
            x = x.view(
                output_shape[0],
                output_shape[1],
                output_shape[2],
                output_shape[3],
                output_shape[4],
            )

            if self.patch_wise_attn_down:
                x = self.patch_wise_attn_up_conv(x)

        if self.patch_wise_adaptive_thr:
            return x, adaptive_thr_bias
        else:
            return x, 0

    def forward(self, x):
        # image to patch
        x = self.image_to_patch(x)
        B, nc, w, h, d = x.shape
        # encoder part
        encoders_features = []

        # adding droppath
        for i, encoder in enumerate(self.encoders):

            if not self.attention_sum:

                x = encoder(x)
                # ------------------------
                # apply voxel transformer
                # ------------------------
                if i == self.encoder_depth_voxel - 1:

                    x = self.voxel_wise_transformer(x)

                # ------------------------
                # apply patch transformer
                # ------------------------
                if i == self.encoder_depth_patch - 1:

                    x, adaptive_thr_bias = self.patch_wise_transformer(x)

            else:

                x = encoder(x)
                # ------------------------
                # apply voxel and patch transformers
                # ------------------------

                # encoder_depth_patch is equal to encoder_depth_voxel
                if (i == self.encoder_depth_voxel - 1) and (
                    i == self.encoder_depth_patch - 1
                ):

                    x_voxel_transformer = self.voxel_wise_transformer(x)
                    x_patch_transformer, adaptive_thr_bias = (
                        self.patch_wise_transformer(x)
                    )

                    if self.attention_weights:
                        # ------------------------
                        # combine voxel_wise and patch_wise if attention_weighing is enabled
                        # ------------------------
                        w = torch.cat(
                            [self.w_voxel_transformer, self.w_patch_transformer]
                        )
                        w_voxel, w_patch = w.softmax(dim=0)
                        w_voxel = torch.unsqueeze(w_voxel, 0)
                        w_patch = torch.unsqueeze(w_patch, 0)

                        x = (
                            w_voxel * x_voxel_transformer
                            + w_patch * x_patch_transformer
                        ) + x  # x is residual block

                    # just add voxel wise and patch wise results
                    else:

                        x = (
                            x_voxel_transformer + x_patch_transformer + x
                        )  # x is residual block

            # reverse the encoder outputs to be aligned with the decoder
            encoders_features.insert(0, x)

        # remove the last encoder's output from the list
        # !!remember: it's the 1st in the list
        encoders_features = encoders_features[1:]
        # in the unet architecture, the last layer of encoder output + output
        # of one layer before will be passed to the first layer of decoder using skip connection

        # decoder part
        deep_supervision_output = []
        for decoder, encoder_features in zip(self.decoders, encoders_features):
            # pass the output from the corresponding encoder and the output
            # of the previous decoder
            x = decoder(encoder_features, x)
            if self.deep_supervision_num > 0:
                deep_supervision_output.append(x)

        x = self.final_conv(x)

        # apply adaptive threshold bias:
        # normalize adaptive thr based on norm of logits
        # logits_reshaped = x.view(x.shape[0], x.shape[1], -1)  # (B, C, HxWxD)
        # logit_norm = torch.norm(logits_reshaped, p=2, dim=2, keepdim=False)  # (B, C)
        # adaptive_thr_bias_norm = torch.norm(adaptive_thr_bias, p=2, dim=1, keepdim=True)  # (64, 1)
        # adaptive_thr_bias_normalized = (logit_norm * adaptive_thr_bias) / adaptive_thr_bias_norm

        if self.patch_wise_adaptive_thr and self.patch_wise_attn:
            x = x + adaptive_thr_bias.reshape(-1, 2, 1, 1, 1)

        # only apply to forground: x[:, 1, :, :, :] = x[:, 1, :, :, :] + adaptive_thr_bias.reshape(-1, 1, 1, 1)
        # x = x + adaptive_thr_bias[0].reshape(-1, 2, 1, 1, 1)

        # apply final_activation (i.e. Sigmoid or Softmax) only during prediction.
        # During training the network outputs logits
        if not self.training and self.final_activation is not None:
            x = self.final_activation(x)

        if self.training and self.deep_supervision_num > 0:
            deep_supervision_output[-1] = x
            deep_supervision_output = self.compute_deep_supervision_output(
                deep_supervision_output
            )
            for i, out in enumerate(deep_supervision_output):
                deep_supervision_output[i] = self.patch_to_image(out)
            x = torch.stack(deep_supervision_output, dim=0)
        else:
            x = self.patch_to_image(x)

        return x


class UNet3D(AbstractUNet):
    """
    3DUnet model from
    `"3D U-Net: Learning Dense Volumetric Segmentation from Sparse Annotation"
        <https://arxiv.org/pdf/1606.06650.pdf>`.

    Uses `DoubleConv` as a basic_module and nearest neighbor upsampling in the decoder
    """

    def __init__(
        self,
        in_channels,
        out_channels,
        final_sigmoid=True,
        f_maps=64,
        layer_order="gcr",
        img_size=(512, 512, 512),
        crop_size=(128, 128, 128),
        dropout_prob=0.2,
        num_groups=8,
        num_levels=4,
        is_segmentation=True,
        conv_padding=1,
        drop_path=0.1,
        attention_weights=True,
        attention_sum=True,
        patch_wise_attn=True,
        patch_wise_attn_down=True,
        patch_wise_attn_down_factor=2,
        patch_wise_adaptive_thr=True,
        patch_wise_PE_3D=True,
        encoder_depth_patch=5,
        atten_dim_patch=512,
        atten_depth_patch=8,
        num_heads_patch=8,
        mlp_ratio_patch=1.0,
        qkv_bias_patch=True,
        qk_scale_patch=1,
        drop_rate_patch=0.0,
        attn_drop_rate_patch=0.0,
        attn_drop_path_patch=0.1,
        norm_layer_patch=nn.LayerNorm,
        voxel_wise_attn=True,
        encoder_depth_voxel=5,
        atten_dim_voxel=512,
        atten_depth_voxel=8,
        num_heads_voxel=8,
        mlp_ratio_voxel=1.0,
        qkv_bias_voxel=True,
        qk_scale_voxel=1,
        drop_rate_voxel=0.0,
        attn_drop_rate_voxel=0.0,
        attn_drop_path_voxel=0.1,
        norm_layer_voxel=nn.LayerNorm,
        **kwargs
    ):
        super(UNet3D, self).__init__(
            in_channels=in_channels,
            out_channels=out_channels,
            final_sigmoid=final_sigmoid,
            basic_module=DoubleConv,
            img_size=img_size,
            crop_size=crop_size,
            f_maps=f_maps,
            layer_order=layer_order,
            num_groups=num_groups,
            num_levels=num_levels,
            is_segmentation=is_segmentation,
            conv_padding=conv_padding,
            is3d=True,
            dropout_prob=dropout_prob,
            drop_path=drop_path,
            attention_weights=attention_weights,
            attention_sum=attention_sum,
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
            norm_layer_patch=norm_layer_patch,
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
            norm_layer_voxel=norm_layer_voxel,
        )


class ResidualUNet3D(AbstractUNet):
    """
    Residual 3DUnet model implementation based on https://arxiv.org/pdf/1706.00120.pdf.
    Uses ResNetBlock as a basic building block, summation joining instead
    of concatenation joining and transposed convolutions for upsampling (watch out for block artifacts).
    Since the model effectively becomes a residual net, in theory it allows for deeper UNet.
    """

    def __init__(
        self,
        in_channels,
        out_channels,
        final_sigmoid=True,
        f_maps=64,
        layer_order="gcr",
        conv_kernel_size=3,
        pool_kernel_size=2,
        is3d=True,
        img_size=(512, 512, 512),
        crop_size=(128, 128, 128),
        dropout_prob=0.2,
        num_groups=8,
        num_levels=5,
        is_segmentation=True,
        conv_padding=1,
        drop_path=0.1,
        attention_weights=True,
        attention_sum=True,
        patch_wise_attn=True,
        patch_wise_attn_down=True,
        patch_wise_attn_down_factor=2,
        patch_wise_adaptive_thr=True,
        patch_wise_PE_3D=True,
        encoder_depth_patch=5,
        atten_dim_patch=512,
        atten_depth_patch=8,
        num_heads_patch=8,
        mlp_ratio_patch=1.0,
        qkv_bias_patch=True,
        qk_scale_patch=1,
        drop_rate_patch=0.0,
        attn_drop_rate_patch=0.0,
        attn_drop_path_patch=0.1,
        norm_layer_patch=nn.LayerNorm,
        voxel_wise_attn=True,
        encoder_depth_voxel=5,
        atten_dim_voxel=512,
        atten_depth_voxel=8,
        num_heads_voxel=8,
        mlp_ratio_voxel=1.0,
        qkv_bias_voxel=True,
        qk_scale_voxel=1,
        drop_rate_voxel=0.0,
        attn_drop_rate_voxel=0.0,
        attn_drop_path_voxel=0.1,
        norm_layer_voxel=nn.LayerNorm,
        deep_supervision=0,
        **kwargs
    ):
        super(ResidualUNet3D, self).__init__(
            in_channels=in_channels,
            out_channels=out_channels,
            final_sigmoid=final_sigmoid,
            basic_module=ResNetBlock,
            img_size=img_size,
            crop_size=crop_size,
            f_maps=f_maps,
            layer_order=layer_order,
            num_groups=num_groups,
            num_levels=num_levels,
            is_segmentation=is_segmentation,
            conv_padding=conv_padding,
            conv_kernel_size=conv_kernel_size,
            pool_kernel_size=pool_kernel_size,
            is3d=is3d,
            dropout_prob=dropout_prob,
            drop_path=drop_path,
            attention_weights=attention_weights,
            attention_sum=attention_sum,
            patch_wise_attn=patch_wise_attn,
            atten_dim_patch=atten_dim_patch,
            atten_depth_patch=atten_depth_patch,
            num_heads_patch=num_heads_patch,
            patch_wise_adaptive_thr=patch_wise_adaptive_thr,
            patch_wise_PE_3D=patch_wise_PE_3D,
            encoder_depth_patch=encoder_depth_patch,
            mlp_ratio_patch=mlp_ratio_patch,
            qkv_bias_patch=qkv_bias_patch,
            qk_scale_patch=qk_scale_patch,
            drop_rate_patch=drop_rate_patch,
            attn_drop_rate_patch=attn_drop_rate_patch,
            patch_wise_attn_down=patch_wise_attn_down,
            patch_wise_attn_down_factor=patch_wise_attn_down_factor,
            attn_drop_path_patch=attn_drop_path_patch,
            norm_layer_patch=norm_layer_patch,
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
            norm_layer_voxel=norm_layer_voxel,
            deep_supervision=deep_supervision,
        )

