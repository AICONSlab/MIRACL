function nii = readnii(fpNii)
tmp = load_nii(fpNii);
nii = tmp.img;
end