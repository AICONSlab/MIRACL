function vol = cropvol(vol, sz)
vol(1:sz, :, :, :) = 0;
vol(end-sz+1:end, :, :, :) = 0;

vol(:, 1:sz, :, :) = 0;
vol(:, end-sz+1:end, :, :) = 0;

vol(:, :, 1:sz, :) = 0;
vol(:, :, end-sz+1:end, :) = 0;
end