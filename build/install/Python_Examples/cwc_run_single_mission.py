# Prototype:
# Two humans - w/ abilities to chat and build block structures
# Record all observations

import os
import sys
import time
import json
import datetime
import copy
import MalmoPython
import numpy as np
import cwc_mission_utils as mission_utils
import cwc_debug_utils as debug_utils
import cwc_io_utils as io_utils
import cwc_planner_utils as planner_utils

# GLOBAL VARIABLES FOR DEBUGGING
SHOW_COMMANDS = True
N_SHAPES = 0
init_location = [(0, 0), (-5, 0), (0, -5), (-5, -5)]
color_map = {
    'red': 1,
    'orange': 2,
    'yellow': 3,
    'green': 4,
    'blue': 5,
    'purple': 6}


def addFixedViewers(n):
    fvs = ''
    for i in range(n):
        fvs += '''<AgentSection mode="Spectator">
                    <Name>FixedViewer''' + str(i + 1) + '''</Name>
                    <AgentStart>
                      ''' + mission_utils.fv_placements[i] + '''
                      </AgentStart>
                    <AgentHandlers/>
                  </AgentSection>
                '''
    return fvs


def drawInventoryBlocks():
    return '''
                <DrawCuboid type="cwcmod:cwc_minecraft_orange_rn" x1="5" y1="1" z1="7" x2="1" y2="2" z2="8"/>
                <DrawCuboid type="cwcmod:cwc_minecraft_yellow_rn" x1="-1" y1="1" z1="7" x2="-5" y2="2" z2="8"/>
                <DrawCuboid type="cwcmod:cwc_minecraft_green_rn" x1="7" y1="1" z1="6" x2="8" y2="2" z2="2"/>
                <DrawCuboid type="cwcmod:cwc_minecraft_blue_rn" x1="7" y1="1" z1="0" x2="8" y2="2" z2="-4"/>
                <DrawCuboid type="cwcmod:cwc_minecraft_purple_rn" x1="-7" y1="1" z1="6" x2="-8" y2="2" z2="2"/>
                 <DrawCuboid type="cwcmod:cwc_minecraft_red_rn" x1="-7" y1="1" z1="0" x2="-8" y2="2" z2="-4"/>
            '''


