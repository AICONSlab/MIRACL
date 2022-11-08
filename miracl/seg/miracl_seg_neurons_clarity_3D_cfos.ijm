// CLARITY 3D nuclei segmentation (cFos)
//
// Macro for Fiji/ImageJ
// Segments cFos positive nuclei in cleared mouse brain in 3D using CLARITY/iDISCO+ and immunolabelling
//
// (c) Maged Goubran, maged.goubran@utoronto.ca, 2022
// 	   Newton Cho, newton.cho@epfl.ch,
// 	   Jordan Squair, jordansquair@gmail.com
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

print("Files path is: " + path);

segpath = path + "/../segmentation_cfos/";

if (File.exists(segpath + "seg_bin_cfos.tif")) {
  print("Segmentation already complete!");
  run("Quit");
}

// Init Parameters:-

// num of CPUS
ncpus = 20;

// radius (px) for nuclei detection
radpx = 1;
radpz = 1;

// max object size
minobjsz = 20;
maxobjsz = 300;

// convert to 8-bit
convert = 1;

// -----------------------------------

// Get files list
list = getFileList(path);
num = list.length;
print("Sequence contains " +num+ " images in total");

// Open stack
print("--Reading stack");

outback = segpath + "norm.tif";

if (!File.exists(outback)) {

  if (convert==1) {

  	// Do not scale when converting to 8-bit
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

} else {

	print("Background subtracted already computed .. skipping & opening it ");

	open(outback);

}

// -----------------------------------

// Subtract Background

outback = segpath + "norm.tif";

// Collect Garbage
call("java.lang.System.gc");

if (!File.exists(outback)) {

	// Duplicate image
	run("Duplicate...","duplicate");

	// Remove background; rolling ball algorithm for uneven illumination; sliding paraboloid
	// Radius should be set to at least the size of the largest object that is not part of the background

	print("-- Subtracting Background");
	run("Subtract Background...", "rolling=5 sliding stack");

	// Save 
	save(outback);

  // Close original stack image
  selectImage(orgstack);
  close();

} else {

	print("Background-less image already computed .. skipping & opening it ");

	open(outback);

  // Close original stack image
  selectImage(orgstack);
  close();

}

backstack = getImageID();
backtitle = getTitle();

rename("BacklessStack");

// -----------------------------------

// Enhance Contrast

outenhance = segpath + "backremov_enhance.tif";

if (!File.exists(outenhance)) {

	// Duplicate image
	run("Duplicate...","duplicate");

	// Enhance contrast; 
	print("-- Enhancing contrast & normalizing Histogram");
	run("Enhance Contrast...", "saturated=0.5 process_all");

	// Save 
	save(outenhance);

} else {

	print("Enhancing contrast already performed .. skipping & openning it ");

	open(outenhance);

}

enhancestack = getImageID();
enhancetitle = getTitle();

rename("EnhanceStack");

// -----------------------------------

// Compute Median Filter

call("java.lang.System.gc");

outmed = segpath + "backremov_enhance_median.tif";

if (!File.exists(outmed)) {

	print("-- Computing Median image");
	print("using " +ncpus+ " CPUs for parallelization");

	// Create median image
	run("3D Fast Filters","filter=Median radius_x_pix="+radpx+" radius_y_pix="+radpx+" radius_z_pix="+radpz+" Nb_cpus="+ncpus+"");

	// Save median image
	save(outmed);

} else {

	print("Median filtering already computed .. skipping & opening it ");

	open(outmed);

}

medstack = getImageID();
medtitle = getTitle();

rename("MedianImg");

// close Back-less image
selectImage(backstack);
close();

// close Enhance image
selectImage(enhancestack);
close();

// Collect Garbage
call("java.lang.System.gc");

// -----------------------------------

// Compute Yen threshold

outyen = segpath + "median_yen.tif";

if (!File.exists(outyen)) {

	// Duplicate image
	run("Duplicate...","duplicate");

	print("-- Computing Yen Threshold");

	//Run Auto Threshold to creak mask for Watershed
  	run("Auto Threshold", "method=Yen ignore_black white stack");

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

// Compute Gradient

call("java.lang.System.gc");

outgrad = segpath + "median_gradient.tif";

if (!File.exists(outgrad)) {

	print("-- Computing Gradient image");

	selectImage("MedianImg");

	// Create Gradient image
  run("Morphological Filters (3D)", "operation=[Gradient] element=Ball x-radius="+radpx+" y-radius="+radpx+" z-radius="+radpz+"");

	// Save Gradient
	save(outgrad);

} else {

	print("Gradient filtering already computed .. skipping & opening it ");

	open(outgrad);

}

gradstack = getImageID();
gradtitle = getTitle();

rename("Gradient");

// -----------------------------------

// Create markers for Watershed

call("java.lang.System.gc");

outmax = segpath + "median_max.tif";

if (!File.exists(outmax)) {

	print("-- Computing 3D Maxima image");

	selectImage("MedianImg");

	// Find 3D Maxima image to create markers for Watershed
  	run("3D Fast Filters","filter=MaximumLocal radius_x_pix="+radpx+" radius_y_pix="+radpx+" radius_z_pix="+radpz+" Nb_cpus=4");

	// Save 3D Maxima image
	save(outmax);

} else {

	print("3D maxima already found .. skipping & opening it ");

	open(outmax);

}

maxstack = getImageID();
maxtitle = getTitle();

rename("Maxima");

// -----------------------------------

// Compute Otsu threshold

outotsu = segpath + "maxima_otsu.tif";

if (!File.exists(outotsu)) {

	// Duplicate image
	run("Duplicate...","duplicate");
	
	print("-- Computing Otsu Threshold");

	//Run Auto Threshold to creak mask for markers
  	run("Auto Threshold", "method=Otsu ignore_black white stack");

	// Save Default
	save(outotsu);


} else {

	print("Otsu Thresholded Maxima img already exists .. skipping & opening it ");

	open(outotsu);

}


otsustack = getImageID();
otsutitle = getTitle();

rename("Otsu");

// close Maxima image
selectImage(maxstack);
close();

// Collect Garbage
call("java.lang.System.gc");

// -----------------------------------

// Compute Marker-controlled Watershed

outseg = segpath + "seg_cfos.tif";

// Collect Garbage
call("java.lang.System.gc");

if (!File.exists(outseg)) {

	print("-- Computing Marker-controlled Watershed segmentation... This might take a while");

	// Watershed
	run("Marker-controlled Watershed", "input=Gradient marker=Otsu mask=Yen calculate use");

	// Filter to get rid of objects too small/large to be nuclei
	run("3D Simple Segmentation", "low_threshold=1 min_size="+minobjsz+" max_size="+maxobjsz+"");

	// Duplicate image
	run("Duplicate...","duplicate");

	// Save segmentation
	save(outseg);

  // close bin
  selectImage("Bin");
  close();

	print("-- Computing binary segmentation");

	// Make binary mask
	run("Make Binary", "method=Percentile background=Default calculate black");

	// Save segmentation bin
	save(segpath + "seg_bin_cfos.tif");

} else {

	print ("Segmentation already computed .. skipping")

}

// save log file
outlog = segpath + "seg_cfos_log.txt";

f = File.open(outlog);
content=getInfo("log");
print(f,content);
File.close(f);

// Quit Fiji
run("Quit");
