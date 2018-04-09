import os, argparse, json, re
from cwc_io_utils import getLogfileNames

def generateTexfile(logfiles, output, screenshots_dir, timestamps):
	if not os.path.isdir("tex/"):
		os.makedirs("tex/")
	if not output.endswith(".tex"):
		output += ".tex"
	if not output.startswith("tex/"):
		output = "tex/"+output
	outfile = open(output, "w")

	header = "\documentclass{book}\n\usepackage[utf8]{inputenc}\n\usepackage[margin=1in,headheight=13.6pt]{geometry}\n\usepackage{graphicx}\n\usepackage{subcaption}\n\usepackage{listings}\n\lstset{basicstyle=\large\\ttfamily,columns=fullflexible,breaklines=true}\n\usepackage{hyperref}\n\usepackage{fancyhdr}\n\n\pagestyle{fancy}\n\\fancyhf{}\n\\fancyhead[L]{\\nouppercase\leftmark}\n\n\\begin{document}\n\\tableofcontents\n"
	outfile.write(header)

	for logfile in logfiles:
		with open(logfile, 'r') as f:
			observations = json.load(f)

		experiment_name = logfile.split("/")[-2]
		m = re.search('B[0-9]+\-A[0-9]+\-([A-z0-9\-]+)\-[0-9]+', experiment_name)
		outfile.write("\chapter{"+(m.group(1).replace("_","\\textunderscore ") if m else experiment_name)+"}\n\\newpage\n\n")

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

		outfile.write("\section{Dialogue}\n")
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

			action = getActionType(screenshots, observations["NumFixedViewers"]) 
			if action is None:
				continue

			outfile.write("\\begin{figure}[!ht]\n\t\centering\n")
			outfile.write("\t\\begin{subfigure}[b]{0.45\\textwidth}\n\t\t\includegraphics[width=\\textwidth]{"+builder_ss+"}\n\t\t\caption{Builder" + ("" if not timestamps else " ("+getScreenshotTimestamp(builder_ss)+")") + "}\n\t\end{subfigure}\n")
			outfile.write("\t\\begin{subfigure}[b]{0.45\\textwidth}\n\t\t\includegraphics[width=\\textwidth]{"+architect_ss+"}\n\t\t\caption{Architect" + ("" if not timestamps else " ("+getScreenshotTimestamp(architect_ss)+")") + "}\n\t\end{subfigure}\n")

			for i in range(len(fixed_viewers_ss)):
				outfile.write("\t\\begin{subfigure}[b]{0.45\\textwidth}\n\t\t\includegraphics[width=\\textwidth]{"+fixed_viewers_ss[i]+"}\n\t\t\caption{FixedViewer"+str(i+1)+("" if not timestamps else " ("+getScreenshotTimestamp(fixed_viewers_ss[i])+")")+"}\n\t\end{subfigure}\n")

			outfile.write("\t\caption{"+action+"}\n")
			outfile.write("\end{figure}\n\n")

			outfile.write("\\begin{lstlisting}\n")
			for i in range(max(len(chat_history)-5, 0), len(chat_history)):
				outfile.write(chat_history[i]+"\n")

			if "chat" in action:
				if len(world_state["ChatHistory"]) > len(chat_history):
					for i in range(len(chat_history), len(world_state["ChatHistory"])):
						outfile.write("* "+world_state["ChatHistory"][i]+"\n")

				chat_history = world_state["ChatHistory"]

			outfile.write("\end{lstlisting}\n")
			outfile.write("\\clearpage\n\n")

	outfile.write("\end{document}")
	outfile.close()

	print "Successfully written tex file to", output

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

def getScreenshotTimestamp(ss_path):
	return str(ss_path.split("/")[-1].split("-")[0])


def main():
	parser = argparse.ArgumentParser(description="Produce .tex file from given json logfiles or directories.")
	parser.add_argument('-l', '--list', nargs='+', help='Json files to be processed, or the directory in which they live', required=True)
	parser.add_argument('-o', '--output', help='Name of output tex file', required=True)
	parser.add_argument('-s', '--screenshots_dir', default="../../../../Minecraft/run/screenshots", help="Screenshots directory path")
	parser.add_argument("--timestamps", default=False, action="store_true", help="Whether or not to print timestamps in Figure captions")
	args = parser.parse_args()

	if args.screenshots_dir[-1] == '/':
		args.screenshots_dir = args.screenshots_dir[:-1]

	logfiles = getLogfileNames(args.list, "aligned-observations.json")
	generateTexfile(logfiles, args.output, args.screenshots_dir, args.timestamps)

if __name__ == '__main__':
	main()