def generateMissionXML(experiment_id, existing_config_xml_substring,
                       num_fixed_viewers, draw_inventory_blocks):
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
                      <DrawingDecorator> ''' + ('' if not draw_inventory_blocks else drawInventoryBlocks()) + '''
                        <DrawCuboid type="cwcmod:cwc_unbreakable_white_rn" x1="''' + str(mission_utils.x_min_build) + '''" y1="0" z1="''' + \
        str(mission_utils.z_min_build) + '''" x2="''' + str(mission_utils.x_max_build) + '''" y2="0" z2="''' + str(mission_utils.z_max_build) + '''"/>
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
                      <ContinuousMovementCommands turnSpeedDegs="180"/>
                      <DiscreteMovementCommands/>
                      <AbsoluteMovementCommands/>
                      <InventoryCommands/>

                      <CwCObservation>
                         <Grid name="BuilderGrid" absoluteCoords="true">
                           <min x="''' + str(mission_utils.x_min_obs) + '''" y="''' + str(mission_utils.y_min_obs) + '''" z="''' + str(mission_utils.z_min_obs) + '''"/>
                           <max x="''' + str(mission_utils.x_max_obs) + '''" y="''' + str(mission_utils.y_max_obs) + '''" z="''' + str(mission_utils.z_max_obs) + '''"/>
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

                  ''' + addFixedViewers(num_fixed_viewers) + '''
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
                        <DrawCuboid type="cwcmod:cwc_unbreakable_white_rn" x1="''' + str(mission_utils.x_min_goal) + '''" y1="0" z1="''' + str(mission_utils.z_min_goal) + \
        '''" x2="''' + str(mission_utils.x_max_goal) + '''" y2="0" z2="''' + str(mission_utils.z_max_goal) + '''"/>''' + gold_config_xml_substring + \
        '''</DrawingDecorator>
                      <ServerQuitWhenAnyAgentFinishes/>
                    </ServerHandlers>
                  </ServerSection>

                  <AgentSection mode="Spectator">
                    <Name>Oracle</Name>
                    <AgentStart>
                      <Placement x = "100" y = "9" z = "93" pitch="45"/>
                    </AgentStart>
                    <AgentHandlers/>
                  </AgentSection>
                </Mission>'''


def cwc_run_mission(args):
    global N_SHAPES
    print "Calling cwc_run_mission with args:", args, "\n"
    start_time = time.time()

    builder_ip, builder_port = args["builder_ip_addr"], args["builder_port"]
    architect_ip, architect_port = args[
        "architect_ip_addr"], args["architect_port"]
    fixed_viewer_ip, fixed_viewer_port, num_fixed_viewers = args[
        "fixed_viewer_ip_addr"], args["fixed_viewer_port"], args["num_fixed_viewers"]

    draw_inventory_blocks = args["draw_inventory_blocks"]
    existing_is_gold = args["existing_is_gold"]

    # Create agent hosts:
    agent_hosts = []
    for i in range(3 + num_fixed_viewers):
        agent_hosts.append(MalmoPython.AgentHost())

    # Set observation policy for builder
    agent_hosts[1].setObservationsPolicy(
        MalmoPython.ObservationsPolicy.KEEP_ALL_OBSERVATIONS)

    # Set up a client pool
    client_pool = MalmoPython.ClientPool()

    if not args["lan"]:
        print "Starting in local mode."
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10000))
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10001))
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10002))

        for i in range(num_fixed_viewers):
            client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10003 + i))
    else:
        print("Builder IP: " + builder_ip), "\tPort:", builder_port
        print "Architect IP:", architect_ip, "\tPort:", architect_port
        print "FixedViewer IP:", fixed_viewer_ip, "\tPort:", fixed_viewer_port, "\tNumber of clients:", num_fixed_viewers, "\n"

        client_pool.add(
            MalmoPython.ClientInfo(
                architect_ip,
                architect_port + 1))
        client_pool.add(MalmoPython.ClientInfo(builder_ip, builder_port))
        client_pool.add(MalmoPython.ClientInfo(architect_ip, architect_port))

        for i in range(num_fixed_viewers):
            client_pool.add(
                MalmoPython.ClientInfo(
                    fixed_viewer_ip,
                    fixed_viewer_port + i))

    # experiment ID
    player_ids = "B" + args["builder_id"] + "-A" + args["architect_id"]
    config_id = os.path.basename(args["gold_config"]).replace(".xml", "")
    experiment_time = str(int(round(time.time() * 1000)))
    experiment_id = player_ids + "-" + config_id + "-" + experiment_time

    # obtain xml substrings
    gold_config_xml_substring = io_utils.readXMLSubstringFromFile(
        args["gold_config"], False)
    existing_config_xml_substring = io_utils.readXMLSubstringFromFile(
        args["existing_config"], existing_is_gold)

    # construct mission xml
    missionXML = generateMissionXML(
        experiment_id,
        existing_config_xml_substring,
        num_fixed_viewers,
        draw_inventory_blocks)
    missionXML_oracle = generateOracleXML(
        experiment_id, gold_config_xml_substring)

    # oracle
    my_mission_oracle = MalmoPython.MissionSpec(missionXML_oracle, True)
    mission_utils.safeStartMission(
        agent_hosts[0],
        my_mission_oracle,
        client_pool,
        MalmoPython.MissionRecordSpec(),
        0,
        "cwc_dummy_mission_oracle")

    # builder, architect
    my_mission = MalmoPython.MissionSpec(missionXML, True)
    my_mission.allowAllInventoryCommands()
    my_mission.allowAllDiscreteMovementCommands()
    my_mission.observeHotBar()
    # my_mission.allowInventoryCommand("swapInventoryItems")
    mission_utils.safeStartMission(
        agent_hosts[1],
        my_mission,
        client_pool,
        MalmoPython.MissionRecordSpec(),
        0,
        "cwc_dummy_mission")
    mission_utils.safeStartMission(
        agent_hosts[2],
        my_mission,
        client_pool,
        MalmoPython.MissionRecordSpec(),
        1,
        "cwc_dummy_mission")

    # fixed viewers
    for i in range(num_fixed_viewers):
        mission_utils.safeStartMission(
            agent_hosts[
                3 + i],
            my_mission,
            client_pool,
            MalmoPython.MissionRecordSpec(),
            2 + i,
            "cwc_dummy_mission")

    mission_utils.safeWaitForStart(agent_hosts)

    # poll for observations
    timed_out = False
    c = -1
    all_observations = []
    while not timed_out:
        for i in range(3 + num_fixed_viewers):
            ah = agent_hosts[i]
            world_state = ah.getWorldState()

            if not world_state.is_mission_running:
                timed_out = True
            elif i == 1 and world_state.number_of_observations_since_last_state > 0:
                total_elements = 0
                for observation in world_state.observations:
                    total_elements += len(json.loads(observation.text))
                # print "Received", len(world_state.observations), "observations. Total number of elements:", total_elements
                # print(json.loads(observation.text))
                for observation in world_state.observations:
                    # print "Processing observation:",
                    # debug_utils.printObservationElements(
                    #     json.loads(observation.text))
                    all_observations.append(observation)
                    if observation.text is not None:
                        # print("===========================")
                        # print("checking: ", observation.text)
                        # print("---------------------------")
                        obsrv = json.loads(observation.text)
                        chat_instruction = obsrv.get("Chat")
                        if chat_instruction is not None:
                            print("******************")
                            print(chat_instruction)
                            print("******************")
                        if chat_instruction is not None and 'place' in chat_instruction[
                                0]:
                            # semantic representation will be invoked here
                            sem_rep = chat_instruction[0].replace(
                                "<Architect> place ", "")
                            print(sem_rep)
                            print("#########chat received#########")
                            print(chat_instruction)

                            # sem_rep = "place row(a) ^ width(a, 4)"
                            # sem_rep = "rectangle(a) ^ height(a, 2) ^ width(a,3)"
                            if "and color" in sem_rep:
                                c = sem_rep.split("and color ")[1]
                                c = color_map[c]
                                sem_rep = sem_rep.split("and color")[0]
                                print("color ", c, " sem rep: ", sem_rep)

                            plan_list = planner_utils.getPlans(sem_rep)
                            print(plan_list)
                            # Communication Protocol Planner-NLG 1
                            if len(plan_list) == 0:
                                print("Planner fails to solve: Planner-NLG 1")
                                continue
                            seed_x, seed_y = init_location[N_SHAPES % 4]
                            for (x, y) in plan_list:
                                c_x = x
                                if y > 0:
                                    c_y = 4
                                    c_z = y
                                else:
                                    c_y = y
                                    c_z = 0

                                teleportMovement(
                                    agent_hosts[1],
                                    teleport_x=seed_x + c_x + 0.5,
                                    teleport_y=c_y,
                                    teleport_z=seed_y + c_z + 0.5)
                                print(c_x, c_z)
                                pickUpBlock(agent_hosts[1], index=c)
                                adjustView(agent_hosts[1])
                                world_state = ah.getWorldState()
                                print(json.loads(
                                    world_state.observations[-1].text))
                                useBlock(agent_hosts[1])
                                restoreView(agent_hosts[1])
                                useBlock(agent_hosts[1])
                            N_SHAPES += 1
                            c = -1
                            # teleportMovement(
                            #     agent_hosts[1],
                            #     teleport_x=0,
                            #     teleport_y=8,
                            #     teleport_z=5)
                            # agent_hosts[1].sendCommand("discardCurrentItem")
                            # for zidx in range(4, -6, -1):
                            #     for xidx in range(5, -6, -1):
                            #         teleportMovement(
                            #             agent_hosts[1],
                            #             teleport_x=xidx + 0.5,
                            #             teleport_z=zidx + 0.5)
                            #         print(xidx, zidx)
                            #         # time.sleep(2)
                            #         pickUpBlock(agent_hosts[1])
                            #         adjustView(agent_hosts[1])
                            #         useBlock(agent_hosts[1])
                            #         restoreView(agent_hosts[1])
                            #         useBlock(agent_hosts[1])
                            #         # time.sleep(2)
                            #         print("***********************")
                            #         ws = agent_hosts[1].getWorldState()
                            #         print(ws)
                            #         for obws in ws.observations:
                            #             print(obws)
                            #         print("***********************")
                        # else:
                        #     agent_hosts[1].sendCommand('movenorth 1')

                    # add the planner output

                # print "-----"

        # time.sleep(1)

    time_elapsed = time.time() - start_time

    print "Mission has been quit. All world states:\n"

    all_world_states = []
    for observation in all_observations:
        world_state = json.loads(observation.text)
        world_state["Timestamp"] = observation.timestamp.replace(
            microsecond=0).isoformat(' ')
        debug_utils.prettyPrintObservation(world_state)
        all_world_states.append(world_state)

    raw_observations = {
        "WorldStates": all_world_states,
        "TimeElapsed": time_elapsed,
        "NumFixedViewers": num_fixed_viewers}
    io_utils.writeJSONtoLog(
        experiment_id,
        "raw-observations.json",
        raw_observations)

    m, s = divmod(time_elapsed, 60)
    h, m = divmod(m, 60)
    print "Done! Mission time elapsed: %d:%02d:%02d (%.2fs)" % (h, m, s, time_elapsed)
    print

    print "Waiting for mission to end..."
    # Mission should have ended already, but we want to wait until all the various agent hosts
    # have had a chance to respond to their mission ended message.
    hasEnded = False
    while not hasEnded:
        hasEnded = True  # assume all good
        sys.stdout.write('.')
        time.sleep(0.1)
        for ah in agent_hosts[1:3]:
            world_state = ah.getWorldState()
            if world_state.is_mission_running:
                hasEnded = False  # all not good

    print "Mission ended"
    # Mission has ended.

    time.sleep(2)


def validate_semantic_representation(sem_rep):
    """validate the semantic representaiton"""
    # check for missing arguments

    # check for unknown shapes

    # check for context but how?


def teleportMovement(ah, teleport_x=None, teleport_y=None, teleport_z=None):
    """Teleport the agent in the map"""
    if teleport_y is None:
        y = 4
    elif teleport_y >= 1:
        y = teleport_y
    else:
        y = 4
    sendCommand(
        ah, "tp " + str(teleport_x) + " " + str(y) + " " + str(teleport_z))
    time.sleep(2)


def adjustView(ah, amount=None):
    """adjust the view for the agent for look down and look up"""
    if amount is None:
        sendCommand(ah, "pitch 0.1")
        time.sleep(2)
    else:
        sendCommand(ah, "pitch " + str(amount))
        time.sleep(2)

    sendCommand(ah, "pitch 0")
    time.sleep(1)


def restoreView(ah, amount=None):
    """restore the view for the agent for look down and look up"""
    if amount is None:
        sendCommand(ah, "pitch -0.1")
        time.sleep(2)
    else:
        sendCommand(ah, "pitch -" + str(amount))
        time.sleep(2)

    sendCommand(ah, "pitch 0")
    time.sleep(1)


def moveRight(ah):
    """move the agent to right"""
    sendCommand(ah, "strafe .1")
    time.sleep(3)
    sendCommand(ah, "strafe 0")


def moveLeft(ah):
    """move the agent to right"""
    sendCommand(ah, "strafe -.1")
    time.sleep(3)
    sendCommand(ah, "strafe 0")


def pickUpBlock(ah, index=-1):
    """select the mentioned color block from the hotbar"""
    print("color index: ", index)
    if index == -1:
        import numpy as np
        ind = np.random.random_integers(6)
        print("ind ", ind)
        selection = "hotbar." + str(ind)
    else:
        selection = "hotbar." + str(int(index))

    sendCommand(ah, selection + " 1")
    sendCommand(ah, selection + " 0")


def useBlock(ah):
    """use the block in hand"""
    sendCommand(ah, 'use 1')
    sendCommand(ah, 'use 0')


def sendCommand(ah, command):
    """execute all the commands through this method"""
    if SHOW_COMMANDS is True:
        print(command)
    ah.sendCommand(command)
