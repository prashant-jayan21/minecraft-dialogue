import os, json, argparse, re
from os.path import join, isdir
from cwc_io_utils import read_metrics_db, write_metrics_db

def merge(metrics_db, metrics_data):
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
            metrics_dict["mean_time"] = float(metrics_dict["time"])
            metrics_dict["mean_num_utterances"] = float(metrics_dict["num_utterances"])
            metrics_dict["mean_utterances_per_turn"] = float(metrics_dict["utterances_per_turn"])
            # convert to lists
            metrics_dict["time"] = [metrics_dict["time"]]
            metrics_dict["num_utterances"] = [metrics_dict["num_utterances"]]
            metrics_dict["utterances_per_turn"] = [metrics_dict["utterances_per_turn"]]
            metrics_db.append(metrics_dict)

def get_metrics_data(logs_root_dir):
    all_log_dirs = filter(lambda x: isdir(join(logs_root_dir, x)), os.listdir(logs_root_dir))

    metrics_data = []

    for log_dir in all_log_dirs:
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

        config_name = re.sub(r"B\d+-A\d+-|-\d\d\d\d\d\d\d+", "", log_dir)
        metrics_dict["config"] = config_name

        # add to dataset list
        metrics_data.append(metrics_dict)

    return metrics_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update metrics DB with metrics data")
    parser.add_argument("metrics_db_csv", help="File path of the spreadsheet (.csv) DB containing all metrics info")
    parser.add_argument("logs_root_dir", help="Root directory for all log data")
    args = parser.parse_args()

    # read metrics DB file
    metrics_db = read_metrics_db(args.metrics_db_csv)

    # get metrics data from logs
    metrics_data = get_metrics_data(args.logs_root_dir)

    # merge both
    merge(metrics_db = metrics_db, metrics_data = metrics_data)

    # write updated db to file
    write_metrics_db(metrics_db, args.metrics_db_csv)
