"""
This script is used to build a word-list of relevant cancer specific terms from the Disease Ontology and UMLS Metathesaurus.
"""
import argparse
import sys
import codecs
import pronto
from collections import defaultdict

def augmentTermList(terms):
	"""
	Adds additional spellings and plurals to a list of cancer terms
	
	Args:
		terms (list of strings): List of strings of terms
		
	Returns:
		list of augmente strings
	"""
	
	# Lower case everything (if not already done anyway)
	terms = [ t.lower() for t in terms ]
	
	# A list of short cancer terms that are acceptable (others like ALL are too ambiguous and excluded)
	acceptedShortTerms = ["gbm","aml","crc","hcc","cll"]
	
	# Filter out smaller terms except the allowed ones
	terms = [ t for t in terms if len(t) > 3 or t in acceptedShortTerms ]

	# Filter out terms with various bits of punctuation
	terms = [ t for t in terms if not any ( p in t for p in ',;()[]{}' ) ]

	# Filter out terms that start with "of "
	terms = [ t for t in terms if not t.startswith('of ') ]
	
	# Try the British spelling of tumor
	terms += [ t.replace('tumor','tumour') for t in terms ]

	# Try the alternative spelling of leukemia
	terms += [ t.replace('leukemia','leukaemia') for t in terms ]

	# Add some synonyms
	synonym_groups = [ ['acute lymphocytic leukemia', 'acute lymphoblastic leukemia', 'acute lymphoid leukemia' ] ]
	terms += [ t.replace(a,b) for t in terms for group in synonym_groups for a in group for b in group ]
	
	# Terms that we can add an 'S' to pluralise (if not already included)
	pluralEndings = ["tumor", "tumour", "neoplasm", "cancer", "oma", "emia"]
	
	# Check if any term ends with one of the plural endings, and then pluralise it
	plurals = []
	for t in terms:
		pluralize = any( [ t.endswith(e) for e in pluralEndings ] )

		if pluralize:
			plurals.append(t + "s")
	terms = sorted(set(terms + plurals))

	return terms


def getCUIDs(term):
	"""
	Gets all CUIDs for a given pronto Ontology object (from the xrefs)

	Args:
		term (pronto Ontology): Term from ontology to extract CUIDs for

	Returns:
		list of CUIDs
	"""
	cuids = []
	for xref in term.xrefs:
		if xref.id.startswith('UMLS_CUI'):
			cuid = xref.id[9:]
			cuids.append(cuid)
	return cuids

def getSynonyms(term):
	"""
	Gets all synonyms for a given pronto Ontology object (with IDs removed)

	Args:
		term (pronto Ontology): Term from ontology to extract CUIDs for

	Returns:
		list of synonyms
	"""
	synonyms = []
	for s in term.synonyms:
		if s.scope == 'EXACT':
			synonyms.append(s.description.lower())
	return synonyms

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
	

