import numpy as np

from cwc_mission_utils import x_min_build, x_max_build, y_min_build, y_max_build, z_min_build, z_max_build

def get_diff(gold_config, built_config):
    """
    Args:
        gold_config: Gold configuration
        built_config: Configuration built so far
        Both are lists of dicts. Each dict contains info on block type and block coordinates.

    Returns:
        Nothing
    """

    # generate all possible perturbations of built config in the build region

    build_region_specs = {
        "x_min_build": x_min_build,
        "x_max_build": x_max_build,
        "y_min_build": y_min_build,
        "y_max_build": y_max_build,
        "z_min_build": z_min_build,
        "z_max_build": z_max_build
    }

    perturbations = generate_perturbations(built_config, build_region_specs)

    # prune infeasible perturbations

    def is_feasible(config):
        def is_feasible_block(d):
            if (x_min_build <= d["x"] <= x_max_build) and (y_min_build <= d["y"] <= y_max_build) and (z_min_build <= d["z"] <= z_max_build):
                return True
            else:
                return False

        all(is_feasible_block(block) for block in config)

    perturbations = filter(is_feasible, perturbations)

    # compute diffs for each perturbation
    diffs = map(lambda t: diff(gold_config, t), perturbations)

    # select perturbation with min diff
    perturbations_and_diffs = zip(perturbations, diffs)

    min_perturbation_and_diff = min(perturbations_and_diffs, key = lambda t: t[1])

    # return
    return min_perturbation_and_diff[1] # FIXME: Return more than just min diff value

def diff(config_1, config_2):
    diff_set = set(config_1) ^ set(config_2)
    return len(diff_set)

def generate_perturbations(config, build_region_specs):
    """
    Args:
        config: A configuration
        build_region_specs: A dict specifying bounds of the build region

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

def generate_perturbation(config, x_target, z_target, rot_target):
    # treat first block in config as pivot always

    # move config to x, z and with rotation

    # compute diff
    x_source = config[0]["x"]
    z_source = config[0]["z"]
    x_diff = x_target - x_source
    z_diff = z_target - z_source

    # translate
    def f(d, x_diff, z_diff):
        r = copy.deepcopy(d)
        r["x"] = r["x"] + x_diff
        r["z"] = r["z"] + z_diff
        return r

    config_translated = map(lambda t: f(t, x_diff = x_diff, z_diff = z_diff), config)

    # rotate

    # convert to pivot's frame of reference
    x_source = config_translated[0]["x"]
    y_source = config_translated[0]["y"]
    z_source = config_translated[0]["z"]

    def g(d, x_source, y_source, z_source):
        r = copy.deepcopy(d)
        r["x"] = r["x"] - x_source
        r["y"] = r["y"] - y_source
        r["z"] = r["z"] - z_source
        return r

    config_translated_referred = map(lambda t: g(t, x_source = x_source, y_source = y_source, z_source = z_source), config_translated)

    # rotate about pivot

    # construct yaw rotation matrix
    theta_yaw = np.radians(-1 * rot_target)
    c, s = np.cos(theta_yaw), np.sin(theta_yaw)
    R_yaw = np.matrix('{} {} {}; {} {} {}; {} {} {}'.format(c, 0, -s, 0, 1, 0, s, 0, c))

    def h(d, rot_matrix):
        r = copy.deepcopy(d)

        v = np.matrix('{}; {}; {}'.format(r["x"], r["y"], r["z"]))
        v_new = rot_matrix * v

        r["x"] = v_new.item(0)
        r["y"] = v_new.item(1)
        r["z"] = v_new.item(2)

        return r

    config_translated_referred_rotated = map(lambda t: h(t, rot_matrix = R_yaw), config_translated_referred)

    # convert back to abs coordinates

    config_translated_rotated = map(lambda t: g(t, x_source = -1.0 * x_source, y_source = -1.0 * y_source, z_source = -1.0 * z_source), config_translated_referred_rotated)

    return config_translated_rotated
