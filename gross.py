#!/usr/bin/env python3
#TODO: Add a wrapper for insane.py
#TODO: Could build the slurm file automatically

STEPS = ["setup", "solvation", "minimization",
         "equilibration", "production"]

import json
import os, sys, getopt
import subprocess, signal

CONFIG = "gross_config.json"

class gromacs_executor:

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



        # Handle doing mdrun on the cluster
        if cluster and step=="production":

            try:
                self.remote
            except NameError:
                print("Remote was not specified! Check %s and ensure \
                that remote and remote_dir are defined. " % CONFIG)

            if self.params["remote_grompp"] == "True":
                # Do the prep step remotely too, to avoid version mismatches
                grompp_cmd = 'ssh -t %s cd %s ; ~/bin/gmx_srd ' % (self.remote, self.remote_dir) + grompp_cmd


            # If an index file has been provided, use it.
            if ".ndx" in _p["other"]:
                # Get the index file from the parameters
                grompp_cmd += " -n %s" % [x for x in _p["other"].split() if ".ndx" in x][0]

            if self.params["remote_grompp"] == "False":
                subprocess.run(grompp_cmd.split(), check=True)

            scheduler = ""
            if "slurm" in _p.keys():
                scheduler = "sbatch"
                batchfile = _p["slurm"]
            elif "grid" in _p.keys():
                scheduler = "qsub"
                batchfile = _p["grid"]
            else:
                raise "No valid scheduler"

            rsync_cmd = \
            "rsync -r {params} {coords} {topol} {out} {other} {batchfile} \
            {remote}:{remote_dir}".format(
            params = _p["parameters"],
            coords = _p["coordinates"],
            topol  = _p["topology"],
            out    = _p["output"],
            other  = _p["other"],
            batchfile  = batchfile,
            remote = self.remote,
            remote_dir = self.remote_dir)

            scheduler_cmd = "ssh {remote} {scheduler} {remote_dir}{batchfile}".format(
            remote = self.remote,
            remote_dir = self.remote_dir,
            scheduler  = scheduler,
            batchfile  = batchfile)

            if dry:
                print(rsync_cmd)

                print(grompp_cmd)

                print(scheduler_cmd)

            else:
                # Sync over necessary files to run
                subprocess.run(rsync_cmd.split(), check=True)


                if self.params["remote_grompp"] == "True":
                    # Prep step on the remote
                    subprocess.run(grompp_cmd.split(), check=True)

                # Execute remote job
                subprocess.run(scheduler_cmd.split(), check=True)

        # Invoke mdrun locally otherwise
        elif not cluster:

            if dry:
                print(grompp_cmd)
            else:
                subprocess.run(grompp_cmd.split(), check=True)

            mdrun_cmd = "mdrun -v -deffnm {mdrun_name}".format(
            mdrun_name = _p["mdrun_name"])

            if dry:
                print(mdrun_cmd)
            else:

                # Use Popen here instead of run so that it's nonblocking and we
                #   can handle errors -- specifically, KeyboardInterrupt.
                # I think Gromacs does some nontrivial cleanup when it receives
                #   a SIGINT that finishes the run nicely and wraps up all the
                #   output files.
                # Keeping this behavior is desirable so we can cancel runs, but
                #   keep usable data from them.
                #
                # The subprocess module already provides a simplified, nonblocking
                #   command in subprocess.run().
                # However, because it's nonblocking, if the called process fails
                #   to complete, a line like
                #   process = subprocess.run(args)
                #   will not actually complete the assignment.
                # Thus, even though you'll be able to catch exceptions, you won't
                #   be able to reference the 'process' object in them, because it
                #   was never actually assigned.
                # If you can't access the process object, then you can't pass
                #   SIGINT to it, and so we must use Popen to handle gracefully
                #   passing SIGINT (Control+C for the uninformed) to Gromacs.
                try:
                    mdrun_process = subprocess.Popen(mdrun_cmd.split())
                    mdrun_process.communicate()

                # Handle mdrun itself crashing
                except subprocess.CalledProcessError as e:

                    print(e) #TODO: This probably isn't right.
                    print("**** mdrun failed locally ****")

                    return

                # Pass Control+C gracefully to gromacs
                except KeyboardInterrupt:

                    print("\nKeyboard interrupt received, passing SIGINT to mdrun.")
                    mdrun_process.send_signal(signal.SIGINT)
                    mdrun_process.communicate()

                    print("Mdrun successfully aborted.")

                    return

                # Handle other exceptions... Shouldn't ever get here.
                except Exception as e:
                    print("Unhandled exception! %s")

        # Use title to capitalize the first letter, so it's pretty.
        print("\n%s complete!" % step.title())


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
