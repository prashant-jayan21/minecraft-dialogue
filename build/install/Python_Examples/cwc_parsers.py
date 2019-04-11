from __future__ import print_function
import re, string, argparse

ordinal_map = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,"1st":1, "2nd":2, "3rd":3, "4th":4, "5th":5, "6th":6, "7th":7, "8th":8, "9th":9, "10th":10}
primitives_map = {"shape": ["row", "column", "tower", "square", "rectangle","cube","cuboid", "it"],                         # FIXME: is just "it" dangerous for regex split?
                           "color": ["red", "blue", "green", "purple", "orange", "yellow"],
                           "number": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],      # FIXME: handle sizes of "x by y", "x x y", etc
                           "spatial_rel": ["north", "south", "east", "west", "top", "bottom"]} # FIXME: "the bottom block of the tower" is troublesome
dirs_map = {"north": ["back", "behind"], "south": ["front"], "east": ["right"], "west": ["left"], "top": ["above"], "bottom": ["below", "under", "underneath"]}
general_dirs_map = {"north": "behind", "south": "front", "east": "right", "west": "left", "top": "top", "bottom": "bottom"}
dims = {"row": ["width"], "tower": ["height"], "column": ["length"], "square": ["size"],"cube": ["side"] ,"rectangle":["length","width"],"cuboid":["length","width","height"]}
ordinals = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",
            "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"]
location_predicates = ['top-behind-left', 'top-left-behind', 'behind-top-left', 'behind-left-top', 'left-behind-top', 'left-top-behind', 'top-behind-right', 'top-right-behind', 'behind-top-right', 'behind-right-top', 'right-behind-top', 'right-top-behind', 'top-front-left', 'top-left-front', 'front-top-left', 'front-left-top', 'left-front-top', 'left-top-front', 'top-front-right', 'top-right-front', 'front-top-right', 'front-right-top', 'right-front-top', 'right-top-front', 'bottom-behind-left', 'bottom-left-behind', 'behind-bottom-left', 'behind-left-bottom', 'left-behind-bottom', 'left-bottom-behind', 'bottom-behind-right', 'bottom-right-behind', 'behind-bottom-right', 'behind-right-bottom', 'right-behind-bottom', 'right-bottom-behind', 'bottom-front-left', 'bottom-left-front', 'front-bottom-left', 'front-left-bottom', 'left-front-bottom', 'left-bottom-front', 'bottom-front-right', 'bottom-right-front', 'front-bottom-right', 'front-right-bottom', 'right-front-bottom', 'right-bottom-front','behind-left', 'left-behind', 'behind-right', 'right-behind', 'front-left', 'left-front', 'front-right', 'right-front','left-end','right-end','front-end','behind-end','top-end','bottom-end']

class DummyParser:
    """ Dummy parser that provides a hard-coded logical form as output parse, or passes through the input text directly to the planner.  """
    def __init__(self):
        pass

    def parse(self, text):
        return text, find_shapes(text)

    def reset(self):
        pass

    
