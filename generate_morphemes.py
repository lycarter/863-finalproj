from optparse import OptionParser

""" Fill the bag of words.
"""
def find_morphemes(names_file, output_file, length):
	nfd = open(names_file)
	names = nfd.readlines()
	names = [line.strip() for line in names]
	nfd.close()

	morphemes = {}

	for name in names:
		# print("working on %s" % name)
		name = name.upper()
		for j in range(1, length+1):
			i = 0
			while i+j <= len(name):
				# find morpheme
				potential_morpheme = name[i:i+j]
				potential_next_morphemes = []

				# find next morphemes
				if i+j == len(name):
					potential_next_morphemes.append('0')
				else:
					for k in range(1, length+1):
						if i+j+k <= len(name):
							potential_next_morphemes.append(name[i+j:i+j+k])
						else:
							break

				# add to bag of words
				if potential_morpheme not in morphemes:
					morphemes[potential_morpheme] = {}
				for next_morpheme in potential_next_morphemes:
					if next_morpheme not in morphemes[potential_morpheme]:
						morphemes[potential_morpheme][next_morpheme] = 0
					morphemes[potential_morpheme][next_morpheme] += 1
				i += 1

	print morphemes
	write_morphemes(morphemes, output_file)

def write_morphemes(morphemes, output_file):
	print("writing output to %s" % output_file)
	with open(output_file, 'w') as f:
		for morpheme in morphemes:
			next_list_str = [n + ': ' + str(morphemes[morpheme][n]) for n in morphemes[morpheme]]
			s = ', '.join(next_list_str)
			f.write(morpheme + '\t[')
			f.write(s)
			f.write(']\n')
	print("done writing to %s" % output_file)





if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-n", "--names", dest="names",
		help="input list of names", metavar="file")
	parser.add_option("-o", "--output", dest="output",
		help="input list of names", metavar="file")
	parser.add_option("-l", "--length", dest="length",
		help="max morpheme length", default=4, metavar="int")

	(options, args) = parser.parse_args()
	options.length = int(options.length)

	if options.names is None or options.output is None:
		parser.print_help()
		exit(1)

	print "reading names file: %s" % (options.names)
	print "outputting to file: %s" % (options.output)
	print "max morpheme length: %s" % (options.length)
	find_morphemes(options.names, options.output, options.length)