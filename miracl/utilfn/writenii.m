% Usage: fpNiiGz = writenii(data, fpNii, [refImgHdr])
%
function fpNiiGz = writenii(varargin)
	fpNii = varargin{2};
	data = varargin{1};
	if strfind(fpNii, 'nii.gz')
		[path, name, ext] = fileparts(fpNii);
		fpNii = fullfile(path, name);
	end

	% if a file header was passed, extract the information needed and generate the nii
	%  otherwise, just generate the image as is
	if nargin > 2 && ~isempty(varargin{3})
		[voxel_size, origin, datatype, description] = extract_hdr_fields(varargin{3});
		nii = make_nii(data, voxel_size, origin, datatype, description);
	else
		nii = make_nii(data);
	end

	save_nii(nii, fpNii);
	fpNiiGz = gzip(fpNii);
	delete(fpNii);
	end
