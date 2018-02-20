from __future__ import print_function
from __future__ import division
# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

from builtins import range
from past.utils import old_div
import MalmoPython
import os
import sys
import time
import json
import copy
import errno
import random
import math
import xml.etree.ElementTree as ET

# Test of DrawSign, DrawItem, and reading NBTTagCompounds from ObservationFromRay.
# This draws a physical decision tree, and then animates the process of traversing it.
# For a data set, we use a dump of item types and their associated attributes, generated by
# the Malmo mod. The tree is created directly from the data, using the ID3/C4.5 approach.
# We use signposts to display the decision at each branch node. The provided attributes
# are not quite sufficient for distinguishing between *all* possible items, so the leaf nodes
# are coloured as follows:
# Green = a leaf that represents just one item.
# Blue = a leaf that represents four or less items (one for each line that can be displayed on a sign).
# Red = a leaf that represents more than four items (only the first four will be listed on the sign).

# To demonstrate the tree in action, we choose an item at random, and then follow the tree for that item.
# The agent "reads" the sign, answers the question, and follows the correct path down the tree.

# If run as a test, this will iterate through the 130-or-so identifiable items, and fail if it doesn't
# manage to collect each one. (They are positioned at their corresponding leaf node.)

# First, read in the json item data we've been given:
schema_dir = None
try:
    schema_dir = os.environ['MALMO_XSD_PATH']
except KeyError:
    print("MALMO_XSD_PATH not set? Check environment.")
    exit(1)
item_json = schema_dir + os.sep + "items.json"

with open(item_json, encoding='utf-8') as data_file:
    item_data = json.loads(data_file.read())

# Now process it into a useful state.
# Due to idiosyncrasies in the way Minecraft items are defined, the variant property isn't always
# visible - do a little cheating to fill in this missing information here:
for item in item_data:
    for wood_type in ['jungle', 'spruce', 'acacia', 'dark_oak', 'oak', 'birch']:
        if (wood_type + "_") in item["type"]:
            item["hasVariant"] = True
            item["variant"] = wood_type
            break   # to avoid matching "oak" where we've already matched "dark_oak"

# Pull out all the different types of attribute we've been given.
# (Note that not all attributes need to exist for each item - the tree-building algorithm will
# deal with this.)
bool_atts = set([k for id in item_data for k in id.keys() if type(id[k]) is bool])
int_atts = set([k for id in item_data for k in id.keys() if type(id[k]) is int])
float_atts = set([k for id in item_data for k in id.keys() if type(id[k]) is float])
string_atts = set([k for id in item_data for k in id.keys() if type(id[k]) is str and k != "type"])

# List of attributes we will use:
attributes = list(bool_atts)

# We are generating a binary tree, so all non-boolean attributes need to be converted, as follows.
# Create boolean attributes from the numerical attributes:
for att in int_atts | float_atts:
    # Find all the values this attribute can take: (we can do this, because there aren't that many!)
    values = sorted(set([i[att] for i in item_data if att in i]))
    # Create a boolean attribute "att > x" for all but max x:
    attributes += [att + ">" + str(v) for v in values[:-1]]
    # And augment item_data with the boolean values for these new attributes:
    for item in item_data:
        if att in item:
            for v in values[:-1]:
                item[att + ">" + str(v)] = (item[att] > v)

# Do essentially the same thing for our string attributes:
for att in string_atts:
    # Find all the values this attribute can take: (we can do this, because there aren't that many!)
    values = set([i[att] for i in item_data if att in i])
    # Create a boolean attribute "att=x" for all x:
    attributes += [att + "=" + v for v in values]
    # And augment item_data with the boolean values for these new attributes:
    for item in item_data:
        if att in item:
            for v in values:
                item[att + "=" + v] = (item[att] == v)

# Add some bonus attributes keyed off the name:
for item in item_data:
    item["isOre"] = (item["type"].endswith("_ore"))
    item["isStairs"] = (item["type"].endswith("_stairs"))
attributes += ["isOre","isStairs"]

item_table = {item["type"]:item for item in item_data}
item_types = list(item_table)

# For tracking to see how helpful the attributes turn out to be for categorising item types:
used_attributes = []
identifiable_objects = []       # Where the item gets its own leaf in the tree.
semi_identifiable_objects = []  # Where the item shares a leaf with < 4 other item types.
unidentifiable_objects = []     # Where four or more items all end up in the same leaf.

