# Prototype:
# Two humans - w/ abilities to chat and build block structures
# Record all observations

import MalmoPython
import os
import sys
import time
import json
from cwc_aligner import align

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

# observation grid parameters
x_min_obs = -10
x_max_obs = 10
y_min_obs = 1
y_max_obs = 16
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
                  <ObservationFromFullStats/>
                   <ObservationFromGrid>
                     <Grid name="builder_grid" absoluteCoords="true">
                       <min x="'''+ str(x_min_obs) + '''" y="'''+ str(y_min_obs) + '''" z="''' + str(z_min_obs) + '''"/>
                       <max x="'''+ str(x_max_obs) + '''" y="''' + str(y_max_obs) + '''" z="''' + str(z_max_obs) + '''"/>
                     </Grid>
                   </ObservationFromGrid>
                   <ObservationFromChat/>
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

def processObservation(observation, prev_blocks_state_abs, prev_dialog_state, prev_game_state, string_to_write):
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
    # world state dict
    current_world_state = {}
    if current_blocks_state_abs != prev_blocks_state_abs or chat_observation != [] or current_game_state != prev_game_state:
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

        blocks_outside = []
        blocks_inside = []

        for i in range(len(current_blocks_state_rel)):

            block_rel = current_blocks_state_rel[i]
            block_abs = current_blocks_state_abs[i]

            perspective_coords = getPerspectiveCoordinates(block_rel["x"], block_rel["y"], block_rel["z"], builder_yaw, builder_pitch)
            absolute_coords = (block_abs["x"], block_abs["y"], block_abs["z"])

            # check if the block is inside or outside the build region
            x = absolute_coords[0]
            y = absolute_coords[1]
            z = absolute_coords[2]

            if x < x_min_build or x > x_max_build \
            or y < y_min_build or y > y_max_build \
            or z < z_min_build or z > z_max_build:
                # outside
                outside = True
            else:
                # inside
                outside = False

            print "["+block_rel["type"]+"]", "outside:", outside, "absolute coordinates:", absolute_coords, " | perspective coordinates:", perspective_coords

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
            if outside:
                blocks_outside.append(block_info)
            else:
                blocks_inside.append(block_info)

            string_to_write += "[" + str(block_rel["type"]) + "]" + " "+  "outside: " + str(outside) + " " + "absolute coordinates:" + " " +  str(absolute_coords) + " " + " | perspective coordinates:" + " " + str(perspective_coords) + "\n"

        current_world_state["blocks_inventory"] = blocks_outside
        current_world_state["blocks_structure"] = blocks_inside

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


    return (prev_blocks_state_abs, prev_dialog_state, prev_game_state, string_to_write, current_world_state)

prev_blocks_state_abs = []
prev_dialog_state = []
prev_game_state = ""

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
                (prev_blocks_state_abs, prev_dialog_state, prev_game_state, string_to_write, world_state) = processObservation(observation, prev_blocks_state_abs, prev_dialog_state, prev_game_state, string_to_write)
                if world_state:
                    all_world_states.append(world_state)

    time.sleep(1)

# write data
print
print "Writing collected data to files..."

# FIXME: Parameterize all of these magic strings

architect_name = "anjali"
builder_name = "prashant"
trial_num = 1
obs_file_name = "cwc_pilot_" + architect_name + "_" + builder_name + "_" + str(trial_num) # for the json data files

screenshots_dir = "/Users/prashant/Work/cwc-minecraft/Minecraft/run/screenshots/" # the screenshots dir populated on the mod side

# human readable log
file = open(obs_file_name + ".txt", "w")
file.write(string_to_write)
file.close()

# machine readable log -- unalinged
obs_data_dict = {"all_world_states": all_world_states}
with open(obs_file_name + ".json", "w") as jsonfile:
    json.dump(obs_data_dict, jsonfile)

# machine readable log -- aligned w/ screenshots
obs_data_dict_aligned = align(obs_data_dict, screenshots_dir)
with open(obs_file_name + "_aligned" + ".json", "w") as jsonfile:
    json.dump(obs_data_dict_aligned, jsonfile)

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
