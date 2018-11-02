import os, json, re, sys, argparse, csv
import xml.etree.ElementTree as ET
from os.path import join, isdir
sys.path.insert(0, '../config_diff_tool')
from diff import get_diff, get_gold_config_distribution, get_built_config_distribution, dict_to_tuple
from diff_apps import get_type_distributions

# NOTE: THIS CODE HAS NOT BEEN CHECKED FOR PYTHON 3 COMPATIBILITY

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

        _, perturbations_and_diffs = get_diff(gold_config = gold_config, built_config = built_config)

        diffs_built_config_space = list(map(lambda x: x.diff.diff_built_config_space, perturbations_and_diffs))
        type_distributions_built_config_space = get_type_distributions(diffs_built_config_space=diffs_built_config_space, built_config=built_config)

        # print(diffs_built_config_space)
        # print("\n\n")

        grid_locations_with_blocks = list(filter(
            lambda x: x.grid_location["type"] != "empty",
            type_distributions_built_config_space
        ))
        print(len(grid_locations_with_blocks))

        empty_grid_locations_with_next_placements = list(filter(
            lambda x: x.grid_location["type"] == "empty" and x.type_distribution["empty"] < 1.0,
            type_distributions_built_config_space
        ))
        print(len(empty_grid_locations_with_next_placements))

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
    log_dir = "B15-A27-C50-1522970698566"
    gold_configs_dir = "/Users/prashant/Work/cwc-minecraft-models/data/gold-configurations"

    process_log_dir(logs_root_dir, log_dir, gold_configs_dir)
