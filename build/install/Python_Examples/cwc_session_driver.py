from multiprocessing import Pool, freeze_support
import time
import csv
from random import shuffle
import argparse
from cwc_all_functions import cwc_all_obs_and_save_data

if __name__ == "__main__":
    # Parse CLAs
    parser = argparse.ArgumentParser(description="Run a session driver.")
    parser.add_argument("user_info_spreadsheet", help="File path of the spreadsheet (.csv) containing all user info")
    parser.add_argument("gold_configs_spreadsheet", help="File path of the spreadsheet (.csv) containing all gold config file paths")
    parser.add_argument("--fixed_viewer_spreadsheet", default="default_fixed_viewer.csv", help="File path of the spreadsheet (.csv) containing all IP addresses of the Fixed Viewer clients")
    parser.add_argument("--num_fixed_viewers", type=int, default=4, help="Number of fixed viewer clients per mission")
    args = parser.parse_args()

    # Read user info from spreadsheet

    all_users = []
    with open(args.user_info_spreadsheet, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_users.append(row)

    num_users = len(all_users)
    assert num_users % 2 == 0 # test that there are even number of users

    # Read gold config file paths from spreadsheet

    all_gold_configs = []
    with open(args.gold_configs_spreadsheet, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_gold_configs.append(row)

    num_gold_configs = len(all_gold_configs)

    fixed_viewers = []
    with open(args.fixed_viewer_spreadsheet, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            fixed_viewers.append(row)

    # Spawn worker processes
    # freeze_support()
    pool = Pool(processes=num_users/2)

    # Execute rounds
    for gold_config in all_gold_configs:

        print "\nROUND STARTED..."
        print "\nGOLD CONFIG: " + gold_config["file path"]

        user_pairs = zip(all_users[0::2], all_users[1::2])
        assert len(fixed_viewers) >= len(user_pairs)
        fxidx = 0

        # create mission args list
        all_mission_args = []
        for user_pair in user_pairs:
            builder_port = (10000 if user_pair[0].get("port") is None else int(user_pair[0]["port"]))
            architect_port = (10000 if user_pair[1].get("port") is None else int(user_pair[1]["port"]))
            mission_args = {
                "lan": True,
                "builder_ip_addr": user_pair[0]["ip address"],
                "builder_id": user_pair[0]["id"],
                "builder_port": builder_port,
                "architect_ip_addr": user_pair[1]["ip address"],
                "architect_id": user_pair[1]["id"],
                "architect_port": architect_port,
                "gold_config": gold_config["file path"],
                "fixed_viewer_ip_addr": fixed_viewers[fxidx]["ip address"],
                "fixed_viewer_port": int(fixed_viewers[fxidx]["port"]),
                "num_fixed_viewers": args.num_fixed_viewers
            }
            all_mission_args.append(mission_args)
            fxidx += 1

        # submit mission jobs to process pool
        print "\nMISSIONS RUNNING..."
        pool.map(cwc_all_obs_and_save_data, all_mission_args)

        print "\nROUND ENDED..."
        print "\nWAITING..."

        # Wait for some time
        time.sleep(10)

    # Cleanup worker processes
    pool.close()
    pool.join()

    print "\nSESSION COMPLETE!"
