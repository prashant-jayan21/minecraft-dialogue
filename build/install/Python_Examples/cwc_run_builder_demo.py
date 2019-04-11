# Prototype:
# Human architect, planner as builder
# Record all observations

from __future__ import print_function
from enum import Enum
from collections import defaultdict, OrderedDict
from cwc_mission_utils import x_min_build, x_max_build, y_min_build, y_max_build, z_min_build, z_max_build
from cwc_parsers import DummyParser, RuleBasedParser
import os, sys, time, json, string, re, datetime, copy, random, traceback, MalmoPython, numpy as np
import cwc_mission_utils as mission_utils
import cwc_debug_utils as debug_utils
import cwc_io_utils as io_utils
import cwc_planner_utils as planner_utils

# GLOBAL VARIABLES FOR DEBUGGING
SHOW_COMMANDS = False
N_SHAPES = 0
ATTEMPT_LIMIT = 3
write_logfiles = True
verbose = False
switch_left_right = True

# map of colors to corresponding hotbar IDs
color_map = {
    'red': 1,
    'orange': 2,
    'yellow': 3,
    'green': 4,
    'blue': 5,
    'purple': 6,
    'white': 1,
    'violet': 6  # FIXME when this is fixed in the planner
}

# agent default location
default_loc = {
    "x": 0,
    "y": 1,
    "z": -6
}

# default pitch values by direction
pitch_dirs = {
    "north": 60,
    "east": 60,
    "south": 60,
    "west": 60,
    "top": 90,
    "bottom": -90,
    "bottom_north": -60,
    "bottom_east": -60,
    "bottom_south": -60,
    "bottom_west": -60,
    "top_north": 55,
    "top_east": 55,
    "top_south": 55,
    "top_west": 55
}

# default yaw values by direction
yaw_dirs = {
    "north": 180,
    "east": 270,
    "south": 0,
    "west": 90,
    "bottom_north": 180,
    "bottom_east": 270,
    "bottom_south": 0,
    "bottom_west": 90,
    "top_north": 180,
    "top_east": 270,
    "top_south": 0,
    "top_west": 90,
}

# map of relative to cardinal directions
relative_to_cardinal = {
    "ahead": "south",
    "left": "east",
    "right": "west", 
    "behind": "north"
}

# delta values by which coordinates should be added to access blocks in specific directions
coord_deltas = {
    "ahead": {
        "north": (0, 0, -1),
        "south": (0, 0, 1),
        "east": (1, 0, 0),
        "west": (-1, 0, 0),
        "top": (0, 0, 1),
        "bottom": (0, 0, 1),
        "bottom_north": (0, 0, -1),
        "bottom_south": (0, 0, 1),
        "bottom_east": (1, 0, 0),
        "bottom_west": (-1, 0, 0),
        "top_north": (0, 0, -1),
        "top_south": (0, 0, 1),
        "top_east": (1, 0, 0),
        "top_west": (-1, 0, 0)
    },
    "left": {
        "north": (-1, 0, 0),
        "south": (1, 0, 0),
        "east": (0, 0, -1),
        "west": (0, 0, 1),
        "top": (1, 0, 0),
        "bottom": (1, 0, 0)  
    },
    "right": {
        "north": (1, 0, 0),
        "south": (-1, 0, 0),
        "east": (0, 0, 1),
        "west": (0, 0, -1),
        "top": (-1, 0, 0),
        "bottom": (-1, 0, 0)
    },
    "behind": {
        "top": (0, 0, -1),
        "bottom": (0, 0, -1)    
    },
    "above": {
        "bottom_north": (0, 1, 0),
        "bottom_south": (0, 1, 0),
        "bottom_east": (0, 1, 0),
        "bottom_west": (0, 1, 0)
    }
}

# delta values by which pitch/yaw values should be added to modify view based on direction
view_deltas = {
    "ahead": (-30, 0),
    "left": (-15, -35),
    "right": (-15, 30),
    "behind": (0, 0),
    "above_bottom": (30, 0),
    "ahead_bottom": (60, 0),
    "ahead_top": (0, 0),
    "top": (-15, 0),
    "bottom": (15, 0)
}

yes_responses = ["yes", "yeah", "good", "ok", "great", "y", "cool"]
no_responses = ["no", "nope", "sorry", "wrong", "incorrect", "bad"]

ordinal_strs = {0: ['1st', 'first'], 1: ['2nd', 'second'], 2: ['3rd', 'third'], 3: ['4th', 'fourth'], 4: ['5th', 'fifth'], 5: ['6th', 'sixth'], 
                6: ['7th', 'seventh'], 7: ['8th', 'eighth'], 8: ['9th', 'ninth'], 9: ['10th', 'tenth']}

number_strs = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
dim_label_map = {'width': ['width', 'wide'], 'length': ['length', 'long'], 'height': ['height', 'high', 'tall']}

class State(Enum):
    START = 0                        # start state
    REQUEST_DESCRIPTION = 1          # request a description
    PARSE_DESCRIPTION = 2            # parse a description
    PLAN = 3                         # plan
    REQUEST_CLARIFICATION = 4        # request a clarification
    PARSE_CLARIFICATION = 5          # parse a clarification
    REQUEST_VERIFICATION = 6         # request a verification
    PARSE_VERIFICATION = 7           # parse a verification
    REQUEST_NEW_SHAPE_DEFINITION = 8 # request definition of new shape
    FINISH_NEW_SHAPE_DEFINITION = 9  # parse definition of new shape
    ADD_NEW_SHAPE_PARAMETER = 10     # add parameter to new shape definition
    FINISHED = 11                    # finished
    FAILURE = 12                     # failure

retry_responses = {State.PARSE_DESCRIPTION: ["Sorry, I had trouble understanding that. Could you explain it differently?", "Sorry, I don't understand. Can you try again?", "Sorry, I'm having trouble understanding. Could you reword that?"],
                   State.PLAN: ["Sorry, I'm not able to do that. Could we try again?", "Sorry, I'm not able to build that. Could you reword that?", "Sorry, I can't do that. Could you explain it differently?"],
                   State.PARSE_CLARIFICATION: ["Sorry, I had trouble understanding that.", "Sorry, I don't understand.", "Sorry, I'm having trouble understanding."],
                   State.PARSE_VERIFICATION: ["Sorry, what?", "Sorry, what's that?", "Sorry, I don't understand."]}

