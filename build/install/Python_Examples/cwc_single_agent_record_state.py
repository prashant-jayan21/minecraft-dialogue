# Prototype:
# Run simple mission using raw XML
# One human
# Performs a task (build some simple structure using blocks)
# Obtain world state representations
# Write to file

import MalmoPython
import os
import sys
import time
import json

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

              <About>
                <Summary>CWC Prototype 1</Summary>
              </About>

              <ServerSection>
                <ServerHandlers>
                  <FlatWorldGenerator generatorString="3;7;1;"/>
                  <ServerQuitFromTimeUp timeLimitMs="180000"/>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>

              <AgentSection mode="Creative">
                <Name>CWCDummyBot</Name>
                <AgentStart/>
                <AgentHandlers>
                  <ObservationFromGrid>
                    <Grid name="big_grid" absoluteCoords="false">
                      <min x="-20" y="-20" z="-20"/>
                      <max x="20" y="20" z="20"/>
                    </Grid>
                  </ObservationFromGrid>
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''

                #   <ObservationFromNearbyEntities>
                #     <Range name="test_range" xrange="5.0" yrange="5.0" zrange="5.0" update_frequency="20"/>
                #   </ObservationFromNearbyEntities>

# Create default Malmo objects:

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print 'ERROR:',e
    print agent_host.getUsage()
    exit(1)
if agent_host.receivedArgument("help"):
    print agent_host.getUsage()
    exit(0)

my_mission = MalmoPython.MissionSpec(missionXML, True)
my_mission_record = MalmoPython.MissionRecordSpec("cwc_prototype_1_data.tgz")
my_mission_record.recordObservations()

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        agent_host.startMission( my_mission, my_mission_record )
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print "Error starting mission:",e
            exit(1)
        else:
            time.sleep(2)

# Loop until mission starts:
print "Waiting for the mission to start ",
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    sys.stdout.write(".")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print "Error:",error.text

print
print "Mission running ",

# Loop until mission ends:
while world_state.is_mission_running:
    sys.stdout.write(".")
    time.sleep(1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print "Error:",error.text
    if world_state.number_of_observations_since_last_state > 0: # Have any observations come in?
        msg = world_state.observations[-1].text                 # Yes, so get the text
        observation = json.loads(msg)                          # and parse the JSON
        grid = observation.get(u'big_grid', 0)                 # and get the grid we asked for
        print list(filter(lambda x: x != "air" and x != "bedrock", grid))


print
print "Mission ended"
# Mission has ended.
