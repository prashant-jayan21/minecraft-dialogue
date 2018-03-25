import os
import argparse
import csv
from cwc_curriculum_generator import read_database, read_people_specs

def update_database(database, curriculums, people_pairs):
    for (curriculum, people_pair) in zip(curriculums, people_pairs):
        update_database_single(database, curriculum, people_pair[0], people_pair[1])

def update_database_single(database, curriculum, person_1, person_2):
    for config in database:
        if config["configuration"] in curriculum:
            config["runs"] += 1
            config["people"] = config["people"] + [person_1, person_2]

def read_curriculum(curriculum_file):
    all_configs = []
    with open(curriculum_file, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row = os.path.basename(row["gold file path"])
            all_configs.append(row)

    return all_configs

def write_database(database, database_file):
    with open(database_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ['configuration','type','runs','people'])
        writer.writeheader()
        for config in database:
            config["people"] = ' '.join(str(x) for x in config["people"])
            writer.writerow(config)
        print "DONE WRITING " + database_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update spreadsheet (.csv) containing gold config info")
    parser.add_argument("database_csv", help="File path of the spreadsheet (.csv) containing gold config info")
    parser.add_argument("people_specs_csv", help="File path of the spreadsheet (.csv) containing all people specs for a session")
    parser.add_argument("curriculums_dir", help="Directory containing the curriculum files")
    args = parser.parse_args()

    # read database file
    database = read_database(args.database_csv)

    # read people specs file
    people_specs = read_people_specs(args.people_specs_csv)
    people_pairs = map(lambda x: (x["person_1"], x["person_2"]), people_specs)

    # read curriculum files
    curriculums = []
    for i in range(len(people_pairs)):
        curriculum_file = os.path.join(args.curriculums_dir, 'curriculum_' + str(i + 1) + '.csv')
        curriculum = read_curriculum(curriculum_file)
        curriculums.append(curriculum)

    # update db
    update_database(database, curriculums, people_pairs)

    # write updated db to file
    write_database(database, args.database_csv)
