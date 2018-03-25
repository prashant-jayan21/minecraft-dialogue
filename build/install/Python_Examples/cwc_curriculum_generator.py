import csv
import argparse
from cwc_io_utils import *

def generate_curriculums(configs_db, people_specs):
    """
    Args:
        configs_db: List of all config info
        people_specs: List of dicts containing people pairs and number of simple and complex configs for each people pair

    Returns:
        A list of gold config curriculums -- one for each people pair
    """
    curriculums = []

    for people_pair_specs in people_specs:
        curriculum = generate_curriculum(
            configs_db = configs_db,
            num_simple = people_pair_specs["num_simple_configs"],
            num_complex = people_pair_specs["num_complex_configs"],
            person_1 = people_pair_specs["person_1"],
            person_2 = people_pair_specs["person_2"]
        )
        curriculums.append(curriculum)

    return curriculums

def generate_curriculum(configs_db, num_simple, num_complex, person_1, person_2):
    """
    Args:
        configs_db: List of all config info
        num_simple: Number of simple configurations required
        num_complex: Number of complex configurations required
        person_1: ID of first person
        person_2: ID of second person

    Returns:
        A curriculum of gold configs as a list
        Also updates configs DB globally
    """

    # split simple and complex configs into two sets
    simple_configs = [x for x in configs_db if x["type"] == "simple"]
    complex_configs = [x for x in configs_db if x["type"] == "complex"]

    # remove configs already seen by people
    simple_configs = [x for x in simple_configs if person_1 not in x["people"] and person_2 not in x["people"]]
    complex_configs = [x for x in complex_configs if person_1 not in x["people"] and person_2 not in x["people"]]

    # sort configs by number of runs
    simple_configs_sorted = sorted(simple_configs, key = lambda x: x["runs"])
    complex_configs_sorted = sorted(complex_configs, key = lambda x: x["runs"])

    # select top-k least run configs
    simple_configs_selected = simple_configs_sorted[:num_simple]
    complex_configs_selected = complex_configs_sorted[:num_complex]

    # concatenate simple and complex configs
    curriculum = map(lambda x: x["configuration"], simple_configs_selected + complex_configs_selected)

    # update configs DB to reflect globally
    for config in configs_db:
        if config["configuration"] in curriculum:
            config["runs"] += 1
            config["people"] = config["people"] + [person_1, person_2]

    return curriculum

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate gold config curriculums for builder/architect pairs")
    parser.add_argument("configs_db_csv", help="File path of the spreadsheet (.csv) DB containing all gold config info")
    parser.add_argument("people_specs_csv", help="File path of the spreadsheet (.csv) containing all people specs for a session")
    args = parser.parse_args()

    # read configs DB file
    configs_db = read_configs_db(args.configs_db_csv)

    # read people specs file
    people_specs = read_people_specs(args.people_specs_csv)

    # generate curriculums
    curriculums = generate_curriculums(configs_db, people_specs)

    # write curriculums to files
    write_curriculums(curriculums, people_specs)
