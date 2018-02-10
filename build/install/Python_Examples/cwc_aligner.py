import re
import os
import json
from os.path import join, isdir, isfile

def postprocess_missions(logs_super_dir, screenshots_super_dir):
    all_log_dirs = filter(lambda x: isdir(join(logs_super_dir, x)), os.listdir(logs_super_dir))

    for log_dir in all_log_dirs:
        if os.path.isfile(join(logs_super_dir, log_dir, "observations_postprocessed.json")):
            continue
        postprocess_observations(join(logs_super_dir, log_dir), join(screenshots_super_dir, log_dir))

def postprocess_observations(logs_dir, screenshots_dir):
    all_filenames = filter(lambda x: x.endswith(".png"), os.listdir(screenshots_dir))
    aligned_pairs = align(all_filenames)

    with open(join(logs_dir, "observations.json")) as observations:
	       observations_dict = json.load(observations)

    observations_dict = add_architect_screenshots(observations_dict, aligned_pairs)

    with open(join(logs_dir, "observations_postprocessed.json"), "w") as observations_processed:
        json.dump(observations_dict, observations_processed)

def add_architect_screenshots(json, aligned_pairs):
    all_states = json["WorldStates"]
    all_states_processed = []

    for state in all_states:
        builder_screenshot = state["ScreenshotPath"]
        architect_screenshot = get_architect_screenshot(builder_screenshot, aligned_pairs)
        if architect_screenshot is not None:
            del state["ScreenshotPath"]
            state["BuilderScreenshotPath"] = builder_screenshot
            state["ArchitectScreenshotPath"] = architect_screenshot
        all_states_processed.append(state)

    json["WorldStates"] = all_states_processed
    return json

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

    # screenshots_dir = "/Users/prashant/Desktop/B1-A2-blue-original-L-1517603132657"
    # all_filenames = filter(lambda x: x.endswith(".png"), os.listdir(screenshots_dir))
    #
    # results = align(all_filenames)
    # pprint.PrettyPrinter().pprint(results)

    # postprocess_observations(
    #     screenshots_dir = "/Users/prashant/Work/cwc-minecraft/Minecraft/run/screenshots/B2-A1-blue-original-L-1518302043792",
    #     logs_dir = "/Users/prashant/Work/cwc-minecraft/build/install/Python_Examples/logs/B2-A1-blue-original-L-1518302043792"
    # )

    postprocess_missions(
        logs_super_dir = "/Users/prashant/Work/cwc-minecraft/build/install/Python_Examples/logs",
        screenshots_super_dir = "/Users/prashant/Work/cwc-minecraft/Minecraft/run/screenshots"
    )

temp_test()