def split_on_attribute(data, attribute):
    '''Return two sets, one where attribute is true, one where attribute is false.'''
    return [d for d in data if item_table[d][attribute]], [d for d in data if not item_table[d][attribute]]

def calc_entropy(data):
    '''Calculate the entropy in this data set.'''
    if len(data) == 0:
        return 0
    ent = 0
    counts = {item:0 for item in item_types}
    for d in data:
        counts[d] += 1
    for item in item_types:
        p_item = counts[item] / len(data)
        if p_item != 0:
            ent += p_item * math.log(p_item)
    return -ent

def perform_split(data, unused_attributes):
    '''Split data on the best attribute, and recurse, building a tree as we go.'''
    # First, calculate the entropy of our data set:
    ent = calc_entropy(data)
    # Now, find the best attribute for splitting:
    gains = {att:0 for att in unused_attributes}
    for att in unused_attributes:
        # Not all attributes are shared by every item, so only use this attribute
        # if all items in the data possess it.
        attribute_present = [att in item_table[d] for d in data]
        if not all(attribute_present):
            continue
        # Trial split on this attribute:
        x, y = split_on_attribute(data, att)
        # Calculate the entropy for each subset, and hence the information gain from
        # performing this split:
        ent_x = calc_entropy(x)
        ent_y = calc_entropy(y)
        px = len(x) / len(data)
        py = len(y) / len(data)
        information_gain = ent - ((px * ent_x) + (py * ent_y))
        gains[att] = information_gain
    # Which attribute produced the greatest information gain?
    split_attribute = max(gains.keys(), key=(lambda key: gains[key]))

    if gains[split_attribute] == 0:
        # We actually gain nothing from performing this split, so don't do it.
        # Instead, add a leaf to our tree.
        if len(data) == 1:
            # Best case - item uniquely identified.
            identifiable_objects.append(data[0])
            return node(data[0], blocktype="emerald_block", itemtype=data[0])
        else:
            # Can't uniquely identify item...
            if len(data) <= 4:  # ...but can list all possible candidates on one sign.
                for d in data:
                    semi_identifiable_objects.append(d)
            else:   # ...red node - whole class of unidentifiable objects.
                for d in data:
                    unidentifiable_objects.append(d)
            # Create the node and return.
            return node("/".join(data), blocktype=("redstone_block" if len(data) > 4 else "diamond_block") )

    # The split is worth performing, so create a decision node and recurse.
    nd = node(split_attribute + "?//&lt;-TRUE FALSE-&gt;", blocktype="iron_block")
    # Track which attributes we've used, for curiosity's sake.
    used_attributes.append(split_attribute)

    # Copy the attributes we were passed in, and remove the attribute we've just split on.
    attributes = unused_attributes[:]
    attributes.remove(split_attribute)
    # And pass this new list of attributes down the tree to perform the next splits.
    x, y = split_on_attribute(data, split_attribute)
    # Add these subtrees as children to our node:
    nd.setLeft(perform_split(x, attributes))
    nd.setRight(perform_split(y, attributes))
    # And return:
    return nd

