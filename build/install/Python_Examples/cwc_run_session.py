import time, csv, argparse, sys
from cwc_run_single_mission import cwc_run_mission
sys.path.append('../../../../cwc-minecraft-models/python')
from vocab import Vocabulary

if __name__ == "__main__":
    # Parse CLAs
    parser = argparse.ArgumentParser(description="Run a session driver.")
    parser.add_argument("user_info_csv", help="File path of the spreadsheet (.csv) containing user info")
    parser.add_argument("configs_csv", help="File path of the spreadsheet (.csv) containing all gold, existing config file paths")
    parser.add_argument("--fixed_viewer_csv", default=None, help="File path of the spreadsheet (.csv) containing all IP addresses of the Fixed Viewer clients")
    parser.add_argument("--num_fixed_viewers", type=int, default=0, help="Number of fixed viewer clients per mission")
    parser.add_argument("--lan", default=False, action="store_true", help="LAN mode")
    parser.add_argument("--draw_inventory_blocks", action="store_true", help="Starts the mission with inventory blocks on the ground")
    parser.add_argument("--existing_is_gold", action="store_true", help="Indicates existing configs are actually gold configs and need to be displaced")
    parser.add_argument("--mode", default="data_collection", choices=['data_collection', 'architect_demo', 'builder_demo', 'create_target_structures', 'replay'], help="Type of application to run: data_collection, architect_demo, builder_demo, create_target_structures, replay")
    parser.add_argument("--generated_sentences_dir", default="generated_sentences/")
    parser.add_argument("--generated_sentences_sources", default=["seq2seq_attn", "acl-model"], nargs='+', help="model types to be evaluated, in the order that their generated sentences jsons are loaded")
    parser.add_argument("--split", default="val")
    parser.add_argument("--shuffle", default=False, action='store_true', help='shuffle sentences to be evaluated')
    parser.add_argument("--num_samples_to_replay", default=1000, type=int, help="Number of samples to view in replay tool")
    parser.add_argument("--jsons_dir", default="jsons/")
    parser.add_argument("--sampled_sentences_dir", default="sampled_sentences/")
    parser.add_argument("--sample_sentences", default=False, action='store_true')
    parser.add_argument("--num_sentences", default=100)
    parser.add_argument("--ignore_ids", default=[1, 2, 39], nargs='+', help='player IDs to be ignored when sampling examples to be evaluated')
    parser.add_argument("--evaluator_id", default=1, help="ID of human evaluator")
    parser.add_argument("--resume_evaluation", default=False, action='store_true', help='resumes evaluation of given player ID by playing examples unseen by that player')
    parser.add_argument("--replay_mode", default="replay", choices=["replay", "evaluate"], help='replay tool mode')
    args = parser.parse_args()

    create_target_structures = args.mode == 'create_target_structures'

    if args.mode in ['data_collection', 'create_target_structures']:
        from cwc_run_single_mission import cwc_run_mission
    elif args.mode == 'builder_demo':
        from cwc_run_builder_demo import cwc_run_mission
    elif args.mode == 'architect_demo':
        from cwc_run_architect_demo import cwc_run_mission
    elif args.mode == 'replay':
        from cwc_replay_mission import cwc_run_mission

    # Read user info from spreadsheet
    all_users = []
    with open(args.user_info_csv, 'rt') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_users.append(row)
    assert len(all_users) == 2

    builder, architect = all_users[0], all_users[1]
    if all_users[0].get("role") is not None:
        builder = all_users[0] if all_users[0]["role"].lower() == "builder" else all_users[1]
        architect = all_users[0] if all_users[0]["role"].lower() == "architect" else all_users[1]

    # Read gold config file paths from spreadsheet
    all_configs = []
    with open(args.configs_csv, 'rt') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_configs.append(row)
    num_configs = len(all_configs)

    # Read fixed viewer info from spreadsheet
    fixed_viewer = None
    if args.fixed_viewer_csv is not None:
        with open(args.fixed_viewer_csv, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                fixed_viewer = row

    # Check that fixed viewer parameters are set
    if args.lan and args.num_fixed_viewers > 0:
        if args.fixed_viewer_csv is None:
            print("Error: In LAN mode, you must specify a --fixed_viewer_csv parameter. Consider using a default localhost, such as the specification in sample_fixed_viewer.csv.")
            exit()

        if fixed_viewer is None:
            print("Error: In LAN mode, you must have at least one available Fixed Viewer client in the Fixed Viewer csv. Consider using a default localhost, such as the specification in sample_fixed_viewer.csv.")
            exit()

    if args.fixed_viewer_csv is not None and args.num_fixed_viewers == 0:
        print("Warning: You specified a --fixed_viewer_csv parameter, but did not specify the number of fixed viewer clients to spawn (--num_fixed_viewers). As a result, the missions will launch with no fixed viewer clients.")

    # Execute rounds
    for config in all_configs:

        print("\nROUND STARTED...")
        print("\nGOLD CONFIG: " + config["gold file path"])
        print("EXISTING CONFIG: " + config["existing file path"])

        builder_port = (10000 if builder.get("port") is None else int(builder["port"]))
        architect_port = (10000 if architect.get("port") is None else int(architect["port"]))
        fixed_viewer_port = None if fixed_viewer is None or args.num_fixed_viewers == 0 else (10000 if fixed_viewer.get("port") is None else int(fixed_viewer["port"]))
        mission_args = {
            "lan": args.lan,
            "builder_ip_addr": builder["ip address"],
            "builder_id": builder["id"],
            "builder_port": builder_port,
            "architect_ip_addr": architect["ip address"],
            "architect_id": architect["id"],
            "architect_port": architect_port,
            "gold_config": config["gold file path"],
            "existing_config": config["existing file path"],
            "fixed_viewer_ip_addr": None if fixed_viewer is None or args.num_fixed_viewers == 0 else fixed_viewer["ip address"],
            "fixed_viewer_port": fixed_viewer_port,
            "num_fixed_viewers": args.num_fixed_viewers,
            "draw_inventory_blocks": args.draw_inventory_blocks,
            "existing_is_gold": args.existing_is_gold,
            "create_target_structures": create_target_structures
        }

        if args.mode == 'replay':
            mission_args["generated_sentences_dir"] = args.generated_sentences_dir
            mission_args["generated_sentences_sources"] = args.generated_sentences_sources
            mission_args["shuffle"] = args.shuffle
            mission_args["jsons_dir"] = args.jsons_dir
            mission_args["sampled_sentences_dir"] = args.sampled_sentences_dir
            mission_args["num_samples_to_replay"] = args.num_samples_to_replay
            mission_args["sample_sentences"] = args.sample_sentences
            mission_args["num_sentences"] = args.num_sentences
            mission_args["ignore_ids"] = args.ignore_ids
            mission_args["evaluator_id"] = args.evaluator_id
            mission_args["resume_evaluation"] = args.resume_evaluation
            mission_args["split"] = args.split
            mission_args["replay_mode"] = args.replay_mode

        # submit mission jobs to process pool
        print("\nMISSIONS RUNNING...")
        cwc_run_mission(mission_args)

        print("\nROUND ENDED...")
        print("\nWAITING...")

        # Wait for some time
        time.sleep(10)

    print("\nSESSION COMPLETE!")
