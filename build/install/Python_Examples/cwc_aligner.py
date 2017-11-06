# Align observations and screenshots

import json
from pprint import pprint
from os import listdir
from os.path import join

def align(obs_data_unalinged, screenshots_dir):

    # get states from json data
    all_world_states = obs_data_unalinged["all_world_states"]

    # get screenshots
    screenshots = listdir(screenshots_dir)

    screenshots = list(filter(lambda x: x.endswith(".png"), screenshots))
    assert len(screenshots)%2 == 0 # test that there are even number of screenshots (equal number from builder and architect)

    screenshots.sort()

    screenshots_paired = [] # each pair will be (architect screenshot, builder screenshot)
    for screenshots_pair in zip(screenshots[::2], screenshots[1::2]):
        assert "Architect" in screenshots_pair[0] # test that first screenshot is architect's
        assert "Builder" in screenshots_pair[1] # test that second screenshot is builder's
        screenshots_pair_dict = {
            "architect" : join(screenshots_dir, screenshots_pair[0]), # also finally obtain full path
            "builder": join(screenshots_dir, screenshots_pair[1]) # also finally obtain full path
        }
        screenshots_paired.append(screenshots_pair_dict)

    # align
    prev_game_state = ""
    all_world_states_aligned = []
    screenshots_paired_counter = 0

    for world_state in all_world_states:

        current_game_state = world_state["state"]

        if current_game_state != prev_game_state:
            # game state change only -- no screenshot to align to -- TODO: implement using state deltas once you have them as part of the state
            prev_game_state = current_game_state
            world_state["screenshots"] = {}
        else:
            # no game state change -- screenshots to align to
            world_state["screenshots"] = screenshots_paired[screenshots_paired_counter] # will also test if there are missing screenshots in case of an index out of bound error
            screenshots_paired_counter += 1

        all_world_states_aligned.append(world_state)

    assert screenshots_paired_counter == len(screenshots_paired) # test that there are no extra screenshots

    # return aligned json data
    return {"all_world_states_aligned": all_world_states_aligned}