failure_responses = ["Something went wrong... Sorry about that. I can't recover from these types of failures yet.", "Sorry. An error occurred. I can't recover from this yet.", "Sorry; something went wrong, and I can't fix this right now. I hope to be able to in the future."]

class DialogueState:
    def __init__(self, state, input=None, output=None, parse=None, response=None, execute_status=None, blocks_in_grid={}):
        self.state = state
        self.input = input
        self.output = output
        self.parse = parse
        self.planner_response = response
        self.execute_status = execute_status
        self.blocks_in_grid = undo_reformat(blocks_in_grid)

    def __str__(self):
        """ String representation of a dialogue state, including input/output text, semantic parse, and plan at this state. """
        print_str = "State: "+str(self.state)
        if self.input is not None:
            print_str += "\nInput: "+str(self.input)
        print_str += "\nOutput: "+str(self.output)
        if self.parse is not None:
            print_str += "\nParse: "+str(self.parse)
        if self.planner_response is not None:
            print_str += "\nPlanner response:"+("\n" if self.planner_response is not None else "")+str(self.planner_response).strip()
        if self.execute_status is not None:
            print_str += "\nPlanner execution status: "+str(self.execute_status)
        print_str += "\nBlocks in grid: "+str(self.blocks_in_grid)
        return print_str

    def as_json(self):
        return {"Dialogue State": self.state.name, "Input Text": self.input, "Output Text": self.output, "Semantic Parse": self.parse, "Planner Response": self.planner_response.as_json() if self.planner_response is not None else None, "Plan Execution Status": self.execute_status}

