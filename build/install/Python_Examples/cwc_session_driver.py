from multiprocessing import Pool
import time
from cwc_all_functions import cwc_all_obs_and_save_data

# Number of rounds in one session
num_rounds = 3
num_missions_per_round = 2

# Spawn worker processes
pool = Pool(processes=num_missions_per_round)

# Execute rounds
for i in range(num_rounds):

    print "\nROUND " + str(i) + " STARTED..."

    # Read info for all missions
    args_mission_1 = {
        "lan": False,
        "builder_ip_addr": None,
        "builder_id": "1",
        "architect_ip_addr": None,
        "architect_id": "2",
        "gold_config": None,
    }

    args_mission_2 = {
        "lan": False,
        "builder_ip_addr": None,
        "builder_id": "3",
        "architect_ip_addr": None,
        "architect_id": "4",
        "gold_config": None,
    }

    mission_args = [args_mission_1, args_mission_2]

    # Submit missions jobs to process pool
    print "\nMISSIONS RUNNING..."
    pool.map(cwc_all_obs_and_save_data, mission_args)

    print "\nROUND " + str(i) + " ENDED..."
    print "\nWAITING FOR CLIENT RESETS..."

    # Wait for client restarts
    time.sleep(120)

# Cleanup worker processes
pool.close()
pool.join()

print "\nSESSION COMPLETE!"
