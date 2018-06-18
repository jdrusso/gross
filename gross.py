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
        except KeyError:
            print("Not configured for cluster!")

        print("Configuration loaded!")


    # Invokes the gromacs command appropriate for the step
    def gmx_cmd(self, step, cluster=False):

        # Load the appropriate set of parameters from the imported JSON
        _p = self.params[step]

        print("Performing %s..." % step)


        # Invoke grompp. Set check=True so an exception is raised if
        #   it's unsuccessful
        subprocess.run(["grompp",
            "-f", _p["parameters"],
            "-c", _p["coordinates"],
            "-p", _p["topology"],
            "-o", _p["output"]
            ], check=True)

        # Handle doing mdrun on the cluster
        if cluster:

            try:
                self.remote
            except NameError:
                print("Remote was not specified! Check %s and ensure \
                that remote and remote_dir are defined. " % CONFIG)

            # Sync over necessary files to run
            subprocess.run(["rsync",
                _p["parameters"], _p["coordinates"], _p["topology"], _p["output"], _p["slurm"],
                self.remote + ":" + self.remote_dir],
            check=True)

            # Execute remote job
            subprocess.run(["ssh", "greene",
            "sbatch", self.remote_dir + _p["slurm"]], check=True)

        # Invoke mdrun locally otherwise
        elif not cluster:
            subprocess.run(["mdrun", "-v", "-deffnm", _p["mdrun_name"]], check=True)

        # Use title to capitalize the first letter, so it's pretty.
        print("%s complete!" % step.title())


    # Convenient callers for each step
    def minimize(self):
        self.gmx_cmd("minimization")
    def equilibrate(self):
        self.gmx_cmd("equilibration")
    def production(self, cluster=False):
        self.gmx_cmd("production", cluster)



if __name__ == "__main__":

    minimize = False
    equilibrate = False
    production = False
    cluster = False

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hmepac")
    except getopt.GetoptError:
        print('Usage: gross.py [-m] [-e] [-p] [-a] [-c]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: gross.py [-m] [-e] [-p] [-a] [-c]\n'+
            '\t -m: Run minimization step\n' +
            '\t -e: Run equilibration step\n' +
            '\t -p: Run production MD run step\n' +
            '\t -a: Run all steps\n' +
            '\t -c: Run production step on cluster')
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

    gmx = gromacs_executor(CONFIG)

    if minimize:
        gmx.minimize()
    if equilibrate:
        gmx.equilibrate()
    if production:
        gmx.production(cluster)