class DialogueManager:
    def __init__(self, all_observations, ah):
        """ Initializes a dialogue manager for a given agent. """
        # agent host handle of the player this dialogue manager is for
        self.agent_host = ah

        # semantic parser
        self.parser = self.init_parser()
        self.last_successful_input = None
        self.last_successful_parse = None                # last (successful) semantic parse
        self.last_successful_parse_by_parts = None
        self.current_shapes = []
        self.built_shapes = []
        self.successfully_parsed_inputs = []  # list of successfully parsed inputs; a join of all elements should be fed to parser for every call for incremental parsing

        # planner
        self.last_planner_response = None  # last (successful) plan
        self.block_id_map = {}             # dict of blocks in grid to their unique ID identifiers
        self.newest_block_id = 1000        # counter for new block IDs that might need to be assigned
        self.blocks_in_grid = None         # dict of existing blocks in grid

        # dialogue manager
        self.next_state = State.START                                               # next dialogue state
        self.dialogue_history = [DialogueState(State.START)]                        # history of dialogue states
        self.attempts = {"description": 0, "verification": 0, "clarification": 0}   # counter of attempt types
        self.system_text = ""                                                       # system text to be pushed to chat
        self.clarification_questions = []
        self.clarification_in_progress = False

        # begin a dialogue
        self.parse(all_observations, "")

    def init_parser(self):
        return RuleBasedParser()

    def send_chat(self):
        """ Pushes the system text to the Minecraft chat interface. """
        sendCommand(self.agent_host, 'chat '+self.system_text)

    def parse(self, all_observations, text, pitch=0, yaw=0):
        """ Calls the dialogue manager to parse an input Architect utterance and handle it appropriately according to the dialogue manager's current dialogue state. """
        print("DialogueManager::received text:", text)

        # State: request additional description
        if self.next_state == State.REQUEST_DESCRIPTION:
            self.last_successful_input = None
            self.last_successful_parse = None
            self.clarification_in_progress = False
            self.system_text = random.choice(["Okay, what's next?", "Okay, now what?", "What are we doing next?"])
            self.append_to_history(DialogueState(State.REQUEST_DESCRIPTION, output=self.system_text, blocks_in_grid=self.blocks_in_grid), all_observations)
            self.next_state = State.PARSE_DESCRIPTION
            self.send_chat()
            return

        # State: start; ask for initial description
        if self.next_state == State.START:
            self.goto_default_loc()
            self.system_text = random.choice(["Hi Architect, what are we building today?", "I'm ready! What are we building?", "Hello! What are we building?", "Hello Architect, I'm ready!"])
            self.append_to_history(DialogueState(State.START, output=self.system_text, blocks_in_grid=self.blocks_in_grid), all_observations)
            self.next_state = State.PARSE_DESCRIPTION
            self.send_chat()
            return

        # State: parse a provided description
        if self.next_state == State.PARSE_DESCRIPTION:
            if any(substr in text.lower() for substr in ["done", "finished", "complete"]):
                self.system_text = random.choice(["Awesome!", "Perfect!", "Great!", "Thanks!"])
                self.append_to_history(DialogueState(State.REQUEST_DESCRIPTION, output=self.system_text, blocks_in_grid=self.blocks_in_grid), all_observations)
                self.next_state = State.FINISHED
                self.send_chat()
                self.parse(all_observations, "", pitch, yaw)
                return 

            if len(self.successfully_parsed_inputs) > 0:
                if not self.successfully_parsed_inputs[-1].strip().endswith('.'):
                    self.successfully_parsed_inputs[-1] = self.successfully_parsed_inputs[-1].strip()+'.'
                text = self.successfully_parsed_inputs[-1]+" "+text

            parse, current_shapes, parse_by_parts = self.parser.parse(text, switch_left_right=switch_left_right)
            ds = DialogueState(State.PARSE_DESCRIPTION, input=text, parse=parse, blocks_in_grid=self.blocks_in_grid)

            self.attempts["description"] += 1
            self.attempts["verification"] = 0

            # TODO: verify well-formedness of semantic parse ?
            if parse is None or len(parse) < 1:
                self.check_for_failure(ds)
                self.append_to_history(ds, all_observations)
                self.send_chat()
                if self.next_state == State.FAILURE:
                    self.parse(all_observations, "", pitch, yaw)
                return

            self.last_successful_input = text
            self.last_successful_parse = parse
            self.last_successful_parse_by_parts = parse_by_parts
            self.current_shapes = current_shapes
            self.append_to_history(ds, all_observations)
            self.next_state = State.PLAN

        # State: produce and execute a plan
        if self.next_state == State.PLAN:
            self.system_text = random.choice(["Okay.", "", "Let me try."])
            ds = DialogueState(State.PLAN, blocks_in_grid=self.blocks_in_grid)
            existing_blocks = self.get_blocks_in_grid_repr()

            print("DialogueManager::semantic parse to planner:", self.last_successful_parse)
            print("DialogueManager::blocks_in_grid to planner:", existing_blocks)

            # produce a plan
            try:
                response =  planner_utils.getPlans(human_input=self.last_successful_parse, existing_blocks=existing_blocks)
            except Exception:
                print("DialogueManager::planner exception occurred")
                traceback.print_exc(file=sys.stdout)
                self.last_planner_response = None
                if self.clarification_in_progress:
                    self.attempts["clarification"] = 999
                self.next_state = State.PARSE_DESCRIPTION
                self.check_for_failure(ds)
                self.append_to_history(ds, all_observations)
                self.send_chat()
                if self.next_state == State.FAILURE:
                    self.parse(all_observations, "", pitch, yaw)
                return

            ds.planner_response = response
            self.append_to_history(ds, all_observations)
            ds.planner_response = None

            # planner returned a successful plan
            if response.responseFlag == 'COMPLETED':
                if len(response.plan) == 0:
                    print("DialogueManager::empty complete plan received from planner")
                    if self.clarification_in_progress:
                        self.attempts["clarification"] = 999
                    self.next_state = State.PARSE_DESCRIPTION
                    self.check_for_failure(ds)
                    self.append_to_history(ds, all_observations)
                    self.send_chat()
                    if self.next_state == State.FAILURE:
                        self.parse(all_observations, "", pitch, yaw)
                    return

                self.last_planner_response = response
                ds.output = self.system_text

                if len(self.system_text) > 0:
                    self.send_chat()

                # execute the plan and return to the default starting location
                execute_status, last_pitch, last_yaw = self.execute_plan(pitch, yaw, all_observations)
                updated_pitch, updated_yaw, _ = self.update_blocks_in_grid(all_observations)
                last_pitch = updated_pitch if updated_pitch is not None else last_pitch
                last_yaw = updated_yaw if updated_yaw is not None else last_yaw
                print("DialogueManager::execute_plan returned with status:", execute_status)

                execute_status, _, _ = self.execute_plan(last_pitch, last_yaw, all_observations, verify=True)
                self.update_blocks_in_grid(all_observations)
                print("DialogueManager::verify_plan returned with status:", execute_status)

                ds.execute_status = execute_status    
                self.goto_default_loc()  
            
                # plan executed successfully
                if execute_status == "SUCCESS":
                    global N_SHAPES
                    N_SHAPES += 1

                    self.built_shapes = self.current_shapes
                    self.current_shapes = []
                    self.attempts["description"] = 0
                    self.append_to_history(ds, all_observations)
                    print(self.built_shapes)
                    self.successfully_parsed_inputs.append(self.last_successful_input)
                    self.next_state = State.REQUEST_VERIFICATION

                # plan execution failed
                else:
                    if self.clarification_in_progress:
                        self.attempts["clarification"] = 999
                    self.next_state = State.PARSE_DESCRIPTION
                    self.check_for_failure(ds, append_text=True)
                    self.append_to_history(ds, all_observations)
                    self.send_chat()
                    if self.next_state == State.FAILURE:
                        self.parse(all_observations, "", pitch, yaw)
                    return

            elif response.responseFlag == 'MISSING' and len(response.missing) > 0:
                self.attempts["description"] = 0
                self.attempts["clarification"] = 0
                self.last_planner_response = response
                self.append_to_history(ds, all_observations)
                self.clarification_questions = generate_clarification_questions(self.last_planner_response.missing, self.current_shapes, self.built_shapes)
                self.next_state = State.REQUEST_CLARIFICATION

            else:
                self.last_planner_response = None
                if self.clarification_in_progress:
                    self.attempts["clarification"] = 999
                self.next_state = State.PARSE_DESCRIPTION
                self.check_for_failure(ds)
                self.append_to_history(ds, all_observations)
                self.send_chat()
                if self.next_state == State.FAILURE:
                    self.parse(all_observations, "", pitch, yaw)
                return

        # State: request verification from the user
        if self.next_state == State.REQUEST_VERIFICATION:
            self.system_text = random.choice(["How's that?", "Like this?", "Is this right?"])
            self.send_chat()
            self.append_to_history(DialogueState(State.REQUEST_VERIFICATION, output=self.system_text, blocks_in_grid=self.blocks_in_grid), all_observations)
            self.next_state = State.PARSE_VERIFICATION
            return

        # State: parse verification from the user
        if self.next_state == State.PARSE_VERIFICATION:
            self.attempts["verification"] += 1
            ds = DialogueState(State.PARSE_VERIFICATION, input=text, blocks_in_grid=self.blocks_in_grid)

            if any(substring in text for substring in yes_responses):
                self.append_to_history(ds, all_observations)
                self.next_state = State.REQUEST_DESCRIPTION
                self.parse(all_observations, "", pitch, yaw)
                return

            elif any(substring in text for substring in no_responses):
                self.attempts["description"] = 999
                self.check_for_failure(ds)
                self.append_to_history(ds, all_observations)
                self.send_chat()
                self.parse(all_observations, "", pitch, yaw)
                return

            self.next_state = State.PARSE_VERIFICATION
            self.check_for_failure(ds)
            self.append_to_history(ds, all_observations)
            self.send_chat()
            if self.next_state == State.FAILURE:
                self.parse(all_observations, "", pitch, yaw)
            return

        # State: request clarification from the user
        if self.next_state == State.REQUEST_CLARIFICATION:
            self.attempts["clarification"] += 1
            self.clarification_in_progress = True
            _, clarification_question = self.clarification_questions[0]
            self.system_text = clarification_question
            self.append_to_history(DialogueState(State.REQUEST_CLARIFICATION, output=self.system_text, blocks_in_grid=self.blocks_in_grid), all_observations)
            self.next_state = State.PARSE_CLARIFICATION
            self.send_chat()
            return

        if self.next_state == State.PARSE_CLARIFICATION:
            ds = DialogueState(State.PARSE_CLARIFICATION, input=text, blocks_in_grid=self.blocks_in_grid)
            missing_queries, _ = self.clarification_questions[0]
            self.next_state = State.REQUEST_CLARIFICATION
            self.system_text = ""
            
            augmentation, unhandled_queries = get_augmentation(text, missing_queries)
            print("\nDialogueManager::generated augmentation:", augmentation)
            augmented_text = augment_text(self.last_successful_input, missing_queries, augmentation, self.last_successful_parse_by_parts)
            print("DialogueManager::final augmented input:", augmented_text)

            if augmented_text is not None:
                parse, current_shapes, parse_by_parts = self.parser.parse(augmented_text, switch_left_right=switch_left_right)
                ds.parse = parse

                if parse is None or len(parse) < 1:
                    self.check_for_failure(ds)
                    self.append_to_history(ds, all_observations)
                    self.send_chat()
                    if self.next_state == State.FAILURE:
                        self.parse(all_observations, "", pitch, yaw)
                    return

                self.attempts["clarification"] = 0
                self.clarification_questions.pop(0)
                self.last_successful_input = augmented_text
                self.last_successful_parse = parse
                self.last_successful_parse_by_parts = parse_by_parts
                self.current_shapes = current_shapes

                if len(unhandled_queries) > 0:
                    remaining_questions = generate_clarification_questions(unhandled_queries, self.current_shapes, self.built_shapes)
                    self.clarification_questions = remaining_questions.extend(self.clarification_questions)

                if len(self.clarification_questions) < 1:
                    self.next_state = State.PLAN
                    self.append_to_history(ds, all_observations)
                    self.parse(all_observations, "", pitch, yaw)
                    return 
            
            if augmented_text is None:
                self.check_for_failure(ds)

            self.append_to_history(ds, all_observations)
            if len(self.system_text) > 0:
                self.send_chat()
            self.parse(all_observations, "", pitch, yaw)
            return

        # State: system failure
        if self.next_state == State.FAILURE:
            if self.dialogue_history[-1].state != State.FAILURE:
                self.system_text = "This session has failed unexpectedly. Please restart the mission and try again."
                self.append_to_history(DialogueState(State.FAILURE, input=text, output=self.system_text, blocks_in_grid=self.blocks_in_grid), all_observations)
                self.send_chat()
            return

        # State: game finished
        if self.next_state == State.FINISHED:
            ds = DialogueState(State.FINISHED, input=text, blocks_in_grid=self.blocks_in_grid)
            if self.dialogue_history[-1].state == State.FINISHED:
                self.system_text = "This session is complete! Please start a new mission to continue playing."
                ds.output = self.system_text
                self.send_chat()
            self.append_to_history(ds, all_observations)
            return

    def goto_default_loc(self):
        """ Teleports the agent to the default starting location. Should be used after executing every Architect instruction. """
        teleportMovement(self.agent_host, teleport_x=default_loc["x"], teleport_y=default_loc["y"], teleport_z=default_loc["z"])
        setPitchYaw(self.agent_host, pitch=0.0, yaw=0.0)

    def append_to_history(self, state, all_observations):
        """ Appends a dialogue state to the history of dialogue states. """
        self.dialogue_history.append(state)
        all_observations[-1][0].append(state.as_json())
        self.print_state(state)

    def check_for_failure(self, ds, append_text=False):
        """ Checks if the dialogue system has exceeded the number of attempts from the user; if so, puts the system in an endless failure state. """
        # critical failure
        if any(self.attempts[key] >= 999 for key in self.attempts):
            self.system_text = random.choice(failure_responses)
            self.next_state = State.FAILURE
        else:
            self.system_text = random.choice(retry_responses[ds.state])
            if self.attempts["description"] >= ATTEMPT_LIMIT or self.attempts["clarification"] >= ATTEMPT_LIMIT or self.attempts["verification"] >= ATTEMPT_LIMIT:
                self.system_text = "Sorry, attempt limit exceeded. I'm giving up!"
                self.next_state = State.FAILURE

        ds.output = (ds.output+"\n"+self.system_text).strip() if append_text else self.system_text

    def execute_plan(self, pitch, yaw, all_observations, verify=False):
        """ Executes the last successful plan. """
        # no plan exists
        if self.last_planner_response is None:
            print("execute_plan::Error: last plan is undefined!")
            return "FAILURE", None, None

        # empty plan (this failure case should be caught before execution)
        if len(self.last_planner_response.plan) < 1:
            print("execute_plan::Warning: execute_plan was called, but the last plan was empty!")
            return "FAILURE", None, None

        plan_list = self.last_planner_response.plan if not verify else get_executed_plan_result(self.blocks_in_grid, self.last_planner_response.plan)
        last_pitch, last_yaw = pitch, yaw

        if verbose:
            print("\nexecute_plan::"+("executing" if not verify else "verifying"), "the plan:", self.last_planner_response.plan)

        # execute the plan
        for (action, block_id, x, y, z, color) in plan_list:
            # trying to putdown in an occupied location
            if not verify and action == "putdown" and not location_is_empty(self.blocks_in_grid, x,y,z):
                print("execute_plan::Error: 'putdown' action for non-empty location")
                return "FAILURE", last_pitch, last_yaw

            # trying to remove a block from an empty location
            if not verify and action == "remove" and location_is_empty(self.blocks_in_grid, x,y,z):
                print("execute_plan::Error: 'remove' action for empty location")
                return "FAILURE", last_pitch, last_yaw

            if not verify or (action == 'putdown' and location_is_empty(self.blocks_in_grid, x, y, z)) or (action == 'remove' and not location_is_empty(self.blocks_in_grid, x, y, z)):
                # find an unoccupied location, pitch, yaw to teleport the agent to
                tx, ty, tz, t_pitch, t_yaw = find_teleport_location(self.blocks_in_grid, x, y, z, action)
                
                # failed to find valid location
                if tx is None:
                    print("execute_plan::Error executing plan")
                    # TODO: what to do here?
                    return "FAILURE", last_pitch, last_yaw

                updated = False
                num_attempts = 0
                last_valid_pitch, last_valid_yaw = None, None

                while not updated and num_attempts < ATTEMPT_LIMIT:
                    self.execute_action(action=action, tx=tx, ty=ty, tz=tz, t_pitch=t_pitch if t_pitch != last_pitch else None, t_yaw=t_yaw if t_yaw != last_yaw else None, color=color)
                    pitch_new, yaw_new, updated = self.update_blocks_in_grid(all_observations)
                    last_valid_pitch = pitch_new if pitch_new is not None else last_valid_pitch
                    last_valid_yaw = yaw_new if yaw_new is not None else last_valid_yaw
                    num_attempts += 1

                last_pitch, last_yaw = last_valid_pitch, last_valid_yaw
                self.update_block_ids(action, block_id, x, y, z)

        return "SUCCESS", last_pitch, last_yaw

    def execute_action(self, action, tx, ty, tz, t_pitch, t_yaw, color):
        """ Executes an action using the agent. """
        if verbose:
                print("execute_plan::teleporting to:", tx, ty, tz, t_pitch, t_yaw, "to", action, color)

        # teleport the agent
        teleportMovement(self.agent_host, teleport_x=tx, teleport_y=ty, teleport_z=tz)

        # choose block color to be placed (if putdown)
        if action == 'putdown':
            chooseInventorySlot(self.agent_host, color_map[color])

        # set agent's pitch and yaw
        setPitchYaw(self.agent_host, pitch=t_pitch, yaw=t_yaw)

        # perform the action
        performAction(self.agent_host, action)

    def update_blocks_in_grid(self, all_observations, debug=False):
        """ Updates the blocks in grid representation with any changes received from recent observations. """
        blocks_in_grid_new, pitch_new, yaw_new = None, None, None
        num_attempts = 0

        if debug: 
            return pitch_new, yaw_new

        # keep polling for observations until one returns updated blocks in grid (or times out)
        while blocks_in_grid_new is None and num_attempts < 999:
            world_state = self.agent_host.getWorldState()

            # retrieve relevant information from the most recent observations
            for observation in world_state.observations:
                if observation.text is not None:
                    all_observations.append(([], observation))
                    obsrv = json.loads(observation.text)
                    blocks_in_grid_new = obsrv.get("BuilderGridAbsolute", blocks_in_grid_new)
                    pitch_new = obsrv.get("Pitch", pitch_new) 
                    yaw_new = obsrv.get("Yaw", yaw_new)

            num_attempts += 1

        # update blocks in grid
        updated = False
        if blocks_in_grid_new is not None:
            self.blocks_in_grid = reformat_builder_grid(blocks_in_grid_new)
            if verbose:
                print("execute_plan::updated blocks_in_grid after polling for", num_attempts, "attempts:", self.blocks_in_grid)
            updated = True

        return pitch_new, yaw_new, updated

    def update_block_ids(self, action, block_id, x, y, z):
        """ Updates the map of locations in the builder grid with their respective planner-assigned block IDs given a planner-returned instruction. """
        bid = int(block_id.replace('b',''))

        # record block id, or remove it if the block is being picked up
        if action == 'putdown':
            self.block_id_map[(x,y,z)] = block_id
        else:
            try:
                self.block_id_map.pop((x,y,z))
            except KeyError:
                print("update_block_ids::Warning: tried to remove non-existent block id for", (x,y,z), "from id map!")

    def get_block_id(self, x, y, z):
        """ Gets the unique block ID for a given location in the grid. If an ID does not exist for that location, assigns a new ID and returns it. """
        if self.block_id_map.get((x,y,z)) is None:
            new_id = self.newest_block_id
            self.block_id_map[(x,y,z)] = 'b'+str(new_id)
            self.newest_block_id += 1

        return self.block_id_map[(x,y,z)]

    def get_blocks_in_grid_repr(self):
        """ Produces a string representation of the existing blocks in the grid, to be used as input by the planner. """
        blocks_in_grid_repr = ""
        for x in self.blocks_in_grid:
            for z in self.blocks_in_grid[x]:
                for y in self.blocks_in_grid[x][z]:
                    color = self.blocks_in_grid[x][z][y]
                    block_id = self.get_block_id(x,y,z)
                    blocks_in_grid_repr += "("+block_id+","+str(x-x_min_build)+","+str(y-y_min_build)+","+str(z-z_min_build)+","+color+")^"

        return blocks_in_grid_repr[:-1] if len(blocks_in_grid_repr) > 0 else None

    def print_state(self, state):
        print("\nDialogueManager::\n"+str(state)+"\n")

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
                      <Placement x = "0" y = "6" z = "-7" pitch="45"/>
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

