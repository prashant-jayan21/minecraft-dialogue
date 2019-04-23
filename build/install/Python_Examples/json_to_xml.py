import sys, os, json, argparse

def blocks_to_xml(conf, displacement=0, postprocessed=True):
	return_str = ''
	for block in conf:
		if postprocessed:
			bt = str(block["Type"])
			bx = str(block["AbsoluteCoordinates"]["X"]+displacement)
			by = str(block["AbsoluteCoordinates"]["Y"])
			bz = str(block["AbsoluteCoordinates"]["Z"]+displacement)

		else:
			bt = "cwc_minecraft_"+str(block["type"])+"_rn"
			bx = str(block["x"]+displacement)
			by = str(block["y"])
			bz = str(block["z"]+displacement)

		return_str += "<DrawBlock type=\"cwcmod:"+bt+"\" x=\""+bx+"\" y=\""+by+"\" z=\""+bz+"\"/>\n"

	return return_str

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

	conf = log["WorldStates"][-1]["BlocksInGrid"]
	gold.write(blocks_to_xml(conf, displacement=args.displacement))

	print "Wrote gold configuration to", gf
	gold.close()

if __name__ == '__main__':
	main()
