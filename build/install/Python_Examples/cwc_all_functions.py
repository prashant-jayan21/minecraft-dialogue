# Prototype:
# Two humans - w/ abilities to chat and build block structures
# Record all observations

import MalmoPython
import os, sys, time, json, argparse, datetime, copy
import numpy as np

# observation grid parameters
x_min_obs = -10
x_max_obs = 10
y_min_obs = 1
y_max_obs = 11
z_min_obs = -10
z_max_obs = 10

# build region parameters
# the build region is defined by the x and z bounds of the white floor and the y bounds of the observation grid
x_min_build = -5
x_max_build = 5
y_min_build = y_min_obs # NOTE: Do not change this relation without thought!
y_max_build = y_max_obs # NOTE: Do not change this relation without thought!
z_min_build = -5
z_max_build = 5

# goal region parameters
displacement = 100
x_min_goal = x_min_build + displacement
x_max_goal = x_max_build + displacement
y_min_goal = y_min_build # NOTE: Do not change this relation without thought!
y_max_goal = y_max_build # NOTE: Do not change this relation without thought!
z_min_goal = z_min_build + displacement
z_max_goal = z_max_build + displacement


def safeStartMission(agent_host, my_mission, my_client_pool, my_mission_record, role, expId):
    used_attempts = 0
    max_attempts = 5
    print("Calling startMission for role", role)
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
                    print("Will wait in case they are starting up.", max_attempts - used_attempts, "attempts left.")
                    time.sleep(2)
            elif errorCode == MalmoPython.MissionErrorCode.MISSION_SERVER_NOT_FOUND:
                print("Server not found - has the mission with role 0 been started yet?")
                used_attempts += 1
                if used_attempts < max_attempts:
                    print("Will wait and retry.", max_attempts - used_attempts, "attempts left.")
                    time.sleep(2)
            else:
                print("Other error:", e.message)
                print("Waiting will not help here - bailing immediately.")
                exit(1)
        if used_attempts == max_attempts:
            print("All chances used up - bailing now.")
            exit(1)
    print("startMission called okay.")

def safeWaitForStart(agent_hosts):
    print "Waiting for the mission to start..."
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
                print(e.text)
            print("Bailing now.")
            exit(1)
        time.sleep(0.1)
        sys.stdout.write('.')
    if time.time() - start_time >= time_out:
        print("Timed out while waiting for mission to start - bailing.")
        exit(1)
    print("\nMission has started.")

def getPerspectiveCoordinates(x, y, z, yaw, pitch):
    # construct vector
    v = np.matrix('{}; {}; {}'.format(x, y, z))
    # construct yaw rotation matrix
    theta_yaw = np.radians(-1 * yaw)
    c, s = np.cos(theta_yaw), np.sin(theta_yaw)
    R_yaw = np.matrix('{} {} {}; {} {} {}; {} {} {}'.format(c, 0, -s, 0, 1, 0, s, 0, c))
    # multiply
    v_new = R_yaw * v
    # construct pitch rotation matrix
    theta_pitch = np.radians(pitch)
    c, s = np.cos(theta_pitch), np.sin(theta_pitch)
    R_pitch = np.matrix('{} {} {}; {} {} {}; {} {} {}'.format(1, 0, 0, 0, c, s, 0, -s, c))
    # multiply
    v_final = R_pitch * v_new
    x_final = v_final.item(0)
    y_final = v_final.item(1)
    z_final = v_final.item(2)
    return (x_final, y_final, z_final)

def processObservations(all_world_states, observations):
    for observation in observations:
        # print "Processing observation:", observation
        obs_dict = reformatJson(observation)
        all_world_states = mergeObservations(all_world_states, obs_dict)

    return all_world_states

