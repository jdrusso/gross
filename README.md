# GROSS
## GROMACS Simple Startup

This is a somewhat more streamlined way of invoking minimization, equilibration, and production runs in GROMACS.
This is VERY MUCH experimental, and only implements what's quite honestly nearly trivial functionality.

####  `gross.py`

`gross.py` can be invoked with any combination of `-m`, `-e`, `-p` to run just minimization,
equilibration, or production runs respectively. `-a` is equivalent to `-m -e -p`, and `-c` will run
the production step on the remote target.

#### `gross_config.json`
Normally, running GROMACS involves passing a bunch of files on the command line.
I find keeping track of these a little annoying and the resulting GROMACS commands unwieldy, so instead this package
stores them in an easily readable .json file.

`slurm` specifies a build script to use.
`remote` and `remote_dir` specify a remote target for the runs and the directory to put them in.

#### `stir.py`

`stir.py` handles preparing a system for SRD. Invoke it with `stir.py -i <input file> -o <output file>`, where the input/output files should be .gro files. 
It will strip any water beads that may exist, and then randomly place SRD particles to achieve an SRD number density of 2.5 per nm^3 in the box.
The box size is automatically determined from the input file.
When finished, `stir.py` outputs the line that must be added to the topology file to complete adding the SRD particles.
