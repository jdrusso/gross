#!/usr/bin/env python3
import getopt
import sys, random
import re

class Parser:

    # Initialize the parser and open the file for IO
    def __init__(self, filename, outfilename, x, y, z):
        self.filename = filename
        self.outfilename = outfilename

        # Save the box size
        # TODO: Get this from the last line
        self.x, self.y, self.z = x, y, z

        try:
            self.file = open(filename, 'r')
        except FileNotFoundError:
            print("%s does not exist!" % filename)
            sys.exit(-1)


        # Store the number of atoms
        for i, line in enumerate(self.file):
            # print(i)
            if i == 1:
                self.num_atoms = int(line)
                break

    # Return the number of non-water molecules
    #   Water molecules will be stripped out
    #   TODO: This is a little bit of a janky way of doing it. Use regex :(
    def get_dry_particle_number(self):

        num_waters = 0

        # Iterate through the lines, counting the number of water
        self.file.seek(0)
        for i, line in enumerate(self.file):
            if 'W' in line:
                num_waters += 1

        print("%d water particles" % num_waters)
        print("Started with %d particles, new file has %d" % (self.num_atoms, self.num_atoms - num_waters))

        # Calculate the number of SRD particles you want for a number density of 2.5

        num_particles = self.num_atoms - num_waters

        return int(num_particles)


    # Get the number of SRD particles to insert
    def get_num_SRD(self, density=2.5):

        volume = self.x*self.y*self.z
        num_srd = volume * density

        return int(num_srd)



    # Write the new file, including new SRD particles and ignoring old particles
    def stir(self):

        num_particles = self.get_dry_particle_number() + self.get_num_SRD()
        print("Adding %d SRD particles" % self.get_num_SRD())

        self.file.seek(0)
        outfile = open(self.outfilename, 'w')

        # Write the header(? not really a header) line
        outfile.write(self.file.readline())

        # Write the particle number
        outfile.write("%d\n" % num_particles)

        # Skip the particle number line
        self.file.readline()

        # Store the highest particle index
        res_id = 0
        atom_id = 0

        # Write all the non-water lines
        for i, line in enumerate(self.file):
            # If it's a water...
            if 'W' in line:
                continue
            # If we've read the last line, it's time to add SRD particles
            if len(re.findall("(\d\.\d)", line)) == 3:
                print("Last line is: %s" % line)
                break

            # If it's a dry particle, just copy it into the output
            outfile.write(line)
            res_id = int(line[0:5])
            atom_id = int(line[15:20])

        # Add the SRD lines
        for i in range(self.get_num_SRD()):
            outfile.write(
    		"%5d%-5s%5s%5d%8.3f%8.3f%8.3f\n" %
            (int(res_id), "SOL", "SRD", int(atom_id),
            random.uniform(0,self.x),
            random.uniform(0,self.y),
            random.uniform(0,self.z)))

            res_id = res_id + 1 if res_id < 99999 else 1
            atom_id = atom_id + 1 if atom_id < 99999 else 1

        # Write the last line with the box size
        outfile.write(("%.5f" % self.x).rjust(10) +
            ("%.5f" % self.y).rjust(10) +
            ("%.5f" % self.z).rjust(10) + '\n')

        outfile.close()

    def close(self):
        self.file.flush()
        self.file.close()



if __name__ == "__main__":

    output = ''
    input = ''

    try:
        opts, args = getopt.getopt(sys.argv[1:],"i:o:")
    except getopt.GetoptError:
        print('Usage: stir.py -i <input file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-i':
            input = arg
        if opt == '-o':
            output = arg

    print("Parsing file %s" % input)

    parser = Parser(input, output, 50, 50, 20)
    parser.stir()

    print("Remember to update the topology file with 'SOL   %d'" % parser.get_num_SRD())
