from collections import Counter
from diff import build_region_specs

# NOTE: THIS CODE NEEDS TO BE MAINTAINED FOR BOTH PYTHON 2 AND 3 COMPATIBILITY

def get_type_distributions(diffs_built_config_space, built_config):
    """
    Args:
        diffs_built_config_space: Minimal diffs in built config space
        built_config: Configuration built so far

    Returns:
        A list of TypeDistribution objects -- each contains a unique grid location and the type distribution computed for it --
        all grid locations are exhaustively covered
    """

    results = []

    all_x_values = [i for i in range(build_region_specs["x_min_build"], build_region_specs["x_max_build"] + 1)]
    all_y_values = [i for i in range(build_region_specs["y_min_build"], build_region_specs["y_max_build"] + 1)]
    all_z_values = [i for i in range(build_region_specs["z_min_build"], build_region_specs["z_max_build"] + 1)]

    for x in all_x_values:
        for y in all_y_values:
            for z in all_z_values:
                grid_location = { "x": x, "y": y, "z": z }

                occurence_in_built_config = next(
                    (t for t in built_config if t["x"] == grid_location["x"] and t["y"] == grid_location["y"] and t["z"] == grid_location["z"]),
                    None
                )

                if occurence_in_built_config:
                    grid_location["type"] = occurence_in_built_config["type"]
                else:
                    grid_location["type"] = "empty"

                types_acc_to_diffs = []

                for diff in diffs_built_config_space:
                    # what does this diff say about grid_location
                    types_acc_to_diffs.append(get_type_acc_to_diff(grid_location, diff))

                counts = Counter(types_acc_to_diffs)
                type_distribution = {}
                for type in all_types:
                    type_distribution[type] = float(counts[type]) / float(len(diffs_built_config_space))

                results.append(
                    TypeDistribution(
                        grid_location=grid_location,
                        type_distribution=type_distribution
                    )
                )

    return results

def get_type_acc_to_diff(grid_location, diff):
    """
    Returns:
        The type that "should" exist at the given grid location according to the given diff
    """

    occurence_in_removals = next(
        (t for t in diff["built_minus_gold"] if t["x"] == grid_location["x"] and t["y"] == grid_location["y"] and t["z"] == grid_location["z"]),
        None
    )

    occurence_in_placements = next(
        (t for t in diff["gold_minus_built"] if t["x"] == grid_location["x"] and t["y"] == grid_location["y"] and t["z"] == grid_location["z"]),
        None
    )

    if occurence_in_removals is None and occurence_in_placements is None:
        return grid_location["type"]
    elif occurence_in_placements:
        return occurence_in_placements["type"]
    elif occurence_in_removals:
        return "empty"

all_types = ["empty", "red", "orange", "green", "blue", "yellow", "purple"] # TODO: centralize this info somewhere

class TypeDistribution:
    def __init__(self, grid_location, type_distribution):
        self.grid_location = grid_location
        self.type_distribution = type_distribution