class RuleBasedParser:
    def __init__(self):
        self.vars = list(string.ascii_lowercase)
        self.var_id = 0
        self.block_id_counter = 0

        self.current_shapes = []

    def reset(self):
        self.reset_var()
        self.current_shapes = []

    def parse(self, instruction):
        """ Parses an utterance by splitting it into chunks separated by periods or the "such as" tokens and processing them linearly. """
        # allow for manually entering logical forms
        if '^' in instruction or '(' in instruction:  # FIXME: disable for demo?
            return instruction, find_shapes(instruction), instruction

        self.reset()

        print("parse::received instructions:", instruction)
        instruction = preprocess(instruction)

        # split the utterance by delimiters '.' and 'such that'
        instructions = [instr.strip() for instr in re.split(r'\.| such that', instruction) if len(instr.strip()) > 0]
        print("parse::parsing instructions:", instructions, "\n")

        # parse the utterances
        logical_form = []
        for instr in instructions:
            to_add = None

            # fine-grained spatial relation
            if any_exist(['corner','block','-end'],instr) and  any_exist(primitives_map["spatial_rel"], instr) and any_exist(primitives_map["shape"], instr) and (any_exist(ordinals,instr) or any_exist(location_predicates, instr)):

            #if "block" in instr and any_exist(primitives_map["spatial_rel"], instr) and any_exist(primitives_map["shape"], instr):
                to_add = self.parse_fine_grained_spatial_rel(instr)
                self.increment_var()

            # general spatial relation
            elif any_exist(primitives_map["spatial_rel"], instr) and any_exist(primitives_map["shape"], instr):
                to_add = self.parse_general_spatial_rel(instr)

            # isolated shape definition
            elif any_exist(primitives_map["shape"], instr):
                to_add = self.parse_isolated_shape(instr)
                self.increment_var()

            # exit if errors occur
            if to_add is None:
                print("parse::Parsing error occurred!")
                return None, None, None

            logical_form.append(to_add)
            print("parse::current_shapes:", self.current_shapes, "\n")

        print("\nparse::parse result:", "^".join(logical_form))
        return "^".join(logical_form), self.current_shapes, logical_form

    def parse_isolated_shape(self, instruction): 
        """ Parses an instruction that defines a shape in isolation. """
        print("parse_isolated_shape::parsing instruction:", instruction, "...")
        # get relevant values
        primitive_values = {}
        for token in instruction.split():
            for primitive_type in primitives_map:
                if token in primitives_map[primitive_type]:
                    if primitive_type in primitive_values:
                        print("parse_isolated_shape::Warning: type", primitive_type, "("+primitive_values[primitive_type][0]+") already processed for instruction", instruction)
                    elif primitive_type not in primitive_values:
                        primitive_values[primitive_type]=[]
                    primitive_values[primitive_type].append(token)

        # missing information?
        if not set(primitive_values.keys()).issuperset(set(['shape', 'number'])):
            print("parse_isolated_shape::Warning: instruction", instruction, "is missing information.")

        # string together logical form fragments
        logical_form = []
        for primitive_type in ['shape', 'color', 'number']:
            lf = format_lf(primitive_type, primitive_values, self.get_var())
            if lf is not None:
                logical_form.append(lf)
            elif primitive_type != 'color':
                print('parse_isolated_shape::Warning: missing type', primitive_type)

        if primitive_values.get("shape") is None:
            print("parse_isolated_shape::Error: no shape found in instruction:", instruction)
            return None

        # add this shape to list of processed shapes
        self.current_shapes.append([primitive_values["shape"][0], self.get_var()])

        # join and return full logical form
        print("parse_isolated_shape::parsed instruction:", instruction, "->", "^".join(logical_form))
        return "^".join(logical_form)

    def parse_general_spatial_rel(self, instruction):
        """ Parses an instruction that defines a shape with a general spatial relation. """
        print("parse_general_spatial_rel::parsing instruction:", instruction, "...")

        # find the general spatial relation
        instr_split = regex_split(instruction, "spatial_rel")
        if instr_split is None:
            return None

        spatial_rel_primitive = instr_split[1]
        spatial_rel_primitive = general_dirs_map[spatial_rel_primitive]  # FIXME: temporary fix for general spatial rels being inconsistently named

        shape_split = regex_split(instr_split[2], "shape")
        if shape_split is None:
            return None

        # find the referent shape
        shape_primitive = shape_split[1]
        referent_var = self.current_shapes[-1][1]
        for shape, var in self.current_shapes:
            if shape == shape_primitive:
                referent_var = var

        # construct the logical form
        var = self.get_var()
        logical_form = self.parse_isolated_shape(instr_split[0])+"^"+spatial_rel_primitive+'('+var+','+referent_var+')'
        print("parse_general_spatial_rel::parsed instruction:", instruction, "->", logical_form)
        return logical_form

    def parse_fine_grained_spatial_rel(self, instruction):
        """ Parses an instruction that defines a fine-grained spatial relation between two existing shapes. """
        print("parse_fine_grained_spatial_rel::parsing instruction:", instruction, "...")

        # find the general spatial relation
        instr_split = regex_split(instruction, "spatial_rel")
        if instr_split is None:
            return None

        spatial_rel_primitive = instr_split[1]

        # parse block-index or location predicates for blocks in the two mentioned shapes
        block_locations = []
        for instr in [instr_split[0], instr_split[2]]:
            # check for regular ordinals
            ordinals_split = regex_split(instr, 'ordinals')

            # otherwise, check for location predicates (WIP/FIXME: this is not grammatical)
            if ordinals_split is None:
                ordinals_split = regex_split(instr, 'location_predicates')

            # find mentioned shape
            shapes_split = regex_split(instr, 'shape')

            # something went wrong
            if shapes_split is None or ordinals_split is None:
                return None

            block_locations.append((ordinals_split[1].replace(" block",""), shapes_split[1]))

        # find referent variables for the two mentioned shapes
        if len(self.current_shapes) < 2:
            return None

        referent_vars = [self.current_shapes[-1][1], self.current_shapes[-2][1]]
        for i in range(len(referent_vars)):
            ordinal, shape = block_locations[i]
            for reference_shape, var in reversed(self.current_shapes):
                if reference_shape == shape:
                    referent_vars[i] = var
                    if i == 1 and var == referent_vars[0]:
                        continue
                    break

        if referent_vars[0] == referent_vars[1]:
            print("parse_fine_grained_spatial_rel::Error: found two of the same referent block")
            return None

        # construct block-representations for the two mentioned locations
        b1, id1 = self.allocate_block_var(ordinal=block_locations[0][0], var=referent_vars[0])
        b2, id2 = self.allocate_block_var(ordinal=block_locations[1][0], var=referent_vars[1])

        # append the general spatial relation and return
        logical_form = b1+"^"+b2+"^spatial-rel("+spatial_rel_primitive+",0,w"+str(id2)+",w"+str(id1)+")"
        print("parse_fine_grained_spatial_rel::parsed instruction:", instruction, "->", logical_form)
        return logical_form

    def allocate_block_var(self, ordinal, var):
        self.block_id_counter += 1
        return define_block(block_id_counter=self.block_id_counter, ordinal=ordinal, var=var), self.block_id_counter

    def get_var(self):
        """ Gets the alphabetical variable id to be used for assigning a new shape identifier. """
        return self.vars[self.var_id]

    def increment_var(self):
        """ Increments the shape identifier. """
        self.var_id += 1

    def reset_var(self):
        self.var_id = 0
        self.block_id_counter = 0

