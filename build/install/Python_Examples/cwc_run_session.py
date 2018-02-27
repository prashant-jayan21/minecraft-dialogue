import time, csv, argparse
from cwc_run_single_mission import cwc_run_mission

if __name__ == "__main__":
    # Parse CLAs
    parser = argparse.ArgumentParser(description="Run a session driver.")
    parser.add_argument("user_info_csv", help="File path of the spreadsheet (.csv) containing user info")
    parser.add_argument("configs_csv", help="File path of the spreadsheet (.csv) containing all gold, existing config file paths")
    parser.add_argument("--fixed_viewer_csv", default=None, help="File path of the spreadsheet (.csv) containing all IP addresses of the Fixed Viewer clients")
    parser.add_argument("--num_fixed_viewers", type=int, default=4, help="Number of fixed viewer clients per mission")
    parser.add_argument("--lan", default=False, action="store_true", help="LAN mode")
    args = parser.parse_args()

    # Read user info from spreadsheet
    all_users = []
    with open(args.user_info_csv, 'rb') as csvfile:
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
    with open(args.configs_csv, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_configs.append(row)
    num_configs = len(all_configs)

    # Read fixed viewer info from spreadsheet
    fixed_viewer = None
    if args.fixed_viewer_csv is not None:
        with open(args.fixed_viewer_csv, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                fixed_viewer = row

    # Check that fixed viewer parameters are set
    if args.lan and args.num_fixed_viewers > 0:
        if args.fixed_viewer_csv is None:
            print "Error: In LAN mode, you must specify a --fixed_viewer_csv parameter. Consider using a default localhost, such as the specification in sample_fixed_viewer.csv."
            exit()

        if fixed_viewer is None:
            print "Error: In LAN mode, you must have at least one available Fixed Viewer client in the Fixed Viewer csv. Consider using a default localhost, such as the specification in sample_fixed_viewer.csv."
            exit()

    if args.fixed_viewer_csv is not None and args.num_fixed_viewers == 0:
        print "Warning: You specified a --fixed_viewer_csv parameter, but did not specify the number of fixed viewer clients to spawn (--num_fixed_viewers). As a result, the missions will launch with no fixed viewer clients -- check that this is your intended behavior."

    # Execute rounds
    for config in all_configs:

        print "\nROUND STARTED..."
        print "\nGOLD CONFIG: " + config["gold file path"]
        print "EXISTING CONFIG: " + config["existing file path"]

        builder_port = (10000 if builder.get("port") is None else int(builder["port"]))
        architect_port = (10000 if architect.get("port") is None else int(architect["port"]))
        fixed_viewer_port = None if fixed_viewer is None else (10000 if fixed_viewer.get("port") is None else int(fixed_viewer["port"]))
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
            "fixed_viewer_ip_addr": None if fixed_viewer is None else fixed_viewer["ip address"],
            "fixed_viewer_port": fixed_viewer_port,
            "num_fixed_viewers": args.num_fixed_viewers
        }

        # submit mission jobs to process pool
        print "\nMISSIONS RUNNING..."
        cwc_run_mission(mission_args)

        print "\nROUND ENDED..."
        print "\nWAITING..."

        # Wait for some time
        time.sleep(10)

    print "\nSESSION COMPLETE!"
