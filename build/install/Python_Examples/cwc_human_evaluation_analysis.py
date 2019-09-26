import sys, os, re, csv, json, copy, nltk, string, argparse, operator, numpy as np, matplotlib.pyplot as plt
from nltk.metrics.agreement import AnnotationTask
from collections import defaultdict

def get_terms(file):
	with open(file, 'r') as f:
		return [x.split()[0] for x in f.readlines()]

simple_terms_file = "/Users/Anjali/Documents/UIUC/research/CwC/BlocksWorld/Minecraft/cwc-minecraft-models/data/lexicons/simple-terms-redux.txt"
colors_file = "/Users/Anjali/Documents/UIUC/research/CwC/BlocksWorld/Minecraft/cwc-minecraft-models/data/lexicons/colors.txt"
spatial_relations_file = "/Users/Anjali/Documents/UIUC/research/CwC/BlocksWorld/Minecraft/cwc-minecraft-models/data/lexicons/spatial-relations.txt"
dialogue_file = "/Users/Anjali/Documents/UIUC/research/CwC/BlocksWorld/Minecraft/cwc-minecraft-models/data/lexicons/dialogue.txt"

question_types = ["fluency", "dialogue-acts", "appropriateness", "executability", "correctness"]
answer_ordering = {'fluency': ['Yes', 'Somewhat', 'No'], 
				   'dialogue-acts': ['Instruct B', 'Describe Target', 'Answer question', "Confirm B's actions or plans", "Correct B's actions or plans", "Clarify or correct A's descriptions or instructions", "Other", 'Multiple acts'],
				   'dialogue-acts_merged': ['Instruct B', 'Describe Target', 'Answer question', "Confirm B's actions or plans", "Correct or clarify A or B", "Other", 'Multiple acts'], 
				   'appropriateness': ['Appropriate', 'Maybe/partially appropriate', 'Inappropriate', 'N/A'], 
				   'executability': ['Perfectly clear', 'Somewhat unclear', 'Completely unclear or impossible', 'N/A'], 
				   'correctness': ['Fully correct', 'Partially correct', 'Incorrect', 'N/A']}
default_answers = {'fluency': 'Somewhat', 'appropriateness': 'Maybe/partially appropriate', 'executability': 'Somewhat unclear', 'correctness': 'Partially correct'}
terms = [('simple_terms', get_terms(simple_terms_file)), ('colors', get_terms(colors_file)), ('spatial_relations', get_terms(spatial_relations_file)), ('dialogue', get_terms(dialogue_file))] 

