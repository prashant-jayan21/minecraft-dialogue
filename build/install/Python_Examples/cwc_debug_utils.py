import sys

# Helper method to print a shortened, prettier version of the JSON's contents.
def prettyPrintWorldState(world_state):
    grouped_elements = "\t"
    for element in world_state:
        if element == 'BlocksOutside' or element == 'BlocksInside' or element == 'BuilderGridAbsolute' or element == 'BuilderGridRelative':
            sys.stdout.write("\t"+element+": ")
            print len(world_state[element]), "values"
        elif element == 'BuilderInventory':
            sys.stdout.write("\t"+element+": ")
            for value in world_state[element]:
                print "\n\t\t", value,
            print
        elif 'Pos' in element or element == 'Yaw' or element == 'Pitch' or element == 'TimeAlive' or element == 'DistanceTravelled':
            grouped_elements += element+": "+str(world_state[element])+"  "
        else:
            sys.stdout.write("\t"+element+": ")
            print world_state[element]

    if len(grouped_elements) > 0:
        print grouped_elements
    print

def prettyPrintObservation(observation):
    for element in observation:
        print element,
    print

# Helper method to print a shortened, prettier version of the string to be written
def prettyPrintString(string_to_write):
    sys.stdout.write("\n\n")
    begin = True
    num_lines = 0

    for line in string_to_write.split("\n"):
        if line.strip().startswith('Type:'):
            num_lines += 1

        elif '[Blocks Outside]' in line or '---' in line:
            if not begin:
                sys.stdout.write('\t('+str(num_lines)+' values)\n')
            else:
                begin = False

            sys.stdout.write(line+"\n")
            num_lines = 0

        elif len(line.strip()) > 0:
            sys.stdout.write(line+"\n")

    sys.stdout.write('\t('+str(num_lines)+' values)\n\n')