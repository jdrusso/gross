<<<<<<< HEAD
#!/usr/bin/env python3

=======
>>>>>>> 087e4249be7438c5feac514c1095d478ac29ae78
import getopt, sys
import re

non_protein = ["SOL", "POPC"]

# Find the numbers of chains of length X
# def build_index(chain_length):


if __name__ == "__main__":

    output = ''
<<<<<<< HEAD
    _input = ''
=======
    input = ''
>>>>>>> 087e4249be7438c5feac514c1095d478ac29ae78

    try:
        opts, args = getopt.getopt(sys.argv[1:],"i:o:")
    except getopt.GetoptError:
<<<<<<< HEAD
        print('Usage: protein_parser.py -i <input file> -o <output file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-i':
            _input = arg
=======
        print('Usage: stir.py -i <input file> -o <output file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-i':
            input = arg
>>>>>>> 087e4249be7438c5feac514c1095d478ac29ae78
        if opt == '-o':
            output = arg

    # print("Parsing file %s" % input)

<<<<<<< HEAD
    data = open(_input).readlines()[2:]
=======
    data = open(input).readlines()[2:]
>>>>>>> 087e4249be7438c5feac514c1095d478ac29ae78

    trimers = []
    monomers = []

    chain_start = -1
    chain_end = -1
    first = True
    for line in data:

        # Strip empty bits
        line = [word for word in line.split(" ") if not word == ""]

        # Skip the final line
        if len(line) == 3:
            continue

        # Strip numbers
<<<<<<< HEAD
        _type = re.sub('[0-9]+', '', line[0])


        # Check if it's any of the non-proteins
        if _type in non_protein:

            resID = int(re.sub('[A-Z]+', '', line[0]))
            chargeID = int(line[2])

            chain_end = chargeID-1
            chain_length = chain_end-chain_start
            # print("Current chain went from %d to %d. (%d)" \
            #     % (chain_start, chain_end, chain_length))

            if chain_length == 110:
                trimers.append(list(range(chain_start, chain_end+1)))
            elif chain_length == 36:
                monomers.append(list(range(chain_start, chain_end+1)))

            break

        else:
            resID = int(re.sub('[A-Z]+', '', line[0]))
            chargeID = int(line[2])
=======
        type = re.sub('[0-9]+', '', line[0])


        # Check if it's any of the non-proteins
        if type in non_protein:
            continue

        resID = int(re.sub('[A-Z]+', '', line[0]))
        chargeID = int(line[2])
>>>>>>> 087e4249be7438c5feac514c1095d478ac29ae78

        # print("{0} | {1}".format(resID, chargeID))

        # This means we're at the beginning of a new chain
<<<<<<< HEAD
        if resID == 1 or resID >= 64:

            if first and _type not in non_protein:
=======
        if resID == 1:

            if first:
>>>>>>> 087e4249be7438c5feac514c1095d478ac29ae78
                chain_start = 1
                first = False

            else:
                chain_end = chargeID-1
                chain_length = chain_end-chain_start
                # print("Current chain went from %d to %d. (%d)" \
                #     % (chain_start, chain_end, chain_length))

                if chain_length == 110:
                    trimers.append(list(range(chain_start,chain_end+1)))
                elif chain_length == 36:
                    monomers.append(list(range(chain_start,chain_end+1)))

                chain_start = chargeID

<<<<<<< HEAD

    # Flatten lists
    monomers = [str(item) for sublist in monomers for item in sublist]
    trimers = [str(item) for sublist in trimers for item in sublist]

    monomer_entry = "[ kalp21m ]\n" + ' '.join(monomers)
    print(monomer_entry)
    # print(len(monomers))

    trimer_entry = "[ kalp21t ]\n" + ' '.join(trimers)
    print(trimer_entry)
    # print(trimers)
    # print(len(trimers))
=======
        # chain_end += 1
        # Find how many

    # Flatten lists
    monomers = [str(item) for sublist in monomers for item in sublist]
    trimers = [item for sublist in trimers for item in sublist]

    monomer_entry = "[ kalp21m ]\n" + ' '.join(monomers)
    print(monomer_entry)
>>>>>>> 087e4249be7438c5feac514c1095d478ac29ae78
    # print(trimers)
    # print(monomers)