def reformat_examples(csv_data, orig_examples, var_maps, merge_corrections, identifiers=['a', 'b', 'c', 'd']):
	# reformat evaluation csv
	evaluation_examples = []
	processed_examples = set()
	utterance_lengths = defaultdict(list)
	utterances_by_length = {}

	for example in csv_data:
		evaluator_id, example_id = example[1], example[2]
		orig_example = orig_examples[int(example_id)]
		formatted_example = {"evaluator_id": evaluator_id, "example_id": example_id, "utterances": {}}
		var_map = var_maps[evaluator_id][example_id]

		utterances = [x[4:] for x in example[3].splitlines() if len(x) > 0]
		for i in range(4):
			identifier = identifiers[i]
			orig_utterance = squash_punctuation(dict(orig_example['generated_sentences'])[var_map[identifier]]) if var_map[identifier] != 'human' else orig_example['ground_truth_utterance']
			if utterances[i] != orig_utterance and utterances[i].replace("<unk>", " <unk>") != orig_utterance:
				print("ERROR: var_map mismatch for evaluator", evaluator_id, "example", example_id)
				print(utterances[i])
				print(orig_utterance)

			formatted_example["utterances"][var_map[identifier]] = utterances[i]
			if example_id not in processed_examples:
				utterance_length = len(squash_punctuation(utterances[i]).split())
				utterance_lengths[var_map[identifier]].append(utterance_length)

				if var_map[identifier] not in utterances_by_length:
					utterances_by_length[var_map[identifier]] = defaultdict(list)
				utterances_by_length[var_map[identifier]][utterance_length].append(squash_punctuation(utterances[i]))

		for term_type, term_list in terms:
			formatted_example['utterances-'+term_type] = {}
			for source in formatted_example['utterances']:
				utterance = formatted_example['utterances'][source]
				utterance = tokenize(utterance)
				formatted_example['utterances-'+term_type][source] = get_simplified(utterance, term_list)

		start_idxs = [4, 9, 14, 19, 24]
		for i in range(len(start_idxs)):
			start_idx = start_idxs[i]
			question_type = question_types[i]
			formatted_example[question_type] = {}
			
			for j in range(4):
				identifier = identifiers[j]
				formatted_example[question_type][var_map[identifier]] = [x.strip() for x in example[start_idx+j].split(',')] if question_type == 'dialogue-acts' else example[start_idx+j]
				
				if question_type == 'dialogue-acts' and merge_corrections:
					orig_annotation = copy.deepcopy(formatted_example[question_type][var_map[identifier]])
					merged = False
					for to_merge in ["Correct B's actions or plans", "Clarify or correct A's descriptions or instructions"]:
						if to_merge in orig_annotation:
							orig_annotation.remove(to_merge)
							merged = True

					if merged:
						orig_annotation.append("Correct or clarify A or B")
						formatted_example[question_type][var_map[identifier]] = orig_annotation

		evaluation_examples.append(formatted_example)
		processed_examples.add(example_id)

	print("Mean utterance lengths:")
	for key in utterance_lengths:
		print((key+":").ljust(15), "{:.2f}".format(np.mean(utterance_lengths[key])))
	print()

	for model in utterances_by_length:
		with open('human_evaluation/utterances_by_length-'+model+'.txt', 'w') as f:
			for length in sorted(utterances_by_length[model]):
				for utterance in utterances_by_length[model][length]:
					f.write(str(length)+'\t'+utterance+'\n')

	return evaluation_examples, utterance_lengths

def organize_by_example_id(evaluation_examples):
	by_example_id = defaultdict(list)
	for example in evaluation_examples:
		by_example_id[example['example_id']].append(example)
	return by_example_id

def organize_by_annotator(by_example_id, model_types):
	by_annotator = {}
	for example_id in by_example_id:
		for question_type in question_types:
			if question_type not in by_annotator:
				by_annotator[question_type] = defaultdict(dict)
			for example in by_example_id[example_id]:
				for model in model_types:
					by_annotator[question_type][example_id+'_'+model]['utterance'] = example['utterances'][model]
					by_annotator[question_type][example_id+'_'+model][example['evaluator_id']] = example[question_type][model] if question_type == 'dialogue-acts' else len(answer_ordering[question_type])-1-answer_ordering[question_type].index(example[question_type][model])

	return by_annotator

def compute_counts(evaluation_examples):
	# compute counts of annotations for percentages
	evaluation_counts = {}
	evaluation_counts_by_dialogue_act = {}
	for dialogue_act in answer_ordering['dialogue-acts']:
		evaluation_counts_by_dialogue_act[dialogue_act] = {}

	for example in evaluation_examples:
		for question_type in question_types:
			if question_type not in evaluation_counts:
				evaluation_counts[question_type] = {}

				if question_type != 'dialogue-acts':
					for dialogue_act in answer_ordering['dialogue-acts']:
						evaluation_counts_by_dialogue_act[dialogue_act][question_type] = {}

			for model in example[question_type]:
				if model not in evaluation_counts[question_type]:
					evaluation_counts[question_type][model] = defaultdict(int)

					if question_type != 'dialogue-acts':
						for dialogue_act in answer_ordering['dialogue-acts']:
							evaluation_counts_by_dialogue_act[dialogue_act][question_type][model] = defaultdict(int)

				if question_type != 'dialogue-acts':
					evaluation_counts[question_type][model][example[question_type][model]] += 1
					evaluation_counts[question_type][model]["total"] += 1

					for dialogue_act in example['dialogue-acts'][model]:
						evaluation_counts_by_dialogue_act[dialogue_act][question_type][model][example[question_type][model]] += 1
						evaluation_counts_by_dialogue_act[dialogue_act][question_type][model]["total"] += 1
				else:
					for act_type in example[question_type][model]:
						evaluation_counts[question_type][model][act_type] += 1
					evaluation_counts[question_type][model]['total'] += 1
					if len(example[question_type][model]) > 1:
						evaluation_counts[question_type][model]['Multiple acts'] += 1

	return evaluation_counts, evaluation_counts_by_dialogue_act

