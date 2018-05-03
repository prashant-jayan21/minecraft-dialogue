import xml.etree.ElementTree as ET
import os, json, re, sys
from os.path import join, isdir
sys.path.insert(0, '../config_diff_tool')
from diff import get_diff
sys.path.insert(0, '..')
from cwc_mission_utils import displacement

color_regex = re.compile("red|orange|purple|blue|green|yellow")

def get_built_config(observations_dict):
    """
    Args:
        observations_dict: The json observations data for a mission

    Returns:
        The built config at the end of the mission
    """

    built_config_raw = observations_dict["WorldStates"][-1]["BlocksInGrid"]

    def reformat(block):
        return {
            "x": block["AbsoluteCoordinates"]["X"],
            "y": block["AbsoluteCoordinates"]["Y"],
            "z": block["AbsoluteCoordinates"]["Z"],
            "type": color_regex.findall(str(block["Type"]))[0] # NOTE: DO NOT CHANGE! Unicode to str conversion needed downstream when stringifying the dict.
        }

    built_config = map(reformat, built_config_raw)

    return built_config

def get_gold_config(gold_config_xml_file):
    with open(gold_config_xml_file) as f:
        all_lines = map(lambda t: t.strip(), f.readlines())

    gold_config_raw = map(ET.fromstring, all_lines)

    def reformat(block):
        return {
            "x": int(block.attrib["x"]) - displacement,
            "y": int(block.attrib["y"]),
            "z": int(block.attrib["z"]) - displacement,
            "type": color_regex.findall(block.attrib["type"])[0]
        }

    gold_config = map(reformat, gold_config_raw)

    return gold_config

def process_logs_root_dir(logs_root_dir, gold_configs_dir):
    all_log_dirs = filter(lambda x: isdir(join(logs_root_dir, x)), os.listdir(logs_root_dir))

    for log_dir in all_log_dirs:
        diff_size = g(logs_root_dir, log_dir, gold_configs_dir)
        print(log_dir)
        print(diff_size)
        print("\n")

def process_log_dir(logs_root_dir, log_dir, gold_configs_dir):
    # get gold config
    config_name = re.sub(r"B\d+-A\d+-|-\d\d\d\d\d\d\d+", "", log_dir)
    config_xml_file = join(gold_configs_dir, config_name + ".xml")

    gold_config = get_gold_config(config_xml_file)

    # get built config
    postprocessed_observations_file = join(logs_root_dir, log_dir, "postprocessed-observations.json")

    with open(postprocessed_observations_file) as observations:
        observations_dict = json.load(observations)

    built_config = get_built_config(observations_dict)

    diff = get_diff(gold_config = gold_config, built_config = built_config)
    diff_size = len(diff["gold_minus_built"]) + len(diff["built_minus_gold"])

    return diff_size
