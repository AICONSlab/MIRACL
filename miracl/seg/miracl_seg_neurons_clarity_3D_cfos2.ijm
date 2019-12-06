// CLARITY 3D neuron segmentation (virus)
// 
// Macro for Fiji/ImageJ 
// Segments neurons in cleared mouse brain of virus stains in 3D
// 
// (c) Maged Goubran, mgoubran@stanford.edu, 2018
//
// based on plugins from:
// 
// the 3D Segmentation plugins (3D ImageJ suite) 
// http://imagejdocu.tudor.lu/doku.php?id=plugin:stacks:3d_ij_suite:start
// 
// &
//
// the Mathematical Morphology plugins 
// http://imagej.net/MorphoLibJ
//
// &
//
// the Shape Filter plugin
// https://imagej.net/Shape_Filter
//
// -----------------------------------

// Get files path
//path = getArgument();

args = split(getArgument()," ");
path = args[0];

if (lengthOf(args)>1) {

    fstr = args[1];

}

print("Files path is:" + path);

segpath = path + "/../segmentation_cfos/" ;

// Init Parameters:-

// num of CPUS
ncpus = 8;
// radius (px) for local maxima
radpx = 1;
radpz = 1;

// max object size
minobjsz = 10;
maxobjsz = 500;

// convert to 8-bit
convert = 1;

// -----------------------------------

// Get files list
list = getFileList(path);
num = list.length;
print("Sequence contains " +num+ " images in total");

// Open stack
print("--Reading stack");

if (convert==1) {

	print("Converting input to 8-bit");

    if (lengthOf(args)>1) {

        print("Reading all files with " +fstr+ " in filename");

        run("Image Sequence...", "open="+path+" starting=1 increment=1 scale=100 file="+fstr+" sort");
	Stack.getStatistics(voxelCount, mean, min, max, stdDev);
	setMinAndMax(min,mean+50*stdDev);
	run("8-bit");

    } else {

        run("Image Sequence...", "open="+path+" starting=1 increment=1 file=tif sort");
	Stack.getStatistics(voxelCount, mean, min, max, stdDev);
	setMinAndMax(min,mean+50*stdDev);
	run("8-bit");

    }

} else {

	print("Keeping input type unchanged");

    if  (lengthOf(args)>1)  {

        print("Reading all files with " +fstr+ " in filename");

        run("Image Sequence...", "open="+path+" starting=1 increment=1 scale=100 file="+fstr+" sort");
	Stack.getStatistics(voxelCount, mean, min, max, stdDev);
	setMinAndMax(min,mean+50*stdDev);

    } else {

        run("Image Sequence...", "open="+path+" starting=1 increment=1 scale=100 file=tif sort");
	Stack.getStatistics(voxelCount, mean, min, max, stdDev);
	setMinAndMax(min,mean+50*stdDev);

    }

}

// Get ID
orgstack = getImageID();
// Get Title
orgtitle = getTitle();

// if needed run("16-bit");

// -----------------------------------

// Substract Background

outback = segpath + "norm.tif";

// Collect Garbage
call("java.lang.System.gc");

if (!File.exists(outback)) {

	// Duplicate image
	run("Duplicate...","duplicate");

	print("-- Subtracting Background");
	run("Subtract Background...", "rolling=2 sliding stack");	

	// Save Normalized int
	save(outback);

} else {

	print("Background-less image already computed .. skipping & openning it ");

	open(outback);

}

backstack = getImageID();
backtitle = getTitle();	

rename("BacklessStack");

// close org image
selectImage(orgstack);
close();

// -----------------------------------

// Enhance Contrast

outenhance = segpath + "backremov_enhance.tif";

// Collect Garbage
call("java.lang.System.gc");

if (!File.exists(outenhance)) {

	// Duplicate image
	run("Duplicate...","duplicate");

	print("-- Enhancing contrast & normalizing Histogram");
	run("Enhance Contrast...", "saturated=0.05 normalize process_all use");
		
	// Save enhanced 
	save(outenhance);

} else {

	print("Enhancing contrast already performed .. skipping & opening it ");
	
	open(outenhance);

}

