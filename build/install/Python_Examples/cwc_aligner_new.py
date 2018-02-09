import re

def align(architect_filenames, builder_filenames):
    aligned_pairs = []

    for architect_filename in architect_filenames:
        architect_timestamp, architect_action = get_key(architect_filename)
        # select all builder screenshots with same action
        builder_filenames_same_action = [f for f in builder_filenames if architect_action in f]
        if not builder_filenames_same_action:
            continue
        # select closest builder screenshot in time
        def f(builder_filename):
            builder_timestamp, builder_action = get_key(builder_filename)
            return abs(float(builder_timestamp) - float(architect_timestamp))
        builder_filename = min(builder_filenames_same_action, key = f)
        # update data structures
        builder_filenames.remove(builder_filename)
        aligned_pairs.append((architect_filename, builder_filename))

    return aligned_pairs

def get_key(filename):
    return (re.split(r"[-.]",filename)[0], re.split(r"[-.]",filename)[2])

import os
import pprint

architect_dir = "/Users/prashant/Desktop/B1-A2-blue-original-L-1517603132657_a"
builder_dir = "/Users/prashant/Desktop/B1-A2-blue-original-L-1517603132657_b"

architect_filenames = os.listdir(architect_dir)
builder_filenames = os.listdir(builder_dir)

results = align(architect_filenames, builder_filenames)

pp = pprint.PrettyPrinter()
pp.pprint(results)
print(len(results))