def get_majority_labels(by_example_id, model_types, debug):
	majority_labels_per_example = {}
	tie_examples, avgd_examples = [], []
	
	for example_id in by_example_id:
		example = by_example_id[example_id]
		majority_labels_per_example[example_id] = {}
		found_tie, avg_taken = False, False

		for question_type in question_types:
			majority_labels_per_example[example_id][question_type] = defaultdict(str) if question_type != 'dialogue-acts' else defaultdict(list)
			
			for model in model_types:
				counts = defaultdict(int)

				if question_type != 'dialogue-acts':
					for annotation in example:
						counts[annotation[question_type][model]] += 1
					sorted_counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)

					majority_label = sorted_counts[0][0]
					if sorted_counts[0][1] < 2:
						if "N/A" in dict(sorted_counts):
							majority_label = "Tie"
							found_tie = True
						else:
							majority_label = default_answers[question_type]
							avg_taken = True

					majority_labels_per_example[example_id][question_type][model] = majority_label

				else:
					for annotation in example:
						for dialogue_act in annotation[question_type][model]:
							counts[dialogue_act] += 1

					for dialogue_act in counts:
						if counts[dialogue_act] >= 2:
							majority_labels_per_example[example_id][question_type][model].append(dialogue_act)

					if len(majority_labels_per_example[example_id][question_type][model]) < 1:
						majority_labels_per_example[example_id][question_type][model].append("Other")
		
		if found_tie and debug:
			print()
			print(json.dumps(example))
			print(json.dumps(majority_labels_per_example[example_id], indent=4))
			tie_examples.append((example, majority_labels_per_example[example_id]))

		if avg_taken:
			avgd_examples.append((example, majority_labels_per_example[example_id]))

	print("\nFound", len(tie_examples), "examples with voting ties.")
	print("Found", len(avgd_examples), "examples with no majority vote and no N/A annotations.\n")
	return majority_labels_per_example

def compute_majority_counts(majority_labels_per_example):
	evaluation_counts_majority = {}
	for example_id in majority_labels_per_example:
		example = majority_labels_per_example[example_id]
		for question_type in question_types:
			if question_type not in evaluation_counts_majority:
				evaluation_counts_majority[question_type] = {}

			for model in example[question_type]:
				if model not in evaluation_counts_majority[question_type]:
					evaluation_counts_majority[question_type][model] = defaultdict(int)

				if question_type != 'dialogue-acts':
					evaluation_counts_majority[question_type][model][example[question_type][model]] += 1
					evaluation_counts_majority[question_type][model]["total"] += 1
				else:
					for act_type in example[question_type][model]:
						evaluation_counts_majority[question_type][model][act_type] += 1
					evaluation_counts_majority[question_type][model]['total'] += 1
					if len(example[question_type][model]) > 1:
						evaluation_counts_majority[question_type][model]['Multiple acts'] += 1

	return evaluation_counts_majority

