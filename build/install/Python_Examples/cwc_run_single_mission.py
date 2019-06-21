# Prototype:
# Two humans - w/ abilities to chat and build block structures
# Record all observations

import os, sys, time, json, datetime, copy, pprint
from os.path import join
from argparse import Namespace
import MalmoPython, numpy as np
import cwc_mission_utils as mission_utils, cwc_debug_utils as debug_utils, cwc_io_utils as io_utils
from cwc_postprocess_observations import reformatObservations, mergeObservations, postprocess

sys.path.append('../../../../cwc-minecraft-models/python')
import generate_seq2seq_online
from utils import get_gold_config
from json_to_xml import to_xml

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

def addArchitect(create_target_structures, architect_demo):
  if create_target_structures:
    return ''

  return '''
            <AgentSection mode="Spectator">
              <Name>Architect</Name>
              <AgentStart>
                <Placement x = "0" y = "5" z = "-6" pitch="45"/>
              </AgentStart>
              <AgentHandlers>''' + ('''
                <ChatCommands/>''' if architect_demo else '''''') + '''
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

def generateMissionXML(experiment_id, existing_config_xml_substring, num_fixed_viewers, draw_inventory_blocks, architect_demo, create_target_structures):
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

                  '''+addArchitect(create_target_structures, architect_demo)+'''

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
    print(("Calling cwc_run_mission with args:", args, "\n"))
    start_time = time.time()

    builder_ip, builder_port = args["builder_ip_addr"], args["builder_port"]
    architect_ip, architect_port = args["architect_ip_addr"], args["architect_port"]
    fixed_viewer_ip, fixed_viewer_port, num_fixed_viewers = args["fixed_viewer_ip_addr"], args["fixed_viewer_port"], args["num_fixed_viewers"]

    draw_inventory_blocks = args["draw_inventory_blocks"]
    existing_is_gold = args["existing_is_gold"]
    create_target_structures = args["create_target_structures"]
    builder_idx = 0 if create_target_structures else 1

    if create_target_structures and os.path.isfile(args["gold_config"]):
      print(("ERROR: attempting to create target structure", args["gold_config"], "but it already exists! Please update the configs_csv file to include file paths for NEW target structures only."))
      sys.exit(0)

    architect_demo = args["architect_demo"]

    # Create agent hosts:
    agent_hosts = []
    for i in range((3+num_fixed_viewers) if not create_target_structures else 1):
        agent_hosts.append(MalmoPython.AgentHost())

    # Set observation policy for builder
    agent_hosts[builder_idx].setObservationsPolicy(MalmoPython.ObservationsPolicy.KEEP_ALL_OBSERVATIONS)

    # Set up a client pool
    client_pool = MalmoPython.ClientPool()

    if not args["lan"]:
        print("Starting in local mode.")
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10000))

        if not create_target_structures:
          client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10001))
          client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10002))

          for i in range(num_fixed_viewers):
              client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10003+i))
    else:
        print((("Builder IP: "+builder_ip), "\tPort:", builder_port))
        print(("Architect IP:", architect_ip, "\tPort:", architect_port))
        print(("FixedViewer IP:", fixed_viewer_ip, "\tPort:", fixed_viewer_port, "\tNumber of clients:", num_fixed_viewers, "\n"))

        if not create_target_structures:
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
    gold_config_xml_substring = io_utils.readXMLSubstringFromFile(args["gold_config"], False) if not create_target_structures else ""
    existing_config_xml_substring = io_utils.readXMLSubstringFromFile(args["existing_config"], existing_is_gold)

    # construct mission xml
    missionXML = generateMissionXML(experiment_id, existing_config_xml_substring, num_fixed_viewers, draw_inventory_blocks, architect_demo, create_target_structures)
    missionXML_oracle = generateOracleXML(experiment_id, gold_config_xml_substring)

    if not create_target_structures:
      # oracle
      my_mission_oracle = MalmoPython.MissionSpec(missionXML_oracle, True)
      mission_utils.safeStartMission(agent_hosts[0], my_mission_oracle, client_pool, MalmoPython.MissionRecordSpec(), 0, "cwc_dummy_mission_oracle")

    # builder, architect
    my_mission = MalmoPython.MissionSpec(missionXML, True)
    mission_utils.safeStartMission(agent_hosts[builder_idx], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 0, "cwc_dummy_mission")

    if not create_target_structures:
      mission_utils.safeStartMission(agent_hosts[2], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 1, "cwc_dummy_mission")

      # fixed viewers
      for i in range(num_fixed_viewers):
          mission_utils.safeStartMission(agent_hosts[3+i], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 2+i, "cwc_dummy_mission")

    mission_utils.safeWaitForStart(agent_hosts)

    # model and gold config xml loading
    if architect_demo:
        args2 = Namespace(
            model_dir = '/Users/prashant/Work/cwc-minecraft-models/models_remote/utterances_and_block_region_counters/20190227/utterances_and_block_region_counters_trainer-1551313181240/1551313181248/',
            data_dir = '/Users/prashant/Work/cwc-minecraft-models/data/logs/',
            gold_configs_dir = '/Users/prashant/Work/cwc-minecraft-models/data/gold-configurations/',
            saved_dataset_dir = None,
            vocab_dir = "/Users/prashant/Work/cwc-minecraft-models/vocabulary/",
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
    while not timed_out:
        for i in range((3+num_fixed_viewers) if not create_target_structures else 1):
            ah = agent_hosts[i]
            world_state = ah.getWorldState()

            if not world_state.is_mission_running:
                timed_out = True

            elif i == builder_idx and world_state.number_of_observations_since_last_state > 0:
                total_elements = 0
                for observation in world_state.observations:
                    total_elements += len(json.loads(observation.text))

                if not architect_demo:
                    print(("Received", len(world_state.observations), "observations. Total number of elements:", total_elements))
                for observation in world_state.observations:
                    if not architect_demo:
                        print("Processing observation:")
                        debug_utils.printObservationElements(json.loads(observation.text))
                        pprint.PrettyPrinter(indent=4).pprint(json.loads(observation.text))
                    all_observations.append(observation)

                if architect_demo:
                    for observation in world_state.observations:
                        if json.loads(observation.text).get('Chat') == ['<Builder> xxx']:
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
                            gen_architect_utterance = generate_seq2seq_online.predict(args2, config_name, config_structure, log, config_params, models, encoder_vocab, decoder_vocab)
                            agent_hosts[2].sendCommand("chat " + gen_architect_utterance)

                            all_observations = all_observations[:-1 * len(world_state.observations)]

                print("-----")

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

    if not create_target_structures:
      io_utils.writeJSONtoLog(experiment_id, "raw-observations.json", raw_observations)
    else:
      reformatted = reformatObservations(raw_observations.get("WorldStates"))
      merged = mergeObservations(reformatted)
      _ = postprocess(merged, False)
      time_elapsed = raw_observations.get("TimeElapsed")
      m, s = divmod(time_elapsed, 60)
      h, m = divmod(m, 60)
      raw_observations["WorldStates"] = merged

      print((json.dumps(raw_observations, indent=4)))
      xml_str = to_xml(raw_observations)

      if len(xml_str) > 0:
        with open(args['gold_config'], 'w') as f:
          f.write(xml_str)
        print(("Wrote gold configuration to", args["gold_config"], " ("+str(len(xml_str.split('\n'))-1)+' blocks)'))
      else:
        print(("WARNING: creating target structures: created structure was empty. Configuration", args["gold_config"], "not saved."))

    m, s = divmod(time_elapsed, 60)
    h, m = divmod(m, 60)
    print(("Done! Mission time elapsed: %d:%02d:%02d (%.2fs)" % (h, m, s, time_elapsed)))
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
