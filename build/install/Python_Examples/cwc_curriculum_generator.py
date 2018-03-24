import csv
import pprint

def generate_curriculum(database, num_simple, num_complex, person_1, person_2):
    """
    Args:
        database: Base data
        num_simple: Number of simple configurations required
        num_complex: Number of complex configurations required
        person_1: ID of first person
        person_2: ID of second person

    Returns:
        A dict with a curriculum of configurations and the updated database
    """

    # split simple and complex configs into two sets
    simple_configs = [x for x in database if x["type"] == "simple"]
    complex_configs = [x for x in database if x["type"] == "complex"]

    # remove those already seen by people
    simple_configs = [x for x in simple_configs if person_1 not in x["people"] and person_2 not in x["people"]]
    complex_configs = [x for x in complex_configs if person_1 not in x["people"] and person_2 not in x["people"]]

    # round robin selection
    # sort
    simple_configs_sorted = sorted(simple_configs, key = lambda x: x["runs"])
    complex_configs_sorted = sorted(complex_configs, key = lambda x: x["runs"])
    #select
    simple_configs_selected = simple_configs_sorted[:num_simple]
    complex_configs_selected = complex_configs_sorted[:num_complex]
    #concatenate
    curriculum = map(lambda x: x["configuration"], simple_configs_selected + complex_configs_selected)

    # update DB
    for config in database:
        if config["configuration"] in curriculum:
            config["runs"] += 1
            config["people"] = config["people"] + [person_1, person_2]

    return {
        "curriculum": curriculum,
        "database": database
    }

def read_database(database_file):
    all_configs = []
    with open(database_file, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row["people"] = map(int, row["people"].split())
            row["runs"] = int(row["runs"])
            all_configs.append(row)

    return all_configs