def initialize_agents(args):
    builder_ip, builder_port = args["builder_ip_addr"], args["builder_port"]
    architect_ip, architect_port = args["architect_ip_addr"], args["architect_port"]
    fixed_viewer_ip, fixed_viewer_port, num_fixed_viewers = args["fixed_viewer_ip_addr"], args["fixed_viewer_port"], args["num_fixed_viewers"]

    # Create agent hosts:
    agent_hosts = []
    for i in range(3+num_fixed_viewers):
        agent_hosts.append(MalmoPython.AgentHost())

    # Set observation policy for builder
    agent_hosts[1].setObservationsPolicy(
        MalmoPython.ObservationsPolicy.KEEP_ALL_OBSERVATIONS)

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

def cwc_run_mission(args):
    print("Calling cwc_run_builder_demo with args:", args, "\n")
    start_time = time.time()

    # initialize the agents
    agent_hosts, client_pool = initialize_agents(args)

    num_fixed_viewers = args["num_fixed_viewers"]
    draw_inventory_blocks = args["draw_inventory_blocks"]
    existing_is_gold = args["existing_is_gold"]

    # experiment ID
    player_ids = "B" + args["builder_id"] + "-A" + args["architect_id"]
    config_id = os.path.basename(args["gold_config"]).replace(".xml", "")
    experiment_time = str(int(round(time.time() * 1000)))
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

    # poll for observations
    timed_out = False

    dm = None
    all_observations = []
    blocks_in_grid, pitch, yaw = None, None, None

    while not timed_out:
        for i in range(3+num_fixed_viewers):
            ah = agent_hosts[i]
            world_state = ah.getWorldState()

            if not world_state.is_mission_running:
                timed_out = True

            elif i == 1 and world_state.number_of_observations_since_last_state > 0:
                chat_instruction = None

                # get the next chat instruction & corresponding world state
                for observation in world_state.observations:
                    all_observations.append(([], observation))
                    if observation.text is not None:
                        obsrv = json.loads(observation.text)
                        print("Observation processed:")
                        if verbose:
                            print(json.dumps(obsrv, indent=4), '\n')

                        chat_instruction = obsrv.get("Chat", chat_instruction) 
                        blocks_in_grid = obsrv.get("BuilderGridAbsolute", blocks_in_grid)
                        pitch = obsrv.get("Pitch", pitch) 
                        yaw = obsrv.get("Yaw", yaw)

                        if obsrv.get("Chat") is not None:
                            print("Chat:", chat_instruction)

                        if obsrv.get("BuilderGridAbsolute") is not None:
                            print("BuilderGridAbsolute:", obsrv["BuilderGridAbsolute"])

                        print()

                # initialize the dialogue manager
                if dm is None:
                    dm = DialogueManager(all_observations, agent_hosts[1])

                if chat_instruction is not None:
                    utterances = ""
                    for utterance in chat_instruction:
                        if "<Architect>" in utterance:
                            utterances += utterance.replace("<Architect>", "")+" "

                    if len(utterances) > 0:
                        dm.blocks_in_grid = reformat_builder_grid(blocks_in_grid)
                        dm.parse(all_observations, utterances, pitch, yaw)

    time_elapsed = time.time() - start_time

    print("Mission has been quit. All world states:\n")

    all_world_states = []
    for dialogue_states, observation in all_observations:
        world_state = json.loads(observation.text)
        world_state["Timestamp"] = observation.timestamp.replace(microsecond=0).isoformat(' ')
        world_state["DialogueManager"] = dialogue_states
        debug_utils.prettyPrintObservation(world_state)
        all_world_states.append(world_state)

    raw_observations = {
        "WorldStates": all_world_states,
        "TimeElapsed": time_elapsed,
        "NumFixedViewers": num_fixed_viewers
    }

    if write_logfiles:
        io_utils.writeJSONtoLog(experiment_id, "raw-observations.json", raw_observations)

    m, s = divmod(time_elapsed, 60)
    h, m = divmod(m, 60)
    print("Done! Mission time elapsed: %d:%02d:%02d (%.2fs)\n" % (h, m, s, time_elapsed))

    print("Waiting for mission to end...")
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

    time.sleep(2)

