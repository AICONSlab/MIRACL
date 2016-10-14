// CLARITY 3D neuron segmentation (sparse)
// 
// Macro for Fiji/ImageJ 
// Segments neurons in cleared mouse brain in 3D
// 
// (c) Maged Goubran, mgoubran@stanford.edu, 2016
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

// Init Parameters:-

// num of CPUS
ncpus = 40;
// radius (px) for local maxima
radpx = 2;
radpz = 2;

// max object size
maxobjsz = 10000;

// convert to 8-bit
convert = 1;

// -----------------------------------

// Substract Background

// Collect Garbage
call("java.lang.System.gc");

// Duplicate image
run("Duplicate...","duplicate");

print("-- Subtracting Background");
run("Subtract Background...", "rolling=50 sliding stack");	

backstack = getImageID();
backtitle = getTitle();

rename("BacklessStack");

// -----------------------------------

// Enhance Contrast

// Duplicate image
run("Duplicate...","duplicate");

print("-- Enhancing contrast & normalizing Histogram");
run("Enhance Contrast...", "saturated=0.5 normalize process_all use");
	
enhancestack = getImageID();
enhancetitle = getTitle();		

rename("EnhanceStack");

// -----------------------------------

// Compute Median Filter

print("-- Computing Median image");
print("using " +ncpus+ " CPUs for parallelization");

// Create median image
run("3D Fast Filters","filter=Median radius_x_pix=&radpx radius_y_pix=&radpx radius_z_pix=&radpz Nb_cpus=&ncpus");

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

// Compute Local threshold 

// Duplicate image
run("Duplicate...","duplicate");

print("-- Computing Local Threshold");

run("Auto Local Threshold", "method=Phansalkar radius=15 parameter_1=0 parameter_2=0 white stack");

locthrstack = getImageID();
locthrtitle = getTitle();

rename("LocalThr");

// -----------------------------------

// Compute Minimum 

print("-- Computing Minimum");

run("3D Fast Filters","filter=Minimum radius_x_pix=&radpx radius_y_pix=&radpx radius_z_pix=&radpz Nb_cpus=ncpus");

minstack = getImageID();
mintitle = getTitle();

// -----------------------------------

// Filter very large objects (like border artifacts)

// Collect Garbage
call("java.lang.System.gc");

print("-- Filtering very large objects");

run("3D Simple Segmentation", "low_threshold=128 min_size=0 max_size=&maxobjsz");

// -----------------------------------

// Close rest of images

// close backless image
selectImage(backstack);
close();

// close enhance image
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

// Collect Garbage
call("java.lang.System.gc");

print("-- Computing Marker-controlled Watershed segmentation... This might take a while");

run("Marker-controlled Watershed", "input=MedianImg marker=Seg mask=LocalThr calculate use");

// Duplicate image
run("Duplicate...","duplicate");


print("-- Computing binary segmentation");

// Make binary mask
run("Make Binary", "method=Percentile background=Default calculate black");

// save log file 
outlog = "log.txt";

f = File.open(outlog); 
content=getInfo("log");
print(f,content);
File.close(f); 