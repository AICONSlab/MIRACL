import os
import glob
import argparse
import argcomplete
import sys
from loguru import logger

import numpy as np
import nibabel as nib
import svgwrite
from nilearn.image import new_img_like
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from PIL import ImageEnhance
from nipype.interfaces.ants.visualization import CreateTiledMosaic
from nipype.interfaces.ants.visualization import ConvertScalarImageToRGB
from math import floor

logger.add(os.getcwd()+"/miracl_stats_heatmap_group_error.log", level='ERROR', mode="w")

ORIENTATION_DICT = {0 : 'x',
                    1 : 'y',
                    2 : 'z'}

def parsefn():
    parser = argparse.ArgumentParser(usage='%(prog)s -f fixed_file -r registered_file [-o output_file] [-s segmentation_file] [-sl slices] [-sc scale] [-c] [-cr min max] \n\n'
                                           "Create svg to check the quality of registration between a fixed image and registered image")

    required = parser.add_argument_group('required arguments')

    required.add_argument('-f', '--fixed', type=str, metavar='', help="fixed image used in registration", required=True)
    required.add_argument('-r', '--reg', type=str, metavar='', help="registration output", required=True)

    optional = parser.add_argument_group('optional arguments')

    optional.add_argument('-s', '--seg', type=str, metavar='', help="segmentation mask")
    optional.add_argument('-sl', '--slices', type=int, metavar='', help="number of slices",
                          default=7)
    optional.add_argument('-sc', '--scale', type=int, metavar='', help="scale of interval between slices",
                          default=15)
    optional.add_argument('-c', '--color', action='store_true', help="display registered image in color scale",
                          default=False)
    optional.add_argument('-cr', '--color_range', nargs=2, type=int, metavar=('min', 'max'), help="display registered image in colour scale within range min to max",
                          default=(None, None))
    optional.add_argument('-o', '--out', type=str, metavar='', help="output image filename")

    return parser

def parse_inputs(parser, args):
    if isinstance(args, list):
        args = parser.parse_args(args)
    argcomplete.autocomplete(parser)

    fixed = args.fixed
    reg = args.reg
    seg = args.seg if args.seg else None
    slices = args.slices
    scale = args.scale
    color = args.color
    minimum, maximum = args.color_range

    if isinstance(minimum, int) and isinstance(maximum, int) and not(color):
        color = True

    out_dir = None
    out_file = None
    if args.out:
        out_dir = os.path.dirname(args.out)
        out_file = args.out
    else:
        out_file = 'reg_comparison.svg'
        out_dir = os.getcwd()
    
    prefix = os.path.splitext(os.path.basename(out_file))[0]

    return fixed, reg, seg, slices, scale, color, minimum, maximum, out_dir, out_file, prefix


def get_orient(image):
    return nib.aff2axcodes(image.affine)

