function sta_track(img, dogsigs, gausigs, angs, fpBmask, fpSmask, dpResult, stepLength, rk2, img_orient)

[ref_hdr, stack] = readnii(img);

for ii = 1 : length(dogsigs)
    dogsig = dogsigs(ii);
    
    % deravitive of gaussian (dog) kernel 
    dogkercc = single(doggen([dogsig, dogsig, dogsig])); % along colume direction
    dogkerrr = permute(dogkercc, [2, 1, 3]); % along row direction
    dogkerzz = permute(dogkercc, [1, 3, 2]); % along z direction

    for jj = 1 : length(gausigs)
        gausig = gausigs(jj);
        
        dpTensor = fullfile(dpResult, ['dog' num2str(dogsig) 'gau' num2str(gausig) 'step' num2str(stepLength)]);
        mkdir(dpTensor);
        
        % gaussian kernel
        gaussker = single(gaussgen([gausig, gausig, gausig]));
        
        % half kernel size
        halfsz = (max(size(dogkercc, 1), size(gaussker, 1)) + 1) / 2;

        % compute gradient
        grr = convn(stack, dogkerrr, 'same');
        gcc = convn(stack, dogkercc, 'same');
        gzz = convn(stack, dogkerzz, 'same');

        % compute gradient product
        gprrrr = grr .* grr;
        gprrcc = grr .* gcc;
        gprrzz = grr .* gzz;
        gpcccc = gcc .* gcc;
        gpcczz = gcc .* gzz;
        gpzzzz = gzz .* gzz;

        % compute gradient amplitude
        ga = sqrt(gprrrr + gpcccc + gpzzzz);
        writenii(cropvol(ga, halfsz), fullfile(dpTensor, 'ga.nii.gz'), ref_hdr);

        % compute gradient vector
        gv = cat(4, grr, gcc, gzz);
        gv = gv ./ repmat(ga, [1, 1, 1, 3]);
        writenii(cropvol(gv, halfsz), fullfile(dpTensor, 'gv.nii.gz'), ref_hdr);
                
        % blur gradient product
        gprrrrgauss = convn(gprrrr, gaussker, 'same');
        gprrccgauss = convn(gprrcc, gaussker, 'same');
        gprrzzgauss = convn(gprrzz, gaussker, 'same');
        gpccccgauss = convn(gpcccc, gaussker, 'same');
        gpcczzgauss = convn(gpcczz, gaussker, 'same');
        gpzzzzgauss = convn(gpzzzz, gaussker, 'same');
                
        % FSL tensor
%         fsltensor = cat(4, gprrrrgauss, gprrccgauss, gprrzzgauss, gpccccgauss, gpcczzgauss, gpzzzzgauss);
%         fpFslTensor = fullfile(dpTensor, 'fsl_tensor.nii.gz');
%         writenii(cropvol(fsltensor, halfsz), fpFslTensor);

        % DTK tensor
        dtktensor = cat(4, gprrrrgauss, gprrccgauss, gpccccgauss, gprrzzgauss, gpcczzgauss, gpzzzzgauss);
        fpDtkTensor = fullfile(dpTensor, 'dtk_tensor.nii.gz');
        writenii(cropvol(dtktensor, halfsz), fpDtkTensor, ref_hdr);
        
        % brain mask 
        [bmask_hdr, bmask_img] = readnii(fpBmask);
        bmask = cropvol(bmask_img, halfsz);
        bmask = uint8(bmask > 0);
        fpBmaskCrop = fullfile(dpTensor, 'bmask.nii.gz');
        writenii(bmask, fpBmaskCrop, bmask_hdr);
        
        % seed mask
        [smask_hdr, smask_img] = readnii(fpSmask);
        smask = cropvol(smask_img, halfsz);
        smask = uint8(smask > 0);
        fpSmaskCrop = fullfile(dpTensor, 'smask.nii.gz');
        writenii(smask, fpSmaskCrop, smask_hdr);
        
        for kk = 1 : length(angs)
            ang = angs(kk);
        
            fpDtkTensor = fullfile(dpTensor, 'dtk');
            fpTrack = fullfile(dpTensor, ['fiber_ang' num2str(ang) '.trk']);
            
            % if rk2, else
            if rk2 == 1
                fpTrack = fullfile(dpTensor, ['fiber_ang' num2str(ang) '.trk']);
                cmd = ['dti_tracker ' fpDtkTensor ' ' fpTrack ' -at ' num2str(ang) ' -v3 -m ' fpBmaskCrop ' 0.1 1.1 -sm ' fpSmaskCrop ' 0.1 1.1 -l ' num2str(stepLength) ' -rk2 -vorder ' img_orient ];
            else
                fpTrack = fullfile(dpTensor, ['fiber_ang' num2str(ang) '.trk']);
                cmd = ['dti_tracker ' fpDtkTensor ' ' fpTrack ' -at ' num2str(ang) ' -v3 -m ' fpBmaskCrop ' 0.1 1.1 -sm ' fpSmaskCrop ' 0.1 1.1 -l ' num2str(stepLength) ' -vorder ' img_orient ];
                [status, result] = system(cmd, '-echo');
                fpTrack = fullfile(dpTensor, ['fiber_ang' num2str(ang) 'rseed5.trk']);
                cmd = ['dti_tracker ' fpDtkTensor ' ' fpTrack ' -at ' num2str(ang) ' -v3 -rseed 5 -m ' fpBmaskCrop ' 0.1 1.1 -sm ' fpSmaskCrop ' 0.1 1.1 -l ' num2str(stepLength) ' -vorder ' img_orient ];
                [status, result] = system(cmd, '-echo');
            end
            % [status, result] = system(cmd, '-echo');
        end
    end
end

end