# Prototype:
# Two humans - w/ abilities to chat and build block structures
# Record all observations

import MalmoPython
import os
import sys
import time
import json

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
    print()
    print("Mission has started.")

# Create one agent host for parsing:
agent_hosts = [MalmoPython.AgentHost()]

# try:
#     agent_hosts[0].parse( sys.argv )
# except RuntimeError as e:
#     print('ERROR:',e)
#     print(agent_hosts[0].getUsage())
#     exit(1)
# if agent_hosts[0].receivedArgument("help"):
#     print(agent_hosts[0].getUsage())
#     exit(0)

# Set observation policy
agent_hosts[0].setObservationsPolicy(MalmoPython.ObservationsPolicy.KEEP_ALL_OBSERVATIONS)

# Create the other agent host
agent_hosts += [MalmoPython.AgentHost()]

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
lan = False

if len(sys.argv) > 1 and sys.argv[1].lower() == 'lan':
	lan = True

# Set up a client pool
client_pool = MalmoPython.ClientPool()

if not lan:
	client_pool.add( MalmoPython.ClientInfo('127.0.0.1', 10000) )
	client_pool.add( MalmoPython.ClientInfo('127.0.0.1', 10001) )

else:
	client_pool.add( MalmoPython.ClientInfo('10.192.95.32', 10000) )
	client_pool.add( MalmoPython.ClientInfo('10.195.220.132', 10000) )

