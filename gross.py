#!/usr/bin/env python3
#TODO: Add a wrapper for insane.py
#TODO: Could build the slurm file automatically

STEPS = ["setup", "solvation", "minimization",
         "equilibration", "production"]

import json
import os, sys, getopt
import subprocess

CONFIG = "gross_config.json"

class gromacs_executor:

    minimization = dict()
    equilibration = dict()
    production = dict()

    def __init__(self, filename):

        self.load_json(filename)

        print("Running in %s..." % self.cwd)
        os.chdir(self.cwd)

    def load_json(self, filename):

        print("Loading configuration file from %s... " % filename, end="")

        try:
            params = json.load(open(filename))
        except FileNotFoundError:
            print("Configuration file not found!")
            exit(-1)

        self.cwd = params["working directory"]
        self.params = params

        try:
            self.remote = params["remote"]
            self.remote_dir = params["remote_dir"]

            # Ensure remote directory path is formatted properly
            if not self.remote_dir[-1] == '/':
                self.remote_dir += '/'

        except KeyError:
            print("Not configured for cluster!")

        print("Configuration loaded!")


    # Invokes the gromacs command appropriate for the step
    def gmx_cmd(self, step, cluster=False, dry=False):

        # Load the appropriate set of parameters from the imported JSON
        _p = self.params[step]

        print("\nPerforming %s..." % step)


        # Invoke grompp. Set check=True so an exception is raised if
        #   it's unsuccessful
        grompp_cmd = "grompp -f {params} -c {coords} -p {topol} -o {out}".format(
        params = _p["parameters"],
        coords = _p["coordinates"],
        topol  = _p["topology"],
        out    = _p["output"]
        )

        if dry:
            print(grompp_cmd)
        else:
            subprocess.run(grompp_cmd.split(), check=True)

        # Handle doing mdrun on the cluster
        if cluster:

            try:
                self.remote
            except NameError:
                print("Remote was not specified! Check %s and ensure \
                that remote and remote_dir are defined. " % CONFIG)

            rsync_cmd = \
            "rsync {params} {coords} {topol} {out} {slurm} {remote}:{remote_dir}".format(
            params = _p["parameters"],
            coords = _p["coordinates"],
            topol  = _p["topology"],
            out    = _p["output"],
            slurm  = _p["slurm"],
            remote = self.remote,
            remote_dir = self.remote_dir)

            sbatch_cmd = "ssh greene sbatch {remote_dir}{slurm}".format(
            remote_dir = self.remote_dir,
            slurm      = _p["slurm"])

            if dry:
                print(rsync_cmd)
                print(sbatch_cmd)

            else:
                # Sync over necessary files to run
                subprocess.run(rsync_cmd.split(), check=True)

                # Execute remote job
                subprocess.run(sbatch_cmd.split(), check=True)

        # Invoke mdrun locally otherwise
        elif not cluster:

            mdrun_cmd = "mdrun -v -deffnm {mdrun_name}".format(
            mdrun_name = _p["mdrun_name"])

            if dry:
                print(mdrun_cmd)
            else:
                subprocess.run(mdrun_cmd.split(), check=True)

        # Use title to capitalize the first letter, so it's pretty.
        print("%s complete!" % step.title())


    # Convenient callers for each step
    def minimize(self, dry=False):
        self.gmx_cmd("minimization", dry=dry)
    def equilibrate(self, dry=False):
        self.gmx_cmd("equilibration", dry=dry)
    def production(self, cluster=False, dry=False):
        self.gmx_cmd("production", cluster=cluster, dry=dry)



if __name__ == "__main__":

    minimize = False
    equilibrate = False
    production = False
    cluster = False
    dry_run = False

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hmepacd")
    except getopt.GetoptError:
        print('Usage: gross.py [-m] [-e] [-p] [-a] [-c] [-d]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: gross.py [-m] [-e] [-p] [-a] [-c] [-d]\n'+
            '\t -m: Run minimization step\n' +
            '\t -e: Run equilibration step\n' +
            '\t -p: Run production MD run step\n' +
            '\t -a: Run all steps\n' +
            '\t -c: Run production step on cluster\n' +
            '\t -d: Dry run. Show commands, but do not execute')
            sys.exit()
        elif opt == "-m":
            minimize = True
        elif opt == "-e":
            equilibrate = True
        elif opt == "-p":
            production = True
        elif opt == "-a":
            minimize, equilibrate, production = True, True, True
        elif opt == "-c":
            cluster = True
        elif opt == "-d":
            dry_run = True

    gmx = gromacs_executor(CONFIG)

    if minimize:
        gmx.minimize(dry=dry_run)
    if equilibrate:
        gmx.equilibrate(dry=dry_run)
    if production:
        gmx.production(cluster=cluster, dry=dry_run)
