# Prototype:
# Run simple mission using raw XML
# Two humans
# Chat with one another
# Obtain world state representations
# Write to file

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

try:
    agent_hosts[0].parse( sys.argv )
except RuntimeError as e:
    print('ERROR:',e)
    print(agent_hosts[0].getUsage())
    exit(1)
if agent_hosts[0].receivedArgument("help"):
    print(agent_hosts[0].getUsage())
    exit(0)

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
                <Summary>CWC Prototype 3</Summary>
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
                  <Placement x = "0" y = "10" z = "10"/>
                </AgentStart>
                <AgentHandlers>
                  <ObservationFromChat/>
                  <ObservationFromGrid>
                    <Grid name="big_grid" absoluteCoords="false">
                      <min x="-5" y="-5" z="-5"/>
                      <max x="5" y="5" z="5"/>
                    </Grid>
                  </ObservationFromGrid>
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
                </AgentHandlers>
              </AgentSection>

              <AgentSection mode="Survival">
                <Name>Instructor</Name>
                <AgentStart>
                  <Placement x = "0" y = "10" z = "0"/>
                </AgentStart>
                <AgentHandlers>
                  <ObservationFromChat/>
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''

my_mission = MalmoPython.MissionSpec(missionXML, True)
# my_mission_record = MalmoPython.MissionRecordSpec("cwc_prototype_2_data.tgz")
# my_mission_record.recordObservations()

safeStartMission(agent_hosts[0], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 0, "cwc_dummy_mission")
safeStartMission(agent_hosts[1], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 1, "cwc_dummy_mission")

safeWaitForStart(agent_hosts)

time.sleep(1)

timed_out = False

prev_blocks_state = []
while not timed_out:
    for i in range(2):
        ah = agent_hosts[i]
        world_state = ah.getWorldState()
        if world_state.is_mission_running == False:
            timed_out = True
        if i == 0 and world_state.is_mission_running and world_state.number_of_observations_since_last_state > 0:
            msg_timestamp = world_state.observations[-1].timestamp
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            # print "observation from agent " + str(i)
            # print ob
            grid = ob.get(u'big_grid', 0)
            current_blocks_state = list(filter(lambda x: x != "air" and x != "grass" and x != "dirt" and x != "bedrock" and x != "cwc_unbreakable_grey_rn", grid))
            if current_blocks_state != prev_blocks_state:
                print "\n"
                print msg_timestamp
                print current_blocks_state
                prev_blocks_state = current_blocks_state
            # chat = ob.get(u'Chat', 0)

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