enhancestack = getImageID();
enhancetitle = getTitle();		

rename("EnhanceStack");

// -----------------------------------

// Compute Median Filter

call("java.lang.System.gc");

outmed = segpath + "backremov_enhance_median.tif";

// Collect Garbage
call("java.lang.System.gc");

if (!File.exists(outmed)) {

	print("-- Computing Median image");
	print("using " +ncpus+ " CPUs for parallelization");

	// Create median image
	run("3D Fast Filters","filter=Median radius_x_pix="+radpx+" radius_y_pix="+radpx+" radius_z_pix="+radpz+" Nb_cpus="+ncpus+"");

	// Save Med
	save(outmed);

} else {

	print("Median filtering already computed .. skipping & opening it ");

	open(outmed);

}

medstack = getImageID();
medtitle = getTitle();

rename("MedianImg");

// -----------------------------------

// Compute Local threshold 

outlocthr = segpath + "median_locthr.tif";

// Collect Garbage
call("java.lang.System.gc");

if (!File.exists(outlocthr)) {

	// Duplicate image
	run("Duplicate...","duplicate");

	print("-- Computing Local Threshold");

	run("Auto Local Threshold", "method=Bernsen radius=15 parameter_1=0 parameter_2=0 white stack");

	// Save LocThr 
	save(outlocthr);


} else {

	print("Local Thresholded Median img already exists .. skipping & opening it ");
	
	open(outlocthr);

}


locthrstack = getImageID();
locthrtitle = getTitle();

rename("LocalThr");


// -----------------------------------

// Filter very large objects (like border artifacts)

outfil = segpath + "median_locthr_filtered.tif";

// Collect Garbage
call("java.lang.System.gc");

if (!File.exists(outfil)) {

	print("-- Filtering large objects and artifacts");

	run("Shape Filter", "area=4-40 circularity=0-15 elongation=0-0.8 draw_holes black_background exclude_on_edges stack");

	save(outfil);

} else {

	print("Filtered Minimum img already exists .. skipping & opening it ");
	
	open(outfil);

}

filstack = getImageID();
filtitle = getTitle();

rename("Filtered");

// -----------------------------------

// Run init seg (Create markers for Watershed)

initseg = segpath + "init_seg.tif";

// Collect Garbage
call("java.lang.System.gc");

if (!File.exists(initseg)) {

	print("-- Running initial segmentation");

	run("3D Simple Segmentation", "low_threshold=128 min_size=7 max_size=400");

	save(initseg);

} else {

	print("Initial segmentation already exists .. skipping & opening it ");
	
	open(initseg);

}

initsegstack = getImageID();
initsegtitle = getTitle();

rename("InitSeg");

// -----------------------------------

// Close rest of images

// close backless image
selectImage(backstack);
close();

// close enhance image
selectImage(enhancestack);
close();

// -----------------------------------

// Compute Marker controlled Watershed 

outseg = segpath + "seg_cfos.tif";

// Collect Garbage
call("java.lang.System.gc");

if (!File.exists(outseg)) {

	print("-- Computing Marker-controlled Watershed segmentation... This might take a while");

	run("Marker-controlled Watershed", "input=MedianImg marker=InitSeg mask=Filtered calculate use");

	// Filter objects again
	run("3D Simple Segmentation", "low_threshold=1 min_size=7 max_size=800");	

	// Duplicate image
	run("Duplicate...","duplicate");

	// Save segmentation
	save(outseg);

	print("-- Computing binary segmentation");

	// Make binary mask
	setOption("BlackBackground", true);
	run("Make Binary", "method=Percentile background=Default calculate black");

	// Save segmentation bin
	save(segpath + "seg_bin_cfos.tif");


} else {

	print ("Segmentation already computed .. skipping");

}

// save log file 
outlog = segpath + "seg_virus_log.txt";

f = File.open(outlog); 
content=getInfo("log");
print(f,content);
File.close(f); 

// Quit Fiji
run("Quit");