def reformatJson(observation):
    obs_dict = {}
    obs_dict["Timestamp"] = observation.timestamp.replace(microsecond=0).isoformat(' ')
    js = json.loads(observation.text)

    if js.get(u'Yaw') is not None:
        yaw = js.get(u'Yaw')
        pitch = js.get(u'Pitch')
        xpos = js.get(u'XPos')
        ypos = js.get(u'YPos')
        zpos = js.get(u'ZPos')
        obs_dict["BuilderPosition"] = {"X": xpos, "Y": ypos, "Z": zpos, "Yaw": yaw, "Pitch": pitch}

    if js.get(u'ScreenshotPath') is not None:
        obs_dict["ScreenshotPath"] = js.get(u'ScreenshotPath')

    if js.get(u'Chat') is not None:
        obs_dict["ChatHistory"] = js.get(u'Chat')

    if js.get(u'BuilderInventory') is not None:
        obs_dict["BuilderInventory"] = []
        inventory = js.get(u'BuilderInventory')
        for block in inventory:
            obs_dict["BuilderInventory"].append({"Index": block["Index"], "Type": block["Type"], "Quantity": block["Quantity"]})

    if js.get(u'BuilderGridAbsolute') is not None:
        obs_dict["BuilderGridAbsolute"] = js.get(u'BuilderGridAbsolute')
        obs_dict["BuilderGridRelative"] = js.get(u'BuilderGridRelative')

    return obs_dict

def mergeObservations(all_world_states, obs_dict):
    if len(all_world_states) == 0:
        all_world_states.append(obs_dict)

    else:
        last_ws = all_world_states[-1]
        last_ws_keys = set(last_ws.keys())
        obs_keys = set(obs_dict.keys())
        obs_keys.remove("Timestamp")

        if len(last_ws_keys.intersection(obs_keys)) > 0:
            all_world_states.append(obs_dict)
        else:
            all_world_states[-1] = dict(obs_dict, **last_ws)

    return all_world_states

def postprocess(all_world_states):
    chat_history = []
    string_to_write = ""
    for world_state in all_world_states:
        # print "---\n", world_state
        if world_state.get("ChatHistory") is not None:
            chat_history += world_state["ChatHistory"]
        world_state["ChatHistory"] = copy.deepcopy(chat_history)
        recordGridCoordinates(world_state)
        string_to_write = writeToString(world_state, string_to_write)

    return string_to_write

# Records the blocks in the builder's grid, separated by outside vs. inside blocks. Also calculates their perspective coordinates.
# Appends these block information, as well as the chat history, to the world state JSON.
def recordGridCoordinates(cws):
    grid_absolute, grid_relative = cws.pop("BuilderGridAbsolute"), cws.pop("BuilderGridRelative")
    yaw, pitch = cws["BuilderPosition"]["Yaw"], cws["BuilderPosition"]["Pitch"]
    blocks_inside, blocks_outside = [], []
    for i in range(len(grid_absolute)):
        block_absolute = grid_absolute[i]
        block_relative = grid_relative[i]

        (ax, ay, az) = (block_absolute["X"], block_absolute["Y"], block_absolute["Z"])
        (px, py, pz) = getPerspectiveCoordinates(block_relative["X"], block_relative["Y"], block_relative["Z"], yaw, pitch)

        block_info = {"Type": block_relative["Type"], "AbsoluteCoordinates": {"X": ax, "Y": ay, "Z": az}, "PerspectiveCoordinates": {"X": px, "Y": py, "Z": pz}}
        outside = ax < x_min_build or ax > x_max_build or ay < y_min_build or ay > y_max_build or az < z_min_build or az > z_max_build
        blocks_outside.append(block_info) if outside else blocks_inside.append(block_info)

    cws["BlocksOutside"] = blocks_outside
    cws["BlocksInside"] = blocks_inside

