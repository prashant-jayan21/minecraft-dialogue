import os
import argparse
import csv
from cwc_io_utils import *

def update_configs_db(configs_db, curriculums, people_pairs):
    """
    Args:
        configs_db: List of all config info
        curriculums: A list of gold config curriculums -- one for each people pair
        people_specs: List of people pairs

    Returns:
        Nothing
        Updates configs DB globally
    """
    for (curriculum, people_pair) in zip(curriculums, people_pairs):
        print(("Updating DB for pair", people_pair, "with curriculum", curriculum))
        update_configs_db_single(configs_db, curriculum, people_pair[0], people_pair[1])

def update_configs_db_single(configs_db, curriculum, person_1, person_2):
    """
    Args:
        configs_db: List of all config info
        curriculum: A gold config curriculum
        person_1: ID of first person
        person_2: ID of second person

    Returns:
        Nothing
        Updates configs DB globally
    """
    for config in configs_db:
        if config["configuration"] in curriculum:
            config["runs"] += 1
            config["people"] = config["people"] + [person_1, person_2]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update spreadsheet (.csv) DB containing all gold config info")
    parser.add_argument("configs_db_csv", nargs='?', default='configs_db.csv', help="File path of the spreadsheet (.csv) DB containing all gold config info")
    parser.add_argument("people_specs_csv", nargs='?', default='sample_people_specs.csv', help="File path of the spreadsheet (.csv) containing all people specs for a session")
    parser.add_argument("--curriculums_dir", default=".", help="Directory containing the curriculum files as curriculum_i.csv (i = 1, 2, ...)")
    args = parser.parse_args()

    # read configs DB file
    configs_db = read_configs_db(args.configs_db_csv)

    # read people specs file
    people_specs = read_people_specs(args.people_specs_csv)
    people_pairs = [(x["person_1"], x["person_2"]) for x in people_specs]

    # read curriculum files
    curriculums = []
    for i in range(len(people_pairs)):
        curriculum_file = os.path.join(args.curriculums_dir, 'curriculum_' + str(i + 1) + '.csv')
        curriculum = read_curriculum(curriculum_file)
        curriculums.append(curriculum)

    # update db
    update_configs_db(configs_db, curriculums, people_pairs)

    # write updated db to file
    write_configs_db(configs_db, args.configs_db_csv)
