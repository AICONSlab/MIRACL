function mat2nii(inmat,x,y,z,outnii)

data=load(inmat);
names=fieldnames(data);
img=eval(sprintf('data.%s',names{1}));
% nii=make_nii(img,[x y z],[cx cy cz]);
nii=make_nii(img,[x y z]);
save_nii(nii,outnii);

end