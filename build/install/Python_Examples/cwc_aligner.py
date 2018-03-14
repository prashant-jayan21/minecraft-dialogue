import re, os, json, argparse
from os.path import join, isdir, isfile

def postprocess_missions(logs_root_dir, screenshots_root_dir, overwrite):
    all_log_dirs = filter(lambda x: isdir(join(logs_root_dir, x)), os.listdir(logs_root_dir))

    for log_dir in all_log_dirs:
        if overwrite == False and os.path.isfile(join(logs_root_dir, log_dir, "aligned-observations.json")):
            continue
        if os.path.isdir(join(screenshots_root_dir, log_dir)):
            postprocess_observations(join(logs_root_dir, log_dir), join(screenshots_root_dir, log_dir))

def postprocess_observations(logs_dir, screenshots_dir):
    all_filenames = filter(lambda x: x.endswith(".png"), os.listdir(screenshots_dir))

    with open(join(logs_dir, "postprocessed-observations.json")) as observations:
	       observations_dict = json.load(observations)

    num_fixed_viewers = observations_dict["NumFixedViewers"]
    aligned_tuples = align(all_filenames, num_fixed_viewers)
    observations_dict = add_other_screenshots(observations_dict, aligned_tuples, num_fixed_viewers)

    with open(join(logs_dir, "aligned-observations.json"), "w") as observations_processed:
        json.dump(observations_dict, observations_processed)

def add_other_screenshots(json, aligned_tuples, num_fixed_viewers):
    all_states = json["WorldStates"]
    all_states_processed = []

    for state in all_states:
        builder_screenshot = state["ScreenshotPath"] # FIXME: Test for when this is a None
        other_screenshots = get_other_screenshots(builder_screenshot, aligned_tuples)
        del state["ScreenshotPath"]
        state["Screenshots"] = {}
        state["Screenshots"]["Builder"] = builder_screenshot
        if other_screenshots is not None:
            state["Screenshots"]["Architect"] = other_screenshots[0]
            for i in range(num_fixed_viewers):
                 state["Screenshots"]["FixedViewer" + str(i+1)] = other_screenshots[i+1]

        all_states_processed.append(state)

    json["WorldStates"] = all_states_processed
    return json

def get_other_screenshots(builder_screenshot, aligned_tuples):
    for t in aligned_tuples:
        if t[1] == builder_screenshot:
            return filter(lambda x: x != t[1], t)
    return None

def align(all_screenshot_filenames, num_fixed_viewers):
    grouping = {} # map from action (e.g. pickup, chat, etc.) to all screenshots corresponding to that action
    for filename in all_screenshot_filenames:
        key = get_key(filename)[1] # action for the screenshot
        if key not in grouping:
            grouping[key] = []
        grouping[key].append(filename)

    aligned_pairs_ab = get_aligned_pairs(grouping, "Architect", "Builder")
    aligned_pairs_af = []
    for i in range(num_fixed_viewers):
        fixed_viewer = "FixedViewer" + str(i+1)
        aligned_pairs_af.append(get_aligned_pairs(grouping, "Architect", fixed_viewer))

    all_aligned_pairs = [aligned_pairs_ab] + aligned_pairs_af

    def merge(list_1, list_2):
        merged_tuples = []
        for tuple_1 in list_1:
            key = tuple_1[0]
            try:
                tuple_2 = next(x for x in list_2 if x[0] == key)
                merged_tuples.append(tuple_1 + tuple_2[1:])
            except StopIteration:
                merged_tuples.append(tuple_1 + (None,))
        return merged_tuples

    aligned_tuples = reduce(merge, all_aligned_pairs)

    all_aligned_filenames = [item for t in aligned_tuples for item in t]
    all_unaligned_filenames = set(all_screenshot_filenames) - set(all_aligned_filenames)
    print "UNALIGNED SCREENSHOTS: " + str(all_unaligned_filenames) + "\n"

    return aligned_tuples

def get_aligned_pairs(grouping, agent_name_1, agent_name_2):
    aligned_pairs = [] # list of all aligned pairs of screenshots

    for action, all_filenames_for_action in grouping.iteritems():
        # split into builder and architect screenshots
        architect_filenames = filter(lambda x: agent_name_1 in x, all_filenames_for_action)
        builder_filenames = filter(lambda x: agent_name_2 in x, all_filenames_for_action)
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Postprocess observations for screenshot alignment")
    parser.add_argument("logs_root_dir", help="Root directory for all log data")
    parser.add_argument("screenshots_root_dir", help="Root directory for all screenshot data")
    parser.add_argument("--overwrite", default=False, action="store_true", help="Whether or not to overwrite previous postprocessed jsons")
    args = parser.parse_args()

    postprocess_missions(args.logs_root_dir, args.screenshots_root_dir, args.overwrite)