def to_digit(number):
    return ordinal_map[number]

def any_exist(substrings, string):
    return any(substring in string for substring in substrings)

def get_regex(primitive_type):
    regex_list = primitives_map.get(primitive_type, [])
    if primitive_type == 'ordinals':
        regex_list = [o+" block" for o in ordinals]
    if primitive_type == 'location_predicates':
        regex_list = location_predicates
    if primitive_type == 'spatial_rel':     # FIXME: temporary fix for general spatial relations (top, bottom) to not trigger on fine-grained ones (bottom-right-etc)
        return "( "+(" | ".join(regex_list))+" )"
    return "("+("|".join(regex_list))+")"

def regex_split(instruction, primitive_type):
    instr_split = re.split(get_regex(primitive_type), instruction)
    # print("regex_split::", instruction, ", regex:", get_regex(primitive_type))

    # unhandled
    if len(instr_split) != 3:
        if primitive_type != "ordinals" and primitive_type != "location_predicates":
            print("parse_general_spatial_rel::Warning: unhandled number of", primitive_type+"s found in instruction:", instruction)
        return None

    return [instr.strip() for instr in instr_split]

def format_lf(primitive_type, primitive_values, var):
    """ Formats information for a primitive predicate into its corresponding logical syntax. """
    value = primitive_values.get(primitive_type)
    if value is None:
        return None

    # for shapes
    if primitive_type == 'shape':
        return value[0]+'('+var+')'

    # for colors
    if primitive_type == 'color':
        return 'color('+var+','+value[0]+')'

    # for dimensions
    if primitive_type == 'number':
        print(primitive_values)
        dim = None if primitive_values.get("shape") is None else dims.get(primitive_values["shape"][0])
        s=""
        print(dim)
        for i in range(len(dim)):
            s+=dim[i]+'('+var+','+value[i]+')^'
        
        return s[:-1]

    print("format_lf::Error: no format found for type:", primitive_type)
    return None

def define_block(block_id_counter, ordinal, var):
    """ Constructs the logical form needed for a block-location representation. """
    by_predicate = False if ordinal in ordinals else True

    # block(bx) ^ block-location(bx, wx) ^ location(wx)
    lf = "block(b"+str(block_id_counter)+")^block-location(" + "b"+str(block_id_counter)+ ",w"+str(block_id_counter)+")^location(w"+str(block_id_counter)+")^"
    
    # for ordinals: block-index(a,bx,ordinal)
    # for location predicates: location_predicate(a,bx)
    lf += ordinal+"("+var+",b"+str(block_id_counter)+")" if by_predicate else "block-index("+var+",b"+str(block_id_counter)+","+str(to_digit(ordinal))+")"
    
    return lf

def find_shapes(instruction):
    current_shapes = []
    for predicate in [x.strip() for x in instruction.split('^')]:
        if any(predicate.startswith(shape) for shape in ['square', 'rectangle', 'cube', 'cuboid', 'row', 'tower', 'column']):
            shape, var = predicate.split('(')
            var = var.replace(')','')
            current_shapes.append([shape, var])

    return current_shapes

def preprocess(text):
    text = text.lower()

    for lp in location_predicates:
        l = lp.replace("-"," ")
        text = text.replace(l,lp)

    for key in dirs_map:
        tokens = text.split()
        modified_text = ""

        for token in tokens:
            if any(to_replace == token for to_replace in dirs_map[key]):
                modified_text += key+" "
            else:
                modified_text += token+" "

        text = modified_text.strip()           

    return text

if __name__ == '__main__':
    parser = RuleBasedParser()
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--text', default="Build a red cuboid of size 4 by 3 by 5. Build a second blue square of size 4 above the cuboid such that the 4th block of the square is above the right back corner block of the cuboid")
    args = argparser.parse_args()
    lf = parser.parse(args.text)
    print(lf)
