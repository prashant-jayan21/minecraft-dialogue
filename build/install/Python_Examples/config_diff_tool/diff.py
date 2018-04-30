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

    # FIXME: prune infeasible perturbations

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
    all_rot_values = [0] # FIXME

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
    config_rotated_and_translated = config_translated # FIXME

    return config_rotated_and_translated
