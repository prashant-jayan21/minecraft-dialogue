from __future__ import print_function
from subprocess import *
from enum import Enum
from cwc_mission_utils import x_min_build, x_max_build, y_min_build, y_max_build, z_min_build, z_max_build

class Response(object):
    """Response classs.

    Args:
        responseFlag: the Flag names. Currently we are using following flags:
        COMPLETED,
        MISSING,
        UNKNOWN,
        SUGGESTION,
        DUPLICATE_IDENTIFIER
    Returns:
        a response class
    Raises:
        till now nothing

    """

    def __init__(self, responseFlag, missing=None, other=None,
                 plan=None, constraints=None):

        self.responseFlag = responseFlag
        self.missing = list()
        self.other = list()
        self.plan = list()
        self.constraints = list()

        if missing is not None:
            missing_list = list()

            for item in missing:
                missing_item = item.replace("(","").replace(")","")
                missing_list.append(missing_item.strip().split())

            self.missing = missing_list

        if other is not None:
            self.other = other

        if plan is not None:
            instruction_list = list()

            for item in plan:
                instruction = item.replace("[", "").replace("]", "")
                instruction = instruction.replace(",", "").replace("(", "").replace(")", "")
                action = "putdown"

                if "stack" in instruction.strip():
                    _, block_id, reference_block_id, x, y, z, color = instruction.strip().split()
                else:
                    action, block_id, x, y, z, color = instruction.strip().split()

                instruction = [action, block_id, float(x)+x_min_build, float(y)+y_min_build, float(z)+z_min_build, color]
                instruction_list.append(instruction)

            self.plan = instruction_list

        if constraints is not None:
            self.constraints = constraints

    def add_missing(self, missing):
        """Add information about a missing logical form."""
        self.missing.append(missing)

    def add_missing_all(self, missing):
        """Add information about all missing logical forms."""
        self.missing.extend(missing)

    def add_other(self, other):
        """Add information about others."""
        self.other.append(other)

    def add_constraints(self, constraints):
        self.constraints.append(constraints)

    def __str__(self):
        return_str = ""
        return_str += "Response flag: "+self.responseFlag+"\n"
        return_str += "Plan: "+str(self.plan)+"\n"
        return_str += "Constraints: "+str(self.constraints)+"\n"
        return_str += "Missing: "+str(self.missing)+"\n"
        return_str += "Other: "+str(self.other)+"\n"
        return return_str

def convert_response(output):
    """ 
    Convert the planner response to Response class.

    Args:
        output: output from the planner. The general convention reads the last 6 lines.
    Returns:
        the command list for the Malmo agent
    Raises:
        till now nothing

    """
    if len(output) < 5:
        print("convert_response::Error: not enough information from the planner")
        return None

    planner_output = output[-6:]
    contents = {"Missing": [], "Other": [], "Plan": [], "Constraints": []}
    print("convert_response::", planner_output)

    for line in planner_output:
        if len(line) == 0:
            continue
        
        splitted_line = line.strip().split(": ")
        if "[" in splitted_line[1]:
            splitted_line[1] = splitted_line[1].replace("[", "").replace("]", "")

        res = splitted_line[1].split(",") if len(splitted_line[1]) > 0 else []
        key = splitted_line[0].strip()

        if "Flag" in key:
            flag = res[0]
        elif key in contents:
            contents[key] = res
        else:
            print("convert_response::Error: unexpected planner output", line)

    # print("##parsed outputs##")
    # print(flag, missing, other, plan, constraints)
    response = Response(flag, contents["Missing"], contents["Other"], contents["Plan"], contents["Constraints"])
    # print(response)
    # print(response.responseFlag)
    # response.add_constraints('hellow')
    # print(response)
    # print("##end of parsed outputs##")
    return response

def jarWrapper(*args):
    """A wrapper fuction that bridges python with Java based planner.

    Args:
        args: the arguments to pass to java program
    Returns:
        return the planner output.
    Raises:


    """
    process = Popen(['java', '-jar'] + list(args), stdout=PIPE, stderr=PIPE)
    
    ret = []
    while process.poll() is None:
        line = str(process.stdout.readline())
        if line != '' and line.endswith('\n'):
            ret.append(line[:-1])
    
    stdout, stderr = process.communicate()
    ret += str(stdout).split('\n')
    
    if stderr != '':
        ret += (str(stderr)).split('\n')
    
    if '' in ret:
        ret.remove('')
    
    return ret

def getPlans(human_input="row(a) ^ width(a,5)"):
    """
    Fetch the plans for a given semantic representation.

    Args:
        human_input: semantic representation format
    Returns:
        the command list for the Malmo agent
    Raises:
        till now nothing

    """
    args = ["jshop2-master.jar", human_input]
    result = jarWrapper(*args)

    response = convert_response(result)
    print("getPlans::response received\n"+str(response))
    return response


if __name__ == '__main__':
    # getPlans(human_input="cube(a) ^ width(a,5)")
    print("*****solving \"row(a) ^ width(a,5)\"*****")
    getPlans(human_input="row(a) ^ width(a,5)")
    print("*****solving missing \"row(a) ^ width(a,5)\"*****")
    getPlans(human_input="row(a)")

    print("*****solving \"rectangle(a) ^ height(a, 2) ^ length(a,4)\"*****")
    getPlans(human_input="rectangle(a) ^ height(a, 2) ^ length(a,4)")

    print("3D Planning problem")
    getPlans(human_input="tower(a)^height(a,4)^square(b)^size(b,2)^right(b,a)"
             + "^ block(c)^location(w1)^block-location(c,w1)^left_end(b,c)^block(d)"
             + " ^location(w2)^block-location(d,w2)^lower_left_near(a,d)^spatial-rel(top,0,w1,w2)")

    print("3D Planning problem missing multiple dimensions")
    getPlans(human_input="tower(a)^square(b)^right(b,a)^ block(c)^location(w1)^block-location(c,w1)^left_end(b,c)^block(d)^location(w2)^block-location(d,w2)^lower_left_near(a,d)^spatial-rel(top,0,w1,w2)")

    getPlans(human_input="tower(a)^height(a,4)^color(a,purple)^square(b)^size(b,2)^color(b,blue)^right(b,a)^block(c)^location(w1)^block-location(c,w1)^left_end(b,c)^block(d)^location(w2)^block-location(d,w2)^lower_left_near(a,d)^spatial-rel(top,0,w1,w2)")
