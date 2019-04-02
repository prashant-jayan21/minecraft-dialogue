from __future__ import print_function
from subprocess import *
from enum import Enum
import json

class Response(object):
    """Response classs.

    Args:
        responseFlag: the Flag names. Currently we are
        using following flags
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
            self.missing = missing.split(",")

        if other is not None:
            self.other = other.split(",")

        if plan is not None:
            instruction_list = list()
            for item in plan.split(","):
                instruction = item.replace("[", "").replace("]", "")
                instruction = instruction.replace(",", "").replace("(", "").replace(")", "")
                action, block_id, x, z = instruction.strip().split()
                instruction = [action, float(x), 1.0, float(z)]
                instruction_list.append(instruction)

            self.plan = instruction_list

        if constraints is not None:
            self.constraints = constraints.split(",")

    def add_missing(self, missing):
        """Add inforamtion about a missing logical form."""
        self.missing.append(missing)

    def add_missing_all(self, missing):
        """Add inforamtion about all missing logical form."""
        self.missing.extend(missing)

    def add_other(self, other):
        """Add inforamtion about others."""
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
    """Convert the planner response to Response classs.

    Args:
        output: output from the planner. The general convention
        reads the last 6 lines.
    Returns:
        the command list for the Malmo agent
    Raises:
        till now nothing

    """
    if len(output) < 5:
        print("convert_response::Error: not enough information from the planner")
        return None

    planner_output = output[-6:]
    print("convert_response::", planner_output)

    for line in planner_output:
        if len(line) == 0:
            continue

        splitted_line = line.strip().split(": ")
        if "[" in splitted_line[1]:
            splitted_line[1] = splitted_line[1].replace("[", "").replace("]", "")
        # print("splitted lines ", splitted_line)
        if "Flag" in splitted_line[0]:
            flag = splitted_line[1]
        elif "Missing" in splitted_line[0]:
            missing = splitted_line[1]
        elif "Other" in splitted_line[0]:
            other = splitted_line[1]
        elif "Plan" in splitted_line[0]:
            plan = splitted_line[1]
        elif "Constraints" in splitted_line[0]:
            constraints = splitted_line[1]

    # print("##parsed outputs##")
    # print(flag, missing, other, plan, constraints)

    response = Response(flag, missing, other, plan, constraints)
    print
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
    """Fetch the plans for a given semantic representation.

    Args:
        human_input: semantic representation format
    Returns:
        the command list for the Malmo agent
    Raises:
        till now nothing

    """
    # print("get plans")
    # args = ["planner/uct_44.jar"]
    args = ["planner/jshop2-master.jar", human_input]
    result = jarWrapper(*args)

    response = convert_response(result)
    print("getPlans::\n"+str(response))
    return response

    # TODO:
    # if "COMPLETED" not in response.responseFlag:
    #     return response

    # instruction_list = list()
    # for item in response.plan:
    #     instruction = item.replace("[", "").replace("]", "")
    #     instruction = instruction.replace(",", "").replace("(", "").replace(")", "")
    #     action, block_id, x, z = instruction.strip().split()
    #     instruction = [action, float(x), 1.0, float(z)]
    #     instruction_list.append(instruction)

    # # print(instruction_list)
    # n_instr = len(instruction_list)

    # command_list = list()
    # x_l = list()
    # y_l = list()
    # z_l = list()
    # for item in instruction_list:
    #     print("item ", item)
    #     action, block_id, x, y = item.strip().split(" ")
    #     x_l.append(int(float(x)))
    #     y_l.append(int(float(y)))
    #     # todo: Rakib when Mayukh is done with the 3D planner.
    #     z_l.append(int(0))

    # command_list = zip(x_l, y_l, z_l)
    # command_list.sort(key=lambda t: t[1], reverse=True) # why?
    # # print(command_list)

    # return (command_list)

if __name__ == '__main__':
    # getPlans(human_input="cube(a) ^ width(a,5)")
    print("*****solving \"row(a) ^ width(a,5)\"*****")
    getPlans(human_input="row(a) ^ width(a,5)")
    print("*****solving missing \"row(a) ^ width(a,5)\"*****")
    getPlans(human_input="row(a)")

    print("*****solving \"rectangle(a) ^ height(a, 2) ^ width(a,4)\"*****")
    getPlans(human_input="rectangle(a) ^ height(a, 2) ^ width(a,4)")
