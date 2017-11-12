from multiprocessing import Pool
from cwc_all_functions import cwc_all_obs_and_save_data

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

num_missions = len(mission_args)

# Spawn processes

pool = Pool(processes=num_missions)

pool.map(cwc_all_obs_and_save_data, mission_args)
