import os, json, re, sys, argparse, csv
from os.path import join, isdir
from diff_check import get_gold_config, reformat_built_config_block
sys.path.insert(0, '../config_diff_tool')
from diff import get_diff, get_gold_config_distribution, get_built_config_distribution

def process_log_dir(logs_root_dir, log_dir, gold_configs_dir):
    # get gold config
    config_name = re.sub(r"B\d+-A\d+-|-\d\d\d\d\d\d\d+", "", log_dir)
    config_xml_file = join(gold_configs_dir, config_name + ".xml")

    gold_config = get_gold_config(config_xml_file)

    # get built config
    postprocessed_observations_file = join(logs_root_dir, log_dir, "postprocessed-observations.json")

    with open(postprocessed_observations_file) as observations:
        observations_dict = json.load(observations)

    f(observations_dict, gold_config)

def f(observations_dict, gold_config):
    for world_state in observations_dict["WorldStates"]:
        built_config_raw = world_state["BlocksInGrid"]
        built_config = list(map(reformat_built_config_block, built_config_raw))

        _, everything_min = get_diff(gold_config = gold_config, built_config = built_config)
        minimal_diffs_gold_config_space = list(map(lambda x: x[0][1].diff_gold_config_space, everything_min))

        scores = get_gold_config_distribution(gold_config, minimal_diffs_gold_config_space)
        print(scores)
        print("\n")

if __name__ == "__main__":
    logs_root_dir = "/Users/prashant/Work/cwc-minecraft-models/data/logs/data-3-30/logs"
    log_dir = "B1-A3-C1-1522435497386"
    gold_configs_dir = "/Users/prashant/Work/cwc-minecraft-models/data/gold-configurations"

    process_log_dir(logs_root_dir, log_dir, gold_configs_dir)
