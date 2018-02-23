import sys, os, json, argparse

def main():
	parser = argparse.ArgumentParser(description="Convert JSON to XML.")
	parser.add_argument("json_file", help="File path of the observations JSON to be converted")
	parser.add_argument("--config_name", default=None, help="Name of output configuration")
	parser.add_argument("--displacement", type=int, default=100, help="Displacement value for X and Z coordinates")
	args = parser.parse_args()

	with open(args.json_file) as jd:
		log = json.load(jd)

	if not os.path.isdir("gold-configurations/"):
		os.makedirs("gold-configurations/")

	gfn = "/".join(args.json_file.split("/")[-2:])
	gf = "gold-configurations/"+ (gfn.replace(".json","") if args.config_name is None else args.config_name)+".xml"
	gold = open(gf, 'w')

	conf = log["WorldStates"][len(log["WorldStates"])-1]["BlocksInside"]
	for block in conf:
		bt = str(block["Type"])
		bx = str(block["AbsoluteCoordinates"]["X"]+args.displacement)
		by = str(block["AbsoluteCoordinates"]["Y"])
		bz = str(block["AbsoluteCoordinates"]["Z"]+args.displacement)
		gold.write("<DrawBlock type=\"cwcmod:"+bt+"\" x=\""+bx+"\" y=\""+by+"\" z=\""+bz+"\"/>\n")

	gold.close()

if __name__ == '__main__':
	main()