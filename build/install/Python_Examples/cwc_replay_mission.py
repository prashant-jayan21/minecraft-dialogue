# Prototype:
# Two humans - w/ abilities to chat and build block structures
# Record all observations

from __future__ import print_function
import os, sys, time, json, datetime, copy, pickle, random, re
import MalmoPython, numpy as np
import cwc_mission_utils as mission_utils, cwc_debug_utils as debug_utils, cwc_io_utils as io_utils
from json_to_xml import blocks_to_xml
from cwc_builder_utils import *
from cwc_debug_utils import *

sys.path.append('./config_diff_tool')
from diff import diff

num_prev_states = 7
color_regex = re.compile("red|orange|purple|blue|green|yellow")

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
					  <Placement x = "0" y = "1" z = "-7"/>
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
					  <Placement x = "0" y = "10" z = "-10" yaw = "0" pitch = "45"/>
					</AgentStart>
					<AgentHandlers>
					  <ChatCommands/>
					</AgentHandlers>
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
					  <Placement x = "100" y = "10" z = "90" pitch="45"/>
					</AgentStart>
					<AgentHandlers/>
				  </AgentSection>
				</Mission>'''

def initialize_agents(args):
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
		print("Starting in local mode.")
		client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10000))
		client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10001))
		client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10002))

		for i in range(num_fixed_viewers):
			client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10003 + i))
	else:
		print("Builder IP: ", builder_ip, "\tPort:", builder_port)
		print("Architect IP:", architect_ip, "\tPort:", architect_port)
		print("FixedViewer IP:", fixed_viewer_ip, "\tPort:", fixed_viewer_port, "\tNumber of clients:", num_fixed_viewers, "\n")

		client_pool.add(MalmoPython.ClientInfo(architect_ip, architect_port+1))
		client_pool.add(MalmoPython.ClientInfo(builder_ip, builder_port))
		client_pool.add(MalmoPython.ClientInfo(architect_ip, architect_port))

		for i in range(num_fixed_viewers):
			client_pool.add(MalmoPython.ClientInfo(fixed_viewer_ip, fixed_viewer_port+i))

	return agent_hosts, client_pool

def read_generated_sentences_json(file):
  with open(file, 'r') as f:
	lines = f.readlines()
	return json.loads('\n'.join(lines[12:]))

def get_built_config(observation):
	"""
	Args:
		observation: The observations for a cetain world state

	Returns:
		The built config for that state as a list of dicts -- one dict per block
	"""

	built_config_raw = observation["BlocksInGrid"]
	built_config = list(map(reformat, built_config_raw))
	return built_config

def reformat(block):
	return {
		"x": block["AbsoluteCoordinates"]["X"],
		"y": block["AbsoluteCoordinates"]["Y"],
		"z": block["AbsoluteCoordinates"]["Z"],
		"type": color_regex.findall(str(block["Type"]))[0] # NOTE: DO NOT CHANGE! Unicode to str conversion needed downstream when stringifying the dict.
	}

def cwc_run_mission(args):
	print("Calling cwc_run_builder_demo with args:", args, "\n")
	start_time = time.time()

	num_fixed_viewers = args["num_fixed_viewers"]
	draw_inventory_blocks = args["draw_inventory_blocks"]
	existing_is_gold = args["existing_is_gold"]
	num_samples_to_replay = args["num_samples_to_replay"]
	use_gold_utterances = args["replay_gold"]

	if args["generated_sentences_file"] is None:
		print("Error: please provide a generated sentences file for the replay tool.")
		sys.exit(0)

	generated_sentences = read_generated_sentences_json(args["generated_sentences_file"])
	if args["shuffle"]:
		random.shuffle(generated_sentences)
	generated_sentences = generated_sentences[:num_samples_to_replay]

	with open(args["jsons_dir"]+"/val-jsons-2.pkl", 'rb') as f:
		reference_dataset = pickle.load(f)

	for sample in generated_sentences:
		json_id = sample["json_id"]
		sample_id = sample["sample_id"]
		reference_json = reference_dataset[json_id]

		print("\nEvaluating sample", sample_id, "from json", str(json_id)+".")
		response = raw_input("Replay this sample? [y: yes, n: skip this sample, q: end evaluation]  ")

		if response == 'q':
			print("Ending the evaluation.")
			sys.exit(0)

		if response == 's':
			continue

		print("Loading sample...")
		# initialize the agents
		agent_hosts, client_pool = initialize_agents(args)
		experiment_prefix = "-".join(reference_json["logfile_path"].split("/")[-2].split("-")[:-1])
		gold_config_xml_substring = blocks_to_xml(reference_json["gold_config_structure"], displacement=100, postprocessed=False)
		prev_idx = max(sample_id-num_prev_states, 0)

		# experiment ID
		experiment_time = str(int(round(time.time() * 1000)))
		experiment_id = str(experiment_prefix + "-" + experiment_time)

		existing_config_xml_substring = blocks_to_xml(reference_json["WorldStates"][prev_idx]["BlocksInGrid"], postprocessed=True)
	  
		missionXML = generateMissionXML(experiment_id, existing_config_xml_substring, num_fixed_viewers, draw_inventory_blocks)
		missionXML_oracle = generateOracleXML(experiment_id, gold_config_xml_substring)

		# oracle
		my_mission_oracle = MalmoPython.MissionSpec(missionXML_oracle, True)
		mission_utils.safeStartMission(agent_hosts[0], my_mission_oracle, client_pool, MalmoPython.MissionRecordSpec(), 0, "cwc_dummy_mission_oracle")

		# builder, architect
		my_mission = MalmoPython.MissionSpec(missionXML, True)
		my_mission.allowAllInventoryCommands()
		my_mission.allowAllAbsoluteMovementCommands()
		my_mission.allowAllDiscreteMovementCommands()
		my_mission.allowAllChatCommands()

		mission_utils.safeStartMission(agent_hosts[1], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 0, "cwc_dummy_mission")
		mission_utils.safeStartMission(agent_hosts[2], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 1, "cwc_dummy_mission")

		# fixed viewers
		for i in range(num_fixed_viewers):
			mission_utils.safeStartMission(agent_hosts[3+i], my_mission, client_pool, MalmoPython.MissionRecordSpec(), 2+i, "cwc_dummy_mission")

		mission_utils.safeWaitForStart(agent_hosts)

		print("Replaying observations:", range(prev_idx, sample_id+1))
		response = raw_input("Begin replay? [y: yes, s: skip this sample, q: end evaluation]  ")

		if response == 'q':
			print("Ending the evaluation.")
			sys.exit(0)

		if response == 's':
			continue

		print("Beginning the replay in 5 seconds...")
		time.sleep(5)
		# todo?: also initialize builder inventory?

		last_chat_history, last_blocks_in_grid = None, None
		for s in range(prev_idx, sample_id):
			logged_observation = reference_json["WorldStates"][s]
			current_blocks_in_grid = get_built_config(logged_observation)
			prettyPrintObservation(logged_observation)	        

			if last_chat_history is not None:
				screenshot_path = logged_observation["ScreenshotPath"]
				observation_type = "chat"
				if "chat" not in screenshot_path:
					observation_type = "putdown" if "putdown" in screenshot_path else "pickup"

				builder_position = logged_observation["BuilderPosition"]
				teleportMovement(agent_hosts[1], teleport_x=builder_position["X"], teleport_y=builder_position["Y"], teleport_z=builder_position["Z"])
				setPitchYaw(agent_hosts[1], pitch=builder_position["Pitch"], yaw=builder_position["Yaw"])

				if len(last_chat_history) < len(logged_observation["ChatHistory"]):
					for i in range(len(last_chat_history), len(logged_observation["ChatHistory"])):
						chat_message = logged_observation["ChatHistory"][i]
						print("Sending chat message:", chat_message)
						ah = agent_hosts[1] if chat_message.startswith("<Builder>") else agent_hosts[2]
						sendChat(ah, " ".join(chat_message.split()[1:]))
						time.sleep(1)

				blocks_delta = diff(gold_config=current_blocks_in_grid, built_config=last_blocks_in_grid)
				print("Computed diff:", blocks_delta)

				if sum(len(lst) for lst in blocks_delta.values()) > 1:
					print("WARNING: multiple actions detected in diff. Quitting this sample.")
					break
					
				if sum(len(lst) for lst in blocks_delta.values()) > 0:
					auto_find_location = False
					if observation_type == 'chat':
						print("WARNING: diff contained actions, but the observation type was 'chat'. Using automated location finder to teleport Builder.")
						auto_find_location = True

					action, block = None, None
					if len(blocks_delta["gold_minus_built"]) > 0:
						action = "putdown"
						block = blocks_delta["gold_minus_built"][0]
					else:
						action = "pickup"
						block = blocks_delta["built_minus_gold"][0]

					x, y, z, color = block['x'], block['y'], block['z'], block['type']
					# todo: find_teleport_location...
					execute_action(agent_hosts[1], action=action, color=color, teleport=False)

					# if auto_find_location: TODO
					# teleportMovement(agent_hosts[1], teleport_x=builder_position["X"], teleport_y=builder_position["Y"], teleport_z=builder_position["Z"])
					# setPitchYaw(agent_hosts[1], pitch=builder_position["Pitch"], yaw=builder_position["Yaw"])

			last_chat_history = logged_observation["ChatHistory"]
			last_blocks_in_grid = current_blocks_in_grid

		time.sleep(1)
		ground_truth_utterance = sample["ground_truth_utterance"]
		generated_utterance = sample["generated_utterance"][0]

		print("Ground truth utterance:", ground_truth_utterance)
		print("Generated utterance:", generated_utterance)

		utterance = generated_utterance
		if use_gold_utterances:
			utterance = ground_truth_utterance

		sendChat(agent_hosts[2], utterance)

		timed_out = False
		while not timed_out:
			for i in range(3+num_fixed_viewers):
				ah = agent_hosts[i]
				world_state = ah.getWorldState()

				if not world_state.is_mission_running:
					timed_out = True

		print("Quit signal received. Waiting for mission to end...")
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

		print("Mission ended")
		# Mission has ended.

		time.sleep(10)
