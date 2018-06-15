#!/usr/bin/env python3

STEPS = ["setup", "solvation", "minimization",
         "equilibration", "production"]

import json
import os, sys, getopt

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
        # self.minimization = params["minimization"]
        # self.equilibration = params["equilibration"]
        # self.production = params["production"]

        print("Configuration loaded!")


    # Invokes the gromacs command appropriate for the step
    def gmx_cmd(self, step):

        _p = self.params[step]

        print("Performing %s..." % type)

        # Invoke grompp
        os.system("grompp \
        -f {0} -c {1} -p {2} -o {3}".format(
        _p["parameters"], _p["coordinates"], _p["topology"], _p["output"]))

        # Invoke mdrun
        os.system("mdrun -v -deffnm %s" % _p["mdrun_name"])

        print("%s complete!" % step)


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
      opts, args = getopt.getopt(argv,"mepa")
   except getopt.GetoptError:
      print 'Usage: gross.py -m -e -p -a'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'Usage: gross.py [-m] [-e] [-p] [-a]\n'+
         '-m: Run minimization step\n' +
         '-e: Run equilibration step\n' +
         '-p: Run production MD run step\n' +
         '-a: Run all steps\n' +
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
