import os, argparse, json, re
from cwc_io_utils import getLogfileNames

def getConfigNameMap():
	with open('tex/configs-to-names.txt') as f:
		config_names = f.readlines()

	config_name_map, name_config_map = {}, {}
	for config in config_names:
		(c,n) = config.split()
		config_name_map[c.strip()] = n.strip()
		name_config_map[n.strip()] = c.strip()

	return config_name_map, name_config_map

def generateTexfile(logfiles, output, screenshots_dir, disable_timestamps):
	if not os.path.isdir("tex/"):
		os.makedirs("tex/")
	if not output.endswith(".tex"):
		output += ".tex"
	if not output.startswith("tex/"):
		output = "tex/"+output
	outfile = open(output, "w")
	simplefile = open(output[:-4]+"-simplified.tex","w")

	header = "\documentclass{book}\n\\usepackage[utf8]{inputenc}\n\\usepackage[margin=1in,headheight=13.6pt]{geometry}\n\\usepackage{graphicx}\n\\usepackage{subcaption}\n\\usepackage{listings}\n\lstset{basicstyle=\large\\ttfamily,columns=fullflexible,breaklines=true}\n\\usepackage{hyperref}\n\\usepackage{fancyhdr}\n\n\pagestyle{fancy}\n\\fancyhf{}\n\\fancyhead[L]{\\nouppercase\leftmark}\n\n\\begin{document}\n\\tableofcontents\n"
	outfile.write(header)
	simplefile.write(header)

	config_name_map, name_config_map = getConfigNameMap()

	for logfile in logfiles:
		with open(logfile, 'r') as f:
			observations = json.load(f)

		experiment_name = logfile.split("/")[-2]
		m = re.search('B[0-9]+\-A[0-9]+\-([A-z0-9\-]+)\-[0-9]+', experiment_name)
		config_name = m.group(1) if m else experiment_name
		if config_name_map.get(config_name) is not None:
			config_name = config_name_map[config_name].replace("_","\\textunderscore ")+" ("+config_name+")"
		else:
			config_name = config_name.replace("_","\\textunderscore ")+" ("+name_config_map[config_name]+")"
		outfile.write("\chapter{"+config_name+"}\n\\newpage\n\n")
		simplefile.write("\chapter{"+config_name+"}\n\\newpage\n\n")

		world_states = observations["WorldStates"]
		final_observation = world_states[-1]
		chat_history = []

		for i in reversed(list(range(len(world_states)))):
			world_state = world_states[i]
			screenshots = world_state["Screenshots"]
			builder_no_chat = True if screenshots.get("Builder") is None else "-chat" not in screenshots.get("Builder")
			architect_no_chat = True if screenshots.get("Architect") is None else "-chat" not in screenshots.get("Architect")
			if builder_no_chat and architect_no_chat:
				fixed_viewers_ss = getFixedViewerScreenshots(screenshots_dir, experiment_name, world_state["Screenshots"], observations["NumFixedViewers"])
				outfile.write("\section{Gold Configuration}\n")
				outfile.write("\\begin{figure}[!hb]\n\t\centering\n")
				for i in range(len(fixed_viewers_ss)):
					outfile.write("\t\\begin{subfigure}[b]{0.45\\textwidth}\n\t\t\includegraphics[width=\\textwidth]{"+fixed_viewers_ss[i]+"}\n\t\t\caption{FixedViewer"+str(i+1)+"}\n\t\end{subfigure}\n")
				outfile.write("\t\caption{Gold configuration}\n")
				outfile.write("\end{figure}\n")
				outfile.write("\\clearpage\n\n")

				simplefile.write("\section{Gold Configuration}\n")
				simplefile.write("\\begin{figure}[!hb]\n\t\centering\n")
				for i in range(len(fixed_viewers_ss)):
					simplefile.write("\t\\begin{subfigure}[b]{0.45\\textwidth}\n\t\t\includegraphics[width=\\textwidth]{"+fixed_viewers_ss[i]+"}\n\t\t\caption{FixedViewer"+str(i+1)+"}\n\t\end{subfigure}\n")
				simplefile.write("\t\caption{Gold configuration}\n")
				simplefile.write("\end{figure}\n")
				simplefile.write("\\clearpage\n\n")
				break

		outfile.write("\section{Dialogue}\n")
		outfile.write("\\begin{lstlisting}\n")
		for i in range(len(final_observation["ChatHistory"])):
			outfile.write(final_observation["ChatHistory"][i]+"\n")
		outfile.write("\end{lstlisting}\n\\newpage\n\n")

		simplefile.write("\section{Dialogue}\n")
		simplefile.write("\\begin{lstlisting}\n")
		for i in range(len(final_observation["ChatHistory"])):
			simplefile.write(final_observation["ChatHistory"][i]+"\n")
		simplefile.write("\end{lstlisting}\n\clearpage\n\n")

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
			outfile.write("\t\\begin{subfigure}[b]{0.45\\textwidth}\n\t\t\includegraphics[width=\\textwidth]{"+builder_ss+"}\n\t\t\caption{Builder" + ("" if disable_timestamps else " ("+getScreenshotTimestamp(builder_ss)+")") + "}\n\t\end{subfigure}\n")
			outfile.write("\t\\begin{subfigure}[b]{0.45\\textwidth}\n\t\t\includegraphics[width=\\textwidth]{"+architect_ss+"}\n\t\t\caption{Architect" + ("" if disable_timestamps else " ("+getScreenshotTimestamp(architect_ss)+")") + "}\n\t\end{subfigure}\n")

			for i in range(len(fixed_viewers_ss)):
				outfile.write("\t\\begin{subfigure}[b]{0.45\\textwidth}\n\t\t\includegraphics[width=\\textwidth]{"+fixed_viewers_ss[i]+"}\n\t\t\caption{FixedViewer"+str(i+1)+("" if disable_timestamps else " ("+getScreenshotTimestamp(fixed_viewers_ss[i])+")")+"}\n\t\end{subfigure}\n")

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
	simplefile.write("\end{document}")
	simplefile.close()

	simple = output[:-4]+"-simplified.tex"
	print("Successfully written tex file to", output)
	print("Successfully written simplified tex file to", simple)

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
	parser.add_argument('-s', '--screenshots_dir', default=None, help="Screenshots directory path. If unspecified, retrieves screenshots from a default location determined from the logfiles path")
	parser.add_argument("--disable_timestamps", default=True, action="store_false", help="Disable printing timestamps in Figure captions (looks nicer)")
	args = parser.parse_args()

	if args.screenshots_dir is None:
		index = -2
		if not os.path.isdir(args.list[0]):
			index -= 1
		args.screenshots_dir = "/".join(args.list[0].split("/")[:index])+"/screenshots/"

	if args.screenshots_dir[-1] == '/':
		args.screenshots_dir = args.screenshots_dir[:-1]

	logfiles = getLogfileNames(args.list, "aligned-observations.json")
	generateTexfile(logfiles, args.output, args.screenshots_dir, args.disable_timestamps)

if __name__ == '__main__':
	main()