def write_per_utterance_scores(by_annotator):
	for question_type in by_annotator:
		if question_type == 'dialogue-acts':
			continue
		for example_id in by_annotator[question_type]:
			example = by_annotator[question_type][example_id]
			example['total'] = sum(example[x] for x in ['1', '2', '39'])
			example['average'] = example['total']/3.0

	for question_type in by_annotator:
		if question_type == 'dialogue-acts':
			continue
		with open('human_evaluation/by_utterance-'+question_type+'.txt', 'w') as f:
			for example_id in by_annotator[question_type]:
				example = by_annotator[question_type][example_id]
				f.write(str(example['total'])+'\t'+str(example['1'])+'\t'+str(example['2'])+'\t'+str(example['39'])+'\t'+example_id.split('_')[1].ljust(15)+example['utterance']+'\n')

	with open('human_evaluation/by_utterance.tsv', 'w') as f:
		header_str = 'example id\tutterance\tsource\tfluency (total)\tfluency (1)\tfluency (2)\tfluency (39)'
		for dialogue_act in answer_ordering['dialogue-acts']:
			header_str += '\t'+dialogue_act+' (total)'
			for i in ['1', '2', '39']:
				header_str += '\t'+dialogue_act+' ('+i+')'
		for question_type in question_types[2:]:
			header_str += '\t'+question_type+' (total)'
			for i in ['1', '2', '39']:
				header_str += '\t'+question_type+' ('+i+')'
		f.write(header_str+'\n')

		for example_id in by_annotator['fluency']:
			to_write = str(example_id.split('_')[0])+'\t'+by_annotator['fluency'][example_id]['utterance']+'\t'+example_id.split('_')[1]+'\t'
			for question_type in answer_ordering:
				example = by_annotator[question_type][example_id]
				if question_type != 'dialogue-acts':
					total = sum(example[x] for x in ['1', '2', '39'])
					to_write += str(total)+'\t'
					for evaluator_id in ['1', '2', '39']:
						to_write += str(example[evaluator_id])+'\t'
				else:
					for dialogue_act in answer_ordering[question_type]:
						if dialogue_act == 'Multiple acts':
							total = sum([1 for x in ['1', '2', '39'] if len(example[x]) > 1])
							to_write += str(total)+'\t'
							for evaluator_id in ['1', '2', '39']:
								to_write += ('1' if len(example[evaluator_id]) > 1 else '0')+'\t'
						else:
							total = sum([1 for x in ['1', '2', '39'] if dialogue_act in example[x]])
							to_write += str(total)+'\t'
							for evaluator_id in ['1', '2', '39']:
								to_write += ('1' if dialogue_act in example[evaluator_id] else '0')+'\t'

			f.write(to_write[:-1]+'\n')

def compute_nltk_agreement(by_annotator):
	print("Using NLTK agreement metrics\n")
	for question_type in question_types:
		if question_type == 'dialogue-acts':
			for dialogue_act in answer_ordering[question_type]:
				tuples_lst = []
				for example_id in by_annotator[question_type]:
					example = by_annotator[question_type][example_id]
					for evaluator_id in ['1', '2', '39']:
						label = '1' if dialogue_act in example[evaluator_id] else '0'
						if dialogue_act == 'Multiple acts':
							label = '1' if len(example[evaluator_id]) > 1 else '0'
						tuples_lst.append(('c'+evaluator_id, example_id, label))

				t = AnnotationTask(data=tuples_lst)
				print(question_type+", "+dialogue_act+" fleiss:", "{:.2f}".format(t.multi_kappa()))
				print(question_type+", "+dialogue_act+" alpha: ", "{:.2f}".format(t.alpha()))
				print()
		else:
			tuples_lst = []
			for example_id in by_annotator[question_type]:
				example = by_annotator[question_type][example_id]
				for evaluator_id in ['1', '2', '39']:
					tuples_lst.append(('c'+evaluator_id, example_id, example[evaluator_id]))

			t = AnnotationTask(data=tuples_lst)
			print(question_type+" fleiss:", "{:.2f}".format(t.multi_kappa()))
			print(question_type+" alpha: ", "{:.2f}".format(t.alpha()))
			print()

def write_krippendorff_files(by_annotator):
	for question_type in question_types:
		if question_type == 'dialogue-acts':
			for dialogue_act in answer_ordering[question_type]:
				with open('human_evaluation/'+question_type+'_'+dialogue_act+'.txt', 'w') as f:
					f.write('1\t2\t39\n')
					for example_id in by_annotator[question_type]:
						example = by_annotator[question_type][example_id]
						if any(x not in example for x in ['1', '2', '39']):
							print("WARNING: missing data for example:", example)
							continue
						for evaluator_id in ['1', '2', '39']:
							label = '1' if dialogue_act in example[evaluator_id] else '0'
							if dialogue_act == 'Multiple acts':
								label = '1' if len(example[evaluator_id]) > 1 else '0'
							f.write(label+'\t')
						f.write('\n')
		else:
			with open('human_evaluation/'+question_type+'.txt', 'w') as f:
				f.write('1\t2\t39\n')
				for example_id in by_annotator[question_type]:
					example = by_annotator[question_type][example_id]
					if any(x not in example for x in ['1', '2', '39']):
						print("WARNING: missing data for example:", example)
						continue
					for evaluator_id in ['1', '2', '39']:
						f.write(str(example[evaluator_id])+'\t')
					f.write('\n')

