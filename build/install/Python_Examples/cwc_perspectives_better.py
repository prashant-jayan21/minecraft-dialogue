# Prototype:

# Simple mission - two humans - w/ abilities to chat and build block structures

# Need to enable flying for builder and architect manually

# Architect is in control -- decides when who follows whom

# Builder starts following architect everywhere , i.e., both pos (x, y, z) and
# dir (yaw, pitch) coordinates of the builder are the same as the architect
# except a delta diff between their x pos coodinates (the diff being 1) [CASE 1]

# To "allow" the builder to go build something and stop following the architect,
# the architect needs to send a chat saying "START".

# Then the architect starts following the builder everywhere (meaning the same
# as in the reverse case above but the diff being -1) [CASE 2]

# To revert back the architect needs to say "STOP". THis will bring us back to
# CASE 1.

# "START" and "STOP" are thus kind of reserved keywords in our dialog.
# Case sensitive.

# FIXME: The weird seemingly random "IndexError: list index out of range" errors
# TODO: Currently we need to keep enabling flying for builder and architect manually and from time-to-time. Should change.

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

def teleportAgentToOtherAgent(other_agent_stats, agent_host):
    # obtain individual pos and dir coordinates for other agent
    other_agent_x = other_agent_stats.get(u"x")
    other_agent_y = other_agent_stats.get(u"y")
    other_agent_z = other_agent_stats.get(u"z")
    other_agent_yaw = other_agent_stats.get(u"yaw")
    other_agent_pitch = other_agent_stats.get(u"pitch")

    # teleport agent there
    teleport_command_1 = "tp " + str(other_agent_x-1) + " " + str(other_agent_y)+ " " + str(other_agent_z)
    teleport_command_2 = "setYaw " + str(other_agent_yaw)
    teleport_command_3 = "setPitch " + str(other_agent_pitch)
    agent_host.sendCommand(teleport_command_1)
    agent_host.sendCommand(teleport_command_2)
    agent_host.sendCommand(teleport_command_3)


# Create one agent host for parsing:
agent_hosts = [MalmoPython.AgentHost()]

try:
    agent_hosts[0].parse( sys.argv )
except RuntimeError as e:
    print('ERROR:',e)
    print(agent_hosts[0].getUsage())
    exit(1)
if agent_hosts[0].receivedArgument("help"):
    print(agent_hosts[0].getUsage())
    exit(0)

agent_hosts[0].setObservationsPolicy(MalmoPython.ObservationsPolicy.KEEP_ALL_OBSERVATIONS)

# Create the other agent host
agent_hosts += [MalmoPython.AgentHost()]

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

# Set up a client pool
client_pool = MalmoPython.ClientPool()
client_pool.add( MalmoPython.ClientInfo('127.0.0.1', 10000) )
client_pool.add( MalmoPython.ClientInfo('127.0.0.1', 10001) )

# Create mission xml
missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

              <About>
                <Summary>CWC Prototype 4</Summary>
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
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>

              <AgentSection mode="Survival">
                <Name>Builder</Name>
                <AgentStart>
                  <Placement x = "0" y = "1" z = "0"/>
                </AgentStart>
                <AgentHandlers>
                    <ObservationFromNearbyEntities>
                        <Range name="builder_range" xrange="20" yrange="20" zrange="20" update_frequency="20"/>
                    </ObservationFromNearbyEntities>
                    <AbsoluteMovementCommands/>
                    <ObservationFromChat/>
                </AgentHandlers>
              </AgentSection>

              <AgentSection mode="Survival">
                <Name>Architect</Name>
                <AgentStart>
                  <Placement x = "1" y = "1" z = "0"/>
                </AgentStart>
                <AgentHandlers>
                    <ObservationFromNearbyEntities>
                        <Range name="architect_range" xrange="20" yrange="20" zrange="20" update_frequency="20"/>
                    </ObservationFromNearbyEntities>
                    <AbsoluteMovementCommands/>
                    <ObservationFromChat/>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''

my_mission = MalmoPython.MissionSpec(missionXML, True)

safeStartMission(agent_hosts[0], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 0, "cwc_dummy_mission")
safeStartMission(agent_hosts[1], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 1, "cwc_dummy_mission")

safeWaitForStart(agent_hosts)

time.sleep(1)

timed_out = False

builder_freedom = False # controls state of builder as free-to-roam-and-build or follow-architect
architect_freedom = True # controls state of architect as free-to-roam-and-instruct or follow-builder
while not timed_out:
    for i in range(2):
        ah = agent_hosts[i]
        world_state = ah.getWorldState()

        if world_state.is_mission_running == False:
            timed_out = True

        if world_state.is_mission_running and world_state.number_of_observations_since_last_state > 0:

            chat_observations = list(filter(lambda x: json.loads(x.text).get(u"Chat", 0) != 0, world_state.observations))
            if len(chat_observations) != 0: # process chat, set freedom states
                chat_msg = json.loads(chat_observations[0].text).get(u"Chat", 0)[0]
                if chat_msg == "<Architect> START":
                    builder_freedom = True
                    architect_freedom = False
                elif chat_msg == "<Architect> STOP":
                    builder_freedom = False
                    architect_freedom = True

            if i == 1: # architect
                if architect_freedom == False:
                    # follow builder
                    architect_range_observations = list(filter(lambda x: json.loads(x.text).get(u"architect_range", 0) != 0, world_state.observations))
                    # print architect_range_observations[0].text -- does this prevent the occassional crash in the following line! WTH!
                    builder_stats = json.loads(architect_range_observations[0].text).get(u"architect_range", 0)[1] # FIXME: "IndexError: list index out of range" # TODO: assumes builder is always in range (pattern repeats elsewhere too)
                    teleportAgentToOtherAgent(builder_stats, ah) # TODO: follow iff builder's stats have changed (pattern repeats elsewhere too) -- might stop the slight tremor in builder?

            if i == 0: # builder
                if builder_freedom == False:
                    # follow architect
                    builder_range_observations = list(filter(lambda x: json.loads(x.text).get(u"builder_range", 0) != 0, world_state.observations))
                    architect_stats = json.loads(builder_range_observations[0].text).get(u"builder_range", 0)[1]
                    teleportAgentToOtherAgent(architect_stats, ah)

    time.sleep(1)

print()

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