def main():

	parser = argparse.ArgumentParser(description='Generate term list from Disease Ontology and UMLS Metathesarus for cancer-specific terms')
	parser.add_argument('--diseaseOntologyFile', required=True, type=str, help='Path to the Disease Ontology OBO file')
	parser.add_argument('--cancerStopwords',required=True,type=str,help='File containing cancer terms to ignore')
	parser.add_argument('--umlsConceptFile', required=True, type=str, help='Path on the MRCONSO.RRF file in UMLS metathesaurus')
	parser.add_argument('--customAdditions', required=False, type=str, help='Some custom additions to the wordlist')
	parser.add_argument('--customDeletions', required=False, type=str, help='Some custom deletions from the wordlist')
	parser.add_argument('--outFile', required=True, type=str, help='Path to output wordlist file')
	args = parser.parse_args()

	print("Loading metathesaurus...")
	metathesaurus = loadMetathesaurus(args.umlsConceptFile)
	metathesaurusMainTerm = { terms[0].lower():cuid for cuid,terms in metathesaurus.items() }

	print("Loading disease ontology...")
	ont = pronto.Ontology(args.diseaseOntologyFile)
	cancerRoot = ont.get('DOID:162')

	print("Loading cancer stopwords...")
	with codecs.open(args.cancerStopwords,'r','utf8') as f:
		cancerstopwords = [ line.strip().lower() for line in f ]
		cancerstopwords = set(cancerstopwords)

	id_to_name = {}
	id_to_synonyms = defaultdict(list)
	if args.customAdditions:
		print("Loading additions...")
		with codecs.open(args.customAdditions,'r','utf-8') as f:
			for line in f:
				termid,singleterm,terms = line.strip().split('\t')
				id_to_name[termid] = singleterm
				id_to_synonyms[termid] += terms.split('|')

	customDeletions = defaultdict(list)
	if args.customDeletions:
		print("Loading deletions...")
		with codecs.open(args.customDeletions,'r','utf-8') as f:
			for line in f:
				termid,singleterm,terms = line.strip().split('\t')
				customDeletions[termid] += terms.split('|')

	print("Processing...")

	# Skip down to the children of the cancer term and then find all their descendents (recursive children)
	cancerImmediateChildren = cancerRoot.subclasses(1)
	cancerTypes = [ c for c in cancerRoot.subclasses() if not c in cancerImmediateChildren ]
	for term in cancerTypes:
		# Skip obsolete terms
		if term.obsolete:
			continue

		# Get the CUIDs for this term
		cuids = getCUIDs(term)

		# Check for an exact match with a metathesaurus term
		if term.name.lower() in metathesaurusMainTerm:
			cuids.append(metathesaurusMainTerm[term.name.lower()])
			cuids = sorted(list(set(cuids)))

		# Skip it if the main name is deemed unimportant
		if term.name.lower() in cancerstopwords:
			continue

		# Get the English terms for the metathesaurus
		mmterms = [ metathesaurus[cuid] for cuid in cuids ]

		# Merge the lists together
		mmterms = sum(mmterms, [])

		# Add in the Disease Ontology term (in case it's not already in there)
		mmterms.append(term.name)

		# Add synonyms from the Disease Ontology term
		mmterms += getSynonyms(term)

		# Add in custom additions
		mmterms += id_to_synonyms[term.id]

		# Remove custom deletions
		mmterms = [ mmterm for mmterm in mmterms if not mmterm in customDeletions[term.id] ]

		if not term.id in id_to_name:
			id_to_name[term.id] = term.name
		id_to_synonyms[term.id] = mmterms
	
	allterms = []
	for termid,name in id_to_name.items():
		mmterms = id_to_synonyms[termid]

		# Lowercase everything
		mmterms = [ mmterm.lower() for mmterm in mmterms ]
		
		# Filter out general terms
		mmterms = [ mmterm for mmterm in mmterms if not mmterm in cancerstopwords ]

		# Remove custom deletions
		mmterms = [ mmterm for mmterm in mmterms if not mmterm in customDeletions[termid] ]

		# Add extra spellings and plurals
		mmterms = augmentTermList(mmterms)

		# Remove any duplicates and sort it
		mmterms = sorted(list(set(mmterms)))

		if len(mmterms) > 0:
			allterms.append( (termid, name, "|".join(mmterms)) )

	print("Post-filtering...")
	mapping = defaultdict(list)
	properNames = set()
	for termid, singleterm, termtext in allterms:
		properNames.add(singleterm)
		properNames.add(singleterm+'s') # Deal with plurals

		for term in termtext.split('|'):
			mapping[term].append(singleterm)

	filteredterms = []
	for termid, singleterm, termtext in allterms:
		terms = termtext.split('|')
		if 'carcinoma' in singleterm:
			terms = [ t for t in terms if not ('cancer' in t and len(mapping[t]) > 1) ]

		terms = [ t for t in terms if t==singleterm or t==(singleterm+'s') or not (t in properNames) ]
		termtext = "|".join(terms)

		if termtext != '':
			filteredterms.append( (termid, singleterm, termtext) )
	allterms = filteredterms

	allterms = sorted(allterms)
	print("Generated %d terms" % len(allterms))

	print("Outputting to file...")
	with codecs.open(args.outFile,'w','utf8') as outF:
		for termid, singleterm, termtext in allterms:
			line = u"%s\t%s\t%s\n" % (termid,singleterm,termtext)
			outF.write(line)

	print("Successfully output to %s" % args.outFile)

if __name__ == '__main__':
	main()

