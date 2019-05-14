# Prototype:
# Two humans - w/ abilities to chat and build block structures
# Record all observations

from __future__ import print_function
import os, sys, time, json, datetime, copy, pickle, random, re, webbrowser, string
import MalmoPython, numpy as np
import cwc_mission_utils as mission_utils, cwc_debug_utils as debug_utils, cwc_io_utils as io_utils
from json_to_xml import blocks_to_xml
from cwc_builder_utils import *
from cwc_debug_utils import *
from collections import defaultdict

sys.path.append('./config_diff_tool')
from diff import diff

num_prev_states = 7
color_regex = re.compile("red|orange|purple|blue|green|yellow")
suppress_form = False
use_grid_form = True
url_pfxs = ["https://docs.google.com/forms/d/e/1FAIpQLSdOJXWyNHPJk7HJgy1tM6h-5dZTK4eOZ-j8ZaoxXiJgkoAdsw/viewform?usp=pp_url&entry.1041006143=", "&entry.736588817=",
			"&entry.528882131=", "&entry.730665366=",
			"&entry.26185139=", "&entry.1201649239=",
			"&entry.2140249019=", "&entry.2001652602=", 
			"&entry.1283703002="]

if use_grid_form:
	url_pfxs = ["https://docs.google.com/forms/d/e/1FAIpQLSe5MYfe3i2TwHkIXS6ecOWJDDFducFnrhSJl1yECIZbgW7uLA/viewform?usp=pp_url&entry.1027302661=", "&entry.1583955982=",
				"&entry.1819794788=", "&entry.1497119261=", "&entry.1890765153=", "&entry.1266038414=", "&entry.1449017998="]


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

		client_pool.add(MalmoPython.ClientInfo(builder_ip, builder_port+1))
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

def squash_punctuation(sentence):
	formatted_sentence = ""
	tokens = sentence.split()
	for i in range(len(tokens)):
		to_add = " "
		if (tokens[i] in string.punctuation or tokens[i][0] in string.punctuation) and tokens[i] != '"':
			if tokens[i].startswith("'") \
			or (tokens[i-1] not in string.punctuation and (i+1 == len(tokens) or not((tokens[i] == ':' or tokens[i] == ';') and tokens[i+1] == ')'))) \
			or (tokens[i-1] == '?' and tokens[i] == '!') or (tokens[i-1] == '!' and tokens[i] == '?') \
			or ((tokens[i-1] == ':' or tokens[i-1] == ';') and tokens[i] == ')') \
			or (tokens[i-1] == tokens[i] and (tokens[i] == '.' or tokens[i] == '!' or tokens[i] == '?')):
				to_add = ""

		formatted_sentence += to_add+tokens[i]
	return formatted_sentence.strip()

