#!/bin/bash
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# Sets up MIRACL environment 

printf "\n Setting up MIRACL PATH  \n"
printf "\n Appending MIRACL HOME to ~/.bashrc \n" 

miraclpath="$(dirname "$PWD")"


echo "#--- MIRACL HOME ----" >> ~/.bashrc

printf "\nexport MIRACL_HOME=`echo $miraclpath`\n" >> ~/.bashrc

cat <<\EOF >> ~/.bashrc

#--- MIRACL path ----

for i in ${MIRACL_HOME}/* ; do export PATH=${i}:$PATH ; done

#--------------------

#--- MIRACL dependecies ----

#---ANTS---

export ANTSPATH=${MIRACL_HOME}/depends/ants

#---C3D---

export PATH=${MIRACL_HOME}/depends/c3d/bin:$PATH

source ${MIRACL_HOME}/depends/c3d/share/bashcomp.sh

#--------------------

EOF

printf "\n MIRACL HOME: `echo $miraclpath` \n"

printf "\n Exporting variables \n"

exec bash

