# Prototype:
# Two humans - w/ abilities to chat and build block structures
# Record all observations

import os, sys, time, json, datetime, copy
import MalmoPython, numpy as np
import cwc_mission_utils as mission_utils, cwc_debug_utils as debug_utils, cwc_io_utils as io_utils

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

fv_placements = ['<Placement x = "0" y = "8" z = "-8" pitch="40"/>', 
                 '<Placement x = "0" y = "8" z = "10" pitch="40" yaw="180"/>', 
                 '<Placement x = "10" y = "8" z = "0" pitch="40" yaw="90"/>', 
                 '<Placement x = "-10" y = "8" z = "0" pitch="40" yaw="-90"/>']

def addFixedViewers(n):
    fvs = ''
    for i in range(n):
        fvs += '''<AgentSection mode="Spectator"> 
                    <Name>FixedViewer'''+str(i+1)+'''</Name> 
                    <AgentStart> 
                      ''' + fv_placements[i] + '''
                      </AgentStart> 
                    <AgentHandlers/> 
                  </AgentSection>
                '''
    return fvs

def generateMissionXML(experiment_id, existing_config_xml_substring, num_fixed_viewers):
    return '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
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
                      <FlatWorldGenerator generatorString="3;247;1;" forceReset="true" destroyAfterUse="true"/>
                      <DrawingDecorator>
                        <DrawCuboid type="cwcmod:cwc_minecraft_orange_rn" x1="5" y1="1" z1="7" x2="1" y2="2" z2="8"/>
                        <DrawCuboid type="cwcmod:cwc_minecraft_yellow_rn" x1="-1" y1="1" z1="7" x2="-5" y2="2" z2="8"/>
                        <DrawCuboid type="cwcmod:cwc_minecraft_green_rn" x1="7" y1="1" z1="6" x2="8" y2="2" z2="2"/>
                        <DrawCuboid type="cwcmod:cwc_minecraft_blue_rn" x1="7" y1="1" z1="0" x2="8" y2="2" z2="-4"/>
                        <DrawCuboid type="cwcmod:cwc_minecraft_purple_rn" x1="-7" y1="1" z1="6" x2="-8" y2="2" z2="2"/>
                        <DrawCuboid type="cwcmod:cwc_minecraft_red_rn" x1="-7" y1="1" z1="0" x2="-8" y2="2" z2="-4"/>
                        <DrawCuboid type="cwcmod:cwc_unbreakable_white_rn" x1="''' + str(x_min_build) +'''" y1="0" z1="''' + str(z_min_build)+ '''" x2="'''+ str(x_max_build)+'''" y2="0" z2="''' + str(z_max_build) + '''"/>
                        ''' + existing_config_xml_substring + '''
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
                      <Placement x = "0" y = "5" z = "-6" pitch="45"/>
                    </AgentStart>
                    <AgentHandlers/>
                  </AgentSection>

                  '''+addFixedViewers(num_fixed_viewers)+'''
                </Mission>'''

def generateOracleXML(experiment_id, gold_config_xml_substring):
    return '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
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
                      <FlatWorldGenerator generatorString="3;247;1;" forceReset="true" destroyAfterUse="true"/>
                      <DrawingDecorator>
                        <DrawCuboid type="cwcmod:cwc_unbreakable_white_rn" x1="''' + str(x_min_goal) +'''" y1="0" z1="''' + str(z_min_goal)+ '''" x2="'''+ str(x_max_goal)+'''" y2="0" z2="''' + str(z_max_goal) + '''"/>''' + gold_config_xml_substring + \
                      '''</DrawingDecorator>
                      <ServerQuitWhenAnyAgentFinishes/>
                    </ServerHandlers>
                  </ServerSection>

                  <AgentSection mode="Spectator">
                    <Name>Oracle</Name>
                    <AgentStart>
                      <Placement x = "100" y = "5" z = "94" pitch="45"/>
                    </AgentStart>
                    <AgentHandlers/>
                  </AgentSection>
                </Mission>'''

