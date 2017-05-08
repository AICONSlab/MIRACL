function stack = loadstack(dpStack)
fnFiles = listfile(fullfile(dpStack, '*'));
img = imread(fullfile(dpStack, fnFiles{1}));
[path, name, ext] = fileparts(fnFiles{1});

fnFiles = listfile(fullfile(dpStack, ['*' ext]));
stack = zeros(size(img, 1), size(img, 2), length(fnFiles), class(img));

for ii = 1 : length(fnFiles)
    img = imread(fullfile(dpStack, fnFiles{ii}));
    stack(:, :, ii) = img;
end
end