class node:
    '''Simple class to help model tree.'''
    def __init__(self, text, blocktype=None, itemtype=None):
        self._text = text
        self._left = None
        self._right = None
        self._parent = None
        self._width = None
        self._blocktype = blocktype
        self._itemtype = itemtype

    def setLeft(self, node):
        self._left = node
        if node is not None:
            node.setParent(self)
        self._width = None

    def setRight(self, node):
        self._right = node
        if node is not None:
            node.setParent(self)
        self._width = None

    def setParent(self, node):
        self._parent = node
        self._width = None

    def isLeaf(self):
        return self._left is None and self._right is None
        
    def getBlockType(self):
        return self._blocktype

    def getItemType(self):
        return self._itemtype

    def getWidth(self):
        # To help build the tree "physically" in Minecraft, we want to track the width of
        # each node. We store this as a tuple: width of left subtree, width of our node,
        # width of right subtree. A leaf node requires (0,1,0), since it has no subtrees.
        # A parent calculates its width as follows:
        # The width of the left subtree is calculated as the width of the left child's subtree,
        # plus the width of the left child's node.
        # The width of the right subtree is calculated similarly as the width of the right child's node + right subtree.
        # The centre is calculated as the width of the children's "inner" trees - eg the left child's *right* subtree
        # plus the right child's *left* subtree - with a minimum value of 1, so that a parent of two leaf nodes doesn't vanish.
        # This calculation is propagated up the tree to the root. The tree can then be drawn, top-down, with each parent
        # node knowing how to allow enough space for its children.
        # Eg the width values for the following tree would be as follows:
        # D, E, F and G: (0,1,0)
        # B and C: (1,1,1)
        # A: (2,2,2)
        #
        #      A
        #    /   \
        #   B     C
        #  / \   / \
        # D   E F   G
        # 
        # Doing it this way allows us to create a much more compact tree, which is useful when your agent
        # is physically walking it.

        if self._width is not None: # cache the width
            return self._width
        if self.isLeaf():
            return (0,1,0)  # Leaf needs a single block for the node itself, and no space for subtrees.
        lh = self._left.getWidth()
        rh = self._right.getWidth()
        self._width = (lh[0] + lh[1], max(lh[2] + rh[0], 1), rh[1] + rh[2])
        return self._width

    def getLeft(self):
        return self._left

    def getRight(self):
        return self._right

    def getText(self):
        lines = self._text.split("/")
        return lines + [''] * (4 - len(lines))

def drawTree(rootNode, x, y, z, isLeft):
    xml = ''
    if rootNode.isLeaf():
        # Draw the leaf node block itself:
        xml = '<DrawBlock x="{}" y="{}" z="{}" type="{}"/>'.format(x, y, z, rootNode.getBlockType())
        # Fill block above with air to remove any leftover items from last drawing:
        xml += '<DrawBlock x="{}" y="{}" z="{}" type="air"/>'.format(x, y+1, z)
        # Draw the signpost:
        lines = rootNode.getText()
        xml += '<DrawSign x="{}" y="{}" z="{}" type="standing_sign" line1="{}" line2="{}" line3="{}" line4="{}"/>'.format(x, y+1, z, lines[0], lines[1], lines[2], lines[3])
        # And draw the corresponding item, if there's only one:
        if rootNode.getItemType() is not None:
            xml += '<DrawItem x="{}" y="{}" z="{}" type="{}"/>'.format(x, y+1, z, rootNode.getItemType())
    else: # Not a leaf node - draw a platform of the correct width, and recurse.
        # Draw the platform:
        width = rootNode.getWidth()
        xml = '<DrawCuboid x1="{}" y1="{}" z1="{}" x2="{}" y2="{}" z2="{}" type="{}"/>'.format(x, y, z, x+width[1]-1, y, z, rootNode.getBlockType())
        # Draw the sign, at the correct end of the platform:
        lines = rootNode.getText()
        xml += '<DrawSign x="{}" y="{}" z="{}" type="standing_sign" line1="{}" line2="{}" line3="{}" line4="{}"/>'.format((x+width[1]-1 if isLeft else x), y+1, z, lines[0], lines[1], lines[2], lines[3])
        # And recurse:
        if rootNode.getLeft() is not None:
            xml += drawTree(rootNode.getLeft(), x - rootNode.getLeft().getWidth()[1], y - 3, z, True)
        if rootNode.getRight() is not None:
            xml += drawTree(rootNode.getRight(), x + width[1], y - 3, z, False)
    return xml
    
def createTree():
    # Just use the full list of types to create our tree:
    sample = list(item_types)
    nd = perform_split(sample, attributes)
    return nd

