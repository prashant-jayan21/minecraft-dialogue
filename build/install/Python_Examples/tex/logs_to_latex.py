import os, argparse, json

def getLogfileNames(arglist):
	filenames = []
	for path in arglist:
		if os.path.isdir(path):
			filenames.append(path+"aligned-observations.json")
		else:
			filenames.append(path)

	return filenames

def generateTexfile(logfiles, output, screenshots_dir):
	if not output.endswith(".tex"):
		output += ".tex"
	outfile = open(output, "w")

	header = "\documentclass{book}\n\usepackage[utf8]{inputenc}\n\usepackage{fullpage}\n\usepackage{graphicx}\n\usepackage{subcaption}\n\usepackage{listings}\n\lstset{basicstyle=\large\\ttfamily,columns=fullflexible,breaklines=true}\n\usepackage{hyperref}\n\n\\begin{document}\n\\tableofcontents\n"
	outfile.write(header)

	for logfile in logfiles:
		with open(logfile, 'r') as f:
			observations = json.load(f)

		experiment_name = logfile.split("/")[-2]
		outfile.write("\chapter{"+experiment_name+"}\n\\newpage\n\n")

		world_states = observations["WorldStates"]
		final_observation = world_states[-1]
		chat_history = []

		for i in reversed(range(len(world_states))):
			world_state = world_states[i]
			if "-chat" not in world_state["Screenshots"]["Builder"] and "-chat" not in world_state["Screenshots"]["Architect"]:
				fixed_viewers_ss = getFixedViewerScreenshots(screenshots_dir, experiment_name, world_state["Screenshots"], observations["NumFixedViewers"])
				outfile.write("\section{Gold Configuration}\n")
				outfile.write("\\begin{figure}[!hb]\n\t\centering\n")
				for i in range(len(fixed_viewers_ss)):
					outfile.write("\t\\begin{subfigure}[b]{0.45\\textwidth}\n\t\t\includegraphics[width=\\textwidth]{"+fixed_viewers_ss[i]+"}\n\t\t\caption{FixedViewer"+str(i+1)+"}\n\t\end{subfigure}\n")
				outfile.write("\t\caption{Gold configuration}\n")
				outfile.write("\end{figure}\n")
				outfile.write("\\clearpage\n\n")
				break

		outfile.write("\section{Final Dialogue}\n")
		outfile.write("\\begin{lstlisting}\n")
		for i in range(len(final_observation["ChatHistory"])):
			outfile.write(final_observation["ChatHistory"][i]+"\n")
		outfile.write("\end{lstlisting}\n\\newpage\n\n")

		outfile.write("\section{Step-by-Step}\n\n")

		for world_state in world_states:
			screenshots = world_state["Screenshots"]
			builder_ss = getScreenshotFilePath(screenshots_dir, experiment_name, screenshots.get("Builder"))
			architect_ss = getScreenshotFilePath(screenshots_dir, experiment_name, screenshots.get("Architect"))

			fixed_viewers_ss = []
			if "-chat" not in builder_ss and "-chat" not in architect_ss:
				fixed_viewers_ss = getFixedViewerScreenshots(screenshots_dir, experiment_name, screenshots, observations["NumFixedViewers"])

			if getActionType(screenshots, observations["NumFixedViewers"]) == "None":
				continue

			outfile.write("\\begin{figure}[!ht]\n\t\centering\n")
			outfile.write("\t\\begin{subfigure}[b]{0.45\\textwidth}\n\t\t\includegraphics[width=\\textwidth]{"+builder_ss+"}\n\t\t\caption{Builder}\n\t\end{subfigure}\n")
			outfile.write("\t\\begin{subfigure}[b]{0.45\\textwidth}\n\t\t\includegraphics[width=\\textwidth]{"+architect_ss+"}\n\t\t\caption{Architect}\n\t\end{subfigure}\n")

			for i in range(len(fixed_viewers_ss)):
				outfile.write("\t\\begin{subfigure}[b]{0.45\\textwidth}\n\t\t\includegraphics[width=\\textwidth]{"+fixed_viewers_ss[i]+"}\n\t\t\caption{FixedViewer"+str(i+1)+"}\n\t\end{subfigure}\n")

			outfile.write("\t\caption{"+getActionType(screenshots, observations["NumFixedViewers"])+"}\n")
			outfile.write("\end{figure}\n\n")

			outfile.write("\\begin{lstlisting}\n")
			for i in range(max(len(chat_history)-5, 0), len(chat_history)):
				outfile.write(chat_history[i]+"\n")

			if "chat" in getActionType(screenshots, observations["NumFixedViewers"]):
				if len(world_state["ChatHistory"]) > len(chat_history):
					for i in range(len(chat_history), len(world_state["ChatHistory"])):
						outfile.write("* "+world_state["ChatHistory"][i]+"\n")

				chat_history = world_state["ChatHistory"]

			outfile.write("\end{lstlisting}\n")
			outfile.write("\\clearpage\n\n")

	outfile.write("\end{document}")

def getScreenshotFilePath(screenshots_dir, experiment_name, file_path):
	return "blank.png" if file_path is None else screenshots_dir+"/"+experiment_name+"/"+file_path

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

	return "None"


def main():
	parser = argparse.ArgumentParser(description="Produce .tex file from given json logfiles or directories.")
	parser.add_argument('-l', '--list', nargs='+', help='Json files to be processed, or the directory in which they live', required=True)
	parser.add_argument('-o', '--output', help='Name of output tex file', required=True)
	parser.add_argument('-s', '--screenshots_dir', default="../../../../Minecraft/run/screenshots", help="Screenshots directory path")
	args = parser.parse_args()

	logfiles = getLogfileNames(args.list)
	generateTexfile(logfiles, args.output, args.screenshots_dir)

if __name__ == '__main__':
	main()