def reformat_builder_grid(blocks_in_grid):
    """ Reformats BuilderGridAbsolute blocks into a nested dictionary of coordinate values, ordered x, z, y. """
    blocks_dict = {}

    if blocks_in_grid is not None:
        for block in blocks_in_grid:
            x = block["X"]
            y = block["Y"]
            z = block["Z"]
            color = block["Type"].replace("cwc_minecraft_","").replace("_rn","")

            if blocks_dict.get(x) is None:
                blocks_dict[x] = {}

            if blocks_dict[x].get(z) is None:
                blocks_dict[x][z] = defaultdict(str)

            blocks_dict[x][z][y] = color

    return blocks_dict

def undo_reformat(blocks_in_grid):
    """ Reformats nested dictionary of blocks in grid back to list format. """
    blocks_list = []

    if blocks_in_grid is not None:
        for x in blocks_in_grid:
            for z in blocks_in_grid[x]:
                for y in blocks_in_grid[x][z]:
                    blocks_list.append((x,y,z,blocks_in_grid[x][z][y]))

    return blocks_list

def find_teleport_location(blocks_in_grid, x, y, z, action):
    """ Finds a feasible (open) location, pitch, and yaw to teleport the agent to such that a block can be placed at (x,y,z). """
    if verbose:
        print("\nfind_teleport_location::finding feasible location for block:", x, y, z, "where blocks_in_grid:", blocks_in_grid)

    # check for unoccupied locations that the agent can teleport to: south/east/north/west of location; above/below location; below and to the south/east/north/west of location
    for px, py, pz, direction in [(x, y, z-1, "south"), (x-1, y, z, "east"), (x, y, z+1, "north"), (x+1, y, z, "west"), (x, y+1, z, "top"), (x, y-2, z, "bottom"), \
                                  (x, y+1, z-1, "top_south"), (x-1, y+1, z, "top_east"), (x, y+1, z+1, "top_north"), (x+1, y+1, z, "top_west"), \
                                  (x, y-1, z-1, "bottom_south"), (x-1, y-1, z, "bottom_east"), (x, y-1, z+1, "bottom_north"), (x+1, y-1, z, "bottom_west")]:
        
        # location is too low
        if py < 1:
            if verbose:
                print("find_teleport_location::", px, py, pz, direction, "is too low!")
            continue 

        # location is occupied
        if not location_is_empty(blocks_in_grid, px, py, pz) or not location_is_empty(blocks_in_grid, px, py+1, pz):
            if verbose:
                print("find_teleport_location::", px, py, pz, direction, "is occupied!")
            continue

        # get default pitch/yaw (facing downwards, to place a block on top of a surface)
        pitch = pitch_dirs.get(direction)
        yaw = yaw_dirs.get(direction, 0)

        # return the default pitch/yaw values if the the block can be placed feasibly with the default view
        if action == 'remove' or (direction == "bottom" and not location_is_empty(blocks_in_grid, x, y+1, z)) or ("_" not in direction and not location_is_empty(blocks_in_grid, x, y-1, z)):
            if verbose: 
                print("find_teleport_location::", px, py, pz, direction, "with default view is eligible!")
            return px+0.5, py, pz+0.5, pitch, yaw

        # check if a block can feasibly be placed from a location in the above or below planes
        if '_' in direction:
            general_dir = 'bottom' if 'bottom' in direction else 'top'

            # cannot place a block from above if the location is obscured by another block from above
            if general_dir == 'top' and not location_is_empty(blocks_in_grid, x, y+1, z):
                if verbose:
                    print("find_teleport_location::ineligible direction", direction, "-- view is blocked!")
                continue

            # consider ahead, above directions from below; consider only ahead direction from above
            view_keys = ["ahead", "above"] if general_dir == 'bottom' else ["ahead"]

            for key in view_keys:
                dx, dy, dz = coord_deltas[key][direction]
                if verbose:
                    print("find_teleport_location::checking location", x+dx, y+dy, z+dz, "using view", key, "while facing from the", direction)

                # check if block can feasibly be placed from this location (i.e., an adjacent block exists in that direction)
                # if so, return this with appropriate pitch/yaw modifications
                if not location_is_empty(blocks_in_grid, x+dx, y+dy, z+dz):
                    if verbose:
                        print("find_teleport_location::found adjacent block with view", key, "while facing from the", direction)

                    d_pitch, d_yaw = view_deltas[key+'_'+general_dir]
                    return px+0.5, py, pz+0.5, pitch+d_pitch, yaw+d_yaw

        # check if a block can feasibly be placed from any of its six immediate sides
        else:
            for key in ["ahead", "left", "right", "behind"]:
                if coord_deltas[key].get(direction) is None:
                    continue

                dx, dy, dz = coord_deltas[key][direction]
                if verbose:
                    print("find_teleport_location::Checking location", x+dx, y+dy, z+dz, "using view", key, "while facing from the", direction)

                # cannot place a block if the location is obscured by another block from above
                if not location_is_empty(blocks_in_grid, x, y+1, z):
                    if verbose:
                        print("find_teleport_location::ineligible direction", direction, "-- view is blocked!")
                    continue

                # check if block can feasibly be placed from this location (i.e., an adjacent block exists in that direction)
                # if so, return this with appropriate pitch/yaw modifications
                if not location_is_empty(blocks_in_grid, x+dx, y+dy, z+dz):
                    if verbose:
                        print("find_teleport_location::Found adjacent block with view", key, "while facing from the", direction)

                    d_pitch, d_yaw = view_deltas[key] 
                    final_yaw = yaw+d_yaw

                    if direction == "top" or direction == "bottom":
                        d_pitch, _ = view_deltas[direction]
                        final_yaw = yaw_dirs[relative_to_cardinal[key]]

                    final_pitch = pitch+d_pitch
                    return px+0.5, py, pz+0.5, final_pitch, final_yaw

    # we went through all that effort and still found nothing :(
    print("find_teleport_location::Error: no feasible location found!")
    return None, None, None, None, None

