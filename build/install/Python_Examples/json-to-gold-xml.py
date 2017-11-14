import sys, os, json

if len(sys.argv) < 2 or len(sys.argv) > 3:
	print "Usage: python json_to_xml.py <name of json file> <(optional) name of configuration>"
	sys.exit(0)

with open(sys.argv[1]) as jd:
	log = json.load(jd)

if not os.path.isdir("gold-configurations/"):
	os.makedirs("gold-configurations/")

gf = "gold-configurations/"+ (sys.argv[1].replace(".json","") if len(sys.argv) < 3 else sys.argv[2])+".xml"
gold = open(gf, 'w')

conf = log["all_world_states"][len(log["all_world_states"])-1]["blocks_structure"]
for block in conf:
	bt = str(block["type"])
	bx = str(block["coordinates_absolute"]["x"]+100)
	by = str(block["coordinates_absolute"]["y"])
	bz = str(block["coordinates_absolute"]["z"]+100)
	gold.write("<DrawBlock type=\"cwcmod:"+bt+"\" x=\""+bx+"\" y=\""+by+"\" z=\""+bz+"\"/>\n")

gold.close()