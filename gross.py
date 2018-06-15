#!/usr/bin/env python3
#TODO: Add a wrapper for insane.py

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

        print("Configuration loaded!")


    # Invokes the gromacs command appropriate for the step
    def gmx_cmd(self, step):

        # Load the appropriate set of parameters from the imported JSON
        _p = self.params[step]

        print("Performing %s..." % type)

        # Invoke grompp. Set check=True so an exception is raised if it's unsuccessful
        subprocess.run(["grompp",
            "-f", _p["parameters"],
            "-c", _p["coordinates"],
            "-p", _p["topology"],
            "-o", _p["output"]
            ], check=True)

        # Invoke mdrun
        subprocess.run(["mdrun", "-v", "-deffnm", _p["mdrun_name"]], check=True)

        # Use title to capitalize the first letter, so it's pretty.
        print("%s complete!" % step.title())


    # Convenient callers for each step
    def minimize(self):
        self.gmx_cmd("minimization")
    def equilibrate(self):
        self.gmx_cmd("equilibration")
    def production(self):
        self.gmx_cmd("production")



if __name__ == "__main__":

    minimize = False
    equilibrate = False
    production = False

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hmepa")
    except getopt.GetoptError:
        print('Usage: gross.py -m -e -p -a')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: gross.py [-m] [-e] [-p] [-a]\n'+
            '\t -m: Run minimization step\n' +
            '\t -e: Run equilibration step\n' +
            '\t -p: Run production MD run step\n' +
            '\t -a: Run all steps')
            sys.exit()
        elif opt == "-m":
            minimize = True
        elif opt == "-e":
            equilibrate = True
        elif opt == "-p":
            production = True
        elif opt == "-a":
            minimize, equilibrate, production = True, True, True

    gmx = gromacs_executor(CONFIG)

    if minimize:
        gmx.minimize()
    if equilibrate:
        gmx.equilibrate()
    if production:
        gmx.production()