# Create mission xml
missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

              <About>
                <Summary>CWC Prototype</Summary>
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
                  <FlatWorldGenerator generatorString="3;241;1;"/>
                  <DrawingDecorator>
                    <DrawCuboid type="cwcmod:cwc_orange_rn" x1="5" y1="1" z1="8" x2="1" y2="1" z2="8"/>
                    <DrawCuboid type="cwcmod:cwc_yellow_rn" x1="-1" y1="1" z1="8" x2="-5" y2="1" z2="8"/>
                    <DrawCuboid type="cwcmod:cwc_green_rn" x1="8" y1="1" z1="6" x2="8" y2="1" z2="2"/>
                    <DrawCuboid type="cwcmod:cwc_blue_rn" x1="8" y1="1" z1="0" x2="8" y2="1" z2="-4"/>
                    <DrawCuboid type="cwcmod:cwc_purple_rn" x1="-8" y1="1" z1="6" x2="-8" y2="1" z2="2"/>
                    <DrawCuboid type="cwcmod:cwc_red_rn" x1="-8" y1="1" z1="0" x2="-8" y2="1" z2="-4"/>
                    <DrawCuboid type="cwcmod:cwc_unbreakable_white_rn" x1="-5" y1="0" z1="-5" x2="5" y2="0" z2="5"/>
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
                  <ObservationFromFullStats/>
                   <ObservationFromGrid>
                     <Grid name="builder_grid" absoluteCoords="true">
                       <min x="-5" y="1" z="-5"/>
                       <max x="5" y="14" z="5"/>
                     </Grid>
                   </ObservationFromGrid>
                   <ObservationFromChat/>
                   <ObservationFromHotBar/>
                </AgentHandlers>
              </AgentSection>

              <AgentSection mode="Spectator">
                <Name>Architect</Name>
                <AgentStart>
                  <Placement x = "0" y = "1" z = "-5"/>
                </AgentStart>
                <AgentHandlers/>
              </AgentSection>
            </Mission>'''

my_mission = MalmoPython.MissionSpec(missionXML, True)

safeStartMission(agent_hosts[0], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 0, "cwc_dummy_mission")
safeStartMission(agent_hosts[1], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 1, "cwc_dummy_mission")

safeWaitForStart(agent_hosts)

time.sleep(1)

timed_out = False

import numpy as np

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

def getFullHotbar(observation_json):
    hotbar_0_size = observation_json.get(u'Hotbar_0_size', 0)
    hotbar_0_item = observation_json.get(u'Hotbar_0_item', 0)

    hotbar_1_size = observation_json.get(u'Hotbar_1_size', 0)
    hotbar_1_item = observation_json.get(u'Hotbar_1_item', 0)

    hotbar_2_size = observation_json.get(u'Hotbar_2_size', 0)
    hotbar_2_item = observation_json.get(u'Hotbar_2_item', 0)

    hotbar_3_size = observation_json.get(u'Hotbar_3_size', 0)
    hotbar_3_item = observation_json.get(u'Hotbar_3_item', 0)

    hotbar_4_size = observation_json.get(u'Hotbar_4_size', 0)
    hotbar_4_item = observation_json.get(u'Hotbar_4_item', 0)

    hotbar_5_size = observation_json.get(u'Hotbar_5_size', 0)
    hotbar_5_item = observation_json.get(u'Hotbar_5_item', 0)

    hotbar_6_size = observation_json.get(u'Hotbar_6_size', 0)
    hotbar_6_item = observation_json.get(u'Hotbar_6_item', 0)

    hotbar_7_size = observation_json.get(u'Hotbar_7_size', 0)
    hotbar_7_item = observation_json.get(u'Hotbar_7_item', 0)

    hotbar_8_size = observation_json.get(u'Hotbar_8_size', 0)
    hotbar_8_item = observation_json.get(u'Hotbar_8_item', 0)

    hotbar_0 = (hotbar_0_item, hotbar_0_size)
    hotbar_1 = (hotbar_1_item, hotbar_1_size)
    hotbar_2 = (hotbar_2_item, hotbar_2_size)
    hotbar_3 = (hotbar_3_item, hotbar_3_size)
    hotbar_4 = (hotbar_4_item, hotbar_4_size)
    hotbar_5 = (hotbar_5_item, hotbar_5_size)
    hotbar_6 = (hotbar_6_item, hotbar_6_size)
    hotbar_7 = (hotbar_7_item, hotbar_7_size)
    hotbar_8 = (hotbar_8_item, hotbar_8_size)

    hotbar_full = [hotbar_0, hotbar_1, hotbar_2, hotbar_3, hotbar_4, hotbar_5, hotbar_6, hotbar_7, hotbar_8]

    hotbar_full = list(filter(lambda x: x[0] != "air", hotbar_full))

    return hotbar_full

def processObservation(observation, prev_blocks_state_abs, prev_dialog_state, prev_game_state, prev_hotbar_state, string_to_write):
    msg_timestamp = observation.timestamp
    msg = observation.text
    json_obj = json.loads(msg)
    # print "-"*20
    # print json_obj
    # print "-"*20
    builder_grid_rel = json_obj.get(u'builder_grid_block_info_relative', 0)
    current_blocks_state_rel = list(filter(lambda x: x["type"] != "air", builder_grid_rel))
    builder_grid_abs = json_obj.get(u'builder_grid_block_info', 0)
    current_blocks_state_abs = list(filter(lambda x: x["type"] != "air", builder_grid_abs))
    # # print "-"*20
    # # print msg_timestamp
    # # print current_blocks_state
    # # print "-"*20
    builder_yaw = json_obj.get(u'Yaw', 0)
    builder_pitch = json_obj.get(u'Pitch', 0)
    builder_x_pos = json_obj.get(u'XPos', 0)
    builder_y_pos = json_obj.get(u'YPos', 0)
    builder_z_pos = json_obj.get(u'ZPos', 0)
    # # print yaw
    # # print pitch
    chat_observation = json_obj.get(u'Chat', [])
    current_game_state = json_obj.get(u'GameState', 0)
    current_hotbar_state = getFullHotbar(json_obj)
    # world state dict
    current_world_state = {}
    if current_hotbar_state != prev_hotbar_state or current_blocks_state_abs != prev_blocks_state_abs or chat_observation != [] or current_game_state != prev_game_state:
        print
        print "-"*20
        print "[STATE]", current_game_state
        current_world_state["state"] = current_game_state

        print "[timestamp]", msg_timestamp
        print
        current_world_state["timestamp"] = msg_timestamp.isoformat()

        print "[builder absolute position] (x, y, z): " + str((builder_x_pos, builder_y_pos, builder_z_pos)), "(yaw, pitch): " + str((builder_yaw, builder_pitch))
        print
        builder_position_absolute = {"x": builder_x_pos, "y": builder_y_pos, "z": builder_z_pos, "yaw": builder_yaw, "pitch": builder_pitch}
        current_world_state["builder_position_absolute"] = builder_position_absolute # TODO: there will be some rounding when encoded to json

        string_to_write += "\n" + "-"*20 + "\n" + "[STATE]" + " " + str(current_game_state) + "\n" + "[timestamp]" + " " + str(msg_timestamp) \
        + "\n" + "\n" + "[builder absolute position] (x, y, z): " + str((builder_x_pos, builder_y_pos, builder_z_pos)) + " " + \
        "(yaw, pitch): " + str((builder_yaw, builder_pitch)) + "\n" + "\n"

        print
        print "[hotbar]"
        string_to_write += "\n" + "[hotbar]" + "\n"

        for hotbar_slot in current_hotbar_state:
            print hotbar_slot
            string_to_write += str(hotbar_slot) + "\n"

        current_world_state["hotbar"] = current_hotbar_state
        prev_hotbar_state = current_hotbar_state

        blocks = []

        for i in range(len(current_blocks_state_rel)):
            block_rel = current_blocks_state_rel[i]
            block_abs = current_blocks_state_abs[i]
            perspective_coords = getPerspectiveCoordinates(block_rel["x"], block_rel["y"], block_rel["z"], builder_yaw, builder_pitch)
            absolute_coords = (block_abs["x"], block_abs["y"], block_abs["z"])
            print "["+block_rel["type"]+"]", "absolute coordinates:", absolute_coords, " | perspective coordinates:", perspective_coords
            coordinates_absolute = {
                "x": absolute_coords[0],
                "y": absolute_coords[1],
                "z": absolute_coords[2]
            }
            coordinates_perspective = {
                "x": perspective_coords[0],
                "y": perspective_coords[1],
                "z": perspective_coords[2]
            }
            block_info = {
                "type": block_rel["type"],
                "coordinates_absolute": coordinates_absolute,
                "coordinates_perspective": coordinates_perspective
            }
            blocks.append(block_info)
            string_to_write += "[" + str(block_rel["type"]) + "]" + " "+ "absolute coordinates:" + " " +  str(absolute_coords) + " " + " | perspective coordinates:" + " " + str(perspective_coords) + "\n"

        current_world_state["blocks"] = blocks

        prev_blocks_state_abs = current_blocks_state_abs
        current_dialog_state = prev_dialog_state + chat_observation

        print
        print "[chat]"
        string_to_write += "\n" + "[chat]" + "\n"

        utterances = []

        for utterance in current_dialog_state:
            print utterance
            utterances.append(utterance)
            string_to_write += str(utterance) + "\n"

        current_world_state["utterances"] = utterances

        prev_dialog_state = current_dialog_state
        prev_game_state = current_game_state

        print "-"*20
        string_to_write += "-"*20 + "\n"

    return (prev_blocks_state_abs, prev_dialog_state, prev_game_state, prev_hotbar_state, string_to_write, current_world_state)

prev_blocks_state_abs = []
prev_dialog_state = []
prev_game_state = ""
prev_hotbar_state = []

string_to_write = ""
all_world_states = []

while not timed_out:

    for i in range(2):

        ah = agent_hosts[i]
        world_state = ah.getWorldState()

        if world_state.is_mission_running == False:
            timed_out = True

        if i == 0 and world_state.is_mission_running and world_state.number_of_observations_since_last_state > 0:
            for observation in world_state.observations:
                (prev_blocks_state_abs, prev_dialog_state, prev_game_state, prev_hotbar_state, string_to_write, world_state) = processObservation(observation, prev_blocks_state_abs, prev_dialog_state, prev_game_state, prev_hotbar_state, string_to_write)
                if world_state:
                    all_world_states.append(world_state)

    time.sleep(1)

print
print "Writing collected data to file..."

architect_name = "anjali"
builder_name = "prashant"
trial_num = 1
file_name = "cwc_pilot_" + architect_name + "_" + builder_name + "_" + str(trial_num)

file = open(file_name + ".txt", "w")
file.write(string_to_write)
file.close()

data_dict = {"all_world_states": all_world_states}
with open(file_name + ".json", "w") as jsonfile:
    json.dump(data_dict, jsonfile)

print "Done!"
print

print "Waiting for mission to end..."
# Mission should have ended already, but we want to wait until all the various agent hosts
# have had a chance to respond to their mission ended message.
hasEnded = False
while not hasEnded:
    hasEnded = True # assume all good
    sys.stdout.write('.')
    time.sleep(0.1)
    for ah in agent_hosts:
        world_state = ah.getWorldState()
        if world_state.is_mission_running:
            hasEnded = False # all not good

print "Mission ended"
# Mission has ended.

time.sleep(2)
