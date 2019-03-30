import numpy as np, sys, random
from scipy.spatial import distance

# NOTE: THIS CODE NEEDS TO BE MAINTAINED FOR BOTH PYTHON 2 AND 3 COMPATIBILITY

build_region_specs = { # FIXME: Import instead
    "x_min_build": -5,
    "x_max_build": 5,
    "y_min_build": 1,
    "y_max_build": 9,
    "z_min_build": -5,
    "z_max_build": 5
}

all_possible_rot_values = [0, 90, 180, -90, -180]
rot_matrices_dict = {}
for rot_value in all_possible_rot_values:
    theta_yaw = np.radians(-1 * rot_value)
    c, s = np.cos(theta_yaw), np.sin(theta_yaw)
    R_yaw = np.matrix([ [ c, 0, -s ], [ 0, 1, 0 ], [ s, 0, c ] ])
    rot_matrices_dict[rot_value] = R_yaw

def get_next_actions(all_next_actions, num_next_actions_needed, last_action, built_config, feasible_next_placements):
    """
    Args:
        all_next_actions: The diff between current state and goal state
        num_next_actions_needed: The number of next actions to sample from all possible next actions
        last_action: The point in space where the last action took place
        built_config: The built configuration
        feasible_next_placements: Whether or not to select from pool of feasible next placements only

    Returns:
        The appropriate next actions in terms of a reduced diff
    """
    assert num_next_actions_needed % 2 == 0 # an even split is needed between removals and placements

    all_next_removals = all_next_actions["built_minus_gold"]
    all_next_placements = all_next_actions["gold_minus_built"]

    # shuffle (out of place to avoid mutation)
    all_next_removals = random.sample(all_next_removals, len(all_next_removals))
    all_next_placements = random.sample(all_next_placements, len(all_next_placements))

    if feasible_next_placements:
        all_next_placements = list([x for x in all_next_placements if is_feasible_next_placement(x, built_config)])

    if last_action:
        # sort all next actions by distance from last action and pick top-k
        all_next_removals_sorted = sorted(all_next_removals, key = lambda x: euclidean_distance(x, last_action))
        all_next_placements_sorted = sorted(all_next_placements, key = lambda x: euclidean_distance(x, last_action))
    else:
        # try:
        #     assert all_next_removals == [] and all_next_placements != [] # at the very start of the game
        # except AssertionError:
        #     print("ASSERTION ERROR!")
        #     print(all_next_placements)
        #     print("\n\n")
        #     print(all_next_removals)
        all_next_removals_sorted = all_next_removals
        # most likely first block to be placed is on the lowest layer
        all_next_placements_sorted = sorted(all_next_placements, key = lambda x: x["y"]) # TODO: already sorted?

    next_removals = all_next_removals_sorted[:int(num_next_actions_needed/2)]
    next_placements = all_next_placements_sorted[:int(num_next_actions_needed/2)]

    return {
        "gold_minus_built": next_placements,
        "built_minus_gold": next_removals
    }

def is_feasible_next_placement(block, built_config, extra_check):
    # check if there is an existing block at block's location
    if extra_check and conflicting_block_exists(block, built_config):
        return False

    # check if block is on ground
    if block_on_ground(block):
        return True

    # check if block has a supporting block
    if block_with_support(block, built_config):
        return True
    else:
        return False

def conflicting_block_exists(block, built_config):
    for existing_block in built_config:
        if conflicts(existing_block, block):
            return True

    return False

def conflicts(existing_block, block):
    return existing_block["x"] == block["x"] and existing_block["y"] == block["y"] and existing_block["z"] == block["z"]

def block_on_ground(block):
    return block["y"] == 1

def block_with_support(block, built_config):
    for existing_block in built_config:
        if supports(existing_block, block):
            return True

    return False

def supports(existing_block, block):
    x_support = abs(existing_block["x"] - block["x"]) == 1 and existing_block["y"] == block["y"] and existing_block["z"] == block["z"]

    y_support = abs(existing_block["y"] - block["y"]) == 1 and existing_block["x"] == block["x"] and existing_block["z"] == block["z"]

    z_support = abs(existing_block["z"] - block["z"]) == 1 and existing_block["x"] == block["x"] and existing_block["y"] == block["y"]

    return x_support or y_support or z_support

def euclidean_distance(block_1, block_2):
    return distance.euclidean(
        [block_1["x"], block_1["y"], block_1["z"]],
        [block_2["x"], block_2["y"], block_2["z"]]
    )

