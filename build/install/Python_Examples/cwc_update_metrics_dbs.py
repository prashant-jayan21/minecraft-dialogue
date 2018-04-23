import os, json, argparse, re, copy
from os.path import join, isdir
from cwc_io_utils import read_config_metrics_db, write_config_metrics_db, read_dialog_metrics_db, write_dialog_metrics_db

def merge_into_dialog_metrics_db(metrics_db, metrics_data):
    # NOTE: Does not mutate either argument -- DO NOT CHANGE THIS BEHAVIOR!
    def f(d, key):
        r = copy.deepcopy(d)
        del r[key]
        return r

    return metrics_db + map(lambda x: f(x,"config"), metrics_data)

def merge_into_config_metrics_db(metrics_db, metrics_data):
    # NOTE: Mutates metrics_db ONLY -- DO NOT CHANGE THIS BEHAVIOR!
    for metrics_dict in metrics_data:
        found = False

        # check if config is already present in db
        for metrics_dict_db in metrics_db:
            if metrics_dict_db["config"] == metrics_dict["config"]:
                found = True
                #merge
                metrics_dict_db["time"].append(metrics_dict["time"])
                metrics_dict_db["num_utterances"].append(metrics_dict["num_utterances"])
                metrics_dict_db["utterances_per_turn"].append(metrics_dict["utterances_per_turn"])
                metrics_dict_db["mean_time"] = float(sum(metrics_dict_db["time"]))/float(len(metrics_dict_db["time"]))
                metrics_dict_db["mean_num_utterances"] = float(sum(metrics_dict_db["num_utterances"]))/float(len(metrics_dict_db["num_utterances"]))
                metrics_dict_db["mean_utterances_per_turn"] = float(sum(metrics_dict_db["utterances_per_turn"]))/float(len(metrics_dict_db["utterances_per_turn"]))
                break

        # if not found
        if not found:
            metrics_dict_to_append = {}
            metrics_dict_to_append["config"] = metrics_dict["config"]
            # add means
            metrics_dict_to_append["mean_time"] = metrics_dict["time"]
            metrics_dict_to_append["mean_num_utterances"] = float(metrics_dict["num_utterances"])
            metrics_dict_to_append["mean_utterances_per_turn"] = metrics_dict["utterances_per_turn"]
            # convert to lists and add remaining stuff
            metrics_dict_to_append["time"] = [metrics_dict["time"]]
            metrics_dict_to_append["num_utterances"] = [metrics_dict["num_utterances"]]
            metrics_dict_to_append["utterances_per_turn"] = [metrics_dict["utterances_per_turn"]]
            metrics_db.append(metrics_dict_to_append)

warmup_configs_blacklist = ["blue-original-L", "C3", "orange-flat-original-L", "C17", "bigger-original-L", "C32", "l-shape", "C38"]

def get_metrics_data(logs_root_dir):
    all_log_dirs = filter(lambda x: isdir(join(logs_root_dir, x)), os.listdir(logs_root_dir))

    metrics_data = []

    for log_dir in all_log_dirs:
        config_name = re.sub(r"B\d+-A\d+-|-\d\d\d\d\d\d\d+", "", log_dir)

        if config_name in warmup_configs_blacklist:
            continue

        # read metrics.json
        metrics_json_file = join(logs_root_dir, log_dir, "metrics.json")
        with open(metrics_json_file) as json_data:
            metrics_dict = json.load(json_data)

        # read postprocessed-observations.json
        postprocessed_observations_json_file = join(logs_root_dir, log_dir, "postprocessed-observations.json")
        with open(postprocessed_observations_json_file) as json_data:
            postprocessed_observations_dict = json.load(json_data)

        # get required metrics data
        del metrics_dict["num_turns"]
        metrics_dict["time"] = float(postprocessed_observations_dict["TimeElapsed"])/float(60)

        metrics_dict["config"] = config_name

        metrics_dict["dialog"] = log_dir

        # add to dataset list
        metrics_data.append(metrics_dict)

    return metrics_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update metrics DBs with metrics data")
    parser.add_argument("dialog_metrics_db_csv", help="File path of the spreadsheet (.csv) DB containing all metrics info at the dialog level")
    parser.add_argument("config_metrics_db_csv", help="File path of the spreadsheet (.csv) DB containing all metrics info at the config level")
    parser.add_argument("logs_root_dir", help="Root directory for all log data")
    args = parser.parse_args()

    # read config metrics DB file
    config_metrics_db = read_config_metrics_db(args.config_metrics_db_csv)

    # get metrics data from logs
    metrics_data = get_metrics_data(args.logs_root_dir)

    # merge new metrics data and config metrics DB
    merge_into_config_metrics_db(metrics_db = config_metrics_db, metrics_data = metrics_data)

    # write updated config metrics DB to file
    write_config_metrics_db(config_metrics_db, args.config_metrics_db_csv)

    # read dialog metrics DB file
    dialog_metrics_db = read_dialog_metrics_db(args.dialog_metrics_db_csv)

    # merge new metrics data and dialog metrics DB
    dialog_metrics_db = merge_into_dialog_metrics_db(metrics_db = dialog_metrics_db, metrics_data = metrics_data)

    # write updated config metrics DB to file
    write_dialog_metrics_db(dialog_metrics_db, args.dialog_metrics_db_csv)
