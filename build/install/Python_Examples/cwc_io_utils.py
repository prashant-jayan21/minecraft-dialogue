import os, json

def readXMLSubstringFromFile(xml_filename):
    config_xml_substring = ""
    if xml_filename is not None and len(xml_filename) > 0:
		print "Reading XML file", xml_filename
        config_file = open(xml_filename, "r")
        config_xml_substring = config_file.read()
        config_file.close()

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