def location_is_empty(blocks_in_grid, x, y, z):
    """ Checks whether or not a grid location is empty given the current world state. """
    blocks_list = blocks_in_grid.get(x, {}).get(z, {})
    return y not in blocks_list and y > 0

def get_executed_plan_result(blocks_in_grid, plan):
    """ Computes the net changes that would occur by executing a series of instructions. """
    executed_plan_grid = {}

    for (action, block_id, x, y, z, color) in plan:
        if color == 'violet': #FIXME when planner fixes this
            color = 'purple'

        if x not in executed_plan_grid:
            executed_plan_grid[x] = {}

        if y not in executed_plan_grid[x]:
            executed_plan_grid[x][y] = {}

        if z not in executed_plan_grid[x][y]:
            executed_plan_grid[x][y][z] = {'red': 0, 'orange': 0, 'yellow': 0, 'green': 0, 'blue': 0, 'purple': 0}

        if action == 'putdown':
            executed_plan_grid[x][y][z][color] += 1
        else:
            executed_plan_grid[x][y][z][color] -= 1

    plan_result = []
    for (action, block_id, x, y, z, color) in plan:
        color = 'purple' if color == 'violet' else color # FIXME! when it's fixed
        net_actions = executed_plan_grid[x][y][z]
        if net_actions[color] == -1 and blocks_in_grid.get(x, {}).get(z, {}).get(y) != color:
            continue

        if net_actions[color] != 0:
            plan_result.append(("putdown" if net_actions[color] == 1 else "remove", block_id, x, y, z, color))

    return plan_result

