import random
import timeit
import pickle
from optparse import OptionParser

""" Fill the bag of words.
"""

incorrect_parses = 0


class NoSuchSyllable(Exception):
	pass

def select_weighted(dct):
	total_weight = 0
	for k, v in dct.items():
		total_weight += v
	rand_val = random.random()*total_weight
	total = 0
	for k, v in dct.items():
		total += v
		if rand_val <= total:
			return k
	assert False, 'unreachable'

class TrieNode():
	def __init__(self, char, head_pointer = None):
		if head_pointer == None:
			self.head_pointer = self
		else:
			self.head_pointer = head_pointer
		self.char = char
		self.children = {}
		self.weighted_children = [] # not guaranteed to be up-to-date
		self.weighted_up_to_date = True
		self.syllable_finished = 0
		self.word_finished = 0
		self.next_syllables = {}
		self.weighted_next_syllables = {}
		self.counter = 1

	def _add_child(self, child_char):
		self.weighted_up_to_date = False
		if child_char in self.children:
			self.children[child_char]._increment_counter()
		else:
			self.children[child_char] = TrieNode(child_char, self.head_pointer)

	def clear_weights(self):
		self.counter = 1
		if self.syllable_finished > 0:
			self.syllable_finished = 1
		if self.word_finished > 0:
			self.word_finished = 1
		for child_char in self.children:
			self.children[child_char].clear_weights()

	def _increment_counter(self):
		self.counter += 1

	def add_suffix(self, suffix):
		if len(suffix) > 0:
			next_char = suffix.pop(0)
			self._add_child(next_char)
			self.children[next_char].add_suffix(suffix)
		else:
			self.syllable_finished += 1

	def _add_next_syllable(self, next_char, weight=1):
		try:
			next_syllable_head = self.head_pointer.children[next_char]
		except KeyError:
			# print("error: no syllables starting with %s" % next_char)
			raise NoSuchSyllable()
		self.next_syllables[next_char] = next_syllable_head
		if next_char not in self.weighted_next_syllables:
			self.weighted_next_syllables[next_char] = 0
		self.weighted_next_syllables[next_char] += weight

	def _extend_syllable(self, start_of_next_syllable, suffix, weight=1):
		global incorrect_parses
		try:
			self.children[start_of_next_syllable].add_word(suffix, weight)
		except KeyError:
			incorrect_parses += 1
			# print("error: this syllable got chopped wrong")
			# print("I am %s, so far I have %s then %s remaining" % (self.char, start_of_next_syllable, suffix))


	def add_word(self, suffix, weight=1):
		if len(suffix) == 0:
			self.word_finished += weight
		else:
			# might have to choose whether to "end" the syllable here.
			# for now defaulting to yes
			start_of_next_syllable = suffix.pop(0)

			if self.syllable_finished > 0:
				# I can end this syllable
				try:
					self._add_next_syllable(start_of_next_syllable, weight)
					self.head_pointer.children[start_of_next_syllable].add_word(suffix, weight)
				except NoSuchSyllable:
					self._extend_syllable(start_of_next_syllable, suffix, weight)
			else:
				# I cannot end this syllable
				self._extend_syllable(start_of_next_syllable, suffix, weight)


	def populate_weighted_children(self):
		new_weighted_children = []
		for child_char in self.children:
			child = self.children[child_char]
			new_weighted_children.append((child.counter, child))
		self.weighted_children = new_weighted_children
		self.weighted_up_to_date = True

	def choose_random_child(self):
		if not self.weighted_up_to_date:
			self.populate_weighted_children()

		total_counter = self.syllable_finished
		for child in self.weighted_children:
			total_counter += child[0]
		r = random.randrange(total_counter)
		for child in self.weighted_children:
			r -= child[0]
			if r <= 0:
				return child[1]
		return None # syllable end

	def generate_random_syllable(self, sofar=[]):
		random_child = self.choose_random_child()
		if random_child is None:
			sofar.append(self.char)
			return sofar
		else:
			sofar.append(self.char)
			return random_child.generate_random_syllable(sofar)

	def generate_random_word(self, sofar=[]):
		random_child = self.choose_random_child()
		if random_child is None:
			sofar.append(self.char)
			if self.word_finished > 0:
				self.weighted_next_syllables[None] = self.word_finished

			if len(self.weighted_next_syllables) == 0:
				# print("error: I am not supposed to finish a word, but i am the end of a syllable")
				next_syllable_char = None
			else:
				# print("selecting a new syllable!")
				next_syllable_char = select_weighted(self.weighted_next_syllables)
			if next_syllable_char is None:
				# print("ending word")
				return sofar
			else:
				return self.next_syllables[next_syllable_char].generate_random_word(sofar)
		else:
			sofar.append(self.char)
			return random_child.generate_random_word(sofar)