# Generates a string representation of the world state JSON's contents and adds it to stw.
def writeToString(cws, stw):
    stw += "\n"+"-"*20+"\n[Timestamp] "+cws["Timestamp"]+"\n[Builder Position] (x, y, z): ("+str(cws["BuilderPosition"]["X"])+", "+str(cws["BuilderPosition"]["Y"])+", "+str(cws["BuilderPosition"]["Z"])+") " + \
           "(yaw, pitch): ("+str(cws["BuilderPosition"]["Yaw"])+", "+str(cws["BuilderPosition"]["Pitch"])+")\n[Screenshot Path] "+cws["ScreenshotPath"]+"\n\n[Chat Log]\n"
    for utterance in cws["ChatHistory"]:
        stw += "\t"+utterance+"\n"
    stw += "\n[Builder Inventory]"
    for block in cws["BuilderInventory"]:
        stw += "\tType: "+block["Type"]+" Index: "+str(block["Index"])+" Quantity: "+str(block["Quantity"])+"\n"
    stw += "\n[Blocks Inside]\n"
    for block in cws["BlocksInside"]:
        stw += "\tType: "+block["Type"]+"  Absolute (x, y, z): ("+str(block["AbsoluteCoordinates"]["X"])+", "+str(block["AbsoluteCoordinates"]["Y"])+", "+str(block["AbsoluteCoordinates"]["Z"])+")  Perspective (x, y, z): " + \
        str(block["PerspectiveCoordinates"]["X"])+", "+str(block["PerspectiveCoordinates"]["Y"])+", "+str(block["PerspectiveCoordinates"]["Z"])+")\n"
    stw += "\n[Blocks Outside]\n"
    for block in cws["BlocksOutside"]:
        stw += "\tType: "+block["Type"]+"  Absolute (x, y, z): ("+str(block["AbsoluteCoordinates"]["X"])+", "+str(block["AbsoluteCoordinates"]["Y"])+", "+str(block["AbsoluteCoordinates"]["Z"])+")  Perspective (x, y, z): " + \
        str(block["PerspectiveCoordinates"]["X"])+", "+str(block["PerspectiveCoordinates"]["Y"])+", "+str(block["PerspectiveCoordinates"]["Z"])+")\n"
    return stw

# Helper method to print a shortened, prettier version of the JSON's contents.
def prettyPrintJson(cws):
    for element in cws:
        sys.stdout.write("\t"+element+": ")
        if element == 'BlocksOutside' or element == 'BuilderGridAbsolute' or element == 'BuilderGridRelative':
            print len(cws[element]), "values",
        elif element == 'Timestamp' or element == 'ScreenshotPath':
            print cws[element],
        elif element == 'BuilderPosition' or element == 'BlocksInside' or element == 'BuilderInventory':
            print cws[element],
        else:
            for value in cws[element]:
                print "\n\t\t", value,
        print
    print

# Helper method to print a shortened, prettier version of the string to be written
def prettyPrintString(stw):
    sys.stdout.write("\n\n")
    begin = True
    num_lines = 0

    for line in stw.split("\n"):
        if line.strip().startswith('Type:'):
            num_lines += 1

        elif '[Blocks Outside]' in line or '---' in line:
            if not begin:
                sys.stdout.write('\t('+str(num_lines)+' values)\n')
            else:
                begin = False

            sys.stdout.write(line+"\n")
            num_lines = 0

        elif len(line.strip()) > 0:
            sys.stdout.write(line+"\n")

    sys.stdout.write('\t('+str(num_lines)+' values)\n\n')

