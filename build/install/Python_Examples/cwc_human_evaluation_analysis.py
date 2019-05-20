import sys, os, csv, json, string, argparse, numpy as np
from nltk.metrics.agreement import AnnotationTask
from collections import defaultdict

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
		orig_examples = dict(json.load(f))

	start_idxs = [4, 9, 14, 19, 24]
	question_types = ["fluency", "dialogue-acts", "appropriateness", "executability", "correctness"]
	answer_ordering = {'fluency': ['Yes', 'Somewhat', 'No'], 'dialogue-acts': ['Instruct B', 'Describe Target', 'Answer question', "Confirm B's actions or plans", "Correct B's actions or plans", "Clarify or correct A's descriptions or instructions", "Other", 'Multiple acts'], 'appropriateness': ['Appropriate', 'Maybe/partially appropriate', 'Inappropriate', 'N/A'], 'executability': ['Perfectly clear', 'Somewhat unclear', 'Completely unclear or impossible', 'N/A'], 'correctness': ['Fully correct', 'Partially correct', 'Incorrect', 'N/A']}
	model_types = ['seq2seq_attn', 'acl-model', 'emnlp-model', 'human']
	identifiers = ['a', 'b', 'c', 'd']

	# reformat evaluation csv
	evaluation_examples = []
	utterance_lengths = defaultdict(list)

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
			utterance_lengths[var_map[identifier]].append(len(utterances[i].split()))

		for i in range(len(start_idxs)):
			start_idx = start_idxs[i]
			question_type = question_types[i]
			formatted_example[question_type] = {}
			
			for j in range(4):
				identifier = identifiers[j]
				formatted_example[question_type][var_map[identifier]] = [x.strip() for x in example[start_idx+j].split(',')] if question_type == 'dialogue-acts' else example[start_idx+j]

		evaluation_examples.append(formatted_example)

	print("Mean utterance lengths:")
	for key in utterance_lengths:
		print((key+":").ljust(15), "{:.2f}".format(np.mean(utterance_lengths[key])))
	print()

	# compute counts of annotations for percentages
	evaluation_counts = {}
	for example in evaluation_examples:
		for question_type in question_types:
			if question_type not in evaluation_counts:
				evaluation_counts[question_type] = {}
			for model in example[question_type]:
				if model not in evaluation_counts[question_type]:
					evaluation_counts[question_type][model] = defaultdict(int)
				if question_type != 'dialogue-acts':
					evaluation_counts[question_type][model][example[question_type][model]] += 1
					evaluation_counts[question_type][model]["total"] += 1
				else:
					for act_type in example[question_type][model]:
						evaluation_counts[question_type][model][act_type] += 1
						evaluation_counts[question_type][model]['total'] += 1
					if len(example[question_type][model]) > 1:
						evaluation_counts[question_type][model]['Multiple acts'] += 1

	# report percentages and averages
	for question_type in question_types:
		print(question_type)
		for model in model_types:
			avg_value = 0
			print_str = ''
			for i in range(len(answer_ordering[question_type])):
				label = answer_ordering[question_type][i]
				print_str += '\t\t'+"{:.2f}".format(100*evaluation_counts[question_type][model][label]/float(evaluation_counts[question_type][model]['total'])).rjust(5)+" % "+label+'\n'
				avg_value += evaluation_counts[question_type][model][label]*(len(answer_ordering[question_type])-i-1)
			print('\t', model.ljust(15), '' if question_type == 'dialogue-acts' else '(average: '+"{:.2f}".format(avg_value/float(evaluation_counts[question_type][model]['total']))+')')
			print(print_str)
		print()

	# collate data per example for computing inter-annotator agreement
	by_example_id = defaultdict(list)
	for example in evaluation_examples:
		by_example_id[example['example_id']].append(example)

	by_annotator = {}
	for example_id in by_example_id:
		for question_type in question_types:
			if question_type not in by_annotator:
				by_annotator[question_type] = defaultdict(dict)
			for example in by_example_id[example_id]:
				for model in model_types:
					by_annotator[question_type][example_id+'_'+model]['utterance'] = example['utterances'][model]
					by_annotator[question_type][example_id+'_'+model][example['evaluator_id']] = example[question_type][model] if question_type == 'dialogue-acts' else len(answer_ordering[question_type])-1-answer_ordering[question_type].index(example[question_type][model])

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
				f.write(str(example['total'])+'\t'+str(example['1'])+'\t'+str(example['2'])+'\t'+str(example['39'])+'\t'+example_id.ljust(15)+example['utterance']+'\n')

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

	# write files to compute Krippendorf's alpha
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

if __name__ == "__main__":
	# Parse CLAs
	parser = argparse.ArgumentParser(description='Runs analysis of human evaluation.')
	parser.add_argument("--results_csv", default='human_evaluation/eval_5-18.csv', help='File path of human evaluation results csv')
	parser.add_argument("--sampled_sentences_dir", default="sampled_sentences", help='Directory path of variable maps for annotators')
	args = parser.parse_args()

	main(args)