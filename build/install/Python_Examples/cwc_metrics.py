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
    # my_list = ["<Builder> Mission has started.", "<Architect> Hi! We're going to build a blue structure", "<Architect> Start by putting a row of three blue blocks down on the grid", "<Builder> great ! what do I have to do", "<Builder> okay", "<Architect> A row", "<Architect> Great!", "<Architect> Now, put two more blocks on top of one of the outer blocks of that row", "<Architect> blue blocks, I should've said", "<Architect> great, we're done!"]
    my_list = ["<Architect> alright, same base as last time, exceot with orange blocks", "<Builder> Mission has started.", "<Architect> and make a floor of red blocks as before, on top of the ones you placed", "<Builder> pardon?", "<Builder> I only got the second sentence", "<Architect> alright, same base as last time, except with orange blocks", "<Builder> ok ok", "<Architect> the center block should be removed though", "<Architect> yup", "<Architect> we;re done", "<Builder> that was a waste of time", "<Architect> Go team", "<Architect> haha", "<Builder> just kill me now", "<Architect> i don't have a weapon", "<Builder> God doesn't need a weapon to murder", "<Architect> sadly, nor can we commit suicide"]
    print get_turn_metrics(my_list)
