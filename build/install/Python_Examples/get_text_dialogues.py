import os, argparse, json
from cwc_io_utils import getLogfileNames

def generateTxtFile(logfiles, output, screenshots_dir):
	if not os.path.isdir("dialogues/"):
		os.makedirs("dialogues/")

	if not output.endswith(".txt"):
		output += ".txt"

	outfile_no_actions = open("dialogues/"+".".join(output.split(".")[:-1])+"-dialogue.txt", "w")
	outfile_with_actions = open("dialogues/"+".".join(output.split(".")[:-1])+"-dialogue-with-actions.txt", "w")

	print "Writing plain dialogues to", outfile_no_actions.name
	print "Writing dialogues with actions to", outfile_with_actions.name

	for logfile in logfiles:
		with open(logfile, 'r') as f:
			observations = json.load(f)

		experiment_name = logfile.split("/")[-2]

		outfile_no_actions.write(experiment_name+"\n")
		writeDialogue(outfile_no_actions, observations, experiment_name, screenshots_dir, False)
		outfile_no_actions.write("\n")

		outfile_with_actions.write(experiment_name+"\n")
		writeDialogue(outfile_with_actions, observations, experiment_name, screenshots_dir, True)
		outfile_with_actions.write("\n")

	outfile_no_actions.close()
	outfile_with_actions.close()

def writeDialogue(outfile, observations, experiment_name, screenshots_dir, with_actions):
	if not with_actions:
		final_observation = observations["WorldStates"][-1]
		for i in range(len(final_observation["ChatHistory"])):
			outfile.write(final_observation["ChatHistory"][i]+"\n")

	else:
		world_states = observations["WorldStates"]
		last_world_state = None
		dialogue = []

		for world_state in world_states:
			screenshots = world_state["Screenshots"]
			builder_ss = getScreenshotFilePath(screenshots_dir, experiment_name, screenshots.get("Builder"))
			architect_ss = getScreenshotFilePath(screenshots_dir, experiment_name, screenshots.get("Architect"))

			fixed_viewers_ss = []
			if "-chat" not in builder_ss and "-chat" not in architect_ss:
				fixed_viewers_ss = getFixedViewerScreenshots(screenshots_dir, experiment_name, screenshots, observations["NumFixedViewers"])

			action = getActionType(screenshots, observations["NumFixedViewers"])
			if action is None:
				continue

			elif "chat" in action:
				if last_world_state is None:
					for i in range(len(world_state["ChatHistory"])):
						dialogue.append(world_state["ChatHistory"][i].strip())

				elif len(world_state["ChatHistory"]) > len(last_world_state["ChatHistory"]):
					for i in range(len(last_world_state["ChatHistory"]), len(world_state["ChatHistory"])):
						dialogue.append(world_state["ChatHistory"][i].strip())

			else:
				block = getMovedBlock(last_world_state, world_state, action)
				if block is not None:
					btype = block["Type"].split("_")[-2]
					bx, by, bz = str(block["AbsoluteCoordinates"]["X"]), str(block["AbsoluteCoordinates"]["Y"]), str(block["AbsoluteCoordinates"]["Z"])
					dialogue.append("[Builder "+("picks up" if "pickup" in action else "puts down")+" a "+btype+" block at X:"+bx+" Y:"+by+" Z:"+bz+"]")

			last_world_state = world_state

		for element in dialogue:
			outfile.write(element+"\n")

def getMovedBlock(last_world_state, world_state, action):
	def containsBlock(last_world_state, block):
		for previous_block in last_world_state["BlocksInGrid"]:
			px, py, pz = previous_block["AbsoluteCoordinates"]["X"], previous_block["AbsoluteCoordinates"]["Y"], previous_block["AbsoluteCoordinates"]["Z"]
			ptype = previous_block["Type"]

			if px == block["AbsoluteCoordinates"]["X"] and py == block["AbsoluteCoordinates"]["Y"] and pz == block["AbsoluteCoordinates"]["Z"] and ptype == block["Type"]:
				return True

		return False

	if "pickup" in action:
		temp = last_world_state
		last_world_state = world_state
		world_state = temp

	moved = None
	for block in world_state["BlocksInGrid"]:
		if not containsBlock(last_world_state, block):
			moved = block
			break

	if moved is None:
		print "Something went wrong! Detected", action, "action but no moved block was found."
		return None

	return moved

def getScreenshotFilePath(screenshots_dir, experiment_name, file_path):
	screenshot_path = None if file_path is None else screenshots_dir+"/"+experiment_name+"/"+file_path
	return "blank.png" if file_path is None or not os.path.exists(screenshot_path) else screenshot_path

def getFixedViewerScreenshots(screenshots_dir, experiment_name, screenshots, num_fixed_viewers):
	fixed_viewers_ss = []
	for i in range(num_fixed_viewers):
		fixed_viewers_ss.append(getScreenshotFilePath(screenshots_dir, experiment_name, screenshots.get("FixedViewer"+str(i+1))))
	return fixed_viewers_ss

def getActionType(screenshots, num_fixed_viewers):
	file_path = screenshots.get("Builder") if screenshots.get("Builder") is not None else screenshots.get("Architect")
	if file_path is not None:
		return file_path.split("-")[-1].replace(".png","")

	for i in range(num_fixed_viewers):
		if screenshots.get("FixedViewer"+str(i+1)) is not None:
			return screenshots.get("FixedViewer"+str(i+1)).split("-")[-1].replace(".png","")

	return None


def main():
	parser = argparse.ArgumentParser(description="Produce .txt file of dialogues from given json logfiles or directories.")
	parser.add_argument('-l', '--list', nargs='+', help='Json files to be processed, or the directory in which they live', required=True)
	parser.add_argument('-o', '--output', help='Name of output txt file', required=True)
	parser.add_argument('-s', '--screenshots_dir', default="../../../../Minecraft/run/screenshots", help="Screenshots directory path")
	args = parser.parse_args()

	logfiles = getLogfileNames(args.list, "aligned-observations.json")
	generateTxtFile(logfiles, args.output, args.screenshots_dir)

if __name__ == '__main__':
	main()