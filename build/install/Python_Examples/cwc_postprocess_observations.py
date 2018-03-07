import os, argparse, json, copy
import numpy as np
import cwc_mission_utils as mission_utils, cwc_debug_utils as debug_utils
from glob import glob

def getPerspectiveCoordinates(x, y, z, yaw, pitch):
    # construct vector
    v = np.matrix('{}; {}; {}'.format(x, y, z))

    # construct yaw rotation matrix
    theta_yaw = np.radians(-1 * yaw)
    c, s = np.cos(theta_yaw), np.sin(theta_yaw)
    R_yaw = np.matrix('{} {} {}; {} {} {}; {} {} {}'.format(c, 0, -s, 0, 1, 0, s, 0, c))

    # multiply
    v_new = R_yaw * v

    # construct pitch rotation matrix
    theta_pitch = np.radians(pitch)
    c, s = np.cos(theta_pitch), np.sin(theta_pitch)
    R_pitch = np.matrix('{} {} {}; {} {} {}; {} {} {}'.format(1, 0, 0, 0, c, s, 0, -s, c))

    # multiply
    v_final = R_pitch * v_new
    x_final = v_final.item(0)
    y_final = v_final.item(1)
    z_final = v_final.item(2)
    return (x_final, y_final, z_final)

def reformatObservations(observations):
    print "reformatting ...",
    reformatted = []
    for observation in observations:
        reformatted.append(reformatObservation(observation))

    return reformatted

def reformatObservation(observation):
    reformatted = {}
    reformatted["Timestamp"] = observation["Timestamp"]

    if observation.get(u'Yaw') is not None:
        yaw = observation.get(u'Yaw')
        pitch = observation.get(u'Pitch')
        xpos = observation.get(u'XPos')
        ypos = observation.get(u'YPos')
        zpos = observation.get(u'ZPos')
        reformatted["BuilderPosition"] = {"X": xpos, "Y": ypos, "Z": zpos, "Yaw": yaw, "Pitch": pitch}

    if observation.get(u'ScreenshotPath') is not None:
        reformatted["ScreenshotPath"] = observation.get(u'ScreenshotPath')

    if observation.get(u'Chat') is not None:
        reformatted["ChatHistory"] = observation.get(u'Chat')

    if observation.get(u'BuilderInventory') is not None:
        reformatted["BuilderInventory"] = []
        inventory = observation.get(u'BuilderInventory')
        for block in inventory:
            reformatted["BuilderInventory"].append({"Index": block["Index"], "Type": block["Type"], "Quantity": block["Quantity"]})

    if observation.get(u'BuilderGridAbsolute') is not None:
        reformatted["BuilderGridAbsolute"] = observation.get(u'BuilderGridAbsolute')
        reformatted["BuilderGridRelative"] = observation.get(u'BuilderGridRelative')

    return reformatted

def mergeObservations(observations):
    print "merging ...",
    merged = []
    for observation in observations:
        mergeObservation(merged, observation)

    return merged

def mergeObservation(observations, next_observation):
    if len(observations) == 0:
        observations.append(next_observation)

    else:
        last_observation = observations[-1]
        last_observation_keys = set(last_observation.keys())
        next_observation_keys = set(next_observation.keys())
        next_observation_keys.remove("Timestamp")

        if len(last_observation_keys.intersection(next_observation_keys)) > 0:
            observations.append(next_observation)
        else:
            observations[-1] = dict(next_observation, **last_observation)

    return observations

def postprocess(observations):
    print "postprocessing ..."
    chat_history = []
    string_to_write = ""
    for observation in observations:
        if observation.get("ChatHistory") is not None:
            chat_history += observation["ChatHistory"]
        observation["ChatHistory"] = copy.deepcopy(chat_history)
        recordGridCoordinates(observation)
        string_to_write = writeToString(observation, string_to_write)

    return string_to_write

# Records the blocks in the builder's grid, separated by outside vs. inside blocks. Also calculates their perspective coordinates.
# Appends these block information, as well as the chat history, to the world state JSON.
def recordGridCoordinates(observation):
    if observation.get(u'BuilderGridAbsolute') is None or observation.get(u'BuilderPosition') is None:
        print "\tWARNING: Something went wrong... the builder", "grid" if observation.get(u'BuilderGridAbsolute') is None else "position", "is missing. Aborting recording grid coordinates for this observation."
        observation["BlocksOutside"] = []
        observation["BlocksInside"]  = []
        return 

    grid_absolute, grid_relative = observation.pop("BuilderGridAbsolute"), observation.pop("BuilderGridRelative")
    yaw, pitch = observation["BuilderPosition"]["Yaw"], observation["BuilderPosition"]["Pitch"]
    blocks_inside, blocks_outside = [], []
    for i in range(len(grid_absolute)):
        block_absolute = grid_absolute[i]
        block_relative = grid_relative[i]

        (ax, ay, az) = (block_absolute["X"], block_absolute["Y"], block_absolute["Z"])
        (px, py, pz) = getPerspectiveCoordinates(block_relative["X"], block_relative["Y"], block_relative["Z"], yaw, pitch)

        block_info = {"Type": block_relative["Type"], "AbsoluteCoordinates": {"X": ax, "Y": ay, "Z": az}, "PerspectiveCoordinates": {"X": px, "Y": py, "Z": pz}}
        outside = ax < mission_utils.x_min_build or ax > mission_utils.x_max_build or ay < mission_utils.y_min_build or ay > mission_utils.y_max_build or az < mission_utils.z_min_build or az > mission_utils.z_max_build
        blocks_outside.append(block_info) if outside else blocks_inside.append(block_info)

    observation["BlocksOutside"] = blocks_outside
    observation["BlocksInside"] = blocks_inside

