// CLARITY 3D neuron segmentation (sparse)
// 
// Macro for Fiji/ImageJ 
// Segments neurons in cleared mouse brain of sparse stains (like Thy1) in 3D 
// 
// (c) Maged Goubran, maged.goubran@utoronto.ca, 2022
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
// -----------------------------------

// Get files path
//path = getArgument();

args = split(getArgument()," ");
path = args[0];

if (lengthOf(args)>1) {

    fstr = args[1];

}

print("Files path is:" + path);

segpath = path + "/../segmentation_sparse/" ;

// Init Parameters:-

// num of CPUS
ncpus = 20;
// radius (px) for local maxima
radpx = 2;
radpz = 2;

// max object size
maxobjsz = 10000;

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

  	// don't scale images linearly
  	run("Conversions...", " ");

	print("Converting input to 8-bit");

    if (lengthOf(args)>1) {

        print("Reading all files with " +fstr+ " in filename");

        run("Image Sequence...", "open="+path+" starting=1 increment=1 scale=100 file="+fstr+" sort convert");

    } else {

        run("Image Sequence...", "open="+path+" starting=1 increment=1 scale=100 file=tif sort convert");

    }

} else {

	print("Keeping input type unchanged");

    if  (lengthOf(args)>1)  {

        print("Reading all files with " +fstr+ " in filename");

        run("Image Sequence...", "open="+path+" starting=1 increment=1 scale=100 file="+fstr+" sort");

    } else {

        run("Image Sequence...", "open="+path+" starting=1 increment=1 scale=100 file=tif sort");

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
	run("Subtract Background...", "rolling=20 sliding stack");

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
	run("Enhance Contrast...", "saturated=0.5 normalize process_all use");
		
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

// Compute Top Hat transform

//print("--Computing Top Hat transform ");
//print("disk radius " +radpx);

//run("3D Fast Filters","filter=TopHat radius_x_pix=&radpx radius_y_pix=&radpx radius_z_pix=&radpz Nb_cpus=&ncpus");

//tophatstack = getImageID();
//rename("TopHat");


// -----------------------------------

// Compute Global threshold

outyen = segpath + "median_yen.tif";

if (!File.exists(outyen)) {

	// Duplicate image
	run("Duplicate...","duplicate");

	print("-- Computing Yen Threshold");

  run("Auto Threshold", "method=Yen ignore_black white stack use_stack_histogram");

	// Save Yen
	save(outyen);


} else {

	print("Yen Thresholded Median img already exists .. skipping & opening it ");

	open(outyen);

}


yenstack = getImageID();
yentitle = getTitle();

rename("Yen");

// -----------------------------------

// Compute Local threshold 

//outlocthr = segpath + "median_locthr.tif";
//
//// Collect Garbage
//call("java.lang.System.gc");
//
//if (!File.exists(outlocthr)) {
//
//	// Duplicate image
//	run("Duplicate...","duplicate");
//
//	print("-- Computing Local Threshold");
//
//	run("Auto Local Threshold", "method=Phansalkar radius=15 parameter_1=0 parameter_2=0 white stack");
//
//	// Save LocThr
//	save(outlocthr);
//
//
//} else {
//
//	print("Local Thresholded Median img already exists .. skipping & opening it ");
//
//	open(outlocthr);
//
//}
//
//
//locthrstack = getImageID();
//locthrtitle = getTitle();
//
//rename("LocalThr");

// -----------------------------------

// Compute Minimum 

outmin = segpath + "median_locthr_min.tif";

// Collect Garbage
call("java.lang.System.gc");

if (!File.exists(outmin)) {

	print("-- Computing Minimum");

	run("3D Fast Filters","filter=Minimum radius_x_pix="+radpx+" radius_y_pix="+radpx+" radius_z_pix="+radpz+" Nb_cpus="+ncpus+"");

	// Save min
	save(outmin);

} else {

	print("Minimum img already exists .. skipping & opening it ");
	
	open(outmin);

}

minstack = getImageID();
mintitle = getTitle();

// -----------------------------------

// Filter very large objects (like border artifacts)

outfil = segpath + "min_filtered.tif";

// Collect Garbage
call("java.lang.System.gc");

if (!File.exists(outfil)) {

	print("-- Filtering very large objects");

	run("3D Simple Segmentation", "low_threshold=128 min_size=0 max_size="+maxobjsz+"");

} else {

	print("Filtered Minimum img already exists .. skipping & opening it ");
	
	open(outfil);

}

// -----------------------------------

// Close rest of images

// close backless image
selectImage(backstack);
close();

// close enhance image
//selectImage("EnhanceStack");
selectImage(enhancestack);
close();

// close min image
selectImage(minstack);
close();

// bin
selectImage("Bin");
close();

// -----------------------------------

// Compute Marker controlled Watershed 

outseg = segpath + "seg_sparse.tif";

// Collect Garbage
call("java.lang.System.gc");

if (!File.exists(outseg)) {

	print("-- Computing Marker-controlled Watershed segmentation... This might take a while");

	run("Marker-controlled Watershed", "input=MedianImg marker=Seg mask=Yen calculate use");

	run("3D Simple Segmentation", "low_threshold=1 min_size=0 max_size="+maxobjsz+"");

	// Duplicate image
	run("Duplicate...","duplicate");

	// Save segmentation
	save(outseg);

	// Save segmentation mhd
	// run("MHD/MHA ...", "save=" +segpath+ "seg_sparse.mhd");

	print("-- Computing binary segmentation");

	// Make binary mask
	run("Make Binary", "method=Percentile background=Default calculate black");

	// Save segmentation bin
	save(segpath + "seg_bin_sparse.tif");

	// Save segmentation bin mhd
	// run("MHD/MHA ...", "save=" +segpath+ "seg_bin_sparse.mhd");

} else {

	print ("Segmentation already computed .. skipping")

}

// save log file 
outlog = segpath + "seg_sparse_log.txt";

f = File.open(outlog); 
content=getInfo("log");
print(f,content);
File.close(f); 

// Quit Fiji
run("Quit");