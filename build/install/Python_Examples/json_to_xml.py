import sys, os, json

if len(sys.argv) < 2 or len(sys.argv) > 3:
	print "Usage: python json_to_xml.py <name of json file> <(optional) name of configuration>"
	sys.exit(0)

with open(sys.argv[1]) as jd:
	log = json.load(jd)

if not os.path.isdir("gold-configurations/"):
	os.makedirs("gold-configurations/")

gfn = "/".join(sys.argv[1].split("/")[-2:])
gf = "gold-configurations/"+ (gfn.replace(".json","") if len(sys.argv) < 3 else sys.argv[2])+".xml"
gold = open(gf, 'w')

conf = log["WorldStates"][len(log["WorldStates"])-1]["BlocksInside"]
for block in conf:
	bt = str(block["Type"])
	bx = str(block["AbsoluteCoordinates"]["X"]+100)
	by = str(block["AbsoluteCoordinates"]["Y"])
	bz = str(block["AbsoluteCoordinates"]["Z"]+100)
	gold.write("<DrawBlock type=\"cwcmod:"+bt+"\" x=\""+bx+"\" y=\""+by+"\" z=\""+bz+"\"/>\n")

gold.close()