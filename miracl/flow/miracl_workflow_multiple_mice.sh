#!/bin/bash

# get version
function getversion()
{
	ver=`cat $MIRACL_HOME/version.txt`
	printf "\n MIRACL pipeline v. $ver \n"
}

# help/usage function
function usage()
{
    
    cat <<usage

 	Wrapper for running a MIRACL script on multiple mice 

 	Script has to run in command-line mode


	Usage: `basename $0` -sm [ script module ] -sc [ script ] -id [ input directory ] -opt [options] -nj [ #_of_jobs] -tj [ time_between_batches(min) ]

	Example: `basename $0` -st reg -sc clar_allen_wb -id my_data_dir -opt "-m combined" -nj 3 -tj 10

	arguments (required):

		st. script module / type 
			example: reg or seg or lbls or connect 

		sc. script name 
			example: clar_allen_wb

		id. input directory with multiple mice data

		opt. input options for script to run

		nj. number of mice to run simultaneously - in parallel "||"

		tj. time for computer to "sleep" between parallel jobs


	-----------------------------------
	
	(c) Maged Goubran @ Stanford University, 2017
	mgoubran@stanford.edu
	
	-----------------------------------

usage
getversion >&2
	

}

# Call help/usage function
if [[ $# -lt 2 || "$1" == "-h" || "$1" == "--help" || "$1" == "-help" ]]; then
    
    usage >&2
    exit 1

fi

printf "\n Running in script mode \n"

while getopts ":st:sc:id:opt:nj:tj:" inopt; do

    case "${inopt}" in

        st)
        	stype=${OPTARG}
        	;;

    	sc)
        	script=${OPTARG}
        	;;

    	id)
        	indir=${OPTARG}
        	;;

    	opt)
        	opts="${OPTARG}"
        	;;

        nj)
        	n=${OPTARG}
        	;;

		tj)

        	t=${OPTARG}
        	;;		        	

    	*)
        	usage            	
        	;;

	esac

done   


# get time
START=$(date +%s)

# output log file of script
exec > >(tee -i flow_multiple_mice_script.log)
exec 2>&1

#---------------------------
#---------------------------

ts=$((${t}*60));

# script to run
# run=${MIRACL_HOME}/${stype}/${script}

j=1;

for i in ${indir}/* ; 
do

	j=$(($j+1))

    num=`basename ${i}`
	printf "\n running ${stype} ${script} for ${num} \n"

	miracl ${stype} ${script} "${opts}" -i ${num} &
	
		# wait before running more || jobs 		
		while [[ "$j" -gt "$n" ]]; do			

			printf "\n $n || jobs submitted .. will sleep $t min before running other jobs \n"
			
			sleep ${ts} # secs

			j=$(($j-$n))

		done

done