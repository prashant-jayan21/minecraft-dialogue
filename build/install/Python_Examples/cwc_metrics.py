def get_turn_metrics(chat_history):
    '''
    chat_history : list of all chat messages
    '''
    # pre-process
    chat_history = chat_history[1:] # remove "mission has started" system message

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

    # compute metrics
    num_utterances = len(chat_history)
    num_turns = len(chat_history_collapsed)
    utterances_per_turn = float(num_utterances) / float(num_turns)

    return {
        "num_utterances": num_utterances,
        "num_turns": num_turns,
        "utterances_per_turn": utterances_per_turn
    }


if __name__ == "__main__":
    my_list = ["<Builder> Mission has started.", "<Architect> Hi! We're going to build a blue structure", "<Architect> Start by putting a row of three blue blocks down on the grid", "<Builder> great ! what do I have to do", "<Builder> okay", "<Architect> A row", "<Architect> Great!", "<Architect> Now, put two more blocks on top of one of the outer blocks of that row", "<Architect> blue blocks, I should've said", "<Architect> great, we're done!"]
    print get_turn_metrics(my_list)
