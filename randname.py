#!/usr/bin/env python2

import argparse
import random

# Parse arguments.  You should not need to modify this.
parser = argparse.ArgumentParser()
parser.add_argument("morphemes", help="path to morphemes file")
parser.add_argument("count", type=int, help="number of names to generate", nargs='?', default=1)
parser.add_argument("--seed", type=int, default=0, help="RNG seed")
args = parser.parse_args()

# Create a random generator.
rng = random.Random(args.seed)

# Here's how to access the args.  (You won't print them in your actual program.)
# print 'path to grammar file:', args.grammar
# print 'count:', args.count
# print 'print tree?', args.tree
# print 'RNG seed:', args.seed

def addRule(line, rules):
	# ignore comments
	tokens = line.split('#')
	if len(tokens) > 0:
		tokens = tokens[0]
	else:
		return
	
	tokens = tokens.split('\t')
	if len(tokens) == 0:
		return
	morpheme = tokens[0]
	if morpheme in rules:
		print "WARNING: double entry for morpheme: %s" % (morpheme,)
	else:
		rules[morpheme] = []

	rhs = tokens[1]
	rhs = rhs.replace('[','').replace(']','')
	rhs = rhs.split(', ')

	next_morphemes_added = set()
	for next_morpheme_prob in rhs:
		(next_morpheme, prob) = next_morpheme_prob.split(": ")
		prob = float(prob)
		rules[morpheme].append((prob, next_morpheme))
		if next_morpheme in next_morphemes_added:
			print "WARNING: double entry for next morpheme %s of %s" % (next_morpheme, morpheme)
		next_morphemes_added.add(next_morpheme)

def selectRandom(choices):
	totalWeight = sum([choice[0] for choice in choices])
	selectedWeight = rng.uniform(0, totalWeight)
	for choice in choices:
		if selectedWeight < choice[0]:
			return choice[1]
		else:
			selectedWeight -= choice[0]

def extendName(name, rules):
	try:
		choices = rules[name[-1]]
		newToken = selectRandom(choices)
		name.extend(newToken)
	except Exception as e:
		raise e

def generateName(rules, start, end):
	name = [start]
	while name[-1] != end:
		extendName(name, rules)
	return ''.join(name[1:-1])


if __name__ == "__main__":
	# parse the morphemes
	rules = {}
	with open(args.morphemes, 'r') as morphemes_file:
		i = 0
		for line in morphemes_file:
			if i == 0:
				start = line.split()[1]
			if i == 1:
				end = line.split()[1]
			elif i>2:
				addRule(line, rules)
			i += 1
	# print start
	# print rules
	# print end

	# generate the names
	for i in range(args.count):
		print generateName(rules, start, end)

