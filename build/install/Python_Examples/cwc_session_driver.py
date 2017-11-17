from multiprocessing import Pool
import time
import csv
from random import shuffle
import argparse
from cwc_all_functions import cwc_all_obs_and_save_data

# Parse CLAs
parser = argparse.ArgumentParser(description="Run a session driver.")
parser.add_argument("user_info_spreadsheet", help="File path of the spreadsheet (.csv) containing all user info")
parser.add_argument("gold_configs_spreadsheet", help="File path of the spreadsheet (.csv) containing all gold config file paths")
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

# Spawn worker processes
pool = Pool(processes=num_users/2)

# Execute rounds
for gold_config in all_gold_configs:

    print "\nROUND STARTED..."
    print "\nGOLD CONFIG: " + gold_config["file path"]

    # randomly pair up users
    shuffle(all_users)
    user_pairs_randomized = zip(all_users[0::2], all_users[1::2])

    # create mission args list
    all_mission_args = []
    for user_pair in user_pairs_randomized:
        mission_args = {
            "lan": False,
            "builder_ip_addr": user_pair[0]["ip address"],
            "builder_id": user_pair[0]["id"],
            "architect_ip_addr": user_pair[1]["ip address"],
            "architect_id": user_pair[1]["id"],
            "gold_config": gold_config["file path"],
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