def tokenize(utterance):
	tokens = utterance.split()
	fixed = ""

	modified_tokens = set()
	for token in tokens:
		original = token

		# fix *word
		if len(token) > 1 and token[0] == '*':
			token = '* '+token[1:]

		# fix word*
		elif len(token) > 1 and token[-1] == '*' and token[-2] != '*':
			token = token[:-1]+' *'

		# fix word..
		if len(token) > 2 and token[-3] is not '.' and ''.join(token[-2:]) == '..':
			token = token[:-2]+' ..'

		# split axb(xc) to a x b (x c)
		if len(token) > 2:
			m = re.match("([\s\S]*\d+)x(\d+[\s\S]*)", token)
			while m:
				token = m.groups()[0]+' x '+m.groups()[1]
				m = re.match("([\s\S]*\d+)x(\d+[\s\S]*)", token)

		if original != token:
			modified_tokens.add(original+' -> '+token)

		fixed += token+' '

	return ' '.join(nltk.tokenize.word_tokenize(fixed.strip()))

def squash_punctuation(sentence):
	formatted_sentence = ""
	tokens = sentence.split()
	for i in range(len(tokens)):
		to_add = " "
		if (tokens[i] in string.punctuation or tokens[i][0] in string.punctuation) and tokens[i] != '"' and tokens[i][0] != '<':
			if tokens[i].startswith("'") \
			or (tokens[i-1] not in string.punctuation and (i+1 == len(tokens) or not((tokens[i] == ':' or tokens[i] == ';') and tokens[i+1] == ')'))) \
			or (tokens[i-1] == '?' and tokens[i] == '!') or (tokens[i-1] == '!' and tokens[i] == '?') \
			or ((tokens[i-1] == ':' or tokens[i-1] == ';') and tokens[i] == ')') \
			or (tokens[i-1] == tokens[i] and (tokens[i] == '.' or tokens[i] == '!' or tokens[i] == '?')):
				to_add = ""

		formatted_sentence += to_add+tokens[i]
	return formatted_sentence.strip()

def compute_syn_recall(reference_sentence, translated_sentence, substitutions_lexicon):
	# get the synsets
	synsets = [set(substitutions_lexicon.get(token, [])) for token in translated_sentence]
	matched_reference = [0]*len(reference_sentence)
	matched_translated = [0]*len(translated_sentence)

	# add the original tokens to the synsets
	for i, t_token in enumerate(translated_sentence):
		synsets[i].add(t_token)

	if len(reference_sentence) == 0:
		return matched_reference, "FAIL"

	if len(translated_sentence) == 0:
		return matched_reference, 0.0

	for i, r_token in enumerate(reference_sentence):
		for j, t_synset in enumerate(synsets):
			if matched_translated[j] != 1 and r_token in t_synset:
				matched_reference[i] = 1
				matched_translated[j] = 1
				break

	return matched_reference, sum(matched_reference)/float(len(reference_sentence))

