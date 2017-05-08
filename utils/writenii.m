function fpNiiGz = writenii(data, fpNii)
if strfind(fpNii, 'nii.gz')
    [path, name, ext] = fileparts(fpNii);
    fpNii = fullfile(path, name);
end

nii = make_nii(data);
save_nii(nii, fpNii);
fpNiiGz = gzip(fpNii);
delete(fpNii);
end