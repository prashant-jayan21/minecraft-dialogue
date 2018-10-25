import os, json, re, sys, argparse, csv
from collections import Counter
import xml.etree.ElementTree as ET
from os.path import join, isdir
sys.path.insert(0, '../config_diff_tool')
from diff import get_diff, get_gold_config_distribution, get_built_config_distribution, dict_to_tuple, build_region_specs

def process_log_dir(logs_root_dir, log_dir, gold_configs_dir):
    # get gold config
    config_name = re.sub(r"B\d+-A\d+-|-\d\d\d\d\d\d\d+", "", log_dir)
    config_xml_file = join(gold_configs_dir, config_name + ".xml")

    gold_config = get_gold_config(config_xml_file)

    # get observations
    postprocessed_observations_file = join(logs_root_dir, log_dir, "postprocessed-observations.json")

    with open(postprocessed_observations_file) as observations:
        observations_dict = json.load(observations)

    # process dialog state by state
    process_dialog_states(observations_dict, gold_config)

def process_dialog_states(observations_dict, gold_config):
    for i, world_state in enumerate(observations_dict["WorldStates"]):
        print("STATE NUMBER: " + str(i) + "\n")
        built_config_raw = world_state["BlocksInGrid"]
        built_config = list(map(reformat_built_config_block, built_config_raw))

        _, everything_min = get_diff(gold_config = gold_config, built_config = built_config)

        minimal_diffs_built_config_space = list(map(lambda x: x[0][1].diff_built_config_space, everything_min))

        print(minimal_diffs_built_config_space)
        print("\n\n")

        all_grid_locations = get_type_distributions(minimal_diffs_built_config_space, built_config)

        grid_locations_with_blocks = list(filter(
            lambda x: x["grid_location"]["type"] != "empty",
            all_grid_locations
        ))

        empty_grid_locations_with_next_placements = list(filter(
            lambda x: x["grid_location"]["type"] == "empty" and x["type_distribution"]["empty"] < 1.0,
            all_grid_locations
        ))

        import pprint
        pp = pprint.PrettyPrinter()
        print("grid_locations_with_blocks\n")
        pp.pprint(grid_locations_with_blocks)
        print("\n\n")
        print("empty_grid_locations_with_next_placements\n")
        pp.pprint(empty_grid_locations_with_next_placements)

        print("\n\n")
        print("*" * 100)
        print("*" * 100)
        print("\n\n")

all_types = ["empty", "red", "orange", "green", "blue", "yellow", "purple"]

def get_type_distributions(minimal_diffs_built_config_space, built_config):
    results = []

    all_x_values = [i for i in range(build_region_specs["x_min_build"], build_region_specs["x_max_build"] + 1)]
    all_y_values = [i for i in range(build_region_specs["y_min_build"], build_region_specs["y_max_build"] + 1)]
    all_z_values = [i for i in range(build_region_specs["z_min_build"], build_region_specs["z_max_build"] + 1)]

    for x in all_x_values:
        for y in all_y_values:
            for z in all_z_values:
                grid_location = {
                    "x": x,
                    "y": y,
                    "z": z
                }

                occurence_in_built_config = next(
                    (t for t in built_config if t["x"] == grid_location["x"] and t["y"] == grid_location["y"] and t["z"] == grid_location["z"]),
                    None
                )

                if occurence_in_built_config:
                    grid_location["type"] = occurence_in_built_config["type"]
                else:
                    grid_location["type"] = "empty"

                types_acc_to_diffs = []

                for diff in minimal_diffs_built_config_space:
                    # what does this diff say about grid_location
                    types_acc_to_diffs.append(get_type_acc_to_diff(grid_location, diff))

                counts = Counter(types_acc_to_diffs)
                type_distribution = {}
                for type in all_types:
                    type_distribution[type] = float(counts[type]) / float(len(minimal_diffs_built_config_space))

                results.append(
                    {
                        "grid_location": grid_location,
                        "type_distribution": type_distribution
                    }
                )

    return results

def get_type_acc_to_diff(grid_location, diff):
    occurence_in_removals = next(
        (t for t in diff["built_minus_gold"] if t["x"] == grid_location["x"] and t["y"] == grid_location["y"] and t["z"] == grid_location["z"]),
        None
    )

    occurence_in_placements = next(
        (t for t in diff["gold_minus_built"] if t["x"] == grid_location["x"] and t["y"] == grid_location["y"] and t["z"] == grid_location["z"]),
        None
    )

    if occurence_in_removals is None and occurence_in_placements is None:
        return grid_location["type"]
    elif occurence_in_placements:
        return occurence_in_placements["type"]
    elif occurence_in_removals:
        return "empty"

color_regex = re.compile("red|orange|purple|blue|green|yellow")
displacement = 100 # TODO: import from cwc_mission_utils

def reformat_built_config_block(block):
    return {
        "x": block["AbsoluteCoordinates"]["X"],
        "y": block["AbsoluteCoordinates"]["Y"],
        "z": block["AbsoluteCoordinates"]["Z"],
        "type": color_regex.findall(str(block["Type"]))[0] # NOTE: DO NOT CHANGE! Unicode to str conversion needed downstream when stringifying the dict.
    }

def get_gold_config(gold_config_xml_file):
    """
    Args:
        gold_config_xml_file: The XML file for a gold configuration

    Returns:
        The gold config as a list of dicts -- one dict per block
    """

    with open(gold_config_xml_file) as f:
        all_lines = list(map(lambda t: t.strip(), f.readlines()))

    gold_config_raw = list(map(ET.fromstring, all_lines))

    def reformat(block):
        return {
            "x": int(block.attrib["x"]) - displacement,
            "y": int(block.attrib["y"]),
            "z": int(block.attrib["z"]) - displacement,
            "type": color_regex.findall(block.attrib["type"])[0]
        }

    gold_config = list(map(reformat, gold_config_raw))

    return gold_config


if __name__ == "__main__":
    logs_root_dir = "/Users/prashant/Work/cwc-minecraft-models/data/logs/data-4-5/logs"
    log_dir = "B13-A30-C3-1522967809907"
    gold_configs_dir = "/Users/prashant/Work/cwc-minecraft-models/data/gold-configurations"

    process_log_dir(logs_root_dir, log_dir, gold_configs_dir)
