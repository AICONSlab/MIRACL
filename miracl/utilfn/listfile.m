function files = listfile(path)
d = dir(path);
idxFile = ~[d(:).isdir];
files = {d(idxFile).name};
end