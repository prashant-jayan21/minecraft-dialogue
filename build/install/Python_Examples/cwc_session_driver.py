from multiprocessing import Pool
import time
import csv
from random import shuffle
import argparse
from cwc_all_functions import cwc_all_obs_and_save_data

# Parse CLAs
parser = argparse.ArgumentParser(description="Run a session driver.")
parser.add_argument("--user_spreadsheet", help="Absolute path of the spreadsheet (.csv) containing all user info")
parser.add_argument("--gold_configs_spreadsheet", help="Absolute path of the spreadsheet (.csv) containing all gold config absolute file paths")
args = parser.parse_args()

# Read user info from spreadsheet

all_users = []
with open(args.user_spreadsheet, 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        all_users.append(row)

assert len(all_users)%2 == 0 # test that there are even number of users

# Read gold config abs file paths from spreadsheet

all_gold_configs = []
with open(args.gold_configs_spreadsheet, 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        all_gold_configs.append(row)

# Some params
num_users = len(all_users)
num_gold_configs = len(all_gold_configs)

num_rounds = num_gold_configs
num_missions_per_round = num_users/2

# Spawn worker processes
pool = Pool(processes=num_missions_per_round)

# Execute rounds
for gold_config in all_gold_configs:

    print "\nROUND STARTED..."
    print "\nGOLD CONFIG: " + gold_config

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
            "gold_config": gold_config,
        }
        all_mission_args.append(mission_args)

    # Submit mission jobs to process pool
    print "\nMISSIONS RUNNING..."
    pool.map(cwc_all_obs_and_save_data, all_mission_args)

    print "\nROUND ENDED..."
    print "\nWAITING FOR CLIENT RESETS..."

    # Wait for client restarts
    time.sleep(120)

# Cleanup worker processes
pool.close()
pool.join()

print "\nSESSION COMPLETE!"
