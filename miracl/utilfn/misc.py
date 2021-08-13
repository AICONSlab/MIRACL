import nibabel as nib
import numpy as np
import os


def convert_dtype(input, dtype):
    """
    """
    img = nib.load(input)
    arr = img.get_fdata()
    new_arr = arr.astype(dtype)
    new_img = nib.Nifti1Image(arr, img.affine, header=img.header)

    return new_img

def get_orient(fp):
    """ Given an input (a filename), return the orient of the file
    """
    try:
        img = nib.load(fp)
        orient_tup = nib.aff2axcodes(img.affine)
        return ''.join(orient_tup)
    except AttributeError:
        print('{fp} is not loadable. Please try again')
        return None


