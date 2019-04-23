from __future__ import print_function
import time, MalmoPython

SHOW_COMMANDS = False
verbose = False

# map of colors to corresponding hotbar IDs
color_map = {
    'red': 1,
    'orange': 2,
    'yellow': 3,
    'green': 4,
    'blue': 5,
    'purple': 6,
    'white': 1
}

# default pitch values by direction
pitch_dirs = {
    "north": 60,
    "east": 60,
    "south": 60,
    "west": 60,
    "top": 90,
    "bottom": -90,
    "bottom_north": -60,
    "bottom_east": -60,
    "bottom_south": -60,
    "bottom_west": -60,
    "top_north": 55,
    "top_east": 55,
    "top_south": 55,
    "top_west": 55
}

# default yaw values by direction
yaw_dirs = {
    "north": 0,
    "east": 90,
    "south": 180,
    "west": 270,
    "bottom_north": 0,
    "bottom_east": 90,
    "bottom_south": 180,
    "bottom_west": 270,
    "top_north": 0,
    "top_east": 90,
    "top_south": 180,
    "top_west": 270,
}

# map of relative to cardinal directions
relative_to_cardinal = {
    "ahead": "north",
    "left": "west",
    "right": "east", 
    "behind": "south"
}

# delta values by which coordinates should be added to access blocks in specific directions
coord_deltas = {
    "ahead": {
        "north": (0, 0, 1),
        "south": (0, 0, -1),
        "east": (-1, 0, 0),
        "west": (1, 0, 0),
        "top": (0, 0, 1),
        "bottom": (0, 0, 1),
        "bottom_north": (0, 0, 1),
        "bottom_south": (0, 0, -1),
        "bottom_east": (-1, 0, 0),
        "bottom_west": (1, 0, 0),
        "top_north": (0, 0, 1),
        "top_south": (0, 0, -1),
        "top_east": (-1, 0, 0),
        "top_west": (1, 0, 0)
    },
    "left": {
        "north": (1, 0, 0),
        "south": (-1, 0, 0),
        "east": (0, 0, 1),
        "west": (0, 0, -1),
        "top": (1, 0, 0),
        "bottom": (1, 0, 0)  
    },
    "right": {
        "north": (-1, 0, 0),
        "south": (1, 0, 0),
        "east": (0, 0, -1),
        "west": (0, 0, 1),
        "top": (-1, 0, 0),
        "bottom": (-1, 0, 0)
    },
    "behind": {
        "top": (0, 0, 1),
        "bottom": (0, 0, 1)    
    },
    "above": {
        "bottom_north": (0, 1, 0),
        "bottom_south": (0, 1, 0),
        "bottom_east": (0, 1, 0),
        "bottom_west": (0, 1, 0)
    }
}

# delta values by which pitch/yaw values should be added to modify view based on direction
view_deltas = {
    "ahead": (-30, 0),
    "left": (-15, -35),
    "right": (-15, 35),
    "behind": (0, 0),
    "above_bottom": (30, 0),
    "ahead_bottom": (60, 0),
    "ahead_top": (0, 0),
    "top": (-15, 0),
    "bottom": (15, 0)
}

def teleportMovement(ah, teleport_x=None, teleport_y=None, teleport_z=None):
    """ Teleports the agent to a specific (x,y,z) location in the map. """
    sendCommand(ah, "tp " + str(teleport_x) + " " + str(teleport_y) + " " + str(teleport_z))
    time.sleep(1)

def setPitchYaw(ah, pitch=None, yaw=None):
    """ Sets the pitch and yaw of the agent. For efficiency, only set pitch/yaw to non-None values if they differ from the agent's current pitch/yaw values. """
    if yaw is not None:
        sendCommand(ah, "setYaw "+str(yaw))
        time.sleep(1)

    if pitch is not None:
        sendCommand(ah, "setPitch "+str(pitch))
        time.sleep(1)

def chooseInventorySlot(ah, index):
    """ Selects the given block color from the hotbar. """
    selection = "hotbar." + str(index)
    sendCommand(ah, selection+" 1")
    sendCommand(ah, selection+" 0")

def performAction(ah, action):
    """ Instructs agent to perform a given action with their hand. """
    action_type = 'use' if action == 'putdown' else 'attack'
    sendCommand(ah, action_type+' 1')
    time.sleep(0.1)
    sendCommand(ah, action_type+' 0')
    time.sleep(0.2)

def sendCommand(ah, command):
    """ Use this method to send all commands to the agent. """
    if SHOW_COMMANDS is True:
        print(command)
    ah.sendCommand(command)