def generate_tile_image(input_img, output_img, axis, slices, image_type, seg_img, color_scale, preprocdir):
    ''' Given dimension, slice indices of image, extract slices at filename and save them to filename
    '''
    
    img = nib.load(input_img)

    slice_count = img.shape[axis]
    slices_shifted = (np.array(slices) + (slice_count // 2))
    slices_shifted = [str(i) for i in slices_shifted]

    width_padding = str((max(img.shape) - img.shape[-2+floor(axis/-2)]) // 2 + 50)
    height_padding = str(((max(img.shape) - img.shape[-1-floor(axis/2)]) // 2) + 10) 
    #width_padding = str((max(img.shape) - img.shape[axis - 2]) // 2)
    #height_padding = str(((max(img.shape) - img.shape[axis - 1]) // 2) + 10)
   
    # generate image with specific slices
    mosaic_slicer = CreateTiledMosaic()
    mosaic_slicer.inputs.input_image = input_img
    mosaic_slicer.inputs.output_image = output_img
    mosaic_slicer.inputs.slices = "x".join(slices_shifted)
    mosaic_slicer.inputs.tile_geometry = "1x"+str(len(slices_shifted))
    mosaic_slicer.inputs.direction = axis
    mosaic_slicer.inputs.pad_or_crop = '[ '+width_padding+'x '+height_padding+' , '+width_padding+'x '+height_padding+' ,0]'
    mosaic_slicer.inputs.flip_slice = "0x1"

    # apply color scale to registered image
    if image_type == 'reg' and color_scale:
        mosaic_slicer.inputs.alpha_value = 1
        mosaic_slicer.inputs.rgb_image = os.path.join(preprocdir, image_type+'_rgb.nii.gz')
        

    else:
        mosaic_slicer.inputs.alpha_value = 0
        mosaic_slicer.inputs.rgb_image = input_img    
    mosaic_slicer.run()

    # draw left, right, slice number
    tiled_image = Image.open(output_img)
    draw = ImageDraw.Draw(tiled_image)
    offset = tiled_image.width // len(slices)

    for i in range(len(slices)):
        draw.text((5 + i*offset, tiled_image.height - 20),ORIENTATION_DICT[axis]+"="+str(slices[i]),(255,255,255))

        if ORIENTATION_DICT[axis] != "x":
            draw.text((20 + i*offset, 20),"L",(255,255,255))
            draw.text(((i+1)*offset - 25, 20),"R",(255,255,255))

    tiled_image.save(output_img)


def generate_pngs(fixed_file, reg_file, prefix, seg_file, color_scale, minimum, maximum, output_dir=None, slices=7, scale=15):
    
    fixed_img = nib.load(fixed_file)
    reg_img = nib.load(reg_file)
    seg_img = nib.load(seg_file) if seg_file else None

    if get_orient(fixed_img) != get_orient(reg_img):
        raise Exception("Both the registration and the fixed image have different orientations")
    
    if fixed_img.shape != reg_img.shape:
        raise Exception("Both the registration and the fixed image have different voxel dimensions ({}, and {})".format(reg_img.shape, fixed_img.shape))

    # check segmentation image
    if seg_img and get_orient(seg_img) != get_orient(reg_img):
        raise Exception("The segmentation mask's orientation is different than the others")

    if slices*scale >= min(fixed_img.shape):
        raise Exception("The slice and/or scale inputs are too large, exceed the dimensions of the registration and fixed images")

    # generate blank image
    if not(seg_file):
        seg_file = new_img_like(fixed_img, np.zeros(fixed_img.shape))

    # create output dir for intermediate images
    preprocdir = os.path.join(output_dir, 'svg_process')
    os.makedirs(preprocdir, exist_ok=True)

    # reorient images to canonical orientation
    canonical_fixed = nib.as_closest_canonical(fixed_img)
    nib.save(canonical_fixed, os.path.join(preprocdir, 'fixed_canonical.nii.gz'))

    canonical_reg = nib.as_closest_canonical(reg_img)
    nib.save(canonical_reg, os.path.join(preprocdir, 'reg_canonical.nii.gz'))  

    # set slice indices
    center = [int(dim / 2) for dim in fixed_img.shape]

    min_slice = (slices // 2) * -scale
    slice_pos = [min_slice + (i*scale) for i in range(slices)]

    # generate 6 images
    for img_type, img in [('fixed', preprocdir+'/fixed_canonical.nii.gz'), ('reg', preprocdir+'/reg_canonical.nii.gz')]:

        # make RGB
        if color_scale and img_type == 'reg':
            if minimum == None and maximum == None:
                command = 'ConvertScalarImageToRGB 3 '+img+' '+preprocdir+'/'+img_type+'_rgb.nii.gz none hot'
                os.system(command)
            else:

                converter = ConvertScalarImageToRGB()
                converter.inputs.dimension = 3
                converter.inputs.input_image = img
                converter.inputs.output_image = os.path.join(preprocdir, img_type+'_rgb.nii.gz')
                converter.inputs.colormap = 'hot'
                converter.inputs.minimum_input = int(minimum)
                converter.inputs.maximum_input = int(maximum)
                converter.run()

        for axis in range(0, 3):
            
            # output
            if output_dir is None:
                output_dir = os.getcwd()
            
            output_file = os.path.join(preprocdir, "{}_{}_{}.png".format(prefix, img_type, axis))

            generate_tile_image(img, output_file, axis, slice_pos, img_type, seg_file, color_scale, preprocdir)

        os.remove(img)

        if color_scale and img_type == 'reg':
            os.remove(preprocdir+'/'+img_type+'_rgb.nii.gz')


def combine_png(out_dir, prefix):
    """
    Combine the generate pngs to be used in the animation
    """

    # grab all fixed and reg images
    fixed_images = glob.glob(os.path.join(out_dir, 'svg_process', '{}_fixed_*.png'.format(prefix)))
    fixed_images.sort()
    reg_images = glob.glob(os.path.join(out_dir, 'svg_process', '{}_reg_*.png'.format(prefix)))
    reg_images.sort()

    if not fixed_images or not reg_images:
        raise Exception("Intermediate files are missing. You may be missing either a registration file or the fixed image")

    # extract images
    fixed_pngs = [Image.open(x) for x in fixed_images]
    reg_pngs = [Image.open(x) for x in reg_images]

    #for i in range(len(reg_pngs)):# - increase PNG image contrast
    #     reg_pngs[i]=ImageEnhance.Contrast(reg_pngs[i]).enhance(10)
    width=max([x.width for x in fixed_pngs])
    #width = fixed_pngs[0].width
    max_height = max([x.height for x in fixed_pngs])
    height = max_height*len(fixed_pngs)


    # create larger fixed and reg images before saving
    fixed_image = Image.new('RGB', (width, height))

    draw = ImageDraw.Draw(fixed_image)

    for i, png in enumerate(fixed_pngs):
        offset = (max_height - png.height) // 2
        fixed_image.paste(png, (0, (i*max_height)+offset))

    draw.text((5, 5),"Fixed",(255,255,255))
    fixed_image.save(os.path.join(out_dir, 'svg_process', '{}_combined_fixed_image.png'.format(prefix)))

    reg_image = Image.new('RGB', (width, height))

    draw = ImageDraw.Draw(reg_image)

    for j, png in enumerate(reg_pngs):
        offset = (max_height - png.height) // 2
        reg_image.paste(png, (0, (j*max_height)+offset))

    draw.text((5, 5),"Reg",(255,255,255))
    reg_image.save(os.path.join(out_dir, 'svg_process', '{}_combined_reg_image.png'.format(prefix)))

def compile_svg(out_dir, out_file, prefix):
    """
    Combine the fixed image and the registration image into an SVG animation.
    """
    fixed_png = glob.glob(os.path.join(out_dir, '**/{}_combined_fixed_image.png'.format(prefix)))
    reg_png = glob.glob(os.path.join(out_dir, '**/{}_combined_reg_image.png'.format(prefix)))

    if not fixed_png or not reg_png:
        raise Exception("Intermediate files are missing. You may be missing either a registration file or the fixed image")

    fixed_png = fixed_png[0]
    reg_png = reg_png[0]

    # get relative paths for swg file
    fixed_relpath = os.path.relpath(fixed_png, out_dir)
    reg_relpath = os.path.relpath(reg_png, out_dir)

    fixed = Image.open(fixed_png)
    size = (fixed.width, fixed.height)

    dwg = svgwrite.Drawing(out_file, size)
    background = dwg.add(svgwrite.image.Image(reg_relpath))
    foreground = dwg.add(svgwrite.image.Image(fixed_relpath))
    
    foreground.add(dwg.animate("opacity", dur="10s", values="0;0;1;1;0", keyTimes="0;0.1;0.5;0.7;1", repeatCount="indefinite"))

    dwg.save()

@logger.catch
def main(args):
    parser = parsefn()
    fixed, reg, seg, slices, scale, color, minimum, maximum, out_dir, out_file, prefix = parse_inputs(parser, args)

    generate_pngs(fixed, reg, prefix, seg, color, minimum, maximum, out_dir, slices, scale)
    combine_png(out_dir, prefix)
    compile_svg(out_dir, out_file, prefix)

if __name__ == "__main__":
    main(sys.argv[1:])
