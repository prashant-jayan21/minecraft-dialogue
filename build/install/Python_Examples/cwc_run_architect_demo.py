# Prototype:
# Human builder, system as architect
# Record all observations

import os, sys, time, json, datetime, copy, pprint
from os.path import join
from argparse import Namespace
import MalmoPython, numpy as np
import cwc_mission_utils as mission_utils, cwc_debug_utils as debug_utils, cwc_io_utils as io_utils
from cwc_postprocess_observations import reformatObservations, mergeObservations, postprocess
from config_diff_tool.diff import get_diff

sys.path.append('../../../../cwc-minecraft-models/python')
import generate_seq2seq_online
from utils import get_gold_config, get_built_config

def addFixedViewers(n):
    fvs = ''
    for i in range(n):
        fvs += '''<AgentSection mode="Spectator">
                    <Name>FixedViewer'''+str(i+1)+'''</Name>
                    <AgentStart>
                      ''' + mission_utils.fv_placements[i] + '''
                      </AgentStart>
                    <AgentHandlers/>
                  </AgentSection>
                '''
    return fvs

def addArchitect():
  return '''
            <AgentSection mode="Spectator">
              <Name>Architect</Name>
              <AgentStart>
                <Placement x = "0" y = "5" z = "-6" pitch="45"/>
              </AgentStart>
              <AgentHandlers>''' + '''
                <ChatCommands/>''' + '''
              </AgentHandlers>
            </AgentSection>
          '''

def drawInventoryBlocks():
    return '''
                <DrawCuboid type="cwcmod:cwc_minecraft_orange_rn" x1="5" y1="1" z1="7" x2="1" y2="2" z2="8"/>
                <DrawCuboid type="cwcmod:cwc_minecraft_yellow_rn" x1="-1" y1="1" z1="7" x2="-5" y2="2" z2="8"/>
                <DrawCuboid type="cwcmod:cwc_minecraft_green_rn" x1="7" y1="1" z1="6" x2="8" y2="2" z2="2"/>
                <DrawCuboid type="cwcmod:cwc_minecraft_blue_rn" x1="7" y1="1" z1="0" x2="8" y2="2" z2="-4"/>
                <DrawCuboid type="cwcmod:cwc_minecraft_purple_rn" x1="-7" y1="1" z1="6" x2="-8" y2="2" z2="2"/>
                 <DrawCuboid type="cwcmod:cwc_minecraft_red_rn" x1="-7" y1="1" z1="0" x2="-8" y2="2" z2="-4"/>
            '''

