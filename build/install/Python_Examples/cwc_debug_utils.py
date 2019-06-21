import sys

# Helper method to print a shortened, prettier version of the JSON's contents.
def prettyPrintObservation(observation):
    grouped_elements = "\t"
    for element in observation:
        if element == 'BlocksOutside' or element == 'BlocksInside' or element == 'BuilderGridAbsolute' or element == 'BuilderGridRelative':
            sys.stdout.write("\t"+element+": ")
            print((len(observation[element]), "values"))
        elif element == 'BuilderInventory':
            sys.stdout.write("\t"+element+": ")
            for value in observation[element]:
                print(("\n\t\t", value))
            print()
        elif 'Pos' in element or element == 'Yaw' or element == 'Pitch' or element == 'TimeAlive' or element == 'DistanceTravelled':
            grouped_elements += element+": "+str(observation[element])+"  "
        else:
            sys.stdout.write("\t"+element+": ")
            print((observation[element]))

    if len(grouped_elements.strip()) > 0:
        print(grouped_elements)
    print()

def printObservationElements(observation):
    for element in observation:
        print(element)
    if observation.get("Chat") is not None:
        print(("\nChat:", observation.get("Chat")))
    print()

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

    sys.stdout.write('\t('+str(num_lines)+' values)\n')
