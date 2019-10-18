#!/bin/bash

# This expects:
#  - A space-separated list of temperatures in a file named 
#	'temps' in the same directory as this script
#  - A .mdp named 'template.mdp' with any references to temperature 
#	replaced with the string 'TEMP' in the same directory as this 
#	script

# This script makes a set of N subdirectories name "equilM" where i
#	N is the total number of temperatures and M is the index of 
#	the temperature.
# It takes the template MDP, replaces the temperatures with the 
#	appropriate values from the 'temps' file, and puts that MDP 
#	in the equilM folder

template='template.mdp'
temps=`cat temps`

let num=0

for i in $temps
do
	mkdir -p equil$num

	# This is just the temperature with anything after the 
	#	decimal truncated. Useful for making better
	#	formatted filenames and such.
	truncated=`echo $i | sed 's/\..*//'`
	cat $template | sed "s/TEMP/$i/g" > equil"$num"/equil.mdp

	let num=$num+1
done