def generateMissionXML(experiment_id, existing_config_xml_substring, num_fixed_viewers, draw_inventory_blocks):
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
                        <DrawCuboid type="cwcmod:cwc_unbreakable_white_rn" x1="''' + str(mission_utils.x_min_build) +'''" y1="0" z1="''' + \
                        str(mission_utils.z_min_build)+ '''" x2="'''+ str(mission_utils.x_max_build)+'''" y2="0" z2="''' + str(mission_utils.z_max_build) + '''"/>
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
                           <min x="'''+ str(mission_utils.x_min_obs) + '''" y="'''+ str(mission_utils.y_min_obs) + '''" z="''' + str(mission_utils.z_min_obs) + '''"/>
                           <max x="'''+ str(mission_utils.x_max_obs) + '''" y="''' + str(mission_utils.y_max_obs) + '''" z="''' + str(mission_utils.z_max_obs) + '''"/>
                         </Grid>
                      </CwCObservation>
                    </AgentHandlers>
                  </AgentSection>

                  '''+addArchitect()+'''

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
                        <DrawCuboid type="cwcmod:cwc_unbreakable_white_rn" x1="''' + str(mission_utils.x_min_goal) +'''" y1="0" z1="''' + str(mission_utils.z_min_goal)+ \
                        '''" x2="'''+ str(mission_utils.x_max_goal)+'''" y2="0" z2="''' + str(mission_utils.z_max_goal) + '''"/>''' + gold_config_xml_substring + \
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
    print("Calling cwc_run_mission with args:", args, "\n")
    start_time = time.time()

    builder_ip, builder_port = args["builder_ip_addr"], args["builder_port"]
    architect_ip, architect_port = args["architect_ip_addr"], args["architect_port"]
    fixed_viewer_ip, fixed_viewer_port, num_fixed_viewers = args["fixed_viewer_ip_addr"], args["fixed_viewer_port"], args["num_fixed_viewers"]

    draw_inventory_blocks = args["draw_inventory_blocks"]
    existing_is_gold = args["existing_is_gold"]
    builder_idx = 1

    # Create agent hosts:
    agent_hosts = []
    for i in range(3+num_fixed_viewers):
        agent_hosts.append(MalmoPython.AgentHost())

    # Set observation policy for builder
    agent_hosts[builder_idx].setObservationsPolicy(MalmoPython.ObservationsPolicy.KEEP_ALL_OBSERVATIONS)

    # Set up a client pool
    client_pool = MalmoPython.ClientPool()

    if not args["lan"]:
        print("Starting in local mode.")
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10000))

        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10001))
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10002))

        for i in range(num_fixed_viewers):
            client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10003+i))
    else:
        print("Builder IP: ", builder_ip, "\tPort:", builder_port)
        print("Architect IP:", architect_ip, "\tPort:", architect_port)
        print("FixedViewer IP:", fixed_viewer_ip, "\tPort:", fixed_viewer_port, "\tNumber of clients:", num_fixed_viewers, "\n")

        client_pool.add(MalmoPython.ClientInfo(architect_ip, architect_port+1))
        client_pool.add(MalmoPython.ClientInfo(builder_ip, builder_port))
        client_pool.add(MalmoPython.ClientInfo(architect_ip, architect_port))

        for i in range(num_fixed_viewers):
            client_pool.add(MalmoPython.ClientInfo(fixed_viewer_ip, fixed_viewer_port+i))
        else:
          client_pool.add(MalmoPython.ClientInfo(builder_ip, builder_port))

    # experiment ID
    player_ids = "B"+args["builder_id"] + "-A" + args["architect_id"]
    config_id = os.path.basename(args["gold_config"]).replace(".xml","")
    experiment_time = str(int(round(time.time()*1000)))
    experiment_id = player_ids + "-" + config_id + "-" + experiment_time

    # obtain xml substrings
    gold_config_xml_substring = io_utils.readXMLSubstringFromFile(args["gold_config"], False)
    existing_config_xml_substring = io_utils.readXMLSubstringFromFile(args["existing_config"], existing_is_gold)

    # construct mission xml
    missionXML = generateMissionXML(experiment_id, existing_config_xml_substring, num_fixed_viewers, draw_inventory_blocks)
    missionXML_oracle = generateOracleXML(experiment_id, gold_config_xml_substring)

    # oracle
    my_mission_oracle = MalmoPython.MissionSpec(missionXML_oracle, True)
    mission_utils.safeStartMission(agent_hosts[0], my_mission_oracle, client_pool, MalmoPython.MissionRecordSpec(), 0, "cwc_dummy_mission_oracle")

    # builder, architect
    my_mission = MalmoPython.MissionSpec(missionXML, True)
    mission_utils.safeStartMission(agent_hosts[builder_idx], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 0, "cwc_dummy_mission")

    mission_utils.safeStartMission(agent_hosts[2], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 1, "cwc_dummy_mission")

    # fixed viewers
    for i in range(num_fixed_viewers):
        mission_utils.safeStartMission(agent_hosts[3+i], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 2+i, "cwc_dummy_mission")

    mission_utils.safeWaitForStart(agent_hosts)

    # model and gold config xml loading
    args2 = Namespace(
        model_dir = '../../../../cwc-minecraft-models/models/utterances_and_block_region_counters/20190505-finetuned/utterances_and_block_region_counters_trainer-1557116167126/1557116167131/',
        data_dir = '../../../../cwc-minecraft-models/data/logs/',
        gold_configs_dir = '../../../../cwc-minecraft-models/data/gold-configurations/',
        saved_dataset_dir = None,
        vocab_dir = "../../../../cwc-minecraft-models/vocabulary/",
        output_path = None,
        num_workers = 0,
        seed = 1234,
        beam_size = 10,
        max_decoding_length = 50,
        development_mode = False,
        decoding_strategy = 'beam',
        gamma = 0.8,
        regenerate_sentences = True,
        model_iteration = 'best',
        split = 'val',
        disable_shuffle = False
    )

    config_name = args["gold_config"].split("/")[-1].split(".")[0]
    config_xml_file = join(args2.gold_configs_dir, config_name + ".xml")
    config_structure = get_gold_config(config_xml_file)

    config_params, models, encoder_vocab, decoder_vocab = generate_seq2seq_online.setup(args2)

    # poll for observations
    timed_out = False
    all_observations = []
    time_at_last_state = time.time()
    prev_minimal_diff, _ = get_diff(config_structure, [])
    prev_diff_size = len(prev_minimal_diff["gold_minus_built"]) + len(prev_minimal_diff["built_minus_gold"])
    prev_gen_architect_utterance = ""
    threshold = 10

    while not timed_out:
        for i in range(3+num_fixed_viewers):
            ah = agent_hosts[i]
            world_state = ah.getWorldState()

            if not world_state.is_mission_running:
                timed_out = True

            elif i == builder_idx and world_state.number_of_observations_since_last_state > 0:
                total_elements = 0
                for observation in world_state.observations:
                    total_elements += len(json.loads(observation.text))

                for observation in world_state.observations:
                    all_observations.append(observation)
                    time_at_last_state = time.time()

                def f(all_observations):
                    all_world_states = []

                    for observation in all_observations:
                        world_state = json.loads(observation.text)
                        world_state["Timestamp"] = observation.timestamp.replace(microsecond=0).isoformat(' ')
                        # debug_utils.prettyPrintObservation(world_state)
                        all_world_states.append(world_state)

                    return all_world_states

                all_world_states = f(all_observations)

                reformatted = reformatObservations(all_world_states)
                all_world_states_merged = mergeObservations(reformatted)
                string_to_write = postprocess(all_world_states_merged, False)

                log = {}
                log["WorldStates"] = all_world_states_merged

                def get_last_state_type(last_state, penultimate_state):
                    if last_state["ChatHistory"] == penultimate_state["ChatHistory"]:
                        return "builder_action"

                    last_utterance = last_state["ChatHistory"][-1]
                    last_speaker = "Architect" if "Architect" in last_utterance.split()[0] else "Builder"
                    if last_speaker == "Architect":
                        return "architect_speaks"
                    else:
                        return "builder_speaks"

                if len(log["WorldStates"]) < 2:
                    penultimate_state = {
                        "ChatHistory": []
                    }
                else:
                    penultimate_state = log["WorldStates"][-2]

                last_state_type = get_last_state_type(log["WorldStates"][-1], penultimate_state)

                if last_state_type == "builder_action":
                    threshold = 5
                elif last_state_type == "architect_speaks":
                    threshold = 10
                else:
                    threshold = 2

                minimal_diff, _ = get_diff(config_structure, get_built_config(log["WorldStates"][-1]))
                diff_size = len(minimal_diff["gold_minus_built"]) + len(minimal_diff["built_minus_gold"])
                print(diff_size)

                if diff_size > prev_diff_size:
                    print("Architect needs to interrupt")
                    print("Speak Architect")

                    def f(all_observations):
                        all_world_states = []

                        for observation in all_observations:
                            world_state = json.loads(observation.text)
                            world_state["Timestamp"] = observation.timestamp.replace(microsecond=0).isoformat(' ')
                            # debug_utils.prettyPrintObservation(world_state)
                            all_world_states.append(world_state)

                        return all_world_states

                    all_world_states = f(all_observations)

                    reformatted = reformatObservations(all_world_states)
                    all_world_states_merged = mergeObservations(reformatted)
                    string_to_write = postprocess(all_world_states_merged, False)

                    log = {}
                    log["WorldStates"] = all_world_states_merged

                    # pprint.PrettyPrinter(indent=4).pprint(log)
                    gen_architect_utterance = "sorry, please undo that action"
                    agent_hosts[2].sendCommand("chat " + gen_architect_utterance)

                    # all_observations = all_observations[:-1 * len(world_state.observations)]

                prev_diff_size = diff_size

                print("-----")

            if i == builder_idx:
                time_since_last_state = time.time()-time_at_last_state

                if time_since_last_state > threshold:
                    print(threshold)
                    print("Speak Architect")

                    def f(all_observations):
                        all_world_states = []

                        for observation in all_observations:
                            world_state = json.loads(observation.text)
                            world_state["Timestamp"] = observation.timestamp.replace(microsecond=0).isoformat(' ')
                            # debug_utils.prettyPrintObservation(world_state)
                            all_world_states.append(world_state)

                        return all_world_states

                    all_world_states = f(all_observations)

                    reformatted = reformatObservations(all_world_states)
                    all_world_states_merged = mergeObservations(reformatted)
                    string_to_write = postprocess(all_world_states_merged, False)

                    extra_dummy_world_state = copy.deepcopy(all_world_states_merged[-1])
                    extra_dummy_world_state["ChatHistory"].append("<Builder> xxx")
                    all_world_states_merged.append(extra_dummy_world_state)

                    log = {}
                    log["WorldStates"] = all_world_states_merged

                    # pprint.PrettyPrinter(indent=4).pprint(log)
                    gen_architect_utterance = generate_seq2seq_online.predict(args2, config_name, config_structure, log, config_params, models, encoder_vocab, decoder_vocab, prev_gen_architect_utterance)
                    agent_hosts[2].sendCommand("chat " + gen_architect_utterance)

                    # all_observations = all_observations[:-1 * len(world_state.observations)]

                    prev_gen_architect_utterance = gen_architect_utterance

        time.sleep(1)

    time_elapsed = time.time()-start_time

    print("Mission has been quit. All world states:\n")

    all_world_states = []
    for observation in all_observations:
        world_state = json.loads(observation.text)
        world_state["Timestamp"] = observation.timestamp.replace(microsecond=0).isoformat(' ')
        debug_utils.prettyPrintObservation(world_state)
        all_world_states.append(world_state)

    raw_observations = {"WorldStates": all_world_states, "TimeElapsed": time_elapsed, "NumFixedViewers": num_fixed_viewers}

    io_utils.writeJSONtoLog(experiment_id, "raw-observations.json", raw_observations)
    
    m, s = divmod(time_elapsed, 60)
    h, m = divmod(m, 60)
    print("Done! Mission time elapsed: %d:%02d:%02d (%.2fs)" % (h, m, s, time_elapsed))
    print()

    print("Waiting for mission to end...")
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

    print("Mission ended")
    # Mission has ended.

    time.sleep(2)
