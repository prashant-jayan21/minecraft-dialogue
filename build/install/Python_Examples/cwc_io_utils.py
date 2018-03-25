import os, json, csv

def readXMLSubstringFromFile(xml_filename, displaced):
    config_xml_substring = ""
    if xml_filename is not None and len(xml_filename) > 0:
        print "Reading XML file", xml_filename
        config_file = open(xml_filename, "r")
        config_xml_substring = config_file.read()
        config_file.close()

    if displaced:
        fixed = None

    return config_xml_substring

def makeLogDirectory(experiment_id):
    if not os.path.isdir("logs/"):
        os.makedirs("logs/")

    experiment_log = "logs/"+experiment_id
    if not os.path.isdir(experiment_log):
        os.makedirs(experiment_log)

    return experiment_log

def writeJSONtoLog(experiment_id, filename, json_data):
    experiment_log = makeLogDirectory(experiment_id)
    print "Writing", filename, "to", experiment_log, "..."
    with open(experiment_log+"/"+filename, "w") as log:
        json.dump(json_data, log)

def getLogfileNames(arglist, suffix):
    filenames = []
    for path in arglist:
        if path[-1] == '/':
            path = path[:-1]

        if os.path.isdir(path):
            filenames.append(path+"/"+suffix)
        else:
            filenames.append(path)

    return filenames

def read_configs_db(configs_db_file):
    all_configs = []

    with open(configs_db_file, 'rb') as csvfile:
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

def read_curriculum(curriculum_file):
    all_configs = []
    with open(curriculum_file, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row = os.path.basename(row["gold file path"])
            all_configs.append(row)

    return all_configs

def write_configs_db(configs_db, configs_db_file):
    with open(configs_db_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ['configuration','type','runs','people'])
        writer.writeheader()
        for config in configs_db:
            config["people"] = ' '.join(str(x) for x in config["people"])
            writer.writerow(config)
        print "DONE WRITING " + configs_db_file