def cwc_all_obs_and_save_data(args):
    start_time = time.time()

    chat_history = []
    last_ws = None

    # Create agent hosts:
    agent_hosts = [MalmoPython.AgentHost(), MalmoPython.AgentHost(), MalmoPython.AgentHost(), MalmoPython.AgentHost()]

    # Set observation policy for builder
    agent_hosts[0].setObservationsPolicy(MalmoPython.ObservationsPolicy.KEEP_ALL_OBSERVATIONS)

    # Set up a client pool
    client_pool = MalmoPython.ClientPool()

    if not args["lan"]:
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10000))
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10001))
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10002))
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10003))
    else:
        client_pool.add(MalmoPython.ClientInfo(args["architect_ip_addr"], 10001))
        client_pool.add(MalmoPython.ClientInfo(args["builder_ip_addr"], 10000))
        client_pool.add(MalmoPython.ClientInfo(args["architect_ip_addr"], 10000))
        client_pool.add(MalmoPython.ClientInfo(args["fixed_viewer_ip_addr"], 10000))

    # Create mission xmls

    # experiment ID
    experiment_time = str(int(round(time.time()*1000)))
    player_ids = "B"+args["builder_id"] + "-A" + args["architect_id"]
    config_id = os.path.basename(args["gold_config"]).replace(".xml","")
    experiment_id = player_ids + "-" + config_id + "-" + experiment_time

    # read gold config file and obtain xml substring
    gold_config_file = open(args["gold_config"], "r")
    gold_config_xml_substring = gold_config_file.read()
    gold_config_file.close()

    string_to_write = ""
    all_world_states = []

    # construct mission xml
    missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
                <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

                  <About>
                    <Summary>''' + experiment_id + '''</Summary>
                  </About>

                  <ServerSection>
                    <ServerInitialConditions>
                      <Time>
                        <StartTime>1000</StartTime>
                        <AllowPassageOfTime>false</AllowPassageOfTime>
                      </Time>
                      <Weather>clear</Weather>
                    </ServerInitialConditions>
                    <ServerHandlers>
                      <FlatWorldGenerator generatorString="3;241;1;" forceReset="true" destroyAfterUse="false"/>
                      <DrawingDecorator>
                        <DrawCuboid type="cwcmod:cwc_orange_rn" x1="5" y1="1" z1="8" x2="1" y2="2" z2="8"/>
                        <DrawCuboid type="cwcmod:cwc_yellow_rn" x1="-1" y1="1" z1="8" x2="-5" y2="2" z2="8"/>
                        <DrawCuboid type="cwcmod:cwc_green_rn" x1="8" y1="1" z1="6" x2="8" y2="2" z2="2"/>
                        <DrawCuboid type="cwcmod:cwc_blue_rn" x1="8" y1="1" z1="0" x2="8" y2="2" z2="-4"/>
                        <DrawCuboid type="cwcmod:cwc_purple_rn" x1="-8" y1="1" z1="6" x2="-8" y2="2" z2="2"/>
                        <DrawCuboid type="cwcmod:cwc_red_rn" x1="-8" y1="1" z1="0" x2="-8" y2="2" z2="-4"/>
                        <DrawCuboid type="cwcmod:cwc_unbreakable_white_rn" x1="''' + str(x_min_build) +'''" y1="0" z1="''' + str(z_min_build)+ '''" x2="'''+ str(x_max_build)+'''" y2="0" z2="''' + str(z_max_build) + '''"/>
                      </DrawingDecorator>
                      <ServerQuitWhenAnyAgentFinishes/>
                    </ServerHandlers>
                  </ServerSection>

                  <AgentSection mode="Survival">
                    <Name>Builder</Name>
                    <AgentStart>
                      <Placement x = "0" y = "1" z = "0"/>
                    </AgentStart>
                    <AgentHandlers>
                      <CwCObservation>
                         <Grid name="BuilderGrid" absoluteCoords="true">
                           <min x="'''+ str(x_min_obs) + '''" y="'''+ str(y_min_obs) + '''" z="''' + str(z_min_obs) + '''"/>
                           <max x="'''+ str(x_max_obs) + '''" y="''' + str(y_max_obs) + '''" z="''' + str(z_max_obs) + '''"/>
                         </Grid>
                      </CwCObservation>
                    </AgentHandlers>
                  </AgentSection>

                  <AgentSection mode="Spectator">
                    <Name>Architect</Name>
                    <AgentStart>
                      <Placement x = "0" y = "5" z = "-5" pitch="45"/>
                    </AgentStart>
                    <AgentHandlers/>
                  </AgentSection>

                  <AgentSection mode="Spectator">
                    <Name>FixedViewer</Name>
                    <AgentStart>
                      <Placement x = "0" y = "5" z = "-7" pitch="45"/>
                    </AgentStart>
                    <AgentHandlers/>
                  </AgentSection>
                </Mission>'''

    missionXML_oracle='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
                <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

                  <About>
                    <Summary>''' + experiment_id + '''</Summary>
                  </About>

                  <ServerSection>
                    <ServerInitialConditions>
                      <Time>
                        <StartTime>1000</StartTime>
                        <AllowPassageOfTime>false</AllowPassageOfTime>
                      </Time>
                      <Weather>clear</Weather>
                    </ServerInitialConditions>
                    <ServerHandlers>
                      <FlatWorldGenerator generatorString="3;241;1;" forceReset="true" destroyAfterUse="false"/>
                      <DrawingDecorator>
                        <DrawCuboid type="cwcmod:cwc_unbreakable_white_rn" x1="''' + str(x_min_goal) +'''" y1="0" z1="''' + str(z_min_goal)+ '''" x2="'''+ str(x_max_goal)+'''" y2="0" z2="''' + str(z_max_goal) + '''"/>''' + gold_config_xml_substring + \
                      '''</DrawingDecorator>
                      <ServerQuitWhenAnyAgentFinishes/>
                    </ServerHandlers>
                  </ServerSection>

                  <AgentSection mode="Spectator">
                    <Name>Oracle</Name>
                    <AgentStart>
                      <Placement x = "100" y = "5" z = "95" pitch="45"/>
                    </AgentStart>
                    <AgentHandlers/>
                  </AgentSection>
                </Mission>'''

    my_mission = MalmoPython.MissionSpec(missionXML, True)
    my_mission_oracle = MalmoPython.MissionSpec(missionXML_oracle, True)

    safeStartMission(agent_hosts[0], my_mission_oracle, client_pool, MalmoPython.MissionRecordSpec(), 0, "cwc_dummy_mission_oracle")
    
    safeStartMission(agent_hosts[1], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 0, "cwc_dummy_mission")
    safeStartMission(agent_hosts[2], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 1, "cwc_dummy_mission")
    safeStartMission(agent_hosts[3], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 2, "cwc_dummy_mission")

    safeWaitForStart(agent_hosts)

    timed_out = False

    while not timed_out:
        for i in range(2):
            ah = agent_hosts[i]
            world_state = ah.getWorldState()

            if not world_state.is_mission_running:
                timed_out = True

            elif i == 0 and world_state.number_of_observations_since_last_state > 0:
                all_world_states = processObservations(all_world_states, world_state.observations)

        time.sleep(1)

    print
    print "Postprocessing world states...\n",
    string_to_write = postprocess(all_world_states)

    # for ws in all_world_states:
    #     prettyPrintJson(ws)

    # write data
    experiment_log = "logs/"+experiment_id

    print
    print "Writing collected data to:", experiment_log,

    # FIXME: Parameterize all of these magic strings

    if not os.path.isdir("logs/"):
        os.makedirs("logs/")

    if not os.path.isdir(experiment_log):
        os.makedirs(experiment_log)

    # human readable log
    txt_log = open(experiment_log+"/log.txt", "w")
    txt_log.write(string_to_write)
    txt_log.close()

    time_elapsed = time.time()-start_time

    # machine readable log -- unalinged
    obs_data_dict = {"WorldStates": all_world_states, "TimeElapsed": time_elapsed}
    with open(experiment_log+"/observations.json", "w") as json_log:
        json.dump(obs_data_dict, json_log)

    m, s = divmod(time_elapsed, 60)
    h, m = divmod(m, 60)
    print "Done! Mission time elapsed: %d:%02d:%02d (%.2fs)" % (h, m, s, time_elapsed)
    print

    print "Waiting for mission to end..."
    # Mission should have ended already, but we want to wait until all the various agent hosts
    # have had a chance to respond to their mission ended message.
    hasEnded = False
    while not hasEnded:
        hasEnded = True # assume all good
        sys.stdout.write('.')
        time.sleep(0.1)
        for ah in agent_hosts[0:2]:
            world_state = ah.getWorldState()
            if world_state.is_mission_running:
                hasEnded = False # all not good

    print "Mission ended"
    # Mission has ended.

    time.sleep(2)