def shape_is_built(built_shapes, var):
    for _, built_var in built_shapes:
        if var == built_var:
            return True
    return False

def get_missing_queries(missing):
    missing_dict = {'dims': [], 'rels': []}
    for query in missing:
        key = 'rels' if 'Not-Connected' in query else 'dims'
        missing_dict[key].append(query)
    return missing_dict['dims']+([missing_dict['rels'][-1]] if len(missing_dict['rels']) > 0 else [])

def get_ordinal(shape, var, current_shapes):
    ordinal, total = -1, 0
    for existing_shape, existing_shape_var in current_shapes:
        if shape == existing_shape:
            total += 1
        if existing_shape_var == var:
            ordinal = total-1
    return "" if total == 1 else random.choice(ordinal_strs[ordinal])+" "

def get_previous_referent(var, current_shapes):
    referent = current_shapes[-1]
    for i in range(1, len(current_shapes)):
        _, existing_var = current_shapes[i]
        if var == existing_var:
            return current_shapes[i-1]

    print("get_previous_referent::Error: could not find referent shape in current_shapes:", current_shapes, "given var:", var)
    return None

def get_dim_values(response):
    response = "".join((char for char in response if char not in string.punctuation))

    # find %dx%d values and separate
    matches = re.findall('[0-9]+x[0-9]+', response)  
    response = separate(response, matches, 'x')

    return [s for s in response.split() if is_number(s)], response

def separate(response, substring_list, separator):
    for substring in substring_list:
        response = response.replace(substring, substring.split(separator)[0]+' '+separator+' '+substring.split(separator)[1])
    return response

def is_number(token):
    return token.isdigit() or token in number_strs

def get_dim_labels(response, queries, dim_values):
    if len(queries) == 1 and len(dim_values) == 1:
        return {queries[0][3]: dim_values[0]}

    dim_labels = {}
    value_idx = 0
    unassigned_values, unassigned_labels = [], []

    # "%x x %y x %z" and "%x by %y by %z" means width = %x, length = %y, height = %z
    i = 0
    tokens = response.lower().split()
    while i < len(tokens):
        if i < len(dim_values)-1 and is_number(tokens[i]) and any(tokens[i+1] == substr for substr in ['x', 'by']) and value_idx < len(dim_values):
            increment_idx = 0
            if dim_labels.get('length') is not None:
                print("get_dim_labels::Warning: duplicate length values")

            dim_labels['length'] = dim_values[value_idx]
            value_idx += 1
            increment_idx += 1

            if value_idx < len(dim_values):
                if dim_labels.get('width') is not None:
                    print("get_dim_labels::Warning: duplicate width values")

                dim_labels['width'] = dim_values[value_idx]
                value_idx += 1
                increment_idx += 2

            if i < len(tokens)-4 and value_idx < len(dim_values):
                if is_number(tokens[i+2]) and any(tokens[i+3] == substr for substr in ['x', 'by']):
                    if dim_labels.get('height') is not None:
                        print("get_dim_labels::Warning: duplicate height values")
                    dim_labels['height'] = dim_values[value_idx]
                    increment_idx += 2

            i += increment_idx

        elif is_number(tokens[i]):
            if len(unassigned_labels) > 0:
                if dim_labels.get(unassigned_labels[-1]) is not None:
                    print("get_dim_labels::Warning: duplicate", unassigned_labels[-1], "values")
                dim_labels[unassigned_labels.pop()] = tokens[i]
            else:
                unassigned_values.append(tokens[i])

        else:
            for key in dim_label_map:
                if tokens[i] in dim_label_map[key]:
                    if len(unassigned_values) > 0:
                        if dim_labels.get(key) is not None:
                            print("get_dim_labels::Warning: duplicate", key, "values")

                        dim_labels[key] = unassigned_values.pop()
                    else:
                        unassigned_labels.append(key)

        i += 1

    for key in ['length', 'width', 'height']:
        if key not in dim_labels and len(unassigned_values) > 0:
            dim_labels[key] = unassigned_values.pop(0)

    print("get_dim_labels::parsed the following dimensions:", dim_labels)
    return dim_labels