def generateText(x, y, z, text):
    '''Silly little drawing routine to convert text into DrawBlock commands.'''
    alphabet = {
        "A":[0x04, 0x0a, 0x11, 0x11, 0x1f, 0x11, 0x11],
        "B":[0x1e, 0x11, 0x11, 0x1e, 0x11, 0x11, 0x1e],
        "C":[0x0e, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0e],
        "D":[0x1e, 0x09, 0x09, 0x09, 0x09, 0x09, 0x1e],
        "E":[0x1f, 0x10, 0x10, 0x1c, 0x10, 0x10, 0x1f],
        "F":[0x1f, 0x10, 0x10, 0x1f, 0x10, 0x10, 0x10],
        "G":[0x0e, 0x11, 0x10, 0x10, 0x13, 0x11, 0x0f],
        "H":[0x11, 0x11, 0x11, 0x1f, 0x11, 0x11, 0x11],
        "I":[0x0e, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0e],
        "J":[0x1f, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0c],
        "K":[0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
        "L":[0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1f],
        "M":[0x11, 0x1b, 0x15, 0x11, 0x11, 0x11, 0x11],
        "N":[0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11],
        "O":[0x0e, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0e],
        "P":[0x1e, 0x11, 0x11, 0x1e, 0x10, 0x10, 0x10],
        "Q":[0x0e, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0d],
        "R":[0x1e, 0x11, 0x11, 0x1e, 0x14, 0x12, 0x11],
        "S":[0x0e, 0x11, 0x10, 0x0e, 0x01, 0x11, 0x0e],
        "T":[0x1f, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
        "U":[0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0e],
        "V":[0x11, 0x11, 0x11, 0x11, 0x11, 0x0a, 0x04],
        "W":[0x11, 0x11, 0x11, 0x15, 0x15, 0x1b, 0x11],
        "X":[0x11, 0x11, 0x0a, 0x04, 0x0a, 0x11, 0x11],
        "Y":[0x11, 0x11, 0x0a, 0x04, 0x04, 0x04, 0x04],
        "Z":[0x1f, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1f],
        " ":[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}
    xml = ""
    for char in text.upper():
        if char not in alphabet:
            continue    # Make no effort to do anything other than [A-Z] and space.
        data = alphabet[char]
        for col, val in enumerate(data):
            for bit in range(5):
                if (val & (2**(4-bit))) > 0:
                    xml += '<DrawBlock x="{}" y="{}" z="{}" type="redstone_block"/>'.format(x + bit, y, z + col)
        x += 6
    return xml


def getMissionXML(target_item, fresh_world, tree, testing):
    forceReset = '"true"' if fresh_world else '"false"'
    structureXML = '''
        <DrawingDecorator>''' + drawTree(tree, 0, 40, 0, False) + generateText(-40, 10, -40, "DECISION TREES ARE FUN") + '''</DrawingDecorator>'''
    startpos=(0.5, 44, 1.24)
    endCondition = ''
    if testing:
        endCondition = '''<AgentQuitFromCollectingItem>
                            <Item type="''' + target_item + '''" description="PASSED"/>
                        </AgentQuitFromCollectingItem>'''

    return '''<?xml version="1.0" encoding="UTF-8" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

    <About>
        <Summary>Looking for ''' + target_item + '''</Summary>
    </About>

    <ModSettings>
        <MsPerTick>10</MsPerTick>
    </ModSettings>

    <ServerSection>
        <ServerHandlers>
            <FlatWorldGenerator generatorString="3;7,2*3,2;12;" forceReset=''' + forceReset + '''/>''' + structureXML + '''
            <ServerQuitWhenAnyAgentFinishes />
        </ServerHandlers>
    </ServerSection>

    <AgentSection mode="Survival">
        <Name>Quinlan</Name>
        <AgentStart>
            <Placement x="''' + str(startpos[0]) + '''" y="''' + str(startpos[1]) + '''" z="''' + str(startpos[2]) + '''" pitch="50" yaw="180"/>
        </AgentStart>
        <AgentHandlers>
            <MissionQuitCommands/>
            <ChatCommands/>
            <ContinuousMovementCommands/>
            <ObservationFromFullStats/>
            <ObservationFromRay includeNBT="true"/>
            <ObservationFromGrid>
                <Grid name="ground" absoluteCoords="false">
                    <min x="-2" y="-1" z="-1"/>
                    <max x="2" y="-1" z="-1"/>
                </Grid>
            </ObservationFromGrid>''' + endCondition + '''
            <RewardForMissionEnd rewardForDeath="-1.0">
                <Reward description="PASSED" reward="1.0"/>
            </RewardForMissionEnd>
        </AgentHandlers>
    </AgentSection>
  </Mission>'''

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools
    print = functools.partial(print, flush=True)

agent_host = MalmoPython.AgentHost()
agent_host.addOptionalStringArgument( "recordingDir,r", "Path to location for saving mission recordings", "" )
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print('ERROR:',e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)

recording = False
my_mission_record = MalmoPython.MissionRecordSpec()
recordingsDirectory = agent_host.getStringArgument("recordingDir")
if len(recordingsDirectory) > 0:
    recording = True
    try:
        os.makedirs(recordingsDirectory)
    except OSError as exception:
        if exception.errno != errno.EEXIST: # ignore error if already existed
            raise
    my_mission_record.recordRewards()
    my_mission_record.recordObservations()
    my_mission_record.recordCommands()
    my_mission_record.recordMP4(24,2000000)

print("GENERATING TREE...")
tree = createTree() # This runs the ID3 and creates the actual XML for sending to Minecraft.

def print_underline(text):
    print()
    print(text)
    print("="*len(text))

# Print some information about the tree-building process:
print_underline("TREE STATS:")
print()

print_underline("IDENTIFIABLE OBJECTS: " + str(len(identifiable_objects)))
print(",".join(identifiable_objects))
print_underline("SEMI-IDENTIFIABLE OBJECTS: " + str(len(semi_identifiable_objects)))
print(",".join(semi_identifiable_objects))
print_underline("UNIDENTIFIABLE OBJECTS: " + str(len(unidentifiable_objects)))
print(",".join(unidentifiable_objects))
print()
set_used_attributes = set(used_attributes)
print_underline("USED ATTRIBUTES: " + str(len(set_used_attributes)))
print(",".join(set_used_attributes))
unused_attributes = [att for att in attributes if not att in used_attributes]
print_underline("UNUSED ATTRIBUTES: " + str(len(unused_attributes)))
print(",".join(unused_attributes))
print()

testing = agent_host.receivedArgument("test")
if testing:
    num_iterations = len(identifiable_objects)
    sleep_scale = 0.3
else:
    num_iterations = 30000
    sleep_scale = 1.0

for i in range(num_iterations):
    if testing:
        target_item = identifiable_objects[i]
    else: # Choose a random item to "find":
        target_item = random.choice(item_types)
    print("Mission {} - target: {}".format(i+1, target_item))
    missionXML = getMissionXML(target_item, i == 0, tree, testing)
    if recording:
        my_mission_record.setDestination(recordingsDirectory + "//" + "Mission_" + str(i+1) + ".tgz")
    my_mission = MalmoPython.MissionSpec(missionXML, True)
    max_retries = 3
    for retry in range(max_retries):
        try:
            agent_host.startMission( my_mission, my_mission_record )
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission:",e)
                exit(1)
            else:
                time.sleep(2)

    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        print(".", end="")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
    print()

    # main loop:
    last_question = None
    direction = 0
    while world_state.is_mission_running:
        if world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            # We use the grid observation to determine how fast to move -
            # if we are near the edge of a platform, slow down!
            if u"ground" in ob and direction != 0:
                grid = ob[u"ground"]
                iron_blocks = grid.count("iron_block")
                speed = direction * (0.5 ** (5 - iron_blocks))
                agent_host.sendCommand("strafe " + str(speed))
            # Use the line of sight observation to "read" the signs:
            if u"LineOfSight" in ob:
                los = ob[u"LineOfSight"]
                if los["type"] == "standing_sign" and "NBTTagCompound" in los:
                    tag = los["NBTTagCompound"]
                    t1 = json.loads(tag["Text1"])
                    if t1["text"].endswith("?"):
                        # Found a question!
                        question = t1["text"][:-1]
                        if not question == last_question:
                            agent_host.sendCommand("strafe 0")
                            agent_host.sendCommand("chat " + question + "?")
                            time.sleep(sleep_scale)
                            last_question = question
                            if not question in item_table[target_item]:
                                print("Something went wrong - did we fall off a branch?")
                                if testing:
                                    exit(1)
                                else:
                                    agent_host.sendCommand("quit")
                            elif item_table[target_item][question]:
                                agent_host.sendCommand("chat Yes!")
                                direction = -1
                            else:
                                agent_host.sendCommand("chat No!")
                                direction = 1
                    else:
                        agent_host.sendCommand("strafe 0")
                        agent_host.sendCommand("chat Finished!")
                        time.sleep(3.0 * sleep_scale)
                        agent_host.sendCommand("quit")
        world_state = agent_host.getWorldState()

    if testing:
        reward = world_state.rewards[-1].getValue()
        print("Result: " + str(reward))
        if reward < 0:
            print("Failed to collect " + target_item)
            exit(1)