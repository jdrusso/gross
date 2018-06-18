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

***NOTE:*** `remote_dir` MUST HAVE A TRAILING BACKSLASH!
