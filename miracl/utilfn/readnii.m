% return both the header and the image for a given nifti input
function [hdr, img] = readnii(fpNii)
tmp = load_nii(fpNii);
img = tmp.img;
hdr = tmp.hdr;
end