class Morphemes():
	def __init__(self):
		self.morphemes = TrieNode('@')

	def find_morphemes(self, syllables_file, output_file):
		nfd = open(syllables_file)
		syllables = nfd.readlines()
		syllables = [line.strip() for line in syllables]
		nfd.close()

		start = timeit.default_timer()

		for syllable in syllables:
			# print("working on %s" % syllable)
			syllable = syllable.split(' ')
			self.morphemes.add_suffix(syllable)

		elapsed = timeit.default_timer() - start
		print("time to parse syllables: %s" % (elapsed,))
		# self.pickle_morphemes()

	def populate_words(self, words_file):
		self.morphemes.clear_weights()
		wfd = open(words_file)
		words = wfd.readlines()
		words = [line.strip() for line in words]
		wfd.close()

		start = timeit.default_timer()

		for word in words:
			word = word.split(' ')
			self.morphemes.add_word(word)

		elapsed = timeit.default_timer() - start
		print("time to parse dictionary: %s" % (elapsed,))
		print("number of incorrect parses: %s out of %s, %s pct" % (incorrect_parses,len(words), 100*float(incorrect_parses)/len(words)))

	def apply_weights(self, words_file):
		# for now, use inverse length to weight things
		self.morphemes.clear_weights()
		wfd = open(words_file)
		words = wfd.readlines()
		words = [line.strip() for line in words]
		wfd.close()

		start = timeit.default_timer()

		for word in words:
			word = word.split(' ')
			self.morphemes.add_word(word, 1.0/len(word))

		elapsed = timeit.default_timer() - start
		print("time to apply weights: %s" % (elapsed,))

	def time_word_generation(self, n):
		wds = []

		start = timeit.default_timer()
		for i in range(n):
			wds.append(self.morphemes.generate_random_word([]))

		elapsed = timeit.default_timer() - start
		print("time to generate %s words: %s" % (n, elapsed))
		wdspersec = n/elapsed
		print("words per sec = %s" % (wdspersec,))

	def pickle_morphemes(self, output_pickle="out.p"):
		pickle.dump(self.morphemes, open(output_pickle, "wb"))

	def translate_to_ipa(self, output_file, number_tests):
		# Load IPA to Syllable doc and build ipa/syllable dict and vocab/consonant ipa lists
		translate = open('IPA_to_syllables.txt')
		sounds = translate.readlines()
		sounds = [line.strip() for line in sounds]
		translate.close()

		syllableToIpa = {}
		vowels = []
		consonants = []

		onVowel = True
		for sound in sounds:
			if (len(sound.split()) > 1):
				sound = sound.split()
				ipa = sound[0]
				syllable = sound[1]
				example = sound[2:]
				# print ipa, syllable
			else:
				onVowel = False
			if onVowel:
				syllableToIpa[syllable] = ipa
				vowels.append(ipa)
			else:
				syllableToIpa[syllable] = ipa
				consonants.append(ipa)


		ipa = open(output_file + ".ipa","w")
		beep = open(output_file + ".beep", "w")
		ipa.write("For speech synthesis, copy and paste examples into: https://itinerarium.github.io/phoneme-synthesis/\n\n")
		output = []
		i = 0

		while i < number_tests:
			hasVowel = False
			beep_word = self.morphemes.generate_random_word([])[1:]
			for char in beep_word:
				if syllableToIpa[char] in vowels:
					hasVowel = True
			ipa_word = ''.join([syllableToIpa[char] for char in beep_word])
			beep_word = ''.join(beep_word)

			if hasVowel:
				i += 1
				ipa.write(ipa_word + '\n')
				beep.write(beep_word + '\n')
				print("%s\t\t%s" % (ipa_word, beep_word))
		ipa.close()
		beep.close()



if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-s", "--syllables", dest="syllables",
		help="input list of syllables", metavar="file")
	parser.add_option("-w", "--words", dest="words",
		help="input list of words", metavar="file")
	parser.add_option("-o", "--output", dest="output",
		help="file to output generated words", metavar="file")
	parser.add_option("-n", "--numberTests", dest="exampleN",
		help="number of words to generate", default=50, metavar="int")
	parser.add_option("-b", "--benchmarkTests", dest="benchmarkN",
		help="number of words to generate for benchmarking", default=100000, metavar="int")
	(options, args) = parser.parse_args()


	if options.syllables is None or options.output is None or options.words is None:
		parser.print_help()
		exit(1)

	print "reading syllables file: %s" % (options.syllables)
	print "reading words file: %s" % (options.words)
	print "outputting to file: %s" % (options.output)
	morphs = Morphemes()
	morphs.find_morphemes(options.syllables, str(options.output))
	morphs.populate_words(options.words)
	morphs.apply_weights(options.words)
	morphs.time_word_generation(options.benchmarkN)
	morphs.translate_to_ipa(options.output, int(options.exampleN))
