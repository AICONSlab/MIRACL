function k = doggen(sigma, X, Y, Z)
% Function to generate derivitive of Gaussian kernels, in 1D, 2D and 3D.
%
% (c) Qiyuan Tian, McNab Lab, Stanford University, September 2015

halfsize = ceil(3 * max(sigma));
x = -halfsize : halfsize;

dim = length(sigma);

if dim == 1
    if ~exist('X', 'var')
        X = x;
    end
    
    k = -X .* exp(-X.^2 / (2 * sigma^2));

elseif dim == 2
    if ~exist('X', 'var') && ~exist('Y', 'var')
        [X, Y] = meshgrid(x, x);
    end
    
    k = -X .* exp(-X.^2 / (2 * sigma(1)^2)) .* exp(-Y.^2 / (2 * sigma(2)^2)); 
    
elseif dim == 3
    if ~exist('X', 'var') && ~exist('Y', 'var') && ~exist('Z', 'var')
        [X, Y, Z] = meshgrid(x, x, x);
    end
    
    k = -X .* exp(-X.^2 / (2 * sigma(1)^2)) .* exp(-Y.^2 / (2 * sigma(2)^2)) .* exp(-Z.^2 / (2 * sigma(3)^2));
    
else
    error('Only support upto dimension 3');
end

k = k / sum(abs(k(:)));

end