def get_dim_value_map(response, queries):
    dim_values, response = get_dim_values(response)
    return get_dim_labels(response, queries, dim_values)

def generate_clarification_questions(missing, current_shapes, built_shapes):
    missing_queries = get_missing_queries(missing)
    clarification_questions = []
    missing_rel_questions = []

    missing_shape_dims = OrderedDict()
    for missing_query in missing_queries:
        if 'dim' in missing_query:
            _, shape, var, dim = missing_query
            if (var, shape) not in missing_shape_dims.keys():
                missing_shape_dims[(var, shape)] = []
            missing_shape_dims[(var, shape)].append(missing_query)

        else:
            prefix = random.choice(["can you describe ", "could you tell me ", "can you tell me "])
            _, shape, var = missing_query
            shape_ordinal = get_ordinal(shape, var, current_shapes) 
            referent_shape, referent_var = get_previous_referent(var, current_shapes)
            suffix = " that you just built" if shape_is_built(built_shapes, referent_var) else " that you are building"
            optional_suffix = "other " if shape == referent_shape else ""
            missing_rel_questions.append(([missing_query], str("In more detail, "+prefix+"where the "+shape_ordinal+shape+" is placed with respect to the "+optional_suffix+referent_shape+suffix+", and how their blocks align?")))

    for key, missing_queries in missing_shape_dims.items():
        var, shape = key
        prefix = random.choice(["What is ", "What's ", "Can you describe ", "Could you tell me "])
        shape_ordinal = get_ordinal(shape, var, current_shapes)

        if (shape == 'rectangle' and len(missing_queries) == 2) or (shape == 'cuboid' and len(missing_queries) == 3):
            if prefix.startswith("What"):
                prefix = prefix.replace("is", "are").replace("'s", " are")
            clarification_questions.append((missing_queries, str(prefix+"the dimensions of the "+shape_ordinal+shape+"?")))
        else:
            for missing_query in missing_queries:
                clarification_questions.append(([missing_query], str(prefix+"the "+dim+" of the "+shape_ordinal+shape+"?")))

    clarification_questions.extend(missing_rel_questions)
    return clarification_questions

def get_augmentation(text, queries):
    if 'Not-Connected' in queries[0]:
        if text.strip().endswith('.'):
            text = text.strip()[:-1]
        return text, []

    _, shape, var, _ = queries[0]
    dim_value_map = get_dim_value_map(text, queries)

    if len(dim_value_map) < 1:
        print("get_augmentation::Error: could not parse any dimensions from text:", text)
        return None, []

    # square parameter descriptions
    if shape == 'square':
        if dim_value_map.get('size') is not None:
            return " size "+str(dim_value_map['size']), []
        if (dim_value_map.get('width') is None and dim_value_map.get('length') is None) or dim_value_map['width'] != dim_value_map['length']:
            print("get_augmentation::Error: cannot parse square dimensions from text:", text)
            return None, []
        return " size "+str(dim_value_map.get('width', dim_value_map['length'])), []

    # other shape parameter descriptions
    missing_str = ""
    unhandled_queries = []

    for missing_query in queries:
        dim = missing_query[3]
        if dim_value_map.get(dim) is None:
            print("get_augmentation::Warning: cannot identify dim", dim, "for shape", shape, "from text:", text)
            unhandled_queries.append(missing_query)
        else:
            missing_str += dim+" "+str(dim_value_map[dim])+" and "

    if len(missing_str) < 1:
        return None, []

    return missing_str[:-5], unhandled_queries

def augment_text(text, queries, augmentation, parse_by_parts):
    if augmentation is None:
        return None

    augmentation = augmentation.strip()
    print("augment_text::augmenting:", text, "with augmentation:", augmentation)

    split_text = [instr.strip() for instr in re.split(r'(\.| such that)', text.lower())]
    modified_input = ""
    parse_idx = 0

    if 'Not-Connected' in queries[0]:
        if text.strip().endswith('.'):
            text = text.strip()[:-1].strip()

        modified_input = text+" such that "+augmentation+"."
    else:
        _, shape, var, dim = queries[0]

        for fragment in split_text:
            if fragment == 'such that' or fragment == '.':
                parse_idx += 1

            elif parse_idx < len(parse_by_parts) and shape+'('+var+')' in parse_by_parts[parse_idx]:
                modified_input += augmentation+' '

            if fragment == '.':
                modified_input = modified_input.strip()

            modified_input += fragment+' '

    return modified_input.strip()

def teleportMovement(ah, teleport_x=None, teleport_y=None, teleport_z=None):
    """ Teleports the agent to a specific (x,y,z) location in the map. """
    sendCommand(ah, "tp " + str(teleport_x) + " " + str(teleport_y) + " " + str(teleport_z))
    time.sleep(1)

def setPitchYaw(ah, pitch=None, yaw=None):
    """ Sets the pitch and yaw of the agent. For efficiency, only set pitch/yaw to non-None values if they differ from the agent's current pitch/yaw values. """
    if yaw is not None:
        sendCommand(ah, "setYaw "+str(yaw))
        time.sleep(1)

    if pitch is not None:
        sendCommand(ah, "setPitch "+str(pitch))
        time.sleep(1)

def chooseInventorySlot(ah, index):
    """ Selects the given block color from the hotbar. """
    selection = "hotbar." + str(index)
    sendCommand(ah, selection+" 1")
    sendCommand(ah, selection+" 0")

def performAction(ah, action):
    """ Instructs agent to perform a given action with their hand. """
    action_type = 'use' if action == 'putdown' else 'attack'
    sendCommand(ah, action_type+' 1')
    time.sleep(0.1)
    sendCommand(ah, action_type+' 0')
    time.sleep(0.2)

def sendCommand(ah, command):
    """ Use this method to send all commands to the agent. """
    if SHOW_COMMANDS is True:
        print(command)
    ah.sendCommand(command)
