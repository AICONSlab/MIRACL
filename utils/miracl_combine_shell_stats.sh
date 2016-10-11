#!/bin/bash

grp=$1
id=$2

projectdir=/data/clarity_project/mouse/stroke_study

datadir=$projectdir/${grp}
subjdir=$datadir/${id}

statdir=$subjdir/stats

comb=$statdir/${id}_comb_shells_stats.csv

pushd $statdir

sed '7,12d' ${id}_stroke_shells_feats.csv > feat.tmp

awk '{print $6}' ${id}_inv_FA_stroke_shells.csv > count.tmp

sed s/Count/LblVol/g count.tmp > count2.tmp

for met in FA MD T1 T2 CT; do

	if [[ "$met" == "CT" ]]; then
		
		awk '{print $2}' ${id}_exv_${met}_stroke_shells.csv > ${met}.tmp

	else

		awk '{print $2}' ${id}_inv_${met}_stroke_shells.csv > ${met}.tmp

	fi

	sed s/Mean/${met}/g ${met}.tmp > ${met}2.tmp

done

paste feat.tmp FA2.tmp MD2.tmp T12.tmp T22.tmp CT2.tmp count2.tmp > test.tmp

awk '{$15="";print}' test.tmp > test2.tmp

sed 's/ /,/g' test2.tmp > $comb

rm *.tmp

popd