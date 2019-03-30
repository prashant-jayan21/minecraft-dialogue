import MalmoPython
import sys, time

# observation grid parameters
x_min_obs, x_max_obs = -10, 10
y_min_obs, y_max_obs = 1, 9
z_min_obs, z_max_obs = -10, 10

# build region parameters
# the build region is defined by the x and z bounds of the white floor and the y bounds of the observation grid
x_min_build, x_max_build = -5, 5
y_min_build, y_max_build = y_min_obs, y_max_obs # NOTE: Do not change this relation without thought!
z_min_build, z_max_build = -5, 5

# goal region parameters
displacement = 100
x_min_goal, x_max_goal = x_min_build + displacement, x_max_build + displacement
y_min_goal, y_max_goal = y_min_build, y_max_build # NOTE: Do not change this relation without thought!
z_min_goal, z_max_goal = z_min_build + displacement, z_max_build + displacement

fv_placements = ['<Placement x = "0" y = "10" z = "-8" pitch="35"/>', 
                 '<Placement x = "0" y = "10" z = "9" pitch="35" yaw="180"/>', 
                 '<Placement x = "9" y = "10" z = "0" pitch="35" yaw="90"/>', 
                 '<Placement x = "-8" y = "10" z = "0" pitch="35" yaw="-90"/>']

def safeStartMission(agent_host, my_mission, my_client_pool, my_mission_record, role, expId):
    used_attempts = 0
    max_attempts = 5
    print(("Calling startMission for role", role))
    while True:
        try:
            # Attempt start:
            agent_host.startMission(my_mission, my_client_pool, my_mission_record, role, expId)
            break
        except MalmoPython.MissionException as e:
            errorCode = e.details.errorCode
            if errorCode == MalmoPython.MissionErrorCode.MISSION_SERVER_WARMING_UP:
                print("Server not quite ready yet - waiting...")
                time.sleep(2)
            elif errorCode == MalmoPython.MissionErrorCode.MISSION_INSUFFICIENT_CLIENTS_AVAILABLE:
                print("Not enough available Minecraft instances running.")
                used_attempts += 1
                if used_attempts < max_attempts:
                    print(("Will wait in case they are starting up.", max_attempts - used_attempts, "attempts left."))
                    time.sleep(2)
            elif errorCode == MalmoPython.MissionErrorCode.MISSION_SERVER_NOT_FOUND:
                print("Server not found - has the mission with role 0 been started yet?")
                used_attempts += 1
                if used_attempts < max_attempts:
                    print(("Will wait and retry.", max_attempts - used_attempts, "attempts left."))
                    time.sleep(2)
            else:
                print(("Other error:", e.message))
                print("Waiting will not help here - bailing immediately.")
                exit(1)
        if used_attempts == max_attempts:
            print("All chances used up - bailing now.")
            exit(1)
    print("startMission called okay.")

def safeWaitForStart(agent_hosts):
    print("Waiting for the mission to start...")
    start_flags = [False for a in agent_hosts]
    start_time = time.time()
    time_out = 120  # Allow a two minute timeout.
    while not all(start_flags) and time.time() - start_time < time_out:
        states = [a.peekWorldState() for a in agent_hosts]
        start_flags = [w.has_mission_begun for w in states]
        errors = [e for w in states for e in w.errors]
        if len(errors) > 0:
            print("Errors waiting for mission start:")
            for e in errors:
                print((e.text))
            print("Bailing now.")
            exit(1)
        time.sleep(0.1)
        sys.stdout.write('.')
    if time.time() - start_time >= time_out:
        print("Timed out while waiting for mission to start - bailing.")
        exit(1)
    print("\nMission has started.")