
// read seg tif

// read label image

// upsample labels

//rename();

selectWindow("allen_lbls.tif");

getStatistics(area, mean, min, max, std)
labels=max;

// get lbls histogram
getHistogram(values,counts,max,1,max);

// add to same table 
name="Result-morpho"
nameOfStatTab="["+name+"]";
table=nameOfStatTab;

// avg table name
tablename = "clarity_features_allen_labels"; 
newtable ="["+tablename+"]";
run("New... ", "name="+newtable+" type=Table");
print(newtable, "\\Headings:Label\tVolumeAvg\tVolumeStd\tVolumeMax\tVolumeMin\tSurfaceAreaAvg\tSurfaceAreaStd\tSurfaceAreaMax\tSurfaceAreaMin\tSphericityAvg\tSphericityStd.");	

c=0;

// loop over labels
for (l = 1; l <= 100 ; l++) {

	// check if label exists	
   	if (counts[l] > 0) {

		c=c+1;

		lbl = l+1;
   		   	 
	    print("processing label " + lbl);

		selectWindow("allen_lbls.tif");

		// Duplicate image
		run("Duplicate...","duplicate");
	
		// threshold
	    setThreshold(lbl,lbl);
	    run("Convert to Mask", "background=Default black");

		lblmaskstack = getImageID();
		rename("lbl_mask");
		
		// make binary (divide by label value)
		run("Divide...", "value=255 stack");
		
		// mask by label img **
		imageCalculator("Multiply create stack","seg.tif","lbl_mask");
		
		// run particle analysis 3D
		run("Particle Analysis 3D", "volume surface sphericity surface=[Crofton (13 dirs.)] euler=C26");
	
		// Add statistics 
		selectWindow("Result-morpho");
		results = getInfo();
		lines = split(results, "\n");
		headings = lines[0];
		titlesofcolumns = split(headings, ",\t");	
		count = lines.length-1;
		
		//Put the results into an array 
		volArray=newArray(); 
		surfArray=newArray(); 
		sphereArray=newArray();
		
		for(i=0;i<count;i++){ 
		    volArray=Array.concat(volArray,getResult("Volume",i));
		    surfArray=Array.concat(surfArray,getResult("SurfaceArea",i)); 
		    sphereArray=Array.concat(sphereArray,getResult("Sphericity",i));
		}; 
		
		//Get the summary out and into variables; 
		Array.getStatistics(volArray,volmin,volmax,volavg,volstDev); 
		Array.getStatistics(surfArray,surfmin,surfmax,surfavg,surfstDev); 
		Array.getStatistics(sphereArray,spheremin,spheremax,sphereavg,spherestDev); 
				
		print(table,count+1+ "\t"+ "Avg" + "\t" + volavg + "\t" + surfavg + "\t" + sphereavg );
		print(table,count+1+ "\t"+ "Max" + "\t" + volmax + "\t" + surfmax + "\t" + spheremax );
		print(table,count+1+ "\t"+ "Min" + "\t" + volmin + "\t" + surfmin + "\t" + spheremin );
		print(table,count+1+ "\t"+ "Std" + "\t" + volstDev + "\t" + surfstDev + "\t" + spherestDev );
		
		// save results
		//saveAs("Results", "particle_analysis_lbl_"+l+".xls");
	
		// populate avg table 	
		print(newtable,lbl+"\t"+volavg+"\t"+volstDev+"\t"+volmax+"\t"+volmin+"\t"+surfavg+"\t"+surfstDev+"\t"+surfmax+"\t"+surfmin+"\t"+sphereavg+"\t"+spherestDev); 
	
		// close masked img
		maskedstack = getImageID();
		selectImage(maskedstack);
		close();

		// close lbl mask
		selectImage(lblmaskstack);
		close();

   	};	

};

// Save 
selectWindow(tablename);
saveAs("Text", tablename+".xls");