def print_micro_statistics(metric_by_source, metric, terms):
	print("Per-token micro", metric, "statistics (overall):")
	for source in ['seq2seq_attn', 'acl-model', 'emnlp-model']:
		values_arr = metric_by_source[metric][source]['orig']
		percent_failed = sum(1 for x in values_arr if x == 'FAIL')/len(values_arr)
		ignore_fail = np.mean([x for x in values_arr if x != 'FAIL'])
		fail_0 = np.mean([x if x != 'FAIL' else 0.0 for x in values_arr])
		fail_1 = np.mean([x if x != 'FAIL' else 1.0 for x in values_arr])
		print(source+", ignoring FAIL: ").ljust(30), "{:.2f}".format(ignore_fail) # should this be normalized by utterance length?
		print(source+", FAIL=0.0: ").ljust(30), "{:.2f}".format(fail_0)
		print(source+", FAIL=1.0: ").ljust(30), "{:.2f}".format(fail_1)
		print(source+"  FAIL %:").ljust(30), "{:.2f}".format(percent_failed)
		print()

	print('\nPer-token micro', metric, 'statistics (modified):')
	for term_type, _ in terms:
		print(term_type)
		for source in ['seq2seq_attn', 'acl-model', 'emnlp-model']:
			values_arr = metric_by_source[metric][source][term_type]
			percent_failed = sum(1 for x in values_arr if x == 'FAIL')/len(values_arr)
			ignore_fail = np.mean([x for x in values_arr if x != 'FAIL'])
			fail_0 = np.mean([x if x != 'FAIL' else 0.0 for x in values_arr])
			fail_1 = np.mean([x if x != 'FAIL' else 1.0 for x in values_arr])
			print('\t', (source+", ignoring FAIL: ").ljust(30), "{:.2f}".format(ignore_fail)) # should this be normalized by utterance length?
			print('\t', (source+", FAIL=0.0: ").ljust(30), "{:.2f}".format(fail_0))
			print('\t', (source+", FAIL=1.0: ").ljust(30), "{:.2f}".format(fail_1))
			print('\t', (source+"  FAIL %:").ljust(30), "{:.2f}".format(percent_failed))
			print()

def print_macro_statistics(macro_metrics, metric, terms):
	print("Per-token macro", metric, "statistics (overall):")
	for source in ['seq2seq_attn', 'acl-model', 'emnlp-model']:
		match_ratio = macro_metrics[metric][source]['orig']
		print(source.ljust(30), "{:.2f}".format(match_ratio['matched']/float(match_ratio['total'])))

	print('\nPer-token macro', metric, 'statistics (modified):')
	for term_type, _ in terms:
		print(term_type)
		for source in ['seq2seq_attn', 'acl-model', 'emnlp-model']:
			match_ratio = macro_metrics[metric][source][term_type]
			print('\t', source.ljust(30), "{:.2f}".format(match_ratio['matched']/float(match_ratio['total'])))
		print()

