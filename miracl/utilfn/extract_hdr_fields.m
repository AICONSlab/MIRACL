%  This function extracts fields that will be used to transform data from 
% it's space to that of the reference file. The fields in question are:
% 	- voxel size
% 	- origin
% 	- datatype
% 	- image description
%  each of the fields should be available from the header
function [voxel_size, origin, datatype, description] = extract_hdr_fields(hdr)
	%  extract the voxel size
	voxel_size = hdr.dime.pixdim(2:4);

	% extract the origin
	origin = hdr.hist.originator(1:3);

	% extract the datatype
	datatype = hdr.dime.datatype;

	% extract the description
	description = hdr.hist.descrip;
	return;