import random
import pickle
from optparse import OptionParser

""" Fill the bag of words.
"""

def select_weighted( d ):
   # calculate total
   total = 0
   for key in d:
      total = total + d[key]
   accept_prob = float( 1.0 / total )

   # pick a weighted value from d
   n_seen = 0
   for key in d:
      current_key = key
      for val in d[key]:
         dice_roll = random.random()
         accept_prob = float( 1.0 / ( total - n_seen ) )
         n_seen = n_seen + 1
         if dice_roll <= accept_prob:
            return current_key

class TrieNode():
	def __init__(self, char, head_pointer = None):
		if head_pointer = None:
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
			self.children[child_char] = TrieNode(child_char)

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

	def _add_next_syllable(self, next_char):
		try:
			next_syllable_head = self.head_pointer.children[next_char]
		except KeyError:
			print("error: no syllables starting with %s" % next_char)
		self.next_syllables[next_char] = next_syllable_head
		if next_char not in self.weighted_next_syllables:
			self.weighted_next_syllables[next_char] = 1
		self.weighted_next_syllables[next_char] += 1

	def add_word(self, suffix):
		if len(suffix) == 0:
			self.word_finished += 1
		else:
			# might have to choose whether to "end" the syllable here.
			# for now defaulting to yes
			start_of_next_syllable = suffix.pop(0)

			if self.syllable_finished > 0:
				self._add_next_syllable(start_of_next_syllable)
				self.head_pointer.children[start_of_next_syllable].add_word(suffix)
			else:
				try:
					self.children[start_of_next_syllable].add_word(suffix)
				except KeyError:
					print("error: this syllable got chopped wrong")


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
			next_syllable = select_weighted(self.weighted_next_syllables)
			if next_syllable is None:
				sofar
			else:
				return next_syllable.generate_random_word(sofar)
		else:
			sofar.append(self.char)
			return random_child.generate_random_word(sofar)


class Morphemes():
	def __init__(self, max_length):
		self.morphemes = TrieNode('@')

	def find_morphemes(self, syllables_file, output_file):
		nfd = open(syllables_file)
		syllables = nfd.readlines()
		syllables = [line.strip() for line in syllables]
		nfd.close()

		for syllable in syllables:
			# print("working on %s" % syllable)
			syllable = syllable.split(' ')
			self.morphemes.add_suffix(syllable)

		print self.morphemes
		print self.morphemes.generate_random_syllable()
		self.pickle_morphemes()
		# self.write_morphemes(output_file, start_char, end_char)

	def write_morphemes(self, output_file):
		print("writing output to %s" % output_file)
		with open(output_file, 'w') as f:
			f.write("START: %s\nEND: %s\n\n" % (start_char, end_char))
			for morpheme in self.morphemes:
				next_list_str = [n + ': ' + str(self.morphemes[morpheme][n]) for n in self.morphemes[morpheme]]
				s = ', '.join(next_list_str)
				f.write(morpheme + '\t[')
				f.write(s)
				f.write(']\n')
		print("done writing to %s" % output_file)

	def pickle_morphemes(self, output_pickle="out.p"):
		pickle.dump(self.morphemes, open(output_pickle, "wb"))



if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-n", "--syllables", dest="syllables",
		help="input list of syllables", metavar="file")
	parser.add_option("-o", "--output", dest="output",
		help="input list of syllables", metavar="file")
	parser.add_option("-l", "--length", dest="length",
		help="max syllable length", default=7, metavar="int")

	(options, args) = parser.parse_args()
	options.length = int(options.length)


	if options.syllables is None or options.output is None:
		parser.print_help()
		exit(1)

	print "reading syllables file: %s" % (options.syllables)
	print "outputting to file: %s" % (options.output)
	print "max morpheme length: %s" % (options.length)
	morphs = Morphemes(options.length)
	morphs.find_morphemes(options.syllables, str(options.output))