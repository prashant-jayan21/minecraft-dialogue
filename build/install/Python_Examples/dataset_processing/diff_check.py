import xml.etree.ElementTree as ET

def get_built_config(observations_dict):
    """
    Args:
        observations_dict: The json observations data for a mission

    Returns:
        The built config at the end of the mission
    """

    built_config_raw = observations_dict["WorldStates"][-1]["BlocksInGrid"]

    def reformat(block):
        return {
            "x": block["AbsoluteCoordinates"]["X"],
            "y": block["AbsoluteCoordinates"]["Y"],
            "z": block["AbsoluteCoordinates"]["Z"],
            "type": block["Type"]
        }

    built_config = map(reformat, built_config_raw)

    return built_config

def get_gold_config(gold_config_xml_file):
    with open(gold_config_xml_file) as f:
        all_lines = map(lambda t: t.strip(), f.readlines())

    gold_config_raw = map(ET.fromstring, all_lines)

    def reformat(block):
        return {
            "x": int(block.attrib["x"]),
            "y": int(block.attrib["y"]),
            "z": int(block.attrib["z"]),
            "type": block.attrib["type"][len("cwcmod:"):]
        }

    gold_config = map(reformat, gold_config_raw)

    return gold_config

if __name__ == "__main__":
    import pprint
    import json

    with open("/Users/prashant/Downloads/data-4-16/B36-A35-C140-1523917326878/postprocessed-observations.json") as observations:
        observations_dict = json.load(observations)

    pprint.PrettyPrinter(indent = 2).pprint(get_built_config(observations_dict))

    pprint.PrettyPrinter(indent = 2).pprint(get_gold_config("../gold-configurations/C1.xml"))
