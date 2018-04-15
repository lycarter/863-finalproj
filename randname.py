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
		rules[morpheme] = {}

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

def expandToken(token, rules):
	if token in rules:
		choices = rules[token]
		return selectRandom(choices)
	else:
		return [token]

def expandSentence(sentence, rules):
	newSentence = []
	for token in sentence:
		newSentence.extend(expandToken(token, rules))
	return newSentence

def generateSentence(rules):
	oldSentence = ['START']
	newSentence = expandSentence(oldSentence, rules)
	while oldSentence != newSentence:
		# print(oldSentence)
		oldSentence = newSentence
		newSentence = expandSentence(newSentence, rules)
	# print newSentence
	return ' '.join(newSentence)



def expandTreeToken(token, rules):
	toReturn = [token]
	if token in rules:
		choices = rules[token]
	else:
		return token
	choice = selectRandom(choices)
	for newToken in choice:
		toReturn.append(expandTreeToken(newToken, rules))
	return toReturn

def treeToStr(tree):
	if isinstance(tree, basestring):
		return tree
	return '(' + ' '.join([treeToStr(token) for token in tree]) + ')'

def generateTree(rules):
	tree = expandTreeToken('START', rules)
	# print(tree)
	return treeToStr(tree)


if __name__ == "__main__":
	# parse the morphemes
	rules = {}
	with open(args.morphemes, 'r') as morphemes_file:
		for line in morphemes_file:
			addRule(line, rules)
	print rules


	# # generate the sentences
	# for i in range(args.count):
	# 	if args.tree:
	# 		print generateTree(rules)
	# 	else:
	# 		print generateSentence(rules)

