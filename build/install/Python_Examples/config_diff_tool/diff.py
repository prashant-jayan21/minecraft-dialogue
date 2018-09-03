import numpy as np, sys
from scipy.spatial import distance

build_region_specs = { # FIXME: Import instead
    "x_min_build": -5,
    "x_max_build": 5,
    "y_min_build": 1,
    "y_max_build": 9,
    "z_min_build": -5,
    "z_max_build": 5
}

def get_next_actions(all_next_actions, num_next_actions_needed, last_action):
    """
    Args:
        all_next_actions: The diff between current state and goal state
        num_next_actions_needed: The number of next actions to sample from all possible next actions
        last_action: The point in space where the last action took place

    Returns:
        The appropriate next actions in terms of a reduced diff
    """

    all_next_removals = all_next_actions["built_minus_gold"]
    all_next_placements = all_next_actions["gold_minus_built"]

    assert num_next_actions_needed % 2 == 0 # an even split is needed between removals and placements

    # sort all next actions by distance from last action and pick top-k
    all_next_removals_sorted = sorted(all_next_removals, key = lambda x: euclidean_distance(x, last_action))
    all_next_placements_sorted = sorted(all_next_placements, key = lambda x: euclidean_distance(x, last_action))

    next_removals = all_next_removals_sorted[:int(num_next_actions_needed/2)]
    next_placements = all_next_placements_sorted[:int(num_next_actions_needed/2)]

    return {
        "gold_minus_built": next_placements,
        "built_minus_gold": next_removals
    }

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
        The diff in terms of actions -- blocks to remove and block to place --
        to take the built config state to the goal config state
    """

    if not built_config:
        return {
            "gold_minus_built": gold_config,
            "built_minus_gold": []
        }

    # generate all possible perturbations of built config in the build region
    perturbations = generate_perturbations(built_config)

    # compute diffs for each perturbation
    diffs = list(map(lambda t: diff(gold_config = gold_config, built_config = t.perturbed_config), perturbations))

    # convert diffs back to actions in the built config space and not the perturbed config space
    # filter out perturbations that yield infeasible diff actions (those outside the build region)
    perturbations_and_diffs = list(filter(lambda x: is_feasible_perturbation(x[0], x[1]), list(zip(perturbations, diffs))))

    # select perturbation with min diff
    min_perturbation_and_diff = min(perturbations_and_diffs, key = lambda t: len(t[1]["gold_minus_built"]) + len(t[1]["built_minus_gold"]))

    return min_perturbation_and_diff[1]

def is_feasible_perturbation(perturbed_config, diff):
    # NOTE: This function mutates `diff`. DO NOT CHANGE THIS BEHAVIOR!
    """
    Args:
        perturbed_config: PerturbedConfig
        diff: Dict
    """

    for key, config in diff.items():
        diff[key] = invert_perturbation_transform(
            config = config,
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

def diff(gold_config, built_config): # PROFILED
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

def generate_perturbations(config):
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
                perturbation = generate_perturbation(config, x_target = x, z_target = z, rot_target = rot)
                perturbations.append(perturbation)

    return perturbations

def generate_perturbation(config, x_target, z_target, rot_target): # PROFILED
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

    config_translated = list(map(lambda t: f(t, x_diff = x_diff, z_diff = z_diff), config))

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

    config_translated_referred = list(map(lambda t: g(t, x_source = x_source, y_source = y_source, z_source = z_source), config_translated))

    # rotate about pivot

    # construct yaw rotation matrix
    theta_yaw = np.radians(-1 * rot_target)
    c, s = np.cos(theta_yaw), np.sin(theta_yaw)
    R_yaw = np.matrix([ [ c, 0, -s ], [ 0, 1, 0 ], [ s, 0, c ] ])

    def h(d, rot_matrix): #PROFILED
        v = np.matrix([ [ d["x"] ], [ d["y"] ], [ d["z"] ] ])
        v_new = rot_matrix * v

        return {
            'x': int(round(v_new.item(0))),
            'y': int(round(v_new.item(1))),
            'z': int(round(v_new.item(2))),
            'type': d["type"]
        }

    config_translated_referred_rotated = list(map(lambda t: h(t, rot_matrix = R_yaw), config_translated_referred))

    # convert back to abs coordinates
    config_translated_rotated = list(map(lambda t: g(t, x_source = -1 * x_source, y_source = -1 * y_source, z_source = -1 * z_source), config_translated_referred_rotated))

    return PerturbedConfig(
        perturbed_config = config_translated_rotated,
        rot_target = rot_target,
        rot_axis_pivot = (x_source, y_source, z_source),
        translation = (x_diff, z_diff)
    )

def invert_perturbation_transform(config, perturbed_config): # PROFILED

    # rotate
    rot_target = -1 * perturbed_config.rot_target

    # convert to pivot's frame of reference
    x_source = perturbed_config.rot_axis_pivot[0]
    y_source = perturbed_config.rot_axis_pivot[1]
    z_source = perturbed_config.rot_axis_pivot[2]

    def g(d, x_source, y_source, z_source): # PROFILED
        return {
            'x': d["x"] - x_source,
            'y': d["y"] - y_source,
            'z': d["z"] - z_source,
            'type': d["type"]
        }

    config_referred = list(map(lambda t: g(t, x_source = x_source, y_source = y_source, z_source = z_source), config))

    # rotate about pivot

    # construct yaw rotation matrix
    theta_yaw = np.radians(-1 * rot_target)
    c, s = np.cos(theta_yaw), np.sin(theta_yaw)
    R_yaw = np.matrix([ [ c, 0, -s ], [ 0, 1, 0 ], [ s, 0, c ] ])

    def h(d, rot_matrix): # PROFILED
        v = np.matrix([ [ d["x"] ], [ d["y"] ], [ d["z"] ] ])
        v_new = rot_matrix * v

        return {
            'x': int(round(v_new.item(0))),
            'y': int(round(v_new.item(1))),
            'z': int(round(v_new.item(2))),
            'type': d["type"]
        }

    config_referred_rotated = list(map(lambda t: h(t, rot_matrix = R_yaw), config_referred))

    # convert back to abs coordinates
    config_rotated = list(map(lambda t: g(t, x_source = -1 * x_source, y_source = -1 * y_source, z_source = -1 * z_source), config_referred_rotated))

    x_diff = -1 * perturbed_config.translation[0]
    z_diff = -1 * perturbed_config.translation[1]

    # translate
    def f(d, x_diff, z_diff): # PROFILED
        return {
            'x': d["x"] + x_diff,
            'y': d["y"],
            'z': d["z"] + z_diff,
            'type': d["type"]
        }

    config_rotated_translated = list(map(lambda t: f(t, x_diff = x_diff, z_diff = z_diff), config_rotated))

    return config_rotated_translated

class PerturbedConfig:
    def __init__(self, perturbed_config, rot_target, rot_axis_pivot, translation):
        self.perturbed_config = perturbed_config
        self.rot_target = rot_target
        self.rot_axis_pivot = rot_axis_pivot
        self.translation = translation

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
            "y": 1,
            "z": 4,
            "type": "blue"
        },
        {
            "x": 1,
            "y": 1,
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
            "z": 3,
            "type": "blue"
        },
        {
            "x": 1,
            "y": 4,
            "z": 3,
            "type": "blue"
        }
    ]

    import pprint
    pp = pprint.PrettyPrinter()
    diff = get_diff(gold_config, built_config)
    pp.pprint(diff)
    print("\n\n")
    next_actions = get_next_actions(diff, 4, {"x": 0, "y": 0, "z": 5})
    pp.pprint(next_actions)