def cwc_run_mission(args):
    print "Calling cwc_run_mission with args:", args, "\n"
    start_time = time.time()

    builder_ip, builder_port = args["builder_ip_addr"], args["builder_port"]
    architect_ip, architect_port = args["architect_ip_addr"], args["architect_port"]
    fixed_viewer_ip, fixed_viewer_port, num_fixed_viewers = args["fixed_viewer_ip_addr"], args["fixed_viewer_port"], args["num_fixed_viewers"]

    # Create agent hosts:
    agent_hosts = []
    for i in range(3+num_fixed_viewers):
        agent_hosts.append(MalmoPython.AgentHost())

    # Set observation policy for builder
    agent_hosts[1].setObservationsPolicy(MalmoPython.ObservationsPolicy.KEEP_ALL_OBSERVATIONS)

    # Set up a client pool
    client_pool = MalmoPython.ClientPool()

    if not args["lan"]:
        print "Starting in local mode."
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10000))
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10001))
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10002))

        for i in range(num_fixed_viewers):
            client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10003+i))
    else:
        print ("Builder IP: "+builder_ip), "\tPort:", builder_port
        print "Architect IP:", architect_ip, "\tPort:", architect_port
        print "FixedViewer IP:", fixed_viewer_ip, "\tPort:", fixed_viewer_port, "\tNumber of clients:", num_fixed_viewers, "\n"

        client_pool.add(MalmoPython.ClientInfo(architect_ip, architect_port+1))
        client_pool.add(MalmoPython.ClientInfo(builder_ip, builder_port))
        client_pool.add(MalmoPython.ClientInfo(architect_ip, architect_port))

        for i in range(num_fixed_viewers):
            client_pool.add(MalmoPython.ClientInfo(fixed_viewer_ip, fixed_viewer_port+i))

    # experiment ID
    player_ids = "B"+args["builder_id"] + "-A" + args["architect_id"]
    config_id = os.path.basename(args["gold_config"]).replace(".xml","")
    experiment_time = str(int(round(time.time()*1000)))
    experiment_id = player_ids + "-" + config_id + "-" + experiment_time

    # obtain xml substrings
    gold_config_xml_substring = io_utils.readXMLSubstringFromFile(args["gold_config"])
    existing_config_xml_substring = io_utils.readXMLSubstringFromFile(args["existing_config"])

    # construct mission xml
    missionXML = generateMissionXML(experiment_id, existing_config_xml_substring, num_fixed_viewers)
    missionXML_oracle = generateOracleXML(experiment_id, gold_config_xml_substring)

    # oracle
    my_mission_oracle = MalmoPython.MissionSpec(missionXML_oracle, True)
    mission_utils.safeStartMission(agent_hosts[0], my_mission_oracle, client_pool, MalmoPython.MissionRecordSpec(), 0, "cwc_dummy_mission_oracle")
    
    # builder, architect
    my_mission = MalmoPython.MissionSpec(missionXML, True)
    mission_utils.safeStartMission(agent_hosts[1], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 0, "cwc_dummy_mission")
    mission_utils.safeStartMission(agent_hosts[2], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 1, "cwc_dummy_mission")

    # fixed viewers
    for i in range(num_fixed_viewers):
        mission_utils.safeStartMission(agent_hosts[3+i], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 2+i, "cwc_dummy_mission")

    mission_utils.safeWaitForStart(agent_hosts)

    # poll for observations
    timed_out = False
    all_observations = []
    while not timed_out:
        for i in range(3+num_fixed_viewers):
            ah = agent_hosts[i]
            world_state = ah.getWorldState()

            if not world_state.is_mission_running:
                timed_out = True

            elif i == 1 and world_state.number_of_observations_since_last_state > 0:
                total_elements = 0
                for observation in world_state.observations:
                    total_elements += len(json.loads(observation.text))

                print "Received", len(world_state.observations), "observations. Total number of elements:", total_elements
                for observation in world_state.observations:
                    print "Processing observation:", 
                    debug_utils.prettyPrintObservation(json.loads(observation.text))
                    all_observations.append(observation)

                print "-----"

        time.sleep(1)

    time_elapsed = time.time()-start_time

    print "Mission has been quit. All world states:\n"

    all_world_states = []
    for observation in all_observations:
        world_state = json.loads(observation.text)
        world_state["Timestamp"] = observation.timestamp.replace(microsecond=0).isoformat(' ')
        debug_utils.prettyPrintWorldState(world_state)
        all_world_states.append(world_state)

    raw_observations = {"WorldStates": all_world_states, "TimeElapsed": time_elapsed}
    io_utils.writeJSONtoLog(experiment_id, "raw-observations.json", raw_observations)

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
        for ah in agent_hosts[1:3]:
            world_state = ah.getWorldState()
            if world_state.is_mission_running:
                hasEnded = False # all not good

    print "Mission ended"
    # Mission has ended.

    time.sleep(2)
