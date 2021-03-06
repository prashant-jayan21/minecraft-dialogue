import os, json, argparse, re
from os.path import join, isdir
from nltk import word_tokenize

def process_missions(logs_root_dir, legacy):
    all_log_dirs = [x for x in os.listdir(logs_root_dir) if isdir(join(logs_root_dir, x))]

    for log_dir in all_log_dirs:
        if legacy:
            process_observations_legacy(join(logs_root_dir, log_dir))
        else:
            process_observations(join(logs_root_dir, log_dir))

def process_observations_legacy(logs_dir): # TODO: Phase this out eventually
    all_sub_dirs = [x for x in os.listdir(logs_dir) if isdir(join(logs_dir, x))]

    for sub_dir in all_sub_dirs:
        all_json_filenames = [x for x in os.listdir(join(logs_dir, sub_dir, "json")) if x.endswith(".json")]
        for json_filename in all_json_filenames:
            metrics_dict = get_all_metrics(join(logs_dir, sub_dir, "json", json_filename))
            with open(join(logs_dir, sub_dir, "json", json_filename[:-5] + "_metrics.json"), "w") as metrics:
                json.dump(metrics_dict, metrics)

def process_observations(logs_dir):
    metrics_dict = get_all_metrics(join(logs_dir, "postprocessed-observations.json"))

    with open(join(logs_dir, "metrics.json"), "w") as metrics:
        json.dump(metrics_dict, metrics)

def get_all_metrics(json_filename):
    with open(json_filename) as observations:
        observations_dict = json.load(observations)

    last_state = observations_dict["WorldStates"][-1]
    chat_history = last_state["ChatHistory"]

    return get_turn_metrics(chat_history)

def get_turn_metrics(chat_history):
    '''
    chat_history : list of all chat messages
    '''
    # pre-process
    chat_history.remove("<Builder> Mission has started.") # remove "mission has started" system message

    # collapse
    chat_history_collapsed = []
    for i in range(len(chat_history)):
        utterance = chat_history[i]
        if i == 0: # always add first utterance to collapsed list
            chat_history_collapsed.append(utterance)
        else: # compare utterance with last element in collapsed list
            last_collapsed_utterance = chat_history_collapsed[-1]
            if last_collapsed_utterance.startswith("<Builder>") and utterance.startswith("<Architect>") or \
            last_collapsed_utterance.startswith("<Architect>") and utterance.startswith("<Builder>"):
                chat_history_collapsed.append(utterance)

    # tokenize utterances
    chat_history_stripped = list([re.sub(r"<Builder> |<Architect> ", "", x) for x in chat_history])
    chat_history_stripped_tokenized = list(map(word_tokenize, chat_history_stripped))
    all_tokens = [item for sublist in chat_history_stripped_tokenized for item in sublist]

    # compute metrics
    num_tokens = len(all_tokens)
    num_utterances = len(chat_history)
    num_turns = len(chat_history_collapsed)
    if num_turns == 0:
        utterances_per_turn = 0.0
    else:
        utterances_per_turn = float(num_utterances) / float(num_turns)

    return {
        "num_utterances": num_utterances,
        "num_turns": num_turns,
        "utterances_per_turn": utterances_per_turn,
        "num_tokens": num_tokens
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process observations to compute various dialog metrics")
    parser.add_argument("logs_root_dir", help="Root directory for all log data")
    parser.add_argument("--legacy", default=False, action="store_true", help="Whether or not this is legacy data")
    args = parser.parse_args()

    process_missions(args.logs_root_dir, args.legacy)
