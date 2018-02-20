from multiprocessing import Pool, freeze_support
import time
import csv
from random import shuffle
import argparse
from cwc_all_functions import cwc_all_obs_and_save_data

if __name__ == "__main__":
    # Parse CLAs
    parser = argparse.ArgumentParser(description="Run a session driver.")
    parser.add_argument("user_info_csv", help="File path of the spreadsheet (.csv) containing all user info")
    parser.add_argument("configs_csv", help="File path of the spreadsheet (.csv) containing all gold, existing config file paths")
    parser.add_argument("--fixed_viewer_csv", default=None, help="File path of the spreadsheet (.csv) containing all IP addresses of the Fixed Viewer clients")
    parser.add_argument("--num_fixed_viewers", type=int, default=4, help="Number of fixed viewer clients per mission")
    parser.add_argument("--lan", default=False, action="store_true", help="LAN mode")
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

    all_configs = []
    with open(args.configs_spreadsheet, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_configs.append(row)
    num_configs = len(all_configs)

    fixed_viewers = []
    if args.fixed_viewer_spreadsheet is not None:
        with open(args.fixed_viewer_spreadsheet, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                fixed_viewers.append(row)

    if args.lan and args.num_fixed_viewers > 0:
        if args.fixed_viewer_spreadsheet is None:
            print "Error: In LAN mode, you must specify a --fixed_viewer_spreadsheet parameter. Consider using a default localhost, such as the specification in default_fixed_viewer.csv."
            exit()

        if len(fixed_viewers) <= 0:
            print "Error: In LAN mode, you must have at least one available Fixed Viewer client in the Fixed Viewer csv. Consider using a default localhost, such as the specification in default_fixed_viewer.csv."
            exit()

    # Spawn worker processes
    # freeze_support()
    pool = Pool(processes=num_users/2)

    # Execute rounds
    for config in all_configs:

        print "\nROUND STARTED..."
        print "\nGOLD CONFIG: " + config["gold file path"]
        print "\nEXISTING CONFIG: " + config["existing file path"]

        user_pairs = zip(all_users[0::2], all_users[1::2])
        assert len(fixed_viewers) == 0 or len(fixed_viewers) >= len(user_pairs)

        # create mission args list
        all_mission_args = []
        for idx in range(len(user_pairs)):
            user_pair = user_pairs[idx]
            builder_port = (10000 if user_pair[0].get("port") is None else int(user_pair[0]["port"]))
            architect_port = (10000 if user_pair[1].get("port") is None else int(user_pair[1]["port"]))
            fixed_viewer_port = None if len(fixed_viewers) == 0 else (10000 if fixed_viewers[idx].get("port") is None else int(fixed_viewers[idx]["port"]))
            mission_args = {
                "lan": args.lan,
                "builder_ip_addr": user_pair[0]["ip address"],
                "builder_id": user_pair[0]["id"],
                "builder_port": builder_port,
                "architect_ip_addr": user_pair[1]["ip address"],
                "architect_id": user_pair[1]["id"],
                "architect_port": architect_port,
                "gold_config": config["gold file path"],
                "existing_config": config["existing file path"],
                "fixed_viewer_ip_addr": None if len(fixed_viewers) == 0 else fixed_viewers[idx]["ip address"],
                "fixed_viewer_port": fixed_viewer_port,
                "num_fixed_viewers": args.num_fixed_viewers
            }
            all_mission_args.append(mission_args)

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