def read_var_maps(sampled_sentences_dir):
	""" Reads the variable map files for all annotators. """
	var_maps = {}
	d = os.path.join('.', sampled_sentences_dir)
	dirs = [os.path.join(d, o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]
	for d in dirs:
		if os.path.isfile(os.path.join(d, 'vars-map.json')):
			with open(os.path.join(d, 'vars-map.json'), 'r') as f:
				m = json.load(f)
				var_maps[d.split('/')[-1]] = m

	return var_maps

def color_stem(token):
	if token in ['reds', 'yellows', 'blues', 'oranges', 'greens', 'purples']:
		return token[:-1]
	return token

def get_simplified(utterance, simple_terms):
	return [color_stem(x) for x in utterance.split() if x in simple_terms]

def main(args):
	csv_data = None
	with open(args.results_csv) as csvfile:
		csv_data = csv.reader(csvfile)
		csv_data = list(csv_data)[1:]

	if csv_data is None:
		print("Error reading csvfile:", args.results_csv)
		sys.exit(0)

	var_maps = read_var_maps(args.sampled_sentences_dir)
	with open(os.path.join(args.sampled_sentences_dir, 'sampled_generated_sentences-test.json'), 'r') as f:
		original_examples = dict(json.load(f))
	with open(args.synonyms_file, 'r') as f:
		substitutions_lexicon = json.loads(f.read())

	model_types = args.model_types
	evaluation_examples, utterance_lengths = reformat_examples(csv_data, original_examples, var_maps, args.merge_corrections)

	if args.merge_corrections:
		answer_ordering["dialogue-acts"] = answer_ordering["dialogue-acts_merged"]
	answer_ordering.pop("dialogue-acts_merged")

	# collate data per example for computing inter-annotator agreement
	by_example_id = organize_by_example_id(evaluation_examples)

	# report percentages and averages
	def print_percentages(counts_map, with_ties=False, ignore_na=False):
		for question_type in question_types:
			print(question_type)
			for model in model_types:
				avg_value = 0
				print_str = ''
				
				for i in range(len(answer_ordering[question_type])):
					label = answer_ordering[question_type][i]
					print_str += '\t\t'+"{:.2f}".format(100*counts_map[question_type][model][label]/float(counts_map[question_type][model]['total'])).rjust(5)+(" % ("+str(counts_map[question_type][model][label])+"/"+str(counts_map[question_type][model]['total'])+") ").ljust(12)+label+'\n'
					avg_value += counts_map[question_type][model][label]*(len(answer_ordering[question_type])-i-1)
				
				if question_type != 'dialogue-acts' and with_ties:
					label = "Tie"
					print_str += '\t\t'+"{:.2f}".format(100*counts_map[question_type][model][label]/float(counts_map[question_type][model]['total'])).rjust(5)+(" % ("+str(counts_map[question_type][model][label])+"/"+str(counts_map[question_type][model]['total'])+") ").ljust(12)+label+'\n'
					avg_value += counts_map[question_type][model][label]*(len(answer_ordering[question_type])-i-1)
				
				print('\t', model.ljust(15), '' if question_type == 'dialogue-acts' else '(average: '+"{:.2f}".format(avg_value/float(counts_map[question_type][model]['total']))+')')
				print(print_str)
			print()

	if not args.use_majority:
		evaluation_counts, evaluation_counts_by_dialogue_act = compute_counts(evaluation_examples)
		print_percentages(evaluation_counts)

		if args.print_counts_by_dialogue_act:
			for dialogue_act in answer_ordering['dialogue-acts'][:-1]:
				print(dialogue_act)
				for question_type in question_types:
					if question_type == 'dialogue-acts':
						continue
					print('\t', question_type)
					for model in model_types:
						avg_value = 0
						print_str = ''
						if evaluation_counts_by_dialogue_act[dialogue_act][question_type][model]['total'] < 1:
							continue
						for i in range(len(answer_ordering[question_type])):
							label = answer_ordering[question_type][i]
							print_str += '\t\t\t'+"{:.2f}".format(100*evaluation_counts_by_dialogue_act[dialogue_act][question_type][model][label]/float(evaluation_counts_by_dialogue_act[dialogue_act][question_type][model]['total'])).rjust(5)+(" % ("+str(evaluation_counts_by_dialogue_act[dialogue_act][question_type][model][label])+"/"+str(evaluation_counts_by_dialogue_act[dialogue_act][question_type][model]['total'])+") ").ljust(12)+label+'\n'
							avg_value += evaluation_counts_by_dialogue_act[dialogue_act][question_type][model][label]*(len(answer_ordering[question_type])-i-1)
						print('\t\t', model.ljust(15), '(average: '+"{:.2f}".format(avg_value/float(evaluation_counts_by_dialogue_act[dialogue_act][question_type][model]['total']))+')')
						print(print_str)
					print()

	else:
		majority_labels_per_example = get_majority_labels(by_example_id, model_types, args.debug)
		evaluation_counts_majority = compute_majority_counts(majority_labels_per_example)
		print_percentages(evaluation_counts_majority, with_ties=True)

	by_annotator = organize_by_annotator(by_example_id, model_types)

	write_per_utterance_scores(by_annotator)

	# compute agreemeent using nltk metrics
	if args.use_nltk:
		compute_nltk_agreement(by_annotator)

	# write files to compute Krippendorff's alpha
	write_krippendorff_files(by_annotator)

	metric_by_source = {'precision': {}, 'recall': {}}
	macro_metrics = {'precision': {}, 'recall': {}}
	for example in evaluation_examples:
		for source in example['utterances']:
			if source == 'human':
				continue

			if source not in metric_by_source['precision']:
				for metric in ['precision', 'recall']:
					metric_by_source[metric][source] = defaultdict(list)
					macro_metrics[metric][source] = {'orig': defaultdict(int)}
					for term_type, _ in terms:
						macro_metrics[metric][source][term_type] = defaultdict(int)

			tokenized_gold = tokenize(example['utterances']['human'])
			tokenized_generated = tokenize(example['utterances'][source])

			matched_tokens_p, precision = compute_syn_recall(tokenized_generated.split(), tokenized_gold.split(), substitutions_lexicon)
			metric_by_source['precision'][source]['orig'].append(precision)
			macro_metrics['precision'][source]['orig']['matched'] += sum(matched_tokens_p)
			macro_metrics['precision'][source]['orig']['total'] += len(matched_tokens_p)

			matched_tokens_r, recall = compute_syn_recall(tokenized_gold.split(), tokenized_generated.split(), substitutions_lexicon)
			metric_by_source['recall'][source]['orig'].append(recall)
			macro_metrics['recall'][source]['orig']['matched'] += sum(matched_tokens_r)
			macro_metrics['recall'][source]['orig']['total'] += len(matched_tokens_r)

			for term_type, _ in terms:
				simplified_gold = example['utterances-'+term_type]['human']
				simplified_generated = example['utterances-'+term_type][source]

				matched_tokens_mp, modified_precision = compute_syn_recall(simplified_generated, simplified_gold, substitutions_lexicon)
				metric_by_source['precision'][source][term_type].append(modified_precision)
				macro_metrics['precision'][source][term_type]['matched'] += sum(matched_tokens_mp)
				macro_metrics['precision'][source][term_type]['total'] += len(matched_tokens_mp)

				matched_tokens_mr, modified_recall = compute_syn_recall(simplified_gold, simplified_generated, substitutions_lexicon)
				metric_by_source['recall'][source][term_type].append(modified_recall)
				macro_metrics['recall'][source][term_type]['matched'] += sum(matched_tokens_mr)
				macro_metrics['recall'][source][term_type]['total'] += len(matched_tokens_mr)

	if args.micro_pr:
		print_micro_statistics(metric_by_source, 'precision', terms)
		print_micro_statistics(metric_by_source, 'recall', terms)
		print()

	if args.macro_pr:
		print_macro_statistics(macro_metrics, 'precision', terms)
		print_macro_statistics(macro_metrics, 'recall', terms)
		print()

	# print(json.dumps(metric_by_source, indent=4))

	figures = [221, 222, 223, 224]
	fig = plt.figure()
	for i, model in enumerate(['seq2seq_attn', 'acl-model', 'emnlp-model', 'human']):
		a = fig.add_subplot(figures[i])
		plt.hist(utterance_lengths[model], bins=np.arange(1,max(utterance_lengths[model])+1))
		plt.title(model)
		plt.xticks(np.arange(0, max(utterance_lengths[model])+1, 1.0))
		plt.ylim(top=50)
		plt.xlim(right=25)

	if args.show_plots:
		plt.show()

if __name__ == "__main__":
	# Parse CLAs
	parser = argparse.ArgumentParser(description='Runs analysis of human evaluation.')
	parser.add_argument("--results_csv", default='human_evaluation/eval_5-18.csv', help='File path of human evaluation results csv')
	parser.add_argument("--sampled_sentences_dir", default="sampled_sentences", help='Directory path of variable maps for annotators')
	parser.add_argument('--synonyms_file', default='/Users/Anjali/Documents/UIUC/research/CwC/BlocksWorld/Minecraft/cwc-minecraft-models/data/lexicons/synonym_substitutions.json')
	parser.add_argument('--merge_corrections', default=False, action='store_true')
	parser.add_argument('--print_counts_by_dialogue_act', default=False, action='store_true')
	parser.add_argument('--percentages', default=False, action='store_true')
	parser.add_argument('--micro_pr', default=False, action='store_true')
	parser.add_argument('--macro_pr', default=False, action='store_true')
	parser.add_argument('--show_plots', default=False, action='store_true')
	parser.add_argument('--use_nltk', default=False, action='store_true')
	parser.add_argument('--debug', default=False, action='store_true')
	parser.add_argument('--use_majority', default=False, action='store_true')
	parser.add_argument('--model_types', default=['seq2seq_attn', 'acl-model', 'human'], nargs='+')
	args = parser.parse_args()

	main(args)