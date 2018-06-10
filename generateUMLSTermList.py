import argparse
import sys
import codecs
from collections import defaultdict
import urllib.request

if __name__ == '__main__':
	selectedTopLevels = "ANAT,CHEM,DISO,GENE,PHYS".split(',')
	filterOut = ['T033']

	parser = argparse.ArgumentParser(description='Generate term list from NCBI gene resource')
	parser.add_argument('--umlsConceptFile', required=True, type=str, help='Path on the MRCONSO.RRF file in UMLS metathesaurus')
	parser.add_argument('--umlsSemanticGroupsFile', required=True, type=str, help='Path on the MRSTY.RRF file in UMLS metathesaurus')
	parser.add_argument('--stopwordsFile',required=True,type=str,help='Stopword file')
	parser.add_argument('--outFile', required=True, type=str, help='Path to output wordlist file')
	args = parser.parse_args()

	print("Loading stopwords...")
	with codecs.open(args.stopwordsFile,'r','utf8') as f:
		stopwords = [ line.strip().lower() for line in f ]
		stopwords = set(stopwords)

	print("Loading semantic group data")
	#semanticGroupIDs = set()
	typeIDToTopLevel = {}
	response = urllib.request.urlopen('https://semanticnetwork.nlm.nih.gov/download/SemGroups.txt')
	responseTxt = response.read().decode('utf-8')
	for line in responseTxt.strip().split('\n'):
		# ACTI|Activities & Behaviors|T052|Activity
		toplevel,_,typeid,_ = line.strip().split('|')
		#if group in defaultGroups:
		#	semanticGroupIDs.add(groupid)
		typeIDToTopLevel[typeid] = toplevel

	print("Filtering CUIDs for semantic types")
	selectedCUIDs = set()
	cuidToTopLevel = defaultdict(set)
	with codecs.open(args.umlsSemanticGroupsFile,'r','utf8') as f:
		for line in f:
			split = line.split('|')
			cuid = split[0]
			typeid = split[1]

			if typeid in filterOut:
				continue
			#if groupid in semanticGroupIDs:
			#	selectedCUIDs.add(cuid)
			#	cuidToType[cuid] = group
			toplevel = typeIDToTopLevel[typeid]
			#assert not cuid in cuidToTopLevel or cuidToTopLevel[cuid] == toplevel, "%s already has type %s" (cuid, cuidToTopLevel[type])
			#assert not cuid in cuidToTopLevel, "%s already has type %s" % (cuid, cuidToTopLevel[cuid])
			cuidToTopLevel[cuid].add(toplevel)

	metathesaurus_singleterm = {}
	metathesaurus_synonyms = defaultdict(list)
	print("Loading metathesaurus...")
	with codecs.open(args.umlsConceptFile,'r','utf8') as f:
		for line in f:
			split = line.split('|')
			cuid = split[0]
			lang = split[1]
			term = split[14]
			if lang != 'ENG':
				continue
			#if not cuid in selectedCUIDs:
			#	continue

			if not cuid in cuidToTopLevel:
				continue

			metathesaurus_synonyms[cuid].append(term)
			if not cuid in metathesaurus_singleterm:
				metathesaurus_singleterm[cuid] = term

	cuids = sorted(list(set(metathesaurus_singleterm.keys())))

	print("Outputting...")
	with codecs.open(args.outFile,'w','utf8') as f:
		for cuid in cuids:
			singleterm = metathesaurus_singleterm[cuid]
			terms = metathesaurus_synonyms[cuid]

			toplevel = sorted(list(cuidToTopLevel[cuid]))

			matchingSelectedTopLevels = any (t in selectedTopLevels for t in toplevel )
			if not matchingSelectedTopLevels:
				continue
			
			toplevelTxt = "|".join(toplevel)

			terms = [ t.lower() for t in terms ]
			terms = [ t for t in terms if not t in stopwords ]
			terms = [ t for t in terms if not "," in t ]
			terms = [ t for t in terms if not ";" in t ]
			terms = [ t for t in terms if len(t) > 3 ]
			terms = sorted(list(set(terms)))

			if len(terms) > 0:
				out = [cuid,toplevelTxt,singleterm,"|".join(terms)]
				f.write("\t".join(out) + "\n")

	print("Done")
