import xml.etree.ElementTree as ET
import os, json, re, sys, argparse, csv
from os.path import join, isdir
from actions_distributions_analysis import get_gold_config, reformat_built_config_block
sys.path.insert(0, '../config_diff_tool')
from diff import get_diff

def get_built_config(observations_dict):
    """
    Args:
        observations_dict: The json observations data for a mission

    Returns:
        The built config at the end of the mission as a list of dicts -- one dict per block
    """

    built_config_raw = observations_dict["WorldStates"][-1]["BlocksInGrid"]

    built_config = list(map(reformat_built_config_block, built_config_raw))

    return built_config

def process_logs_dataset(logs_dataset_dir, gold_configs_dir):
    all_logs_root_dirs = [x for x in os.listdir(logs_dataset_dir) if isdir(join(logs_dataset_dir, x))]

    results = []

    for logs_root_dir in all_logs_root_dirs:
        results_for_logs_root_dir = process_logs_root_dir(join(logs_dataset_dir, logs_root_dir), gold_configs_dir)
        results = results + results_for_logs_root_dir

    return results

def process_logs_root_dir(logs_root_dir, gold_configs_dir):
    all_log_dirs = [x for x in os.listdir(logs_root_dir) if isdir(join(logs_root_dir, x))]

    results = []

    for log_dir in all_log_dirs:
        print("Computing diff for " + logs_root_dir + "/" + log_dir + " ...")
        diff_size = process_log_dir(logs_root_dir, log_dir, gold_configs_dir)
        result = {
            "mission": log_dir,
            "diff_size": diff_size
        }
        results.append(result)

    return results

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process observations to check diff between gold config and built config")
    parser.add_argument("logs_dataset_dir", help="Root directory for entire logs dataset")
    parser.add_argument("gold_configs_dir", help="Root directory for all gold configs")
    args = parser.parse_args()

    # process logs dataset and collect results
    results = process_logs_dataset(args.logs_dataset_dir, args.gold_configs_dir)

    # write results to DB
    with open("diffs_db.csv", 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ['mission','diff_size'])
        writer.writeheader()
        for mission_dict in results:
            writer.writerow(mission_dict)
        print("DONE WRITING " + "diffs_db.csv")