def get_diff(gold_config, built_config):
    """
    Args:
        gold_config: Gold configuration
        built_config: Configuration built so far
        Both are lists of dicts. Each dict contains info on block type and block coordinates.

    Returns:
        A minimal diff in built config space -- in terms of placement and removal actions --
        to take the built config state to the goal config state

        All minimal diffs (each in both built and gold config space) with corresponding complementary info --
        complementary info would be the original built config, a perturbed config and the transformation to transform
        the former into the latter
    """

    # generate all possible perturbations of built config in the build region
    perturbations = generate_perturbations(built_config, gold_config = gold_config)

    # compute diffs for each perturbation
    diffs = list([diff(gold_config = gold_config, built_config = t.perturbed_config) for t in perturbations])

    # convert diffs back to actions in the built config space and not the perturbed config space
    # filter out perturbations that yield infeasible diff actions (those outside the build region)
    perturbations_and_diffs = list([x for x in list(zip(perturbations, diffs)) if is_feasible_perturbation(x[0], x[1])])

    # recompute diffs in gold config space
    orig_diffs = list([diff(gold_config = gold_config, built_config = x[0].perturbed_config) for x in perturbations_and_diffs])
    perturbations_diffs_and_orig_diffs = [x + (y,) for x, y in zip(perturbations_and_diffs, orig_diffs)]
    perturbations_and_diffs = list([(x[0], Diff(diff_built_config_space = x[1], diff_gold_config_space = x[2])) for x in perturbations_diffs_and_orig_diffs])

    # select perturbation with min diff
    min_perturbation_and_diff = min(perturbations_and_diffs, key = lambda t: len(t[1].diff_built_config_space["gold_minus_built"]) + len(t[1].diff_built_config_space["built_minus_gold"]))

    # get all minimal diffs
    diff_sizes = list([len(t[1].diff_built_config_space["gold_minus_built"]) + len(t[1].diff_built_config_space["built_minus_gold"]) for t in perturbations_and_diffs])
    min_diff_size = min(diff_sizes)

    perturbations_and_diffs_and_diff_sizes = list(zip(perturbations_and_diffs, diff_sizes))
    perturbations_and_minimal_diffs_and_diff_sizes = list([x for x in perturbations_and_diffs_and_diff_sizes if x[1] == min_diff_size])

    # reformat final output
    perturbations_and_minimal_diffs = list([PerturbedConfigAndDiff(perturbed_config=x[0][0], diff=x[0][1]) for x in perturbations_and_minimal_diffs_and_diff_sizes])

    return min_perturbation_and_diff[1].diff_built_config_space, perturbations_and_minimal_diffs

def is_feasible_perturbation(perturbed_config, diff):
    # NOTE: This function mutates `diff`. DO NOT CHANGE THIS BEHAVIOR!
    """
    Args:
        perturbed_config: PerturbedConfig
        diff: Dict
    """

    def find_orig_block(block, block_pairs):
        return next(x[1] for x in block_pairs if x[0] == block)

    for key, diff_config in list(diff.items()):
        if key == "built_minus_gold": # retrieve from original built config instead of applying inverse transform
            block_pairs = list(zip(perturbed_config.perturbed_config, perturbed_config.original_config))
            diff[key] = list([find_orig_block(x, block_pairs) for x in diff_config])
        else:
            diff[key] = invert_perturbation_transform(
                config = diff_config,
                perturbed_config = perturbed_config
            )

    return is_feasible_config(diff["gold_minus_built"])

def is_feasible_config(config):
    """
    Args:
        config: List of blocks
    """
    def is_feasible_block(d):
        if (build_region_specs["x_min_build"] <= d["x"] <= build_region_specs["x_max_build"]) and (build_region_specs["y_min_build"] <= d["y"] <= build_region_specs["y_max_build"]) and (build_region_specs["z_min_build"] <= d["z"] <= build_region_specs["z_max_build"]):
            return True
        else:
            return False

    return all(is_feasible_block(block) for block in config)

def diff(gold_config, built_config):
    gold_config_reformatted = list(map(dict_to_tuple, gold_config))
    built_config_reformatted = list(map(dict_to_tuple, built_config))

    gold_minus_built = set(gold_config_reformatted) - set(built_config_reformatted)
    built_minus_gold = set(built_config_reformatted) - set(gold_config_reformatted)

    gold_minus_built = list(map(dict, gold_minus_built))
    built_minus_gold = list(map(dict, built_minus_gold))

    return {
        "gold_minus_built": gold_minus_built,
        "built_minus_gold": built_minus_gold
    }

def dict_to_tuple(d):
    return tuple(sorted(d.items()))

def generate_perturbations(config, gold_config):
    """
    Args:
        config: A configuration

    Returns:
        All perturbations of the config in build region
    """

    all_x_values = [i for i in range(build_region_specs["x_min_build"], build_region_specs["x_max_build"] + 1)]
    all_z_values = [i for i in range(build_region_specs["z_min_build"], build_region_specs["z_max_build"] + 1)]
    all_rot_values = [0, 90, 180, -90]

    perturbations = []

    for x in all_x_values:
        for z in all_z_values:
            for rot in all_rot_values:
                perturbation = generate_perturbation(config, x_target = x, z_target = z, rot_target = rot, gold_config = gold_config)
                perturbations.append(perturbation)

    return perturbations