def cwc_run_mission(args):
	print("Calling cwc_replay_mission with args:", args, "\n")
	start_time = time.time()

	num_fixed_viewers = args["num_fixed_viewers"]
	draw_inventory_blocks = args["draw_inventory_blocks"]
	existing_is_gold = args["existing_is_gold"]
	num_samples_to_replay = args["num_samples_to_replay"]
	use_gold_utterances = args["replay_gold"]
	split = args["split"]
	evaluator_id = str(args["evaluator_id"])

	with open(args["jsons_dir"]+"/"+split+"-jsons-2.pkl", 'rb') as f:
		reference_dataset = pickle.load(f)

	if args["sample_sentences"]:
		if args["generated_sentences_sources"] is None or len(args["generated_sentences_sources"]) < 1:
			print("Error: please provide generated sentences sources for the replay tool.")
			sys.exit(0)

		generated_sentences = []
		for source in args["generated_sentences_sources"]:
			generated_sentences_file = os.path.join(args["generated_sentences_dir"], source, "generated_sentences-best-"+split+"-beam_10-gamma_0.8.txt")
			if not os.path.isfile(generated_sentences_file):
				print("Error: file does not exist:", generated_sentences_file)
				sys.exit(0)

			sentences = read_generated_sentences_json(generated_sentences_file)

			for i in range(len(sentences)):
				sentence = sentences[i]
				
				if len(generated_sentences) <= i:
					generated_sentences.append({"json_id": sentence["json_id"], "sample_id": sentence["sample_id"], "ground_truth_utterance": sentence["ground_truth_utterance_raw"], "generated_sentences": []})
				
				if sentence["json_id"] != generated_sentences[i]["json_id"] or sentence["sample_id"] != generated_sentences[i]["sample_id"]:
					print("WARNING: JSON or sample ID do not match; skipping.")
					continue

				generated_sentences[i]["generated_sentences"].append((source, sentence["generated_utterance"][0]))

		print("Loaded", len(generated_sentences), "examples; filtering...")
		
		filtered_sentences = []
		ignored_logs = set()
		for sentence in generated_sentences:
			reference_json = reference_dataset[sentence["json_id"]]
			reference_logfile = reference_json["logfile_path"]
			experiment_params = reference_logfile.split("/")[-2].split("-")
			builder, architect = int(experiment_params[0].replace("B","")), int(experiment_params[1].replace("A",""))
			if builder in args["ignore_ids"] or architect in args["ignore_ids"]:
				ignored_logs.add(reference_logfile)
				continue

			sample_id = sentence["sample_id"]
			prev_idx = max(sample_id-num_prev_states, 0)

			if prev_idx > 0:
				last_chat_history, chat_delta = None, []
				for s in range(prev_idx, sample_id):
					logged_observation = reference_json["WorldStates"][s]
					if last_chat_history is not None and len(last_chat_history) < len(logged_observation["ChatHistory"]):
						for i in range(len(last_chat_history), len(logged_observation["ChatHistory"])):
							chat_delta.append(logged_observation["ChatHistory"][i].split()[0])
					last_chat_history = logged_observation["ChatHistory"]

				if not any("Architect" in cd for cd in chat_delta):
					while prev_idx > 0:
						prev_idx -= 1
						sample_chat = reference_json["WorldStates"][prev_idx]["ChatHistory"][-1]
						if sample_chat.startswith("<Architect>"):
							break

			last_blocks_in_grid = None
			error_encountered = False
			for s in range(prev_idx, sample_id):
				logged_observation = reference_json["WorldStates"][s]
				current_blocks_in_grid = get_built_config(logged_observation)
				screenshot_path = logged_observation["ScreenshotPath"]
				observation_type = "chat"
				if screenshot_path is not None and "chat" not in screenshot_path:
					observation_type = "putdown" if "putdown" in screenshot_path else "pickup"

				if last_blocks_in_grid is not None:
					blocks_delta = diff(gold_config=current_blocks_in_grid, built_config=last_blocks_in_grid)

					if sum(len(lst) for lst in blocks_delta.values()) > 1:
						print("WARNING: multiple actions detected in diff. Ignoring this sample.") # FIXME: what do we do about these potential problematic examples?
						error_encountered = True
						break
						
					if sum(len(lst) for lst in blocks_delta.values()) > 0 and screenshot_path is not None and observation_type == 'chat':
						print("WARNING: diff contained actions, but the observation type was 'chat'. Ignoring this sample.") # FIXME: what do we do about these potential problematic examples?
						error_encountered = True
						break

				last_blocks_in_grid = current_blocks_in_grid

			if not error_encountered:
				filtered_sentences.append(sentence)

		print("Ignored logs:", ignored_logs)

		generated_sentences = filtered_sentences
		print("\nLoaded", len(generated_sentences), "filtered examples.")

		if args["shuffle"]:
			random.shuffle(generated_sentences)
		generated_sentences = generated_sentences[:args["num_sentences"]]
		print("Sampled", len(generated_sentences), "examples.")

		sentences_with_ids = []
		for i, sentence in enumerate(generated_sentences):
			sentences_with_ids.append((i, sentence))
		generated_sentences = sentences_with_ids

		if not os.path.exists(args["sampled_sentences_dir"]):
			os.makedirs(args["sampled_sentences_dir"])

		with open(os.path.join(args["sampled_sentences_dir"], 'sampled_generated_sentences-'+split+'.json'), 'w') as f:
			print("Saving sampled examples to:", os.path.join(args["sampled_sentences_dir"], 'sampled_generated_sentences-'+split+'.json'))
			json.dump(generated_sentences, f)

		print("Sampled examples. Please re-run with sample_sentences=False to initiate the replay.")
		sys.exit(0)

	sentences_path = os.path.join(args["sampled_sentences_dir"], 'sampled_generated_sentences-'+split+'.json')
	vars_map_path = os.path.join(args["sampled_sentences_dir"], evaluator_id, "vars-map.json")
	
	if args["resume_evaluation"]:
		sentences_path = os.path.join(args["sampled_sentences_dir"], evaluator_id, "unfinished-"+split+".json")

	if not os.path.isfile(sentences_path):
		print("Error: cannot find file:", sentences_path)
		sys.exit(0)

	if args["resume_evaluation"] and not os.path.isfile(vars_map_path):
		print("Error: cannot find file:", vars_map_path)
		sys.exit(0)

	with open(sentences_path, 'r') as f:
		generated_sentences = json.load(f)
	print("Loaded", len(generated_sentences), "examples from", sentences_path)

	vars_map = {}
	if args["resume_evaluation"]:
		with open(vars_map_path, 'r') as f:
			vars_map = json.load(f)
			print("Loaded vars_map from", vars_map_path)

	if args["shuffle"]:
		random.shuffle(generated_sentences)

	sentence_id = 0
	while sentence_id < len(generated_sentences) and sentence_id < num_samples_to_replay:
		eval_id, sample = generated_sentences[sentence_id]
		json_id = sample["json_id"]
		sample_id = sample["sample_id"]
		reference_json = reference_dataset[json_id]

		print("\nEvaluating sample", sample_id, "from json", str(json_id)+" ("+str(sentence_id+1)+"/"+str(len(generated_sentences))+") with eval_id", str(eval_id)+".")
		print(json.dumps(sample, indent=4))

		response = raw_input("Begin replay? [y: yes, s: skip this sample, q: end evaluation]  ")

		if response == 'q':
			print("Ending the evaluation; saving", len(generated_sentences[sentence_id:]), "unfinished samples to", os.path.join(args["sampled_sentences_dir"], evaluator_id, "unfinished-"+split+".json"))	
			if not os.path.exists(os.path.join(args["sampled_sentences_dir"], evaluator_id)):
				os.makedirs(os.path.join(args["sampled_sentences_dir"], evaluator_id))

			with open(os.path.join(args["sampled_sentences_dir"], evaluator_id, "unfinished-"+split+".json"), 'w') as f:
				print("Saving remaining", len(generated_sentences[sentence_id:]), "examples to", os.path.join(args["sampled_sentences_dir"], evaluator_id, "unfinished-"+split+".json"))
				json.dump(generated_sentences[sentence_id:], f)

			with open(vars_map_path, 'w') as f:
				print("Saving vars_map to", vars_map_path)
				json.dump(vars_map, f)

			sys.exit(0)

		if response == 's':
			sentence_id += 1
			continue

		print("Loading sample...")

		prev_idx = max(sample_id-num_prev_states, 0)
		chat_to_emit = None

		if prev_idx > 0:
			print("\nChecking for Architect utterances in the history...")
			last_chat_history, chat_delta = None, []
			for s in range(prev_idx, sample_id):
				logged_observation = reference_json["WorldStates"][s]
				if last_chat_history is not None and len(last_chat_history) < len(logged_observation["ChatHistory"]):
					for i in range(len(last_chat_history), len(logged_observation["ChatHistory"])):
						print(logged_observation["ChatHistory"][i])
						chat_delta.append(logged_observation["ChatHistory"][i].split()[0])
				last_chat_history = logged_observation["ChatHistory"]

			if not any("Architect" in cd for cd in chat_delta):
				print("No Architect utterance found: scanning additional samples. old prev_idx:", prev_idx, end=', ')

				while prev_idx > 0:
					prev_idx -= 1
					sample_chat = reference_json["WorldStates"][prev_idx]["ChatHistory"][-1]
					if sample_chat.startswith("<Architect>"):
						chat_to_emit = sample_chat.replace("<Architect> ", "")
						break

				print("new prev_idx:", prev_idx)

			print()
		else:
			print("\nChat history starts from index 0.\n")

		# initialize the agents
		agent_hosts, client_pool = initialize_agents(args)
		experiment_prefix = "-".join(reference_json["logfile_path"].split("/")[-2].split("-")[:-1])
		gold_config_xml_substring = blocks_to_xml(reference_json["gold_config_structure"], displacement=100, postprocessed=False)

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
			print("Ending the evaluation; saving", len(generated_sentences[sentence_id:]), "unfinished samples to", os.path.join(args["sampled_sentences_dir"], evaluator_id, "unfinished-"+split+".json"))
			if not os.path.exists(os.path.join(args["sampled_sentences_dir"], evaluator_id)):
				os.makedirs(os.path.join(args["sampled_sentences_dir"], evaluator_id))

			with open(os.path.join(args["sampled_sentences_dir"], evaluator_id, "unfinished-"+split+".json"), 'w') as f:
				print("Saving remaining", len(generated_sentences[sentence_id:]), "examples to", os.path.join(args["sampled_sentences_dir"], evaluator_id, "unfinished-"+split+".json"))
				json.dump(generated_sentences[sentence_id:], f)

			with open(vars_map_path, 'w') as f:
				print("Saving vars_map to", vars_map_path)
				json.dump(vars_map, f)

			sys.exit(0)

		if response == 's':
			sentence_id += 1
			continue

		print("Beginning the replay in 5 seconds...")
		time.sleep(5)

		if chat_to_emit is not None:
			sendChat(agent_hosts[2], chat_to_emit)

		error_encountered = False
		last_chat_history, last_blocks_in_grid = None, None
		last_pitch, last_yaw = None, None
		for s in range(prev_idx, sample_id):
			logged_observation = reference_json["WorldStates"][s]
			current_blocks_in_grid = get_built_config(logged_observation)

			if last_chat_history is not None:
				screenshot_path = logged_observation["ScreenshotPath"]
				observation_type = "chat"
				if screenshot_path is not None and "chat" not in screenshot_path:
					observation_type = "putdown" if "putdown" in screenshot_path else "pickup"

				builder_position = logged_observation["BuilderPosition"]
				teleportMovement(agent_hosts[1], teleport_x=builder_position["X"], teleport_y=builder_position["Y"], teleport_z=builder_position["Z"])
				setPitchYaw(agent_hosts[1], pitch=builder_position["Pitch"] if builder_position["Pitch"] != last_pitch else None, yaw=builder_position["Yaw"] if builder_position["Yaw"] != last_yaw else None)
				last_pitch, last_yaw = builder_position["Pitch"], builder_position["Yaw"]

				if len(last_chat_history) < len(logged_observation["ChatHistory"]):
					for i in range(len(last_chat_history), len(logged_observation["ChatHistory"])):
						chat_message = logged_observation["ChatHistory"][i]
						print("Sending chat message:", chat_message)
						ah = agent_hosts[1] if chat_message.startswith("<Builder>") else agent_hosts[2]
						sendChat(ah, " ".join(chat_message.split()[1:]))
						time.sleep(0.3)

				blocks_delta = diff(gold_config=current_blocks_in_grid, built_config=last_blocks_in_grid)

				if sum(len(lst) for lst in blocks_delta.values()) > 1:
					print("WARNING: multiple actions detected in diff. Quitting this sample.") # FIXME: what do we do about these potential problematic examples?
					error_encountered = True
					break
					
				if sum(len(lst) for lst in blocks_delta.values()) > 0:
					auto_find_location = False
					if screenshot_path is not None and observation_type == 'chat':
						print("WARNING: diff contained actions, but the observation type was 'chat'. Quitting this sample.") # FIXME: what do we do about these potential problematic examples?
						auto_find_location = True
						error_encountered = True
						break

					action, block = None, None
					if len(blocks_delta["gold_minus_built"]) > 0:
						action = "putdown"
						block = blocks_delta["gold_minus_built"][0]
					else:
						action = "pickup"
						block = blocks_delta["built_minus_gold"][0]

					x, y, z, color = block['x'], block['y'], block['z'], block['type']
					# todo: if auto_find_location: find_teleport_location...
					execute_action(agent_hosts[1], action=action, color=color, teleport=False)

					# if auto_find_location: TODO
					# teleportMovement(agent_hosts[1], teleport_x=builder_position["X"], teleport_y=builder_position["Y"], teleport_z=builder_position["Z"])
					# setPitchYaw(agent_hosts[1], pitch=builder_position["Pitch"], yaw=builder_position["Yaw"])

			last_chat_history = logged_observation["ChatHistory"]
			last_blocks_in_grid = current_blocks_in_grid
			time.sleep(0.1)

		time.sleep(1)

		if not error_encountered: # TODO: format puncutation here
			print("Full chat history:", last_chat_history)
			sentences = sample["generated_sentences"]
			if not any(sen[0] == 'human' for sen in sentences):
				sentences.append(('human', sample["ground_truth_utterance"]))
			random.shuffle(sentences)
			sendChat(agent_hosts[2], "=== Example ID: "+str(eval_id)+" ===")

			form_sentences = [evaluator_id, str(eval_id)]
			formatted_sens = []
			for k, (source, sentence) in enumerate(sentences):
				identifier = string.ascii_letters[k]
				if eval_id not in vars_map:
					vars_map[eval_id] = {}
				if identifier in vars_map[eval_id]:
					print("Warning: overwriting vars_map entry for eval_id", eval_id, "identifier", identifier)
				vars_map[eval_id][identifier] = source

				if source != 'human':
					sentence = squash_punctuation(sentence)
				# print('Sending chat message to be evaluated: ('+identifier+') ('+source+')', sentence)
				# sendChat(agent_hosts[2], '('+identifier+') '+sentence)

				sentence = sentence.replace(' ','+')
				if not use_grid_form:
					form_sentences.append(sentence)
					form_sentences.append(sentence)
				formatted_sens.append('('+identifier+')+'+sentence)
				time.sleep(0.2)

			if not use_grid_form:
				form_sentences.append('%0A'.join(formatted_sens))
			else:
				for i in range(5):
					form_sentences.append('%0A%0A'.join(formatted_sens))

			if not suppress_form:
				url = ""
				for i in range(len(url_pfxs)):
					url += url_pfxs[i]+form_sentences[i]
				time.sleep(2)
				webbrowser.open(url, new=1)

		timed_out, replay_example = False, False
		while not timed_out:
			for i in range(3+num_fixed_viewers):
				ah = agent_hosts[i]
				world_state = ah.getWorldState()
				for observation in world_state.observations:
					if observation.text is not None:
						obsrv = json.loads(observation.text)
						if obsrv.get("Chat") is not None and any("replay" in chat for chat in obsrv.get("Chat")):
							replay_example = True
							print("NOTICE: will replay this example.")

				if not world_state.is_mission_running:
					timed_out = True
					if not replay_example:
						sentence_id += 1

		print("Quit signal received. Waiting for mission to end...")
		if not os.path.exists(os.path.join(args["sampled_sentences_dir"], evaluator_id)):
			os.makedirs(os.path.join(args["sampled_sentences_dir"], evaluator_id))

		with open(os.path.join(args["sampled_sentences_dir"], evaluator_id, "unfinished-"+split+".json"), 'w') as f:
			print("Saving remaining", len(generated_sentences[sentence_id:]), "examples to", os.path.join(args["sampled_sentences_dir"], evaluator_id, "unfinished-"+split+".json"))
			json.dump(generated_sentences[sentence_id:], f)

		with open(vars_map_path, 'w') as f:
			print("Saving vars_map to", vars_map_path)
			json.dump(vars_map, f)

		# Mission should have ended already, but we want to wait until all the various agent hosts
		# have had a chance to respond to their mission ended message.
		hasEnded = False
		timeElapsed = 0
		while not hasEnded and timeElapsed < 100:
			hasEnded = True  # assume all good
			sys.stdout.write('.')
			time.sleep(0.1)
			timeElapsed += 1
			for ah in agent_hosts[1:3]:
				world_state = ah.getWorldState()
				if world_state.is_mission_running:
					hasEnded = False  # all not good

		print("Mission ended")
		# Mission has ended.

		time.sleep(2)