# Generates a string representation of the world state JSON's contents and adds it to the string to be written.
def writeToString(observation, string_to_write):
    def getStringValueAndFix(observation, key):
        try:
            value = observation[key]
        except KeyError:
            print "\tWARNING: KeyError occurred for key:", key
            observation[key] = None
            return "None"
        return str(value)

    string_to_write += "\n"+"-"*20+"\n[Timestamp] "+getStringValueAndFix(observation, "Timestamp")
    string_to_write += "\n[Builder Position] (x, y, z): ("+("None" if getStringValueAndFix(observation, "BuilderPosition") == "None" else 
           getStringValueAndFix(observation["BuilderPosition"], "X") + ", "+getStringValueAndFix(observation["BuilderPosition"], "Y")+", "+getStringValueAndFix(observation["BuilderPosition"], "Z")+") " + \
           "(yaw, pitch): ("+getStringValueAndFix(observation["BuilderPosition"], "Yaw")+", "+getStringValueAndFix(observation["BuilderPosition"], "Pitch"))

    string_to_write += ")\n[Screenshot Path] "+getStringValueAndFix(observation, "ScreenshotPath")
    
    string_to_write += "\n\n[Chat Log]\n"
    if getStringValueAndFix(observation, "ChatHistory") == "None":
        string_to_write += "\tNone\n"
    else:
        for utterance in observation["ChatHistory"]:
            string_to_write += "\t"+utterance+"\n"
    
    string_to_write += "\n[Builder Inventory]"
    if getStringValueAndFix(observation, "BuilderInventory") == "None":
        string_to_write += "\tNone\n"
    else:
        for block in observation["BuilderInventory"]:
            string_to_write += "\tType: "+getStringValueAndFix(block, "Type")+" Index: "+getStringValueAndFix(block, "Index")+" Quantity: "+getStringValueAndFix(block, "Quantity")+"\n"
    
    string_to_write += "\n[Blocks Inside]\n"
    for block in observation["BlocksInside"]:
        string_to_write += "\tType: "+block["Type"]+"  Absolute (x, y, z): ("+str(block["AbsoluteCoordinates"]["X"])+", "+str(block["AbsoluteCoordinates"]["Y"])+", "+str(block["AbsoluteCoordinates"]["Z"]) + \
               ")  Perspective (x, y, z): "+str(block["PerspectiveCoordinates"]["X"])+", "+str(block["PerspectiveCoordinates"]["Y"])+", "+str(block["PerspectiveCoordinates"]["Z"])+")\n"
    
    string_to_write += "\n[Blocks Outside]\n"
    for block in observation["BlocksOutside"]:
        string_to_write += "\tType: "+block["Type"]+"  Absolute (x, y, z): ("+str(block["AbsoluteCoordinates"]["X"])+", "+str(block["AbsoluteCoordinates"]["Y"])+", "+str(block["AbsoluteCoordinates"]["Z"]) + \
               ")  Perspective (x, y, z): "+str(block["PerspectiveCoordinates"]["X"])+", "+str(block["PerspectiveCoordinates"]["Y"])+", "+str(block["PerspectiveCoordinates"]["Z"])+")\n"
    
    return string_to_write

def main():
    parser = argparse.ArgumentParser(description="Postprocess all raw observation files recursively within a given directory.")
    parser.add_argument("observations_dir", nargs="?", default=".", help="Directory within which to search for raw observation files")
    parser.add_argument("--verbose", default=False, action="store_true", help="Print observations to console as they are written")
    args = parser.parse_args()

    observation_files = [y for x in os.walk(args.observations_dir) for y in glob(os.path.join(x[0], '*raw-observations.json'))]
    for observation_file_path in observation_files:
        if os.path.getsize(observation_file_path) <= 0:
            print "Encountered empty file", observation_file_path, "-- skipping."
            continue

        if os.path.exists(observation_file_path.replace("raw-","")):
            if args.verbose:
                print "Postprocessed file already exists for path:", observation_file_path
            continue

        print "\nReading", observation_file_path, "...",
        with open(observation_file_path, 'r') as f:
            observations = json.load(f)

        reformatted = reformatObservations(observations.get("WorldStates"))
        merged = mergeObservations(reformatted)
        string_to_write = postprocess(merged)
        string_to_write += "\nTime elapsed: "+str(observations.get("TimeElapsed"))+" s"
        observations["WorldStates"] = merged

        print "\nDone.", 
        if args.verbose:
            debug_utils.prettyPrintString(string_to_write)
            print 20*"-"
        print

        print "Writing postprocessed JSON to:", observation_file_path.replace("raw-","")
        with open(observation_file_path.replace("raw-",""), "w") as log:
            json.dump(observations, log)

        print "Writing human-readable log to:", observation_file_path.replace("raw-observations.json","log.txt")
        log = open(observation_file_path.replace("raw-observations.json","log.txt"), "w")
        log.write(string_to_write)
        log.close()

        print

if __name__ == '__main__':
    main()