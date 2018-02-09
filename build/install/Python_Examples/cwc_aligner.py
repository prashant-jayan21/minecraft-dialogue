import re

def get_architect_screenshot(builder_screenshot, aligned_pairs):
    for pair in aligned_pairs:
        if pair[1] == builder_screenshot:
            return pair[0]
    return None

def align(all_screenshot_filenames):
    grouping = {} # map from action (e.g. pickup, chat, etc.) to all screenshots corresponding to that action
    for filename in all_screenshot_filenames:
        key = get_key(filename)[1] # action for the screenshot
        if key not in grouping:
            grouping[key] = []
        grouping[key].append(filename)

    aligned_pairs = get_aligned_pairs(grouping)

    all_aligned_filenames = [item for pair in aligned_pairs for item in pair]
    all_unaligned_filenames = set(all_screenshot_filenames) - set(all_aligned_filenames)
    print "UNALIGNED SCREENSHOTS: " + str(all_unaligned_filenames) + "\n"

    return aligned_pairs

def get_aligned_pairs(grouping):
    aligned_pairs = [] # list of all aligned pairs of screenshots

    for action, all_filenames_for_action in grouping.iteritems():
        # split into builder and architect screenshots
        architect_filenames = filter(lambda x: "Architect" in x, all_filenames_for_action)
        builder_filenames = filter(lambda x: "Builder" in x, all_filenames_for_action)
        # create a weighted complete bipartite graph
        # nodes in first set are architect screenshots and in second are builder ones
        # each weight is the time lag between screenshots
        graph = []
        for a in architect_filenames:
            for b in builder_filenames:
                weight = get_weight(a, b)
                graph.append((a, b, weight))
        # process graph to find closest pairs of screenshots
        while graph:
            # select edge with min weight
            a_min, b_min, w_min = min(graph, key = lambda x: x[2])
            aligned_pairs.append((a_min, b_min))
            # delete all edges with these as nodes
            graph = filter(lambda x: x[0] != a_min and x[1] != b_min, graph)

    return aligned_pairs

def get_weight(architect_filename, builder_filename):
    # get time lag between screenshots
    architect_timestamp, architect_action = get_key(architect_filename)
    builder_timestamp, builder_action = get_key(builder_filename)
    return abs(float(architect_timestamp) - float(builder_timestamp))

def get_key(filename):
    # get timestamp and action for screenshot
    return (re.split(r"[-.]",filename)[0], re.split(r"[-.]",filename)[2])

def temp_test():
    import os
    import pprint

    screenshots_dir = "/Users/prashant/Desktop/B1-A2-blue-original-L-1517603132657"
    all_filenames = filter(lambda x: x.endswith(".png"), os.listdir(screenshots_dir))

    results = align(all_filenames)
    pprint.PrettyPrinter().pprint(results)

temp_test()
