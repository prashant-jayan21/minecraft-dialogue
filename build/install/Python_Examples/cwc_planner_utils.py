from subprocess import *


def jarWrapper(*args):
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
    print("get plans")
    # args = ["planner/uct_44.jar"]
    args = ["planner/jshop2-master.jar", human_input]
    result = jarWrapper(*args)
    print(result[-2])
    print("planner is providing this result")
    instruction_list = result[-2].replace("[", "").replace("]", "")
    instruction_list = instruction_list.replace(
        ",", "").replace("(", "").replace(")", "")
    instruction_list = instruction_list.split(" ")
    print(instruction_list)
    n_instr = len(instruction_list)

    command_list = list()
    x_l = list()
    y_l = list()
    for i in range(0, n_instr, 4):
        x_l.append(int(float(instruction_list[i + 2])))
        y_l.append(int(float(instruction_list[i + 3])))

    command_list = zip(x_l, y_l)
    command_list.sort(key=lambda t: t[1], reverse=True)
    print(command_list)

    return (command_list)


if __name__ == '__main__':
    # getPlans(human_input="cube(a) ^ width(a,5)")
    getPlans(human_input="row(a) ^ width(a,5)")
    getPlans(human_input="rectangle(a) ^ height(a, 2) ^ width(a,4)")
