"""
This script is used to build a word-list of relevant cancer specific terms from the Disease Ontology and UMLS Metathesaurus.
"""
import argparse
import sys
import codecs
import pronto
from collections import defaultdict

def tidyTermList(terms):
	"""
	Does a little bit of extra tidying to a term list
	
	Args:
		terms (list of strings): List of strings of terms
		
	Returns:
		list of augmente strings
	"""
	
	# Lower case everything (if not already done anyway)
	terms = [ t.lower().strip() for t in terms ]
	
	# Remove short terms
	terms = [ t for t in terms if len(t) > 3 ]

	# Remove terms that start with hyphens
	terms = [ t for t in terms if not t.startswith('-') ]

	# List of characters that are not allowed in terms
	filterChars = [ ',', '(', ')', '[', ']', '{', '}' ]

	# Filter out terms with a comma
	for char in filterChars:
		terms = [ t for t in terms if not char in t ]
	
	return terms

def findTerm(ont,name):
	"""
	Searches an ontology for a specific term name and returns the first hit

	Args:
		ont (pronto Ontology): Ontology to search
		name (str): Search query

	Returns:
		pronto Ontology: Term that matched name or None if not found
	"""
	for term in ont:
		if term.name == name:
			return term
	return None



def getCUIDs(term):
	"""
	Gets all CUIDs for a given pronto Ontology object (from the xrefs)

	Args:
		term (pronto Ontology): Term from ontology to extract CUIDs for

	Returns:
		list of CUIDs
	"""
	cuids = []
	if 'xref' in term.other:
		for xref in term.other['xref']:
			if xref.startswith('UMLS'):
				firstpart = xref.split()[0]
				cuid = firstpart[5:]
				cuids.append(cuid)
			elif xref.startswith('UMLS_CUI'):
				firstpart = xref.split()[0]
				cuid = firstpart[9:]
				cuids.append(cuid)
	return cuids

def loadMetathesaurus(filename):
	"""
	Loads the UMLS metathesaurus into a dictionary where CUID relates to a set of terms. Only English terms are included

	Args:
		filename (str): Filename of UMLS Concept file (MRCONSO.RRF)

	Returns:
		Dictionary where each key (CUID) points to a list of strings (terms)
	"""
	meta = defaultdict(list)
	with codecs.open(filename,'r','utf8') as f:
		for line in f:
			split = line.split('|')
			cuid = split[0]
			lang = split[1]
			term = split[14]
			if lang != 'ENG':
				continue
			meta[cuid].append(term)
	return meta
	
if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Generate term list from an ontology file and UMLS Metathesarus for cancer-specific terms')
	parser.add_argument('--ontologyFile', required=True, type=str, help='Path to the Disease Ontology OBO file')
	parser.add_argument('--stopwordsFile',required=True,type=str,help='File containing terms to ignore')
	parser.add_argument('--umlsConceptFile', required=True, type=str, help='Path on the MRCONSO.RRF file in UMLS metathesaurus')
	parser.add_argument('--outFile', required=True, type=str, help='Path to output wordlist file')
	args = parser.parse_args()

	print "Loading metathesaurus..."
	metathesaurus = loadMetathesaurus(args.umlsConceptFile)

	print "Loading disease ontology..."
	ont = pronto.Ontology(args.ontologyFile)
	#cancerTerm = findTerm(ont,'cancer')

	print "Loading stopwords..."
	with codecs.open(args.stopwordsFile,'r','utf8') as f:
		stopwords = [ line.strip().lower() for line in f ]
		stopwords = set(stopwords)

	print "Processing"
	allterms = []
	# Skip down to the grandchildren of the cancer term and then find all their descendents (recursive children)
	count = 0
	for term in ont:
		# Get the CUIDs for this term
		cuids = getCUIDs(term)

		# Get the English terms for the metathesaurus
		mmterms = [ metathesaurus[cuid] for cuid in cuids ]

		# Merge the lists together
		mmterms = sum(mmterms, [])

		# Add in the Disease Ontology term (in case it's not already in there)
		mmterms.append(term.name)

		# Lowercase everything
		mmterms = [ mmterm.lower() for mmterm in mmterms ]
		
		# Add extra spellings and plurals
		mmterms = tidyTermList(mmterms)

		# Filter out general terms
		mmterms = [ mmterm for mmterm in mmterms if not mmterm in stopwords ]

		# Do some trimming
		mmterms = [ mmterm.strip() for mmterm in mmterms ]

		# Remove any duplicates and sort it
		mmterms = sorted(list(set(mmterms)))

		# Remove any empties
		mmterms = [ mmterm for mmterm in mmterms if len(mmterm) > 0 ]

		if len(mmterms) > 0:
			# Then output to the file
			tmpterm = (term.id, u"|".join(mmterms))
			allterms.append(tmpterm)
	
	allterms = sorted(allterms)
	print "Generated %d terms" % len(allterms)
	
	print "Outputting to file..."
	with codecs.open(args.outFile,'w','utf8') as outF:
		for termid, termtext in allterms:
			line = u"%s\t%s\n" % (termid,termtext)
			outF.write(line)
	
	print "Successfully output to %s" % args.outFile

		

