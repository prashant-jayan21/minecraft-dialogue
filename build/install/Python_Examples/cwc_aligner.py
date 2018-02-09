import re

def get_architect_screenshot(builder_screenshot, aligned_pairs):
    for pair in aligned_pairs:
        if pair[1] == builder_screenshot:
            return pair[0]
    return None

def align_fixed(architect_filenames, builder_filenames):
    all_filenames = architect_filenames + builder_filenames

    grouping = {}
    for filename in all_filenames:
        key = get_key(filename)[1]
        if key not in grouping:
            grouping[key] = []
        grouping[key].append(filename)

    aligned_pairs = get_pairs(grouping)

    all_aligned_filenames = [item for pair in aligned_pairs for item in pair]
    all_unaligned_filenames = set(all_filenames) - set(all_aligned_filenames)
    print "UNALIGNED SCREENSHOTS: " + str(all_unaligned_filenames)

    return aligned_pairs

def get_pairs(grouping):
    aligned_pairs = []

    for action, all_filenames_for_action in grouping.iteritems():
        # split into builder and architect screenshots
        architect_filenames = filter(lambda x: "Architect" in x, all_filenames_for_action)
        builder_filenames = filter(lambda x: "Builder" in x, all_filenames_for_action)
        # create graph
        graph = []
        for a in architect_filenames:
            for b in builder_filenames:
                weight = get_weight(a, b)
                graph.append((a, b, weight))
        # process graph
        while graph:
            # select edge with min weight
            a_min, b_min, w_min = min(graph, key = lambda x: x[2])
            aligned_pairs.append((a_min, b_min))
            # deletions
            graph = filter(lambda x: x[0] != a_min and x[1] != b_min, graph)

    return aligned_pairs

def get_weight(architect_filename, builder_filename):
    architect_timestamp, architect_action = get_key(architect_filename)
    builder_timestamp, builder_action = get_key(builder_filename)
    return abs(float(architect_timestamp) - float(builder_timestamp))

def get_key(filename):
    return (re.split(r"[-.]",filename)[0], re.split(r"[-.]",filename)[2])

import os
import pprint

architect_dir = "/Users/prashant/Desktop/B1-A2-blue-original-L-1517603132657_a"
builder_dir = "/Users/prashant/Desktop/B1-A2-blue-original-L-1517603132657_b"

architect_filenames = filter(lambda x: x.endswith(".png"), os.listdir(architect_dir))
builder_filenames = filter(lambda x: x.endswith(".png"), os.listdir(builder_dir))

results = align_fixed(architect_filenames, builder_filenames)

pp = pprint.PrettyPrinter()
pp.pprint(results)
print(len(results))
