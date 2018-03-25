import csv
import pprint
import argparse

def generate_curriculums(database, people_specs):
    """
    Args:
        database: Base data
        people_specs: List of dicts containing people pairs and number of simple and complex configs for each people pair

    Returns:
        A list of curriculums
    """
    curriculums = []

    for people_pair_specs in people_specs:
        curriculum = generate_curriculum(
            database = database,
            num_simple = people_pair_specs["num_simple"],
            num_complex = people_pair_specs["num_complex"],
            person_1 = people_pair_specs["person_1"],
            person_2 = people_pair_specs["person_2"]
        )
        curriculums.append(curriculum)

    return curriculums

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
        Also updates database
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

    return curriculum

def read_database(database_file):
    all_configs = []
    with open(database_file, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row["people"] = map(int, row["people"].split())
            row["runs"] = int(row["runs"])
            all_configs.append(row)

    return all_configs

def read_people_specs(people_specs_file):
    all_people_specs = []
    with open(people_specs_file, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for key in row:
                row[key] = int(row[key])
            all_people_specs.append(row)

    return all_people_specs

def write_curriculums(curriculums, people_specs):
    i = 0
    for (curriculum, people_pair_specs) in zip(curriculums, people_specs):
        i += 1
        with open('curriculum_' + str(i) + '.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = ['gold file path', 'existing file path'])
            writer.writeheader()
            for config in curriculum:
                writer.writerow({'gold file path': 'gold-configurations/' + config, 'existing file path': ''})
            print "DONE WRITING " + 'curriculum_' + str(i) + '.csv' + " FOR PEOPLE PAIR " + str(people_pair_specs["person_1"]) + ", " + str(people_pair_specs["person_2"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate gold config curriculums for builder/architect pairs")
    parser.add_argument("database_csv", help="File path of the spreadsheet (.csv) containing gold config info")
    parser.add_argument("people_specs_csv", help="File path of the spreadsheet (.csv) containing all people specs for a session")
    args = parser.parse_args()

    # read database file
    database = read_database(args.database_csv)

    # read people specs file
    people_specs = read_people_specs(args.people_specs_csv)

    # generate curriculums
    curriculums = generate_curriculums(database, people_specs)

    # write curriculums to files
    write_curriculums(curriculums, people_specs)
