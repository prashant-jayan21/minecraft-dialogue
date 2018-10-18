import os, json, re, sys, argparse, csv
from os.path import join, isdir
from diff_check import get_gold_config, reformat_built_config_block
sys.path.insert(0, '../config_diff_tool')
from diff import get_diff, get_gold_config_distribution, get_built_config_distribution, dict_to_tuple

def process_log_dir(logs_root_dir, log_dir, gold_configs_dir):
    # get gold config
    config_name = re.sub(r"B\d+-A\d+-|-\d\d\d\d\d\d\d+", "", log_dir)
    config_xml_file = join(gold_configs_dir, config_name + ".xml")

    gold_config = get_gold_config(config_xml_file)

    # process dialog state by state
    postprocessed_observations_file = join(logs_root_dir, log_dir, "postprocessed-observations.json")

    with open(postprocessed_observations_file) as observations:
        observations_dict = json.load(observations)

    process_dialog_states(observations_dict, gold_config)

def process_dialog_states(observations_dict, gold_config):
    for i, world_state in enumerate(observations_dict["WorldStates"]):
        built_config_raw = world_state["BlocksInGrid"]
        built_config = list(map(reformat_built_config_block, built_config_raw))

        _, everything_min = get_diff(gold_config = gold_config, built_config = built_config)

        minimal_diffs_gold_config_space = list(map(lambda x: x[0][1].diff_gold_config_space, everything_min))
        probs = get_gold_config_distribution(gold_config, minimal_diffs_gold_config_space)
        print("placement probability distribution over gold config blocks:")
        print(probs)
        print("\n")

        minimal_diffs_built_config_space = list(map(lambda x: x[0][1].diff_built_config_space, everything_min))
        probs = get_built_config_distribution(built_config, minimal_diffs_built_config_space)
        print("removal probability distribution over built config blocks:")
        print(probs)
        print("\n")
        print(minimal_diffs_gold_config_space)
        print("\n")
        print(minimal_diffs_built_config_space)

        next_placements = list(map(lambda x: x["gold_minus_built"], minimal_diffs_built_config_space))
        # union
        print(next_placements)
        all_next_placement_blocks = [item for sublist in next_placements for item in sublist]
        all_next_placement_blocks_reformatted = list(map(dict_to_tuple, all_next_placement_blocks))
        all_next_placement_blocks_reformatted_unique = set(all_next_placement_blocks_reformatted)
        all_next_placement_blocks_unique = list(map(dict, all_next_placement_blocks_reformatted_unique))
        print(all_next_placement_blocks_unique)
        probs = get_gold_config_distribution(all_next_placement_blocks_unique, minimal_diffs_built_config_space)
        print("idk:")
        print(probs)
        print("\n")

        print("-" * 50)

if __name__ == "__main__":
    logs_root_dir = "/Users/prashant/Work/cwc-minecraft-models/data/logs/data-3-30/logs"
    log_dir = "B1-A3-C8-1522432497234"
    gold_configs_dir = "/Users/prashant/Work/cwc-minecraft-models/data/gold-configurations"

    process_log_dir(logs_root_dir, log_dir, gold_configs_dir)