def find_teleport_location(blocks_in_grid, x, y, z, action):
    """ Finds a feasible (open) location, pitch, and yaw to teleport the agent to such that a block can be placed at (x,y,z). """
    if verbose:
        print("\nfind_teleport_location::finding feasible location for block:", x, y, z, "where blocks_in_grid:", blocks_in_grid)

    # check for unoccupied locations that the agent can teleport to: south/east/north/west of location; above/below location; below and to the south/east/north/west of location
    for px, py, pz, direction in [(x, y, z+1, "south"),  (x-1, y, z, "west"), (x, y, z-1, "north"), (x+1, y, z, "east"), (x, y+1, z, "top"), (x, y-2, z, "bottom"), \
                                  (x, y+1, z+1, "top_south"), (x-1, y+1, z, "top_west"), (x, y+1, z-1, "top_north"), (x+1, y+1, z, "top_east"), \
                                  (x, y-1, z+1, "bottom_south"), (x-1, y-1, z, "bottom_west"), (x, y-1, z-1, "bottom_north"), (x+1, y-1, z, "bottom_east")]:

        if verbose:
            print("find_teleport_location::checking location", px, py, pz, direction)
        
        # location is too low
        if py < 1:
            if verbose:
                print("find_teleport_location::", px, py, pz, direction, "is too low!")
            continue 

        # location is occupied
        if not location_is_empty(blocks_in_grid, px, py, pz) or not location_is_empty(blocks_in_grid, px, py+1, pz):
            if verbose:
                print("find_teleport_location::", px, py, pz, direction, "is occupied!")
            continue

        # get default pitch/yaw (facing downwards, to place a block on top of a surface)
        pitch = pitch_dirs.get(direction)
        yaw = yaw_dirs.get(direction, 0)

        # return the default pitch/yaw values if the the block can be placed feasibly with the default view
        if action == 'remove' or (direction == "bottom" and not location_is_empty(blocks_in_grid, x, y+1, z)) or ("_" not in direction and not location_is_empty(blocks_in_grid, x, y-1, z)):
            if verbose: 
                print("find_teleport_location::", px, py, pz, direction, "with default view is eligible!")
            return px+0.5, py, pz+0.5, pitch, yaw

        # check if a block can feasibly be placed from a location in the above or below planes
        if '_' in direction:
            general_dir = 'bottom' if 'bottom' in direction else 'top'

            # cannot place a block from above if the location is obscured by another block from above
            if general_dir == 'top' and not location_is_empty(blocks_in_grid, x, y+1, z):
                if verbose:
                    print("find_teleport_location::ineligible direction", direction, "-- view is blocked!")
                continue

            # consider ahead, above directions from below; consider only ahead direction from above
            view_keys = ["ahead", "above"] if general_dir == 'bottom' else ["ahead"]

            for key in view_keys:
                dx, dy, dz = coord_deltas[key][direction]
                if verbose:
                    print("find_teleport_location::checking location", x+dx, y+dy, z+dz, "using view", key, "while facing from the", direction)

                # check if block can feasibly be placed from this location (i.e., an adjacent block exists in that direction)
                # if so, return this with appropriate pitch/yaw modifications
                if not location_is_empty(blocks_in_grid, x+dx, y+dy, z+dz):
                    if verbose:
                        print("find_teleport_location::found adjacent block with view", key, "while facing from the", direction)

                    d_pitch, d_yaw = view_deltas[key+'_'+general_dir]
                    return px+0.5, py, pz+0.5, pitch+d_pitch, yaw+d_yaw

        # check if a block can feasibly be placed from any of its six immediate sides
        else:
            for key in ["ahead", "left", "right", "behind"]:
                if coord_deltas[key].get(direction) is None:
                    continue

                dx, dy, dz = coord_deltas[key][direction]
                if verbose:
                    print("find_teleport_location::Checking location", x+dx, y+dy, z+dz, "using view", key, "while facing from the", direction)

                # cannot place a block if the location is obscured by another block from above
                if not location_is_empty(blocks_in_grid, x, y+1, z):
                    if verbose:
                        print("find_teleport_location::ineligible direction", direction, "-- view is blocked!")
                    continue

                # check if block can feasibly be placed from this location (i.e., an adjacent block exists in that direction)
                # if so, return this with appropriate pitch/yaw modifications
                if not location_is_empty(blocks_in_grid, x+dx, y+dy, z+dz):
                    if verbose:
                        print("find_teleport_location::Found adjacent block with view", key, "while facing from the", direction)

                    d_pitch, d_yaw = view_deltas[key] 
                    final_yaw = yaw+d_yaw

                    if direction == "top" or direction == "bottom":
                        d_pitch, _ = view_deltas[direction]
                        final_yaw = yaw_dirs[relative_to_cardinal[key]]

                    final_pitch = pitch+d_pitch
                    return px+0.5, py, pz+0.5, final_pitch, final_yaw

    # we went through all that effort and still found nothing :(
    print("find_teleport_location::Error: no feasible location found!")
    return None, None, None, None, None

def location_is_empty(blocks_in_grid, x, y, z):
    """ Checks whether or not a grid location is empty given the current world state. """
    blocks_list = blocks_in_grid.get(x, {}).get(z, {})
    return y not in blocks_list and y > 0

def execute_action(ah, action, tx, ty, tz, t_pitch, t_yaw, color):
    """ Executes an action using the agent. """
    if verbose:
        print("execute_plan::teleporting to:", tx, ty, tz, t_pitch, t_yaw, "to", action, color)

    # teleport the agent
    teleportMovement(ah, teleport_x=tx, teleport_y=ty, teleport_z=tz)

    # choose block color to be placed (if putdown)
    if action == 'putdown':
        chooseInventorySlot(ah, color_map[color])

    # set agent's pitch and yaw
    setPitchYaw(ah, pitch=t_pitch, yaw=t_yaw)

    # perform the action
    performAction(ah, action)