def generate_perturbation(config, x_target, z_target, rot_target, gold_config):

    if not config:
        # compute diff
        x_source = x_target
        z_source = z_target
        x_target = gold_config[0]["x"]
        z_target = gold_config[0]["z"]

        x_diff = x_target - x_source
        z_diff = z_target - z_source

        # translate
        def f(d, x_diff, z_diff):
            return {
                'x': d["x"] + x_diff,
                'y': d["y"],
                'z': d["z"] + z_diff,
                'type': d["type"]
            }

        dummy_config = [
            {
                "x": x_source,
                "z": z_source,
                "y": gold_config[0]["y"],
                "type": gold_config[0]["type"]
            }
        ]

        dummy_config_translated = list([f(t, x_diff = x_diff, z_diff = z_diff) for t in dummy_config])

        # rotate

        # convert to pivot's frame of reference
        x_source = dummy_config_translated[0]["x"]
        y_source = dummy_config_translated[0]["y"]
        z_source = dummy_config_translated[0]["z"]

        return PerturbedConfig(
            perturbed_config = [],
            rot_target = -1 * rot_target,
            rot_axis_pivot = (x_source, y_source, z_source),
            translation = (x_diff, z_diff),
            original_config = config
        )

    # treat first block in config as pivot always

    # move config to x, z and with rotation

    # compute diff
    x_source = config[0]["x"]
    z_source = config[0]["z"]
    x_diff = x_target - x_source
    z_diff = z_target - z_source

    # translate
    def f(d, x_diff, z_diff):
        return {
            'x': d["x"] + x_diff,
            'y': d["y"],
            'z': d["z"] + z_diff,
            'type': d["type"]
        }

    config_translated = list([f(t, x_diff = x_diff, z_diff = z_diff) for t in config])

    # rotate

    # convert to pivot's frame of reference
    x_source = config_translated[0]["x"]
    y_source = config_translated[0]["y"]
    z_source = config_translated[0]["z"]

    def g(d, x_source, y_source, z_source):
        return {
            'x': d["x"] - x_source,
            'y': d["y"] - y_source,
            'z': d["z"] - z_source,
            'type': d["type"]
        }

    config_translated_referred = list([g(t, x_source = x_source, y_source = y_source, z_source = z_source) for t in config_translated])

    # rotate about pivot

    # obtain yaw rotation matrix
    R_yaw = rot_matrices_dict[rot_target]

    def h(d, rot_matrix):
        v = np.matrix([ [ d["x"] ], [ d["y"] ], [ d["z"] ] ])
        v_new = rot_matrix * v

        return {
            'x': int(round(v_new.item(0))),
            'y': int(round(v_new.item(1))),
            'z': int(round(v_new.item(2))),
            'type': d["type"]
        }

    config_translated_referred_rotated = list([h(t, rot_matrix = R_yaw) for t in config_translated_referred])

    # convert back to abs coordinates
    config_translated_rotated = list([g(t, x_source = -1 * x_source, y_source = -1 * y_source, z_source = -1 * z_source) for t in config_translated_referred_rotated])

    return PerturbedConfig(
        perturbed_config = config_translated_rotated,
        rot_target = rot_target,
        rot_axis_pivot = (x_source, y_source, z_source),
        translation = (x_diff, z_diff),
        original_config = config
    )

def invert_perturbation_transform(config, perturbed_config):

    # rotate
    rot_target = -1 * perturbed_config.rot_target

    # convert to pivot's frame of reference
    x_source = perturbed_config.rot_axis_pivot[0]
    y_source = perturbed_config.rot_axis_pivot[1]
    z_source = perturbed_config.rot_axis_pivot[2]

    def g(d, x_source, y_source, z_source):
        return {
            'x': d["x"] - x_source,
            'y': d["y"] - y_source,
            'z': d["z"] - z_source,
            'type': d["type"]
        }

    config_referred = list([g(t, x_source = x_source, y_source = y_source, z_source = z_source) for t in config])

    # rotate about pivot

    # obtain yaw rotation matrix
    R_yaw = rot_matrices_dict[rot_target]

    def h(d, rot_matrix):
        v = np.matrix([ [ d["x"] ], [ d["y"] ], [ d["z"] ] ])
        v_new = rot_matrix * v

        return {
            'x': int(round(v_new.item(0))),
            'y': int(round(v_new.item(1))),
            'z': int(round(v_new.item(2))),
            'type': d["type"]
        }

    config_referred_rotated = list([h(t, rot_matrix = R_yaw) for t in config_referred])

    # convert back to abs coordinates
    config_rotated = list([g(t, x_source = -1 * x_source, y_source = -1 * y_source, z_source = -1 * z_source) for t in config_referred_rotated])

    x_diff = -1 * perturbed_config.translation[0]
    z_diff = -1 * perturbed_config.translation[1]

    # translate
    def f(d, x_diff, z_diff):
        return {
            'x': d["x"] + x_diff,
            'y': d["y"],
            'z': d["z"] + z_diff,
            'type': d["type"]
        }

    config_rotated_translated = list([f(t, x_diff = x_diff, z_diff = z_diff) for t in config_rotated])

    return config_rotated_translated

