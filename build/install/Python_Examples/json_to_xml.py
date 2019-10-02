import sys, os, json, argparse

def blocks_to_xml(conf, displacement=0, postprocessed=True):
	xml_str = ''
	for block in conf:
		bt = str(block["Type"]) if postprocessed else "cwc_"+str(block['type'])+"_rn"
		bx = str((block["AbsoluteCoordinates"]["X"] if postprocessed else block['x'])+displacement)
		by = str(block["AbsoluteCoordinates"]["Y"] if postprocessed else block['y'])
		bz = str((block["AbsoluteCoordinates"]["Z"] if postprocessed else block['z'])+displacement)
		xml_str += "<DrawBlock type=\"cwcmod:"+bt+"\" x=\""+bx+"\" y=\""+by+"\" z=\""+bz+"\"/>\n"
	return xml_str

def get_gold_config_xml(log):
	conf = log["WorldStates"][len(log["WorldStates"])-1]["BlocksInGrid"]
	return blocks_to_xml(conf, displacement=100)

def main(args):
	with open(args.json_file) as jd:
		log = json.load(jd)

	if not os.path.isdir("gold-configurations/"):
		os.makedirs("gold-configurations/")

	gfn = "/".join(args.json_file.split("/")[-2:])
	gf = "gold-configurations/"+ (gfn.replace(".json","") if args.config_name is None else args.config_name)+".xml"
	gold = open(gf, 'w')
	gold.write(to_xml(log))

	print("Wrote gold configuration to", gf)
	gold.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Convert JSON to XML.")
	parser.add_argument("json_file", help="File path of the observations JSON to be converted")
	parser.add_argument("--config_name", default=None, help="Name of output configuration")
	args = parser.parse_args()
	main(args)
