#!/bin/bash

# This is a (nigh-trivial) script to run grompp on all the equil
#	subdirectories in the script directory

# Expects a starting structure 'em.gro'

equil_dirs=`find -name "equil*" -type d`
start_struct="em.gro"
mdp="equil.mdp"
top="topol.top"
out="equil.tpr"

for dir in $equil_dirs
do 
	prefix=$dir
	gmx grompp -f $prefix/$mdp -c $start_struct \
		   -p $top -o $prefix/$out -r $start_struct
done