class PerturbedConfig:
    def __init__(self, perturbed_config, rot_target, rot_axis_pivot, translation, original_config):
        self.perturbed_config = perturbed_config
        self.rot_target = rot_target
        self.rot_axis_pivot = rot_axis_pivot
        self.translation = translation
        self.original_config = original_config

class Diff:
    def __init__(self, diff_built_config_space, diff_gold_config_space):
        self.diff_built_config_space = diff_built_config_space
        self.diff_gold_config_space = diff_gold_config_space

class PerturbedConfigAndDiff:
    def __init__(self, perturbed_config, diff):
        self.perturbed_config = perturbed_config
        self.diff = diff

def get_built_config_distribution(built_config, minimal_diffs):
    """
    Args:
        built_config: Configuration built so far
        minimal_diffs: List of all the minimal diffs in built config space

    Returns:
        A probability distribution over blocks in the built config -- probabilities of next removal
    """

    def f(block, minimal_diffs):
        diffs_containing_block = list([x for x in minimal_diffs if block in x["built_minus_gold"]])
        return len(diffs_containing_block)

    # get counts
    scores = list([f(x, minimal_diffs) for x in built_config])
    # normalize
    if not sum(scores) == 0:
        normalized_scores = list([float(x)/float(sum(scores)) for x in scores])
    else:
        normalized_scores = scores

    return normalized_scores

def get_gold_config_distribution(gold_config, minimal_diffs):
    """
    Args:
        gold_config: Gold configuration
        minimal_diffs: List of all the minimal diffs in gold config space

    Returns:
        A probability distribution over blocks in the gold config -- probabilities of next placement
    """

    def f(block, minimal_diffs):
        diffs_containing_block = list([x for x in minimal_diffs if block in x["gold_minus_built"]])
        return len(diffs_containing_block)

    # get counts
    scores = list([f(x, minimal_diffs) for x in gold_config])
    # normalize
    if not sum(scores) == 0:
        normalized_scores = list([float(x)/float(sum(scores)) for x in scores])
    else:
        normalized_scores = scores

    return normalized_scores

if __name__  == "__main__":
    gold_config = [
        {
            "x": 1,
            "y": 1,
            "z": 1,
            "type": "red"
        },
        {
            "x": 1,
            "y": 1,
            "z": 2,
            "type": "red"
        },
        {
            "x": 1,
            "y": 1,
            "z": 3,
            "type": "blue"
        },
        {
            "x": 1,
            "y": 2,
            "z": 5,
            "type": "orange"
        }
    ]

    built_config = [
        {
            "x": 1,
            "y": 1,
            "z": 1,
            "type": "red"
        },
        {
            "x": 1,
            "y": 1,
            "z": 2,
            "type": "red"
        },
        {
            "x": 1,
            "y": 1,
            "z": 3,
            "type": "blue"
        }
    ]

    import pprint
    pp = pprint.PrettyPrinter()
    diff, everything_min = get_diff(gold_config, built_config)
    # pp.pprint(diff)
    # print("\n\n")
    # pp.pprint(everything_min)
    # print(len(everything_min))

    # print("BUILT")
    #
    # minimal_diffs_built_config_space = list(map(lambda x: x[0][1].diff_built_config_space, everything_min))
    # # pp.pprint(minimal_diffs_built_config_space)
    #
    # scores = get_built_config_distribution(built_config, minimal_diffs_built_config_space)
    # pp.pprint(scores)
    #
    # print("\n")
    # print("GOLD")
    #
    # minimal_diffs_gold_config_space = list(map(lambda x: x[0][1].diff_gold_config_space, everything_min))
    # # pp.pprint(minimal_diffs_gold_config_space)
    #
    # scores = get_gold_config_distribution(gold_config, minimal_diffs_gold_config_space)
    # pp.pprint(scores)

    # diff["built_minus_gold"] = []
    # diff["gold_minus_built"] = []
    next_actions = get_next_actions(diff, 4, {"x": 0, "y": 0, "z": 5}, built_config, True)
    pp.pprint(next_actions)
