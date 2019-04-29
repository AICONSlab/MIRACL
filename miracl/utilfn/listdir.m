function dirs = listdir(path)
d = dir(path);
idxDir = [d(:).isdir];
dirs = {d(idxDir).name};
dirs(ismember(dirs, {'.', '..'})) = [];
end