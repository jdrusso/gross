# Getting Started with GROMACS


## Running a Simulation

### Basic steps

The general workflow of an MD simulation looks something like:

1. **Set up your system**, i.e. generate the starting topology
1. **Run an energy minimization.**
This *can* help resolve some slightly funky starting configurations -- emphasis on *can*. A really bad starting configuration can still cause you major headaches, and simply not minimize well. This is often just done with a gradient descent on the potential energy and forces of the system. Move a particle a bit, see if it lowered energy, repeat type deal.
1. **Equilibrate the system.** This can be done in either NPT, which should stabilize the temperature (and may modify the box size), NVT, which stabilizes the pressure, or both.
1. **Production MD.** This is the step where you're running what is hopefully now a physical, equilibrated system, and generating your data.

Details on how you do the steps may vary depending on what exactly you're doing, but that's the general overview.


### Tutorials

I suggest running through the following tutorials to get your bearings (in this order):

1. http://www.mdtutorials.com/gmx/lysozyme/index.html
This is a good tutorial on simulating a single protein in a box of water. Pretty simple starting setup, and they do a great job of explaining what's going on in the steps. The forcefield this uses is not what we use, but that is a detail which can be swapped out. This website's tutorials are "updated for GROMACS 2018", but if I recall they should all be backwards compatible with GROMACS 5 without any issues.

1. http://www.mdtutorials.com/gmx/membrane_protein/index.html
This one gets a little spicier by having you simulating a membrane with a protein inside it.

1. http://cgmartini.nl/index.php/tutorials-general-introduction-gmx5/bilayers-gmx5#Bilayer-self-assembly The bilayer self-assembly part is pretty cool and more or less painless. This will have you do a sort of similar process, but now using the forcefield we actually use. It's also super cool to watch the movie of the bilayer assembling itself from a bunch of lipids floating around. I recommend that at the part where they have you use `gmx view`, download, install, and figure out how to use VMD to visualize that instead of using `gmx view`. VMD is a common tool for visualizing these trajectories which we (and others) use a lot.

1. http://cgmartini.nl/index.php/tutorials-general-introduction-gmx5/proteins-gmx5#membrane-protein The previous tutorials have you set up the system sort of "the hard way" using `genbox` and `solvate`.
In practice, you can usually skip a lot of that by using a script from the Martini people called `insane.py` which builds a bilayer system for you (bonus points awarded when you get the joke in the name).
When you run `insane.py` you pass it the size of the system you want, the type of lipids you want it to be made out of, the boundary conditions, and the files to write to. This is basically the Martini version of the second tutorial.

### Martini

Martini is a coarse-grained (represents groups of certain numbers of atoms as a single super-atom for computational efficiency) forcefield (parameterizes interaction strengths between different types of particles).

Simulating a ton of water in a box is pretty expensive though, and isn't the part of the system you're interested in, but you need it to reproduce accurate physics. There's another variation on Martini called Dry Martini, which parameterizes these interactions slightly differently to try and avoid needing to simulate all the water.

To run a simulation with Dry Martini, you need to use some different parameters when setting up the simulation.

### SRD

SRD was something Andrew developed (group member that just graduated you may have met a couple times) to reproduce hydrodynamics more accurately than Dry Martini in a more efficient way than explicitly simulating all the water.
Refer to his thesis for more detail on the algorithm, implementation, etc -- you can ask me about it, but I won't retype it all here.

The related code is available at https://github.com/EnergyLandscape/strd-gromacs and he also has a very helpful user guide at https://github.com/EnergyLandscape/strd-gromacs/blob/master/STRD%20User%20Guide.pdf

I

## Types of files

All of these filetypes have amazing, well-written and very informative pages in the GROMACS user guide. This is in no way shape or form meant to be an exhaustive list, just a quick rundown on some of the popular ones.

Things you'll have to care about off the bat:
- `.top` - Topology files, just enumerates all the types of residues and how many there are
- `.gro` - Positions of all the residues at one slice in time
- `.xtc` - A compressed format for storing trajectories
- `.tpr` - A file that contains everything you need to start a step of the simulation (the result of running `grompp`, `mdrun` requires this)

Things you may not have to deal with immediately:
- `.trr` - Uncompressed trajectory. Usually don't have to use these, they can be big boys
- `.edr` - This is analogous to a `.trr`, but for energies instead of positions
- `.cpt` - Checkpoint file, GROMACS writes these occasionally so you can restart a simulation if it dies
- `.log` - One guess to what's in this


## GROMACS User Guide

The GROMACS 5.1 user guide is available at http://manual.gromacs.org/5.1-current/index.html and has a lot of awesome, super helpful sections.

There are technical pages that give really detailed explanations of some of the algorithms themselves, along with more manpage style pages that describe details of various functions.


### My Scripts

All the custom scripts I've made live in https://github.com/jdrusso/gross

There are a few things you might find useful in here.

`gross.py` is just a streamlined way of doing minimization, equilibration, production. There's one master configuration file `gross_config.json` that should live in the folder where all your relevant GROMACS config files are.

Running `gross.py` with `-m`, `-e`, and/or `-p` will run the minimization, equilibration, and/or production steps respectively, using the files that are labeled for each in `gross_config.json`. You can even do `gross.py -mep` to do all of them. This just cuts out having to re-enter `grompp` and `mdrun` for each step with all the specific filenames -- just enter them once in the `json` file.

`gross_config.json` also has a field for a remote machine and directory, and a build script for `slurm`, a piece of software that schedules running jobs on a cluster. You can use this and the `-c` flag to `gross.py` to run code on, for example, greene. It'll run the production and equilibration steps locally, then on the remote machine generate the `tpr` file and run it.

`pinsane.py` is a modified version of `insane.py` that allows you to add multiple proteins in the membrane. `insane.py` does some weird stuff when you try to insert multiple proteins and chokes. You run it identically to `insane.py`, but if you want to insert proteins you add the flag `-nf [.gro file for protein]:[name of protein]:[number to insert]`. Number to insert can be 0, and it won't insert any.

`stir.py` does pretty much the same thing as Andrew's `add_srd_uniform.py`. When you generate a simulation for SRD, you want to add a certain density of SRD particles. This script does that for you by modifying the `.gro` file and telling you the line you need to add to the `.top` file.

Don't worry too much about `protein_parser.py` for the time being.
