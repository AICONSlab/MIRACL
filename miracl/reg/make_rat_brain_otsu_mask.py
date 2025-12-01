import SimpleITK as sitk
import sys

input_path, out_mask_path, out_masked_path = sys.argv[1:4]

img = sitk.ReadImage(input_path, sitk.sitkFloat32)

mask = sitk.OtsuThreshold(img, 0, 1, 200)

masked_img = sitk.Mask(img, mask)

sitk.WriteImage(mask, out_mask_path)
sitk.WriteImage(masked_img, out_masked_path)
print(f"Saved mask: {out_mask_path}\n Saved masked image: {out_